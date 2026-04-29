"""
念念 - proactive路由
"""
from fastapi import APIRouter, Depends, Header, HTTPException, Request, UploadFile, File
from fastapi.responses import Response, FileResponse
from typing import Any, Dict, List, Optional
import sqlite3
import json
import uuid
import os
import base64
import mimetypes
from pathlib import Path
from datetime import datetime, timedelta, timezone

from ..app_helpers import *  # noqa: F401,F403

router = APIRouter(tags=["proactive"])

def generate_proactive_payload_sync(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    loved_one_id: str,
    reason: str,
    preferred_channel: str,
    preferred_message_mode: str,
    phone_number: str,
    source_kind: str,
    source_id: Optional[str],
    scheduled_for: Optional[str],
) -> Optional[dict]:
    return asyncio.run(
        generate_proactive_payload(
            conn,
            user_id=user_id,
            loved_one_id=loved_one_id,
            reason=reason,
            preferred_channel=preferred_channel,
            preferred_message_mode=preferred_message_mode,
            phone_number=phone_number,
            source_kind=source_kind,
            source_id=source_id,
            scheduled_for=scheduled_for,
        )
    )




@router.get("/api/proactive/feed")
async def get_proactive_feed(limit: int = 20, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM proactive_events
            WHERE user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (current_user["id"], limit),
        ).fetchall()
        unread_count = conn.execute(
            "SELECT COUNT(*) FROM proactive_events WHERE user_id = ? AND consumed_at IS NULL",
            (current_user["id"],),
        ).fetchone()[0]
        flows = conn.execute(
            """
            SELECT pf.*, lo.name AS loved_one_name
            FROM proactive_flows pf
            JOIN loved_ones lo ON lo.id = pf.loved_one_id
            WHERE pf.user_id = ?
            ORDER BY lo.updated_at DESC
            """,
            (current_user["id"],),
        ).fetchall()
    return {
        "events": [serialize_proactive_event(conn, row) for row in rows],
        "unread_count": unread_count,
        "flows": [
            {
                **serialize_proactive_flow(row),
                "loved_one_id": row["loved_one_id"],
                "loved_one_name": row["loved_one_name"],
            }
            for row in flows
        ],
    }


@router.get("/api/proactive/settings/{loved_one_id}")
async def get_proactive_settings(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        contact = get_user_contact_snapshot(conn, current_user["id"])
        subscription = get_subscription_snapshot(conn, current_user["id"])
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        bridge_status = build_call_bridge_status(loved_one=loved_one, proactive_flow=serialize_proactive_flow(flow), subscription=subscription)
    return {
        "loved_one_id": loved_one_id,
        "flow": serialize_proactive_flow(flow),
        "contact": contact,
        "call_bridge_configured": bridge_status["configured"],
        "call_bridge": bridge_status,
    }




@router.get("/api/proactive/settings/{loved_one_id}")
async def get_proactive_settings(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        contact = get_user_contact_snapshot(conn, current_user["id"])
        subscription = get_subscription_snapshot(conn, current_user["id"])
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        bridge_status = build_call_bridge_status(loved_one=loved_one, proactive_flow=serialize_proactive_flow(flow), subscription=subscription)
    return {
        "loved_one_id": loved_one_id,
        "flow": serialize_proactive_flow(flow),
        "contact": contact,
        "call_bridge_configured": bridge_status["configured"],
        "call_bridge": bridge_status,
    }


@router.post("/api/proactive/settings/{loved_one_id}")
async def save_proactive_settings(
    loved_one_id: str,
    payload: ProactiveSettingsPayload,
    current_user: dict = Depends(get_current_user),
):
    if payload.loved_one_id != loved_one_id:
        raise HTTPException(status_code=400, detail="档案标识不一致")
    cadence = payload.cadence if payload.cadence in {"daily", "weekly"} else "daily"
    preferred_channel = normalize_proactive_channel(payload.preferred_channel)
    preferred_message_mode = normalize_proactive_message_mode(payload.preferred_message_mode)
    preferred_weekday = payload.preferred_weekday if cadence == "weekly" else None
    phone_number = normalize_phone_number(payload.phone_number)

    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        next_run_at = (
            compute_next_run_at(cadence, payload.preferred_time, preferred_weekday, payload.timezone)
            if payload.enabled
            else None
        )
        conn.execute(
            """
            UPDATE proactive_flows
            SET enabled = ?, cadence = ?, preferred_time = ?, preferred_weekday = ?, preferred_channel = ?,
                preferred_message_mode = ?, phone_number = ?, timezone = ?, next_run_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                int(payload.enabled),
                cadence,
                payload.preferred_time,
                preferred_weekday,
                preferred_channel,
                preferred_message_mode,
                phone_number or None,
                payload.timezone or DEFAULT_TIMEZONE,
                next_run_at,
                now_iso(),
                flow["id"],
            ),
        )
        conn.execute(
            """
            UPDATE users
            SET phone_number = ?, proactive_opt_in = ?, preferred_contact_channel = ?, preferred_contact_time = ?,
                timezone = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                phone_number or None,
                int(payload.enabled),
                preferred_channel,
                payload.preferred_time,
                payload.timezone or DEFAULT_TIMEZONE,
                now_iso(),
                current_user["id"],
            ),
        )
        saved = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        contact = get_user_contact_snapshot(conn, current_user["id"])
        subscription = get_subscription_snapshot(conn, current_user["id"])
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        bridge_status = build_call_bridge_status(
            loved_one=loved_one,
            proactive_flow=serialize_proactive_flow(saved),
            subscription=subscription,
        )
    return {
        "status": "saved",
        "loved_one_id": loved_one_id,
        "flow": serialize_proactive_flow(saved),
        "contact": contact,
        "call_bridge_configured": bridge_status["configured"],
        "call_bridge": bridge_status,
    }




@router.post("/api/proactive/settings/{loved_one_id}")
async def save_proactive_settings(
    loved_one_id: str,
    payload: ProactiveSettingsPayload,
    current_user: dict = Depends(get_current_user),
):
    if payload.loved_one_id != loved_one_id:
        raise HTTPException(status_code=400, detail="档案标识不一致")
    cadence = payload.cadence if payload.cadence in {"daily", "weekly"} else "daily"
    preferred_channel = normalize_proactive_channel(payload.preferred_channel)
    preferred_message_mode = normalize_proactive_message_mode(payload.preferred_message_mode)
    preferred_weekday = payload.preferred_weekday if cadence == "weekly" else None
    phone_number = normalize_phone_number(payload.phone_number)

    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        next_run_at = (
            compute_next_run_at(cadence, payload.preferred_time, preferred_weekday, payload.timezone)
            if payload.enabled
            else None
        )
        conn.execute(
            """
            UPDATE proactive_flows
            SET enabled = ?, cadence = ?, preferred_time = ?, preferred_weekday = ?, preferred_channel = ?,
                preferred_message_mode = ?, phone_number = ?, timezone = ?, next_run_at = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                int(payload.enabled),
                cadence,
                payload.preferred_time,
                preferred_weekday,
                preferred_channel,
                preferred_message_mode,
                phone_number or None,
                payload.timezone or DEFAULT_TIMEZONE,
                next_run_at,
                now_iso(),
                flow["id"],
            ),
        )
        conn.execute(
            """
            UPDATE users
            SET phone_number = ?, proactive_opt_in = ?, preferred_contact_channel = ?, preferred_contact_time = ?,
                timezone = ?, updated_at = ?
            WHERE id = ?
            """,
            (
                phone_number or None,
                int(payload.enabled),
                preferred_channel,
                payload.preferred_time,
                payload.timezone or DEFAULT_TIMEZONE,
                now_iso(),
                current_user["id"],
            ),
        )
        saved = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        contact = get_user_contact_snapshot(conn, current_user["id"])
        subscription = get_subscription_snapshot(conn, current_user["id"])
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        bridge_status = build_call_bridge_status(
            loved_one=loved_one,
            proactive_flow=serialize_proactive_flow(saved),
            subscription=subscription,
        )
    return {
        "status": "saved",
        "loved_one_id": loved_one_id,
        "flow": serialize_proactive_flow(saved),
        "contact": contact,
        "call_bridge_configured": bridge_status["configured"],
        "call_bridge": bridge_status,
    }




@router.post("/api/proactive/trigger-now/{loved_one_id}")
async def trigger_proactive_now(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        payload = await generate_proactive_payload(
            conn,
            user_id=current_user["id"],
            loved_one_id=loved_one_id,
            reason="用户希望现在就收到一次主动联系。",
            preferred_channel=flow["preferred_channel"],
            preferred_message_mode=flow["preferred_message_mode"],
            phone_number=flow["phone_number"] or "",
            source_kind="manual",
            source_id=flow["id"],
            scheduled_for=now_iso(),
        )
        if not payload:
            raise HTTPException(status_code=500, detail="主动联系生成失败")
        event_id = str(uuid.uuid4())
        metadata = {
            "reason": payload["reason"],
            "manual": True,
            "requested_message_mode": payload["preferred_message_mode"],
            "actual_message_mode": payload["actual_message_mode"],
        }
        if payload.get("fallback_reason"):
            metadata["provider_note"] = payload["fallback_reason"]
        status = "ready"
        if payload["channel"] == "phone":
            status, provider_meta = dispatch_outbound_call(
                event_id=event_id,
                phone_number=payload["phone_number"],
                loved_one=payload["loved_one"],
                message_text=payload["message_text"],
                audio_url=payload["audio_url"],
            )
            metadata.update(provider_meta)
        create_proactive_event(
            conn,
            event_id=event_id,
            user_id=current_user["id"],
            loved_one_id=loved_one_id,
            flow_id=flow["id"],
            source_kind="manual",
            source_id=flow["id"],
            event_type=payload["event_type"],
            channel=payload["channel"],
            status=status,
            title=f"{payload['loved_one']['name']} 主动联系了你",
            message_text=payload["message_text"],
            audio_asset_id=payload["audio_asset_id"],
            video_asset_id=payload["video_asset_id"],
            scheduled_for=now_iso(),
            metadata=metadata,
        )
        row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
    return {"status": "created", "event": serialize_proactive_event(conn, row)}


@router.post("/api/proactive/test-call/{loved_one_id}")
async def trigger_proactive_test_call(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        if not flow["phone_number"]:
            raise HTTPException(status_code=400, detail="请先填写接听手机号")
        payload = await generate_proactive_payload(
            conn,
            user_id=current_user["id"],
            loved_one_id=loved_one_id,
            reason="测试电话外呼",
            preferred_channel="phone",
            preferred_message_mode="voice",
            phone_number=flow["phone_number"],
            source_kind="test_call",
            source_id=flow["id"],
            scheduled_for=now_iso(),
        )
        if not payload:
            raise HTTPException(status_code=500, detail="测试外呼生成失败")
        event_id = str(uuid.uuid4())
        metadata = {
            "reason": payload["reason"],
            "test_call": True,
            "requested_message_mode": payload["preferred_message_mode"],
            "actual_message_mode": payload["actual_message_mode"],
        }
        status, provider_meta = dispatch_outbound_call(
            event_id=event_id,
            phone_number=payload["phone_number"],
            loved_one=payload["loved_one"],
            message_text=payload["message_text"],
            audio_url=payload["audio_url"],
        )
        metadata.update(provider_meta)
        create_proactive_event(
            conn,
            event_id=event_id,
            user_id=current_user["id"],
            loved_one_id=loved_one_id,
            flow_id=flow["id"],
            source_kind="test_call",
            source_id=flow["id"],
            event_type=payload["event_type"],
            channel="phone",
            status=status,
            title=f"{payload['loved_one']['name']} 测试外呼",
            message_text=payload["message_text"],
            audio_asset_id=payload["audio_asset_id"],
            video_asset_id=payload["video_asset_id"],
            scheduled_for=now_iso(),
            metadata=metadata,
        )
        row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
    return {"status": "created", "event": serialize_proactive_event(conn, row)}




@router.post("/api/proactive/test-call/{loved_one_id}")
async def trigger_proactive_test_call(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        flow = get_proactive_flow_row(conn, current_user["id"], loved_one_id)
        if not flow["phone_number"]:
            raise HTTPException(status_code=400, detail="请先填写接听手机号")
        payload = await generate_proactive_payload(
            conn,
            user_id=current_user["id"],
            loved_one_id=loved_one_id,
            reason="测试电话外呼",
            preferred_channel="phone",
            preferred_message_mode="voice",
            phone_number=flow["phone_number"],
            source_kind="test_call",
            source_id=flow["id"],
            scheduled_for=now_iso(),
        )
        if not payload:
            raise HTTPException(status_code=500, detail="测试外呼生成失败")
        event_id = str(uuid.uuid4())
        metadata = {
            "reason": payload["reason"],
            "test_call": True,
            "requested_message_mode": payload["preferred_message_mode"],
            "actual_message_mode": payload["actual_message_mode"],
        }
        status, provider_meta = dispatch_outbound_call(
            event_id=event_id,
            phone_number=payload["phone_number"],
            loved_one=payload["loved_one"],
            message_text=payload["message_text"],
            audio_url=payload["audio_url"],
        )
        metadata.update(provider_meta)
        create_proactive_event(
            conn,
            event_id=event_id,
            user_id=current_user["id"],
            loved_one_id=loved_one_id,
            flow_id=flow["id"],
            source_kind="test_call",
            source_id=flow["id"],
            event_type=payload["event_type"],
            channel="phone",
            status=status,
            title=f"{payload['loved_one']['name']} 测试外呼",
            message_text=payload["message_text"],
            audio_asset_id=payload["audio_asset_id"],
            video_asset_id=payload["video_asset_id"],
            scheduled_for=now_iso(),
            metadata=metadata,
        )
        row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
    return {"status": "created", "event": serialize_proactive_event(conn, row)}


@router.post("/api/proactive/events/{event_id}/consume")
async def consume_proactive_event(event_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM proactive_events WHERE id = ? AND user_id = ?",
            (event_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        conn.execute(
            "UPDATE proactive_events SET consumed_at = COALESCE(consumed_at, ?), status = CASE WHEN status = 'ready' THEN 'completed' ELSE status END WHERE id = ?",
            (now_iso(), event_id),
        )
        updated = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
    return {"status": "consumed", "event": serialize_proactive_event(conn, updated)}




@router.post("/api/proactive/events/{event_id}/consume")
async def consume_proactive_event(event_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM proactive_events WHERE id = ? AND user_id = ?",
            (event_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        conn.execute(
            "UPDATE proactive_events SET consumed_at = COALESCE(consumed_at, ?), status = CASE WHEN status = 'ready' THEN 'completed' ELSE status END WHERE id = ?",
            (now_iso(), event_id),
        )
        updated = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
    return {"status": "consumed", "event": serialize_proactive_event(conn, updated)}


@router.post("/api/proactive/events/{event_id}/delivery")
async def update_proactive_delivery(event_id: str, request: Request):
    if not OUTBOUND_CALL_WEBHOOK_TOKEN:
        raise HTTPException(status_code=403, detail="当前未配置外呼回调令牌")
    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {OUTBOUND_CALL_WEBHOOK_TOKEN}":
        raise HTTPException(status_code=403, detail="外呼回调校验失败")
    payload = await request.json()
    status = payload.get("status", "delivered")
    metadata = payload.get("metadata") or {}
    with get_db() as conn:
        row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        current_meta = json.loads(row["metadata_json"] or "{}")
        current_meta.update(metadata)
        conn.execute(
            "UPDATE proactive_events SET status = ?, delivered_at = COALESCE(delivered_at, ?), metadata_json = ? WHERE id = ?",
            (status, now_iso(), json.dumps(current_meta, ensure_ascii=False), event_id),
        )
    return {"status": "ok"}




@router.post("/api/proactive/events/{event_id}/delivery")
async def update_proactive_delivery(event_id: str, request: Request):
    if not OUTBOUND_CALL_WEBHOOK_TOKEN:
        raise HTTPException(status_code=403, detail="当前未配置外呼回调令牌")
    auth = request.headers.get("authorization", "")
    if auth != f"Bearer {OUTBOUND_CALL_WEBHOOK_TOKEN}":
        raise HTTPException(status_code=403, detail="外呼回调校验失败")
    payload = await request.json()
    status = payload.get("status", "delivered")
    metadata = payload.get("metadata") or {}
    with get_db() as conn:
        row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        current_meta = json.loads(row["metadata_json"] or "{}")
        current_meta.update(metadata)
        conn.execute(
            "UPDATE proactive_events SET status = ?, delivered_at = COALESCE(delivered_at, ?), metadata_json = ? WHERE id = ?",
            (status, now_iso(), json.dumps(current_meta, ensure_ascii=False), event_id),
        )
    return {"status": "ok"}


@router.get("/api/bridge/status")
async def get_call_bridge_status_endpoint(
    loved_one_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        if not loved_one_id:
            return build_call_bridge_status()
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        proactive_flow = serialize_proactive_flow(get_proactive_flow_row(conn, current_user["id"], loved_one_id))
        return build_call_bridge_status(loved_one=loved_one, proactive_flow=proactive_flow, subscription=subscription)




@router.get("/api/bridge/status")
async def get_call_bridge_status_endpoint(
    loved_one_id: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        if not loved_one_id:
            return build_call_bridge_status()
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        proactive_flow = serialize_proactive_flow(get_proactive_flow_row(conn, current_user["id"], loved_one_id))
        return build_call_bridge_status(loved_one=loved_one, proactive_flow=proactive_flow, subscription=subscription)




@router.api_route("/api/bridge/twilio/connect/{event_id}", methods=["GET", "POST"])
async def twilio_call_connect(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    with get_db() as conn:
        event_row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if event_row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        loved_one_row = conn.execute("SELECT * FROM loved_ones WHERE id = ?", (event_row["loved_one_id"],)).fetchone()
        if loved_one_row is None:
            raise HTTPException(status_code=404, detail="亲人档案未找到")
        audio_ref = get_media_asset_reference(conn, event_row["audio_asset_id"])
        audio_url = audio_ref["url"] if audio_ref else None
        form = await request.form() if request.method == "POST" else {}
        update_proactive_event_metadata(
            conn,
            event_id,
            status="delivered",
            delivered=True,
            metadata_updates={
                "provider": "twilio",
                "call_sid": str(form.get("CallSid") or ""),
                "call_status": str(form.get("CallStatus") or "answered"),
            },
        )

    action_url = build_call_bridge_url(f"/api/bridge/twilio/respond/{event_id}", event_id, turn=0)
    no_input_url = build_call_bridge_url(f"/api/bridge/twilio/no-input/{event_id}", event_id, turn=0)
    twiml = build_twiml_playback(
        str(event_row["message_text"] or ""),
        audio_url,
        allow_follow_up=True,
        action_url=action_url,
    ).replace(
        "</Response>",
        f"<Redirect method=\"POST\">{html.escape(no_input_url)}</Redirect></Response>",
    )
    return Response(content=twiml, media_type="text/xml")


@router.api_route("/api/bridge/twilio/respond/{event_id}", methods=["POST"])
async def twilio_call_respond(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    turn = max(0, int(request.query_params.get("turn", "0") or 0))
    form = await request.form()
    transcript = str(form.get("SpeechResult") or form.get("Digits") or "").strip()
    if not transcript:
        no_input_url = build_call_bridge_url(f"/api/bridge/twilio/no-input/{event_id}", event_id, turn=turn)
        return Response(
            content=f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Redirect method=\"POST\">{html.escape(no_input_url)}</Redirect></Response>",
            media_type="text/xml",
        )

    with get_db() as conn:
        event_row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if event_row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        loved_one, ai_response, audio_result = await generate_phone_followup_response(
            conn,
            user_id=event_row["user_id"],
            loved_one_id=event_row["loved_one_id"],
            user_message=transcript,
        )
        persist_phone_turn(
            conn,
            user_id=event_row["user_id"],
            loved_one_id=event_row["loved_one_id"],
            user_message=transcript,
            ai_response=ai_response,
            response_audio_asset_id=audio_result["asset_id"] if audio_result else None,
        )
        update_proactive_event_metadata(
            conn,
            event_id,
            status="delivered",
            delivered=True,
            metadata_updates={
                "provider": "twilio",
                "call_sid": str(form.get("CallSid") or ""),
                "call_status": str(form.get("CallStatus") or "in-progress"),
                "last_user_utterance": transcript,
                "last_ai_reply": ai_response,
                "turn_count": turn + 1,
                "loved_one_name": loved_one["name"],
            },
        )

    if turn + 1 >= PHONE_CALL_MAX_TURNS:
        closing_text = f"{ai_response} 我先不打扰你了，想我的时候再和我说。"
        return Response(
            content=build_twiml_closing(closing_text, audio_result["url"] if audio_result else None),
            media_type="text/xml",
        )

    next_turn = turn + 1
    action_url = build_call_bridge_url(f"/api/bridge/twilio/respond/{event_id}", event_id, turn=next_turn)
    no_input_url = build_call_bridge_url(f"/api/bridge/twilio/no-input/{event_id}", event_id, turn=next_turn)
    twiml = build_twiml_playback(
        ai_response,
        audio_result["url"] if audio_result else None,
        allow_follow_up=True,
        action_url=action_url,
    ).replace(
        "</Response>",
        f"<Redirect method=\"POST\">{html.escape(no_input_url)}</Redirect></Response>",
    )
    return Response(content=twiml, media_type="text/xml")




@router.api_route("/api/bridge/twilio/respond/{event_id}", methods=["POST"])
async def twilio_call_respond(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    turn = max(0, int(request.query_params.get("turn", "0") or 0))
    form = await request.form()
    transcript = str(form.get("SpeechResult") or form.get("Digits") or "").strip()
    if not transcript:
        no_input_url = build_call_bridge_url(f"/api/bridge/twilio/no-input/{event_id}", event_id, turn=turn)
        return Response(
            content=f"<?xml version=\"1.0\" encoding=\"UTF-8\"?><Response><Redirect method=\"POST\">{html.escape(no_input_url)}</Redirect></Response>",
            media_type="text/xml",
        )

    with get_db() as conn:
        event_row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if event_row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        loved_one, ai_response, audio_result = await generate_phone_followup_response(
            conn,
            user_id=event_row["user_id"],
            loved_one_id=event_row["loved_one_id"],
            user_message=transcript,
        )
        persist_phone_turn(
            conn,
            user_id=event_row["user_id"],
            loved_one_id=event_row["loved_one_id"],
            user_message=transcript,
            ai_response=ai_response,
            response_audio_asset_id=audio_result["asset_id"] if audio_result else None,
        )
        update_proactive_event_metadata(
            conn,
            event_id,
            status="delivered",
            delivered=True,
            metadata_updates={
                "provider": "twilio",
                "call_sid": str(form.get("CallSid") or ""),
                "call_status": str(form.get("CallStatus") or "in-progress"),
                "last_user_utterance": transcript,
                "last_ai_reply": ai_response,
                "turn_count": turn + 1,
                "loved_one_name": loved_one["name"],
            },
        )

    if turn + 1 >= PHONE_CALL_MAX_TURNS:
        closing_text = f"{ai_response} 我先不打扰你了，想我的时候再和我说。"
        return Response(
            content=build_twiml_closing(closing_text, audio_result["url"] if audio_result else None),
            media_type="text/xml",
        )

    next_turn = turn + 1
    action_url = build_call_bridge_url(f"/api/bridge/twilio/respond/{event_id}", event_id, turn=next_turn)
    no_input_url = build_call_bridge_url(f"/api/bridge/twilio/no-input/{event_id}", event_id, turn=next_turn)
    twiml = build_twiml_playback(
        ai_response,
        audio_result["url"] if audio_result else None,
        allow_follow_up=True,
        action_url=action_url,
    ).replace(
        "</Response>",
        f"<Redirect method=\"POST\">{html.escape(no_input_url)}</Redirect></Response>",
    )
    return Response(content=twiml, media_type="text/xml")


@router.api_route("/api/bridge/twilio/no-input/{event_id}", methods=["GET", "POST"])
async def twilio_call_no_input(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    with get_db() as conn:
        event_row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if event_row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        loved_one_row = conn.execute("SELECT name FROM loved_ones WHERE id = ?", (event_row["loved_one_id"],)).fetchone()
        name = loved_one_row["name"] if loved_one_row else "ta"
        update_proactive_event_metadata(
            conn,
            event_id,
            status="completed",
            delivered=True,
            metadata_updates={
                "provider": "twilio",
                "call_status": "completed",
                "provider_note": "电话已结束；本次外呼未继续收到用户语音输入。",
            },
        )

    closing_text = f"我是{name}。我先不打扰你了，想我的时候再来和我说说话。"
    return Response(content=build_twiml_closing(closing_text), media_type="text/xml")




@router.api_route("/api/bridge/twilio/no-input/{event_id}", methods=["GET", "POST"])
async def twilio_call_no_input(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    with get_db() as conn:
        event_row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
        if event_row is None:
            raise HTTPException(status_code=404, detail="主动联系事件未找到")
        loved_one_row = conn.execute("SELECT name FROM loved_ones WHERE id = ?", (event_row["loved_one_id"],)).fetchone()
        name = loved_one_row["name"] if loved_one_row else "ta"
        update_proactive_event_metadata(
            conn,
            event_id,
            status="completed",
            delivered=True,
            metadata_updates={
                "provider": "twilio",
                "call_status": "completed",
                "provider_note": "电话已结束；本次外呼未继续收到用户语音输入。",
            },
        )

    closing_text = f"我是{name}。我先不打扰你了，想我的时候再来和我说说话。"
    return Response(content=build_twiml_closing(closing_text), media_type="text/xml")


@router.api_route("/api/bridge/twilio/status/{event_id}", methods=["POST"])
async def twilio_call_status(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    form = await request.form()
    call_status = str(form.get("CallStatus") or "").strip().lower()
    mapped_status = {
        "queued": "provider_pending",
        "initiated": "provider_pending",
        "ringing": "provider_pending",
        "in-progress": "delivered",
        "answered": "delivered",
        "completed": "completed",
        "busy": "failed",
        "failed": "failed",
        "no-answer": "failed",
        "canceled": "failed",
    }.get(call_status, "provider_pending")

    with get_db() as conn:
        update_proactive_event_metadata(
            conn,
            event_id,
            status=mapped_status,
            delivered=call_status in {"in-progress", "answered", "completed"},
            metadata_updates={
                "provider": "twilio",
                "call_sid": str(form.get("CallSid") or ""),
                "call_status": call_status,
                "call_duration": str(form.get("CallDuration") or ""),
                "answered_by": str(form.get("AnsweredBy") or ""),
            },
        )
    return {"status": "ok"}




@router.api_route("/api/bridge/twilio/status/{event_id}", methods=["POST"])
async def twilio_call_status(event_id: str, request: Request):
    bridge_token = request.query_params.get("bridge_token")
    if not verify_call_bridge_token(event_id, bridge_token):
        raise HTTPException(status_code=403, detail="电话桥接校验失败")

    form = await request.form()
    call_status = str(form.get("CallStatus") or "").strip().lower()
    mapped_status = {
        "queued": "provider_pending",
        "initiated": "provider_pending",
        "ringing": "provider_pending",
        "in-progress": "delivered",
        "answered": "delivered",
        "completed": "completed",
        "busy": "failed",
        "failed": "failed",
        "no-answer": "failed",
        "canceled": "failed",
    }.get(call_status, "provider_pending")

    with get_db() as conn:
        update_proactive_event_metadata(
            conn,
            event_id,
            status=mapped_status,
            delivered=call_status in {"in-progress", "answered", "completed"},
            metadata_updates={
                "provider": "twilio",
                "call_sid": str(form.get("CallSid") or ""),
                "call_status": call_status,
                "call_duration": str(form.get("CallDuration") or ""),
                "answered_by": str(form.get("AnsweredBy") or ""),
            },
        )
    return {"status": "ok"}


@router.post("/api/loved-ones", response_model=LovedOne)
async def create_loved_one(loved_one: LovedOne, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        subscription = get_subscription_snapshot(conn, current_user["id"])
        assert_loved_one_limit(conn, current_user["id"], subscription)

        loved_one_id = str(uuid.uuid4())
        timestamp = now_iso()
        personality_traits = loved_one.personality_traits or {}
        initial_memories = unique_preserve_order(loved_one.memories)
        conn.execute(
            """
            INSERT INTO loved_ones (
                id, user_id, name, relationship, birth_date, pass_away_date, cover_title, cover_photo_asset_id,
                personality_traits_json, speaking_style, identity_model_summary, created_at, updated_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                loved_one_id,
                current_user["id"],
                loved_one.name.strip(),
                loved_one.relationship.strip() or "亲人",
                loved_one.birth_date,
                loved_one.pass_away_date,
                loved_one.cover_title.strip() if loved_one.cover_title else "",
                None,
                json.dumps(personality_traits, ensure_ascii=False),
                loved_one.speaking_style.strip() or (personality_traits.get("catchphrase") or "温柔亲切"),
                "",
                timestamp,
                timestamp,
            ),
        )

        for content in initial_memories:
            conn.execute(
                """
                INSERT INTO memories (
                    id, user_id, loved_one_id, content, memory_type, memory_date, importance, created_at
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """,
                (
                    str(uuid.uuid4()),
                    current_user["id"],
                    loved_one_id,
                    content,
                    "conversation",
                    None,
                    7,
                    timestamp,
                ),
            )

        refresh_identity_model_summary(conn, loved_one_id, trigger_source="create")
        ensure_default_proactive_flow(conn, current_user["id"], loved_one_id)
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        return serialize_loved_one(conn, loved_one_row, subscription=subscription)




