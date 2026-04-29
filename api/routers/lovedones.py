"""
念念 - lovedones路由
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

router = APIRouter(tags=["lovedones"])

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


@router.get("/api/loved-ones", response_model=List[LovedOne])
async def list_loved_ones(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        subscription = get_subscription_snapshot(conn, current_user["id"])
        rows = conn.execute(
            "SELECT * FROM loved_ones WHERE user_id = ? ORDER BY updated_at DESC",
            (current_user["id"],),
        ).fetchall()
        return [serialize_loved_one(conn, row, subscription=subscription) for row in rows]




@router.get("/api/loved-ones", response_model=List[LovedOne])
async def list_loved_ones(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        subscription = get_subscription_snapshot(conn, current_user["id"])
        rows = conn.execute(
            "SELECT * FROM loved_ones WHERE user_id = ? ORDER BY updated_at DESC",
            (current_user["id"],),
        ).fetchall()
        return [serialize_loved_one(conn, row, subscription=subscription) for row in rows]


@router.get("/api/loved-ones/{loved_one_id}", response_model=LovedOne)
async def get_loved_one(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        return serialize_loved_one(conn, row, subscription=subscription)




@router.get("/api/loved-ones/{loved_one_id}", response_model=LovedOne)
async def get_loved_one(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        return serialize_loved_one(conn, row, subscription=subscription)


@router.post("/api/loved-ones/{loved_one_id}/cover", response_model=LovedOne)
async def update_loved_one_cover(
    loved_one_id: str,
    payload: LovedOneCoverPayload,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        if payload.cover_photo_asset_id:
            media_row = conn.execute(
                """
                SELECT * FROM media_assets
                WHERE id = ? AND loved_one_id = ? AND user_id = ? AND kind = 'photo'
                """,
                (payload.cover_photo_asset_id, loved_one_id, current_user["id"]),
            ).fetchone()
            if media_row is None:
                raise HTTPException(status_code=404, detail="封面照片未找到")

        next_cover_title = loved_one_row["cover_title"] if payload.cover_title is None else payload.cover_title.strip()
        next_cover_asset_id = (
            loved_one_row["cover_photo_asset_id"]
            if payload.cover_photo_asset_id is None
            else (payload.cover_photo_asset_id.strip() or None)
        )

        conn.execute(
            "UPDATE loved_ones SET cover_title = ?, cover_photo_asset_id = ?, updated_at = ? WHERE id = ?",
            (next_cover_title, next_cover_asset_id, now_iso(), loved_one_id),
        )
        updated = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        return serialize_loved_one(conn, updated, subscription=subscription)




@router.post("/api/loved-ones/{loved_one_id}/cover", response_model=LovedOne)
async def update_loved_one_cover(
    loved_one_id: str,
    payload: LovedOneCoverPayload,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        if payload.cover_photo_asset_id:
            media_row = conn.execute(
                """
                SELECT * FROM media_assets
                WHERE id = ? AND loved_one_id = ? AND user_id = ? AND kind = 'photo'
                """,
                (payload.cover_photo_asset_id, loved_one_id, current_user["id"]),
            ).fetchone()
            if media_row is None:
                raise HTTPException(status_code=404, detail="封面照片未找到")

        next_cover_title = loved_one_row["cover_title"] if payload.cover_title is None else payload.cover_title.strip()
        next_cover_asset_id = (
            loved_one_row["cover_photo_asset_id"]
            if payload.cover_photo_asset_id is None
            else (payload.cover_photo_asset_id.strip() or None)
        )

        conn.execute(
            "UPDATE loved_ones SET cover_title = ?, cover_photo_asset_id = ?, updated_at = ? WHERE id = ?",
            (next_cover_title, next_cover_asset_id, now_iso(), loved_one_id),
        )
        updated = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        return serialize_loved_one(conn, updated, subscription=subscription)




@router.get("/api/loved-ones/{loved_one_id}/digital-human")
async def get_digital_human_model_endpoint(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        model_row = get_digital_human_model_row(conn, loved_one_id)
        if model_row is None:
            rebuild_digital_human_model(conn, loved_one_id, trigger_source="api_fetch")
            model_row = get_digital_human_model_row(conn, loved_one_id)
        return serialize_digital_human_model(conn, model_row)


@router.get("/api/loved-ones/{loved_one_id}/digital-human/fragments")
async def get_digital_human_fragments_endpoint(
    loved_one_id: str,
    source_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        rows = get_digital_human_fragments(conn, loved_one_id, source_type=source_type, limit=limit)
        return {
            "loved_one_id": loved_one_id,
            "count": len(rows),
            "items": [serialize_digital_human_fragment(row) for row in rows],
        }




@router.get("/api/loved-ones/{loved_one_id}/digital-human/fragments")
async def get_digital_human_fragments_endpoint(
    loved_one_id: str,
    source_type: Optional[str] = None,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        rows = get_digital_human_fragments(conn, loved_one_id, source_type=source_type, limit=limit)
        return {
            "loved_one_id": loved_one_id,
            "count": len(rows),
            "items": [serialize_digital_human_fragment(row) for row in rows],
        }




@router.get("/api/loved-ones/{loved_one_id}/digital-human/builds")
async def get_digital_human_builds_endpoint(
    loved_one_id: str,
    limit: int = 6,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        rows = conn.execute(
            """
            SELECT * FROM digital_human_build_runs
            WHERE loved_one_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (loved_one_id, max(1, min(12, int(limit)))),
        ).fetchall()
    return {
        "loved_one_id": loved_one_id,
        "count": len(rows),
        "items": [
            {
                "id": row["id"],
                "status": row["status"],
                "trigger_source": row["trigger_source"],
                "notes": row["notes"],
                "source_counts": json_object(row["source_counts_json"]),
                "created_at": row["created_at"],
                "completed_at": row["completed_at"],
                "updated_at": row["updated_at"],
            }
            for row in rows
        ],
    }




@router.get("/api/loved-ones/{loved_one_id}/digital-human/history")
async def get_digital_human_history_endpoint(
    loved_one_id: str,
    limit: int = 12,
    current_user: dict = Depends(get_current_user),
):
    sample_limit = max(4, min(40, int(limit) * 3))
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        chat_rows = conn.execute(
            """
            SELECT id, created_at, user_message, ai_response, mode, response_audio_asset_id, response_video_asset_id
            FROM chat_messages
            WHERE loved_one_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (loved_one_id, current_user["id"], sample_limit),
        ).fetchall()
        proactive_rows = conn.execute(
            """
            SELECT id, created_at, event_type, channel, title, message_text, audio_asset_id, video_asset_id, metadata_json
            FROM proactive_events
            WHERE loved_one_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (loved_one_id, current_user["id"], sample_limit),
        ).fetchall()

        items = []
        for row in chat_rows:
            audio_ref = get_media_asset_reference(conn, row["response_audio_asset_id"])
            video_ref = get_media_asset_reference(conn, row["response_video_asset_id"])
            if not (
                (audio_ref and audio_ref["kind"] == "generated_audio")
                or (video_ref and video_ref["kind"] == "generated_video")
            ):
                continue
            items.append(
                {
                    "id": row["id"],
                    "source": "conversation",
                    "source_label": "对话陪伴",
                    "mode": row["mode"],
                    "title": "Mimo 陪伴回复",
                    "prompt_text": row["user_message"],
                    "response_text": row["ai_response"],
                    "audio_url": audio_ref["url"] if audio_ref else None,
                    "audio_kind": audio_ref["kind"] if audio_ref else None,
                    "video_url": video_ref["url"] if video_ref else None,
                    "video_kind": video_ref["kind"] if video_ref else None,
                    "created_at": row["created_at"],
                    "metadata": {},
                }
            )

        for row in proactive_rows:
            audio_ref = get_media_asset_reference(conn, row["audio_asset_id"])
            video_ref = get_media_asset_reference(conn, row["video_asset_id"])
            if not (
                (audio_ref and audio_ref["kind"] == "generated_audio")
                or (video_ref and video_ref["kind"] == "generated_video")
            ):
                continue
            items.append(
                {
                    "id": row["id"],
                    "source": "proactive",
                    "source_label": "主动联系",
                    "mode": row["event_type"],
                    "title": row["title"] or "主动联系",
                    "prompt_text": None,
                    "response_text": row["message_text"],
                    "audio_url": audio_ref["url"] if audio_ref else None,
                    "audio_kind": audio_ref["kind"] if audio_ref else None,
                    "video_url": video_ref["url"] if video_ref else None,
                    "video_kind": video_ref["kind"] if video_ref else None,
                    "created_at": row["created_at"],
                    "metadata": json_object(row["metadata_json"]),
                }
            )

    items.sort(key=lambda item: item["created_at"] or "", reverse=True)
    items = items[: max(1, min(24, int(limit)))]
    return {
        "loved_one_id": loved_one_id,
        "count": len(items),
        "items": items,
    }




@router.post("/api/loved-ones/{loved_one_id}/digital-human/rebuild")
async def rebuild_digital_human_endpoint(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        model = rebuild_digital_human_model(conn, loved_one_id, trigger_source="manual_rebuild")
    return {"status": "rebuilt", "loved_one_id": loved_one_id, "digital_human_model": model}


@router.delete("/api/loved-ones/{loved_one_id}")
async def delete_loved_one(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        media_rows = fetch_media_rows(conn, loved_one_id, include_generated=True)
        for media_row in media_rows:
            cleanup_path(media_row["file_path"])
        conn.execute("DELETE FROM loved_ones WHERE id = ? AND user_id = ?", (loved_one_id, current_user["id"]))
    return {"status": "deleted", "loved_one_id": loved_one_id, "name": row["name"]}




@router.delete("/api/loved-ones/{loved_one_id}")
async def delete_loved_one(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        media_rows = fetch_media_rows(conn, loved_one_id, include_generated=True)
        for media_row in media_rows:
            cleanup_path(media_row["file_path"])
        conn.execute("DELETE FROM loved_ones WHERE id = ? AND user_id = ?", (loved_one_id, current_user["id"]))
    return {"status": "deleted", "loved_one_id": loved_one_id, "name": row["name"]}


async def handle_media_upload(
    *,
    kind: str,
    loved_one_id: str,
    file: UploadFile,
    request: Request,
    current_user: dict,
) -> dict:
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        if kind == "voice":
            assert_plan_capability(subscription, "voice_upload", "当前套餐不包含语音建模上传，请先升级套餐。")
        if kind == "video":
            assert_plan_capability(subscription, "video_upload", "当前套餐不包含视频陪伴上传，请先升级套餐。")

        folder_map = {
            "voice": "voices",
            "photo": "photos",
            "video": "videos",
            "model3d": "model3d",
        }
        target_path = safe_upload_path(folder_map.get(kind, f"{kind}s"), loved_one_id, file.filename)
        content = await file.read()
        target_path.write_bytes(content)
        summary = await analyze_media_with_mimo(kind, target_path, request=request) if kind in {"voice", "photo", "video"} else None
        if kind == "model3d" and not summary:
            summary = "已上传真人 3D 重建素材，会作为数字人的立体外观与空间形态底稿。"
        asset_id = str(uuid.uuid4())
        existing_primary = conn.execute(
            "SELECT id FROM media_assets WHERE loved_one_id = ? AND kind = ? AND is_primary = 1",
            (loved_one_id, kind),
        ).fetchone()
        is_primary = 0 if existing_primary else 1
        metadata_payload = {}
        conn.execute(
            """
            INSERT INTO media_assets (
                id, user_id, loved_one_id, kind, file_path, original_filename,
                mime_type, byte_size, summary, tags_json, metadata_json, is_primary, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                asset_id,
                current_user["id"],
                loved_one_id,
                kind,
                str(target_path),
                file.filename or target_path.name,
                file.content_type or infer_mime_type(target_path, "application/octet-stream"),
                len(content),
                summary,
                "[]",
                json.dumps(
                    {"stage": "uploaded", "pipeline": ["uploaded", "aligned", "textured", "rigged", "ready"]}
                    if kind == "model3d"
                    else metadata_payload,
                    ensure_ascii=False,
                ),
                is_primary,
                now_iso(),
            ),
        )
        if kind == "photo":
            current_cover = conn.execute(
                "SELECT cover_photo_asset_id FROM loved_ones WHERE id = ?",
                (loved_one_id,),
            ).fetchone()
            if current_cover and not current_cover["cover_photo_asset_id"]:
                conn.execute(
                    "UPDATE loved_ones SET cover_photo_asset_id = ?, updated_at = ? WHERE id = ?",
                    (asset_id, now_iso(), loved_one_id),
                )
        refresh_identity_model_summary(conn, loved_one_id, trigger_source=f"upload_{kind}")
        conn.execute(
            "UPDATE loved_ones SET updated_at = ? WHERE id = ?",
            (now_iso(), loved_one_id),
        )
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()

    messages = {
        "voice": "语音样本已上传，正在为这个数字分身校准声音与通话语气...",
        "photo": "照片已上传，分身的面容正在变得更清晰。",
        "video": "视频已上传，分身开始拥有更完整的动态神态。",
        "model3d": "真人 3D 重建已上传，数字人的立体外观底稿正在更新。",
    }
    return {
        "status": "uploaded",
        "asset_id": asset_id,
        "path": str(target_path),
        "url": public_media_url(str(target_path)),
        "message": messages[kind],
        "loved_one": loved_one,
    }




