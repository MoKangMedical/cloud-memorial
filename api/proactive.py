"""
念念 - 主动关怀系统
定时推送、节日问候、Twilio电话桥接
"""
import asyncio
import hashlib
import json
import os
import threading
import time
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional
from zoneinfo import ZoneInfo

import httpx

from .core import (
    runtime_config, get_db, row_to_dict, now_iso, now_utc,
    json_object, json_list, public_media_url,
    get_user_contact_snapshot, get_subscription_snapshot,
)

def resolve_timezone(tz_name: Optional[str]) -> ZoneInfo:
    try:
        return ZoneInfo(tz_name or DEFAULT_TIMEZONE)
    except Exception:
        return ZoneInfo(DEFAULT_TIMEZONE)


def normalize_phone_number(phone_number: str) -> str:
    value = "".join(ch for ch in str(phone_number or "").strip() if ch.isdigit() or ch == "+")
    return value[:24]


def parse_preferred_time(preferred_time: str) -> tuple[int, int]:
    raw = (preferred_time or "20:30").strip()
    try:
        hour_str, minute_str = raw.split(":", 1)
        hour = min(max(int(hour_str), 0), 23)
        minute = min(max(int(minute_str), 0), 59)
        return hour, minute
    except Exception:
        return 20, 30


def compute_next_run_at(
    cadence: str,
    preferred_time: str,
    preferred_weekday: Optional[int],
    tz_name: Optional[str],
    *,
    from_dt: Optional[datetime] = None,
) -> str:
    base = from_dt or now_utc()
    local_base = base.astimezone(resolve_timezone(tz_name))
    hour, minute = parse_preferred_time(preferred_time)
    candidate = local_base.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if cadence == "weekly":
        target_weekday = preferred_weekday if preferred_weekday is not None else local_base.weekday()
        day_delta = (target_weekday - local_base.weekday()) % 7
        candidate = candidate + timedelta(days=day_delta)
        if candidate <= local_base:
            candidate += timedelta(days=7)
    else:
        if candidate <= local_base:
            candidate += timedelta(days=1)

    return candidate.astimezone(timezone.utc).isoformat()


def build_memory_context(conn: sqlite3.Connection, loved_one_id: str, limit: int = 6) -> str:
    fragment_rows = conn.execute(
        """
        SELECT content FROM digital_human_fragments
        WHERE loved_one_id = ? AND fragment_kind IN ('memory_anchor', 'trait_signal', 'voice_trait', 'visual_trait', 'motion_trait')
        ORDER BY weight DESC, created_at DESC
        LIMIT ?
        """,
        (loved_one_id, limit),
    ).fetchall()
    if fragment_rows:
        return "\n".join([f"- {row['content']}" for row in fragment_rows])
    rows = conn.execute(
        "SELECT content FROM memories WHERE loved_one_id = ? ORDER BY created_at DESC LIMIT ?",
        (loved_one_id, limit),
    ).fetchall()
    return "\n".join([f"- {row['content']}" for row in reversed(rows)])


def get_user_contact_snapshot(conn: sqlite3.Connection, user_id: str) -> dict:
    row = conn.execute(
        """
        SELECT phone_number, proactive_opt_in, preferred_contact_channel, preferred_contact_time, timezone
        FROM users WHERE id = ?
        """,
        (user_id,),
    ).fetchone()
    if row is None:
        return {
            "phone_number": "",
            "proactive_opt_in": False,
            "preferred_contact_channel": "app",
            "preferred_contact_time": "20:30",
            "timezone": DEFAULT_TIMEZONE,
        }
    return {
        "phone_number": row["phone_number"] or "",
        "proactive_opt_in": bool(row["proactive_opt_in"]),
        "preferred_contact_channel": row["preferred_contact_channel"] or "app",
        "preferred_contact_time": row["preferred_contact_time"] or "20:30",
        "timezone": row["timezone"] or DEFAULT_TIMEZONE,
    }


def normalize_proactive_channel(value: Optional[str]) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"app", "phone"}:
        return normalized
    return "app"


def normalize_proactive_message_mode(value: Optional[str]) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"text", "voice", "video"}:
        return normalized
    return "voice"


def ensure_default_proactive_flow(conn: sqlite3.Connection, user_id: str, loved_one_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM proactive_flows WHERE user_id = ? AND loved_one_id = ?",
        (user_id, loved_one_id),
    ).fetchone()
    if row is not None:
        return row

    contact = get_user_contact_snapshot(conn, user_id)
    created_at = now_iso()
    flow_id = str(uuid.uuid4())
    next_run_at = compute_next_run_at(
        cadence="daily",
        preferred_time=contact["preferred_contact_time"],
        preferred_weekday=None,
        tz_name=contact["timezone"],
    )
    conn.execute(
        """
        INSERT INTO proactive_flows (
            id, user_id, loved_one_id, enabled, cadence, preferred_time, preferred_weekday,
            preferred_channel, preferred_message_mode, phone_number, timezone, next_run_at, last_run_at, created_at, updated_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            flow_id,
            user_id,
            loved_one_id,
            1,
            "daily",
            contact["preferred_contact_time"],
            None,
            normalize_proactive_channel(contact["preferred_contact_channel"]),
            "voice",
            contact["phone_number"] or None,
            contact["timezone"],
            next_run_at,
            None,
            created_at,
            created_at,
        ),
    )
    return conn.execute(
        "SELECT * FROM proactive_flows WHERE id = ?",
        (flow_id,),
    ).fetchone()


def get_proactive_flow_row(conn: sqlite3.Connection, user_id: str, loved_one_id: str) -> sqlite3.Row:
    row = conn.execute(
        "SELECT * FROM proactive_flows WHERE user_id = ? AND loved_one_id = ?",
        (user_id, loved_one_id),
    ).fetchone()
    return row or ensure_default_proactive_flow(conn, user_id, loved_one_id)


def serialize_proactive_flow(row: Optional[sqlite3.Row]) -> dict:
    if row is None:
        return {
            "enabled": True,
            "cadence": "daily",
            "preferred_time": "20:30",
            "preferred_weekday": None,
            "preferred_channel": "app",
            "preferred_message_mode": "voice",
            "phone_number": "",
            "timezone": DEFAULT_TIMEZONE,
            "next_run_at": None,
            "last_run_at": None,
        }
    return {
        "id": row["id"],
        "enabled": bool(row["enabled"]),
        "cadence": row["cadence"],
        "preferred_time": row["preferred_time"],
        "preferred_weekday": row["preferred_weekday"],
        "preferred_channel": normalize_proactive_channel(row["preferred_channel"]),
        "preferred_message_mode": normalize_proactive_message_mode(row["preferred_message_mode"]),
        "phone_number": row["phone_number"] or "",
        "timezone": row["timezone"] or DEFAULT_TIMEZONE,
        "next_run_at": row["next_run_at"],
        "last_run_at": row["last_run_at"],
    }


def proactive_event_media_refs(
    conn: sqlite3.Connection,
    audio_asset_id: Optional[str],
    video_asset_id: Optional[str],
) -> tuple[Optional[dict], Optional[dict]]:
    return get_media_asset_reference(conn, audio_asset_id), get_media_asset_reference(conn, video_asset_id)


def serialize_proactive_event(conn: sqlite3.Connection, row: sqlite3.Row) -> dict:
    metadata = {}
    try:
        metadata = json.loads(row["metadata_json"] or "{}")
    except json.JSONDecodeError:
        metadata = {}
    audio_ref, video_ref = proactive_event_media_refs(conn, row["audio_asset_id"], row["video_asset_id"])
    return {
        "id": row["id"],
        "loved_one_id": row["loved_one_id"],
        "flow_id": row["flow_id"],
        "source_kind": row["source_kind"],
        "event_type": row["event_type"],
        "channel": row["channel"],
        "status": row["status"],
        "title": row["title"],
        "message_text": row["message_text"],
        "audio_asset_id": row["audio_asset_id"],
        "audio_kind": audio_ref["kind"] if audio_ref else None,
        "audio_url": audio_ref["url"] if audio_ref else None,
        "video_asset_id": row["video_asset_id"],
        "video_kind": video_ref["kind"] if video_ref else None,
        "video_url": video_ref["url"] if video_ref else None,
        "scheduled_for": row["scheduled_for"],
        "delivered_at": row["delivered_at"],
        "consumed_at": row["consumed_at"],
        "created_at": row["created_at"],
        "metadata": metadata,
    }


def choose_proactive_message_mode(
    preferred_message_mode: str,
    *,
    can_voice: bool,
    can_video: bool,
) -> tuple[str, Optional[str]]:
    requested = normalize_proactive_message_mode(preferred_message_mode)
    if requested == "video":
        if can_video:
            return "video", None
        if can_voice:
            return "voice", "当前视频素材或权限还不足以生成视频问候，已自动回退为语音消息。"
        return "text", "当前素材还不足以生成视频问候，已自动回退为文字消息。"
    if requested == "voice":
        if can_voice:
            return "voice", None
        return "text", "当前语音素材或权限还不足以生成语音问候，已自动回退为文字消息。"
    return "text", None


async def generate_proactive_message_with_mimo(
    loved_one: dict,
    *,
    reason: str,
    memory_context: str,
    mode: str,
) -> str:
    instruction = (
        f"{build_personality_prompt(loved_one)}\n\n"
        f"请主动联系用户，不要等待用户先开口。\n"
        f"触发原因：{reason}\n"
        f"互动模式：{mode}\n"
        f"相关记忆：\n{memory_context or '暂无'}\n\n"
        "请像亲人主动联系时那样开场，先问候、再自然带入熟悉的生活细节，控制在 80 到 140 字。"
    )

    payload = {
        "model": "mimo-v2-omni" if loved_one.get("identity_model_summary") else "mimo-v2-pro",
        "messages": [{"role": "user", "content": instruction}],
        "temperature": 0.85,
        "max_completion_tokens": 220,
    }
    result = await call_mimo_chat_completion(payload, timeout=60.0)
    return (result["choices"][0]["message"]["content"] or "").strip()


def build_proactive_fallback(loved_one: dict, reason: str, memory_context: str) -> str:
    name = loved_one["name"]
    catchphrase = (loved_one.get("personality_traits") or {}).get("catchphrase", "").strip()
    prefix = f"{catchphrase} " if catchphrase else ""
    memory_line = ""
    if memory_context:
        latest = memory_context.split("\n")[-1].replace("- ", "").strip()
        if latest:
            memory_line = f" 我刚刚又想起“{latest}”。"
    return f"{prefix}今天我想主动来找你说说话。{memory_line} {name}一直惦记着你，记得按时吃饭，也别把心事都一个人扛着。"


def create_proactive_event(
    conn: sqlite3.Connection,
    *,
    event_id: Optional[str] = None,
    user_id: str,
    loved_one_id: str,
    flow_id: Optional[str],
    source_kind: str,
    source_id: Optional[str],
    event_type: str,
    channel: str,
    status: str,
    title: str,
    message_text: str,
    audio_asset_id: Optional[str],
    video_asset_id: Optional[str],
    scheduled_for: Optional[str],
    metadata: Optional[dict] = None,
) -> str:
    event_id = event_id or str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO proactive_events (
            id, user_id, loved_one_id, flow_id, source_kind, source_id, event_type, channel, status, title,
            message_text, audio_asset_id, video_asset_id, scheduled_for, delivered_at, consumed_at, metadata_json, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            event_id,
            user_id,
            loved_one_id,
            flow_id,
            source_kind,
            source_id,
            event_type,
            channel,
            status,
            title,
            message_text,
            audio_asset_id,
            video_asset_id,
            scheduled_for,
            now_iso() if status in {"ready", "provider_pending", "delivered"} else None,
            None,
            json.dumps(metadata or {}, ensure_ascii=False),
            now_iso(),
        ),
    )
    return event_id


def get_call_bridge_provider() -> str:
    if TWILIO_ACCOUNT_SID and TWILIO_AUTH_TOKEN and TWILIO_FROM_NUMBER:
        return "twilio"
    if OUTBOUND_CALL_WEBHOOK_URL:
        return "webhook"
    return "none"


def get_call_bridge_secret() -> str:
    return TWILIO_AUTH_TOKEN or OUTBOUND_CALL_WEBHOOK_TOKEN or ""


def build_call_bridge_token(event_id: str) -> str:
    secret = get_call_bridge_secret()
    if not secret:
        return ""
    return hmac.new(secret.encode("utf-8"), event_id.encode("utf-8"), hashlib.sha256).hexdigest()


def verify_call_bridge_token(event_id: str, token: Optional[str]) -> bool:
    expected = build_call_bridge_token(event_id)
    if not expected:
        return True
    return bool(token) and hmac.compare_digest(expected, str(token))


def build_call_bridge_url(path: str, event_id: str, **query: Any) -> str:
    base = (TWILIO_STATUS_CALLBACK_BASE_URL or APP_BASE_URL).rstrip("/")
    parts = [f"bridge_token={build_call_bridge_token(event_id)}"]
    for key, value in query.items():
        if value is None:
            continue
        parts.append(f"{quote_plus(str(key))}={quote_plus(str(value))}")
    separator = "&" if "?" in path else "?"
    return f"{base}{path}{separator}{'&'.join(parts)}"


def build_call_bridge_status(
    loved_one: Optional[dict] = None,
    proactive_flow: Optional[dict] = None,
    subscription: Optional[dict] = None,
) -> dict:
    provider = get_call_bridge_provider()
    provider_label = {
        "twilio": "Twilio 内建外呼",
        "webhook": "外部电话桥接 webhook",
        "none": "尚未配置电话桥接",
    }[provider]
    configured = provider != "none"
    flow = proactive_flow or {}
    blockers: List[str] = []
    preferred_channel = flow.get("preferred_channel", "app")
    phone_number = flow.get("phone_number") or ""
    wants_phone = preferred_channel == "phone"
    phone_number_configured = bool(phone_number)
    voice_ready = False
    digital_human_ready = False
    model = {}

    if loved_one:
        twin = loved_one.get("digital_twin_profile") or {}
        model = loved_one.get("digital_human_model") or {}
        features = (subscription or {}).get("features", {})
        voice_ready = "voice" in twin.get("available_modes", ["text"]) and bool(features.get("voice"))
        digital_human_ready = model.get("build_status") == "ready" and int(model.get("knowledge_count") or 0) > 0

    if wants_phone and not configured:
        blockers.append("还没有接通电话桥接服务")
    if wants_phone and not phone_number_configured:
        blockers.append("还没有填写接听手机号")
    if wants_phone and loved_one and not voice_ready:
        blockers.append("当前套餐或素材还不足以支撑语音外呼")
    if wants_phone and loved_one and not digital_human_ready:
        blockers.append("数字人模型还在搭建，先继续补记忆和声音素材")

    call_ready = wants_phone and configured and phone_number_configured
    if loved_one:
        call_ready = call_ready and voice_ready and digital_human_ready

    if call_ready:
        readiness_note = (
            "当前已经满足主动外呼条件，系统会直接以电话方式发起联系。"
            if provider == "twilio"
            else "当前已经满足主动外呼条件，系统会把任务交给外部电话桥接服务。"
        )
    elif wants_phone:
        readiness_note = "；".join(blockers) or "电话外呼仍在准备中。"
    else:
        readiness_note = "当前默认仍以站内主动问候为主，切到电话优先后会按外呼条件校验。"

    return {
        "provider": provider,
        "provider_label": provider_label,
        "configured": configured,
        "direct_call_enabled": provider == "twilio",
        "webhook_handoff_enabled": provider == "webhook",
        "preferred_channel": preferred_channel,
        "phone_number_configured": phone_number_configured,
        "voice_ready": voice_ready,
        "digital_human_ready": digital_human_ready,
        "call_ready": call_ready,
        "blockers": blockers,
        "readiness_note": readiness_note,
        "status_callback_base_url": (TWILIO_STATUS_CALLBACK_BASE_URL or APP_BASE_URL).rstrip("/"),
        "build_version": model.get("build_version") if model else None,
    }


def build_twiml_playback(message_text: str, audio_url: Optional[str], *, allow_follow_up: bool, action_url: Optional[str] = None) -> str:
    pieces = ["<?xml version=\"1.0\" encoding=\"UTF-8\"?>", "<Response>"]
    if allow_follow_up and action_url:
        pieces.append(
            f"<Gather input=\"speech\" language=\"zh-CN\" speechTimeout=\"auto\" timeout=\"4\" action=\"{html.escape(action_url, quote=True)}\" method=\"POST\">"
        )
    if audio_url:
        pieces.append(f"<Play>{html.escape(audio_url)}</Play>")
    else:
        pieces.append(f"<Say language=\"zh-CN\">{html.escape(message_text)}</Say>")
    if allow_follow_up and action_url:
        pieces.append("<Pause length=\"1\"/>")
        pieces.append("<Say language=\"zh-CN\">你可以现在跟我说话，我会继续陪你聊。</Say>")
        pieces.append("</Gather>")
    pieces.append("</Response>")
    return "".join(pieces)


def build_twiml_closing(message_text: str, audio_url: Optional[str] = None) -> str:
    playback = build_twiml_playback(message_text, audio_url, allow_follow_up=False)
    return playback.replace("</Response>", "<Hangup/></Response>")


def place_twilio_outbound_call(
    event_id: str,
    phone_number: str,
    loved_one: dict,
    message_text: str,
    audio_url: Optional[str],
) -> tuple[str, dict]:
    connect_url = build_call_bridge_url(f"/api/bridge/twilio/connect/{event_id}", event_id, turn=0)
    status_url = build_call_bridge_url(f"/api/bridge/twilio/status/{event_id}", event_id)
    payload = [
        ("To", phone_number),
        ("From", TWILIO_FROM_NUMBER),
        ("Url", connect_url),
        ("Method", "POST"),
        ("StatusCallback", status_url),
        ("StatusCallbackMethod", "POST"),
        ("StatusCallbackEvent", "initiated"),
        ("StatusCallbackEvent", "ringing"),
        ("StatusCallbackEvent", "answered"),
        ("StatusCallbackEvent", "completed"),
    ]

    try:
        with httpx.Client(timeout=20.0, auth=(TWILIO_ACCOUNT_SID, TWILIO_AUTH_TOKEN)) as client:
            response = client.post(
                f"https://api.twilio.com/2010-04-01/Accounts/{TWILIO_ACCOUNT_SID}/Calls.json",
                data=payload,
            )
            response.raise_for_status()
            data = response.json()
        return "provider_pending", {
            "provider": "twilio",
            "provider_note": f"已通过 Twilio 发起外呼，等待 {loved_one['name']} 接通电话。",
            "phone_number": phone_number,
            "call_sid": data.get("sid"),
            "call_status": data.get("status"),
            "audio_url": audio_url,
        }
    except Exception as exc:
        return "ready", {
            "provider": "twilio",
            "provider_note": f"Twilio 外呼失败：{exc}。已保留语音和通话脚本，可先在站内收听。",
            "phone_number": phone_number,
            "audio_url": audio_url,
        }


def dispatch_outbound_call(
    event_id: str,
    phone_number: str,
    loved_one: dict,
    message_text: str,
    audio_url: Optional[str],
) -> tuple[str, dict]:
    provider = get_call_bridge_provider()
    if provider == "twilio":
        return place_twilio_outbound_call(event_id, phone_number, loved_one, message_text, audio_url)

    if provider == "none":
        return "provider_pending", {
            "provider_note": "尚未配置外呼桥接服务，已生成来电脚本与语音素材，可先在站内收听。",
            "phone_number": phone_number,
        }

    payload = {
        "event_id": event_id,
        "phone_number": phone_number,
        "loved_one_name": loved_one["name"],
        "message_text": message_text,
        "audio_url": audio_url,
    }
    headers = {"Content-Type": "application/json"}
    if OUTBOUND_CALL_WEBHOOK_TOKEN:
        headers["Authorization"] = f"Bearer {OUTBOUND_CALL_WEBHOOK_TOKEN}"

    try:
        with httpx.Client(timeout=20.0) as client:
            response = client.post(OUTBOUND_CALL_WEBHOOK_URL, headers=headers, json=payload)
            response.raise_for_status()
        return "provider_pending", {
            "provider": "webhook",
            "provider_note": "已把外呼任务交给电话桥接服务，等待运营商回呼结果。",
            "phone_number": phone_number,
        }
    except Exception as exc:
        return "ready", {
            "provider": "webhook",
            "provider_note": f"电话桥接调用失败：{exc}",
            "phone_number": phone_number,
        }


async def generate_proactive_payload(
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
    loved_one_row = ensure_loved_one_owner(conn, user_id, loved_one_id)
    subscription = get_subscription_snapshot(conn, user_id)
    loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
    memory_context = build_memory_context(conn, loved_one_id)
    available_modes = loved_one.get("digital_twin_profile", {}).get("available_modes", ["text"])
    requested_channel = normalize_proactive_channel(preferred_channel)
    can_voice = "voice" in available_modes and subscription.get("features", {}).get("voice")
    can_video = "video" in available_modes and subscription.get("features", {}).get("video")
    wants_phone = requested_channel == "phone" and bool(phone_number)
    can_phone = wants_phone and can_voice
    actual_message_mode, mode_fallback_reason = choose_proactive_message_mode(
        preferred_message_mode,
        can_voice=can_voice,
        can_video=can_video,
    )
    generation_mode = "voice" if can_phone else actual_message_mode

    if MIMO_API_KEY:
        try:
            message_text = await generate_proactive_message_with_mimo(
                loved_one,
                reason=reason,
                memory_context=memory_context,
                mode=generation_mode,
            )
        except Exception:
            message_text = build_proactive_fallback(loved_one, reason, memory_context)
    else:
        message_text = build_proactive_fallback(loved_one, reason, memory_context)

    audio_result = None
    if can_phone or actual_message_mode in {"voice", "video"}:
        try:
            audio_result = await synthesize_speech_with_mimo(
                conn=conn,
                user_id=user_id,
                loved_one_id=loved_one_id,
                text=message_text,
                emotion="missing",
            )
        except Exception:
            audio_result = None

    video_result = None
    synthesis_fallback_reason = None
    if actual_message_mode == "video":
        try:
            video_result = await synthesize_video_with_mimo(
                conn=conn,
                user_id=user_id,
                loved_one_id=loved_one_id,
                loved_one=loved_one,
                user_message=reason,
                ai_response=message_text,
                emotion="missing",
                memory_context=memory_context,
                request=None,
                audio_result=audio_result,
            )
        except Exception:
            video_result = None
        if video_result is None:
            if audio_result:
                actual_message_mode = "voice"
                synthesis_fallback_reason = "MIMO 视频短片合成暂时失败，已自动回退为语音消息。"
            else:
                actual_message_mode = "text"
                synthesis_fallback_reason = "MIMO 视频短片暂时未生成成功，已自动回退为文字消息。"

    if actual_message_mode == "voice" and not audio_result and not can_phone:
        actual_message_mode = "text"
        synthesis_fallback_reason = "MIMO 语音合成暂时失败，已自动回退为文字消息。"

    channel = "phone" if can_phone else "app"
    event_type = "voice_call" if can_phone else {
        "text": "message",
        "voice": "voice_message",
        "video": "video_message",
    }[actual_message_mode]

    fallback_reasons: List[str] = []
    if wants_phone and not can_phone:
        fallback_reasons.append("当前套餐或数字人素材还不足以发起语音外呼，已自动回退为站内主动问候。")
    if mode_fallback_reason:
        fallback_reasons.append(mode_fallback_reason)
    if synthesis_fallback_reason:
        fallback_reasons.append(synthesis_fallback_reason)

    return {
        "loved_one": loved_one,
        "message_text": message_text,
        "channel": channel,
        "event_type": event_type,
        "preferred_message_mode": normalize_proactive_message_mode(preferred_message_mode),
        "actual_message_mode": "voice" if can_phone else actual_message_mode,
        "audio_asset_id": audio_result["asset_id"] if audio_result else None,
        "audio_url": audio_result["url"] if audio_result else None,
        "video_asset_id": video_result["asset_id"] if video_result else None,
        "video_url": video_result["url"] if video_result else None,
        "reason": reason,
        "source_kind": source_kind,
        "source_id": source_id,
        "scheduled_for": scheduled_for,
        "phone_number": phone_number,
        "fallback_reason": "；".join(fallback_reasons) if fallback_reasons else None,
    }


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


async def generate_phone_followup_response(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    loved_one_id: str,
    user_message: str,
) -> tuple[dict, str, Optional[dict]]:
    loved_one_row = ensure_loved_one_owner(conn, user_id, loved_one_id)
    subscription = get_subscription_snapshot(conn, user_id)
    loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
    memory_context = build_memory_context(conn, loved_one_id)

    if MIMO_API_KEY:
        try:
            ai_response = await generate_text_response_with_mimo(
                loved_one=loved_one,
                user_message=user_message,
                emotion=None,
                memory_context=memory_context,
                request=None,
                mode="voice",
            )
        except Exception:
            ai_response = build_fallback_response(
                loved_one=loved_one,
                user_message=user_message,
                emotion="missing",
                memory_context=memory_context,
            )
    else:
        ai_response = build_fallback_response(
            loved_one=loved_one,
            user_message=user_message,
            emotion="missing",
            memory_context=memory_context,
        )

    audio_result = await synthesize_speech_with_mimo(
        conn=conn,
        user_id=user_id,
        loved_one_id=loved_one_id,
        text=ai_response,
        emotion="missing",
    )
    return loved_one, ai_response, audio_result


def persist_phone_turn(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    loved_one_id: str,
    user_message: str,
    ai_response: str,
    response_audio_asset_id: Optional[str],
):
    conn.execute(
        """
        INSERT INTO chat_messages (
            id, user_id, loved_one_id, user_message, ai_response, emotion, mode,
            response_audio_asset_id, response_video_asset_id, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            str(uuid.uuid4()),
            user_id,
            loved_one_id,
            user_message,
            ai_response,
            "missing",
            "voice",
            response_audio_asset_id,
            None,
            now_iso(),
        ),
    )
    conn.execute("UPDATE loved_ones SET updated_at = ? WHERE id = ?", (now_iso(), loved_one_id))


def update_proactive_event_metadata(
    conn: sqlite3.Connection,
    event_id: str,
    *,
    status: Optional[str] = None,
    delivered: bool = False,
    metadata_updates: Optional[dict] = None,
):
    row = conn.execute("SELECT * FROM proactive_events WHERE id = ?", (event_id,)).fetchone()
    if row is None:
        return
    metadata = json.loads(row["metadata_json"] or "{}")
    metadata.update(metadata_updates or {})
    conn.execute(
        """
        UPDATE proactive_events
        SET status = COALESCE(?, status),
            delivered_at = CASE WHEN ? THEN COALESCE(delivered_at, ?) ELSE delivered_at END,
            metadata_json = ?
        WHERE id = ?
        """,
        (
            status,
            int(delivered),
            now_iso(),
            json.dumps(metadata, ensure_ascii=False),
            event_id,
        ),
    )


def process_due_proactive_flows():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM proactive_flows
            WHERE enabled = 1 AND next_run_at IS NOT NULL AND next_run_at <= ?
            ORDER BY next_run_at ASC
            LIMIT 10
            """,
            (now_iso(),),
        ).fetchall()

        for row in rows:
            payload = generate_proactive_payload_sync(
                conn,
                user_id=row["user_id"],
                loved_one_id=row["loved_one_id"],
                reason="按照设定的主动联系节奏，像亲人那样主动来问候一下。",
                preferred_channel=row["preferred_channel"],
                preferred_message_mode=row["preferred_message_mode"],
                phone_number=row["phone_number"] or "",
                source_kind="flow",
                source_id=row["id"],
                scheduled_for=row["next_run_at"],
            )
            if not payload:
                continue

            status = "ready"
            metadata = {
                "reason": payload["reason"],
                "requested_message_mode": payload["preferred_message_mode"],
                "actual_message_mode": payload["actual_message_mode"],
            }
            if payload.get("fallback_reason"):
                metadata["provider_note"] = payload["fallback_reason"]
            event_id = str(uuid.uuid4())
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
                user_id=row["user_id"],
                loved_one_id=row["loved_one_id"],
                flow_id=row["id"],
                source_kind="flow",
                source_id=row["id"],
                event_type=payload["event_type"],
                channel=payload["channel"],
                status=status,
                title=f"{payload['loved_one']['name']} 主动联系了你",
                message_text=payload["message_text"],
                audio_asset_id=payload["audio_asset_id"],
                video_asset_id=payload["video_asset_id"],
                scheduled_for=row["next_run_at"],
                metadata=metadata,
            )

            next_run_at = compute_next_run_at(
                row["cadence"],
                row["preferred_time"],
                row["preferred_weekday"],
                row["timezone"],
                from_dt=now_utc(),
            )
            conn.execute(
                "UPDATE proactive_flows SET last_run_at = ?, next_run_at = ?, updated_at = ? WHERE id = ?",
                (now_iso(), next_run_at, now_iso(), row["id"]),
            )


def process_due_greetings():
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM greetings
            WHERE status = 'scheduled' AND trigger_date <= ?
            ORDER BY trigger_date ASC
            LIMIT 10
            """,
            (now_iso(),),
        ).fetchall()

        for row in rows:
            flow_row = get_proactive_flow_row(conn, row["user_id"], row["loved_one_id"])
            payload = generate_proactive_payload_sync(
                conn,
                user_id=row["user_id"],
                loved_one_id=row["loved_one_id"],
                reason=row["message_template"] or "这是一个特别的日子，想主动给你打个招呼。",
                preferred_channel=flow_row["preferred_channel"],
                preferred_message_mode=flow_row["preferred_message_mode"],
                phone_number=flow_row["phone_number"] or "",
                source_kind="greeting",
                source_id=row["id"],
                scheduled_for=row["trigger_date"],
            )
            if not payload:
                continue
            metadata = {
                "greeting_type": row["greeting_type"],
                "reason": payload["reason"],
                "requested_message_mode": payload["preferred_message_mode"],
                "actual_message_mode": payload["actual_message_mode"],
            }
            if payload.get("fallback_reason"):
                metadata["provider_note"] = payload["fallback_reason"]
            status = "ready"
            event_id = str(uuid.uuid4())
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
                user_id=row["user_id"],
                loved_one_id=row["loved_one_id"],
                flow_id=flow_row["id"],
                source_kind="greeting",
                source_id=row["id"],
                event_type=payload["event_type"],
                channel=payload["channel"],
                status=status,
                title=f"{payload['loved_one']['name']} 主动联系了你",
                message_text=payload["message_text"],
                audio_asset_id=payload["audio_asset_id"],
                video_asset_id=payload["video_asset_id"],
                scheduled_for=row["trigger_date"],
                metadata=metadata,
            )
            conn.execute("UPDATE greetings SET status = 'completed' WHERE id = ?", (row["id"],))


def proactive_worker_loop():
    while True:
        try:
            process_due_greetings()
            process_due_proactive_flows()
        except Exception:
            pass
        time.sleep(PROACTIVE_POLL_SECONDS)


# ===== API =====

