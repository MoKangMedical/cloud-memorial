"""
念念 - admin路由
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

router = APIRouter(tags=["admin"])

@router.get("/api/admin/overview")
async def admin_overview(current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    with get_db() as conn:
        total_users = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        total_loved = conn.execute("SELECT COUNT(*) FROM loved_ones").fetchone()[0]
        total_media = conn.execute("SELECT COUNT(*) FROM media_assets WHERE kind IN ('voice', 'photo', 'video', 'model3d')").fetchone()[0]
        total_messages = conn.execute("SELECT COUNT(*) FROM chat_messages").fetchone()[0]
        total_proactive = conn.execute("SELECT COUNT(*) FROM proactive_events").fetchone()[0]
        media_breakdown = {
            row["kind"]: row["count"]
            for row in conn.execute(
                """
                SELECT kind, COUNT(*) AS count
                FROM media_assets
                WHERE kind IN ('voice', 'photo', 'video', 'model3d')
                GROUP BY kind
                """
            ).fetchall()
        }
    return {
        "total_users": total_users,
        "total_loved_ones": total_loved,
        "total_media_assets": total_media,
        "total_messages": total_messages,
        "total_proactive_events": total_proactive,
        "media_breakdown": media_breakdown,
    }


@router.get("/api/admin/users")
async def admin_list_users(limit: int = 50, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    limit = max(1, min(200, int(limit)))
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT u.*, (
                SELECT COUNT(*) FROM loved_ones l WHERE l.user_id = u.id
            ) AS loved_one_count, (
                SELECT COUNT(*) FROM media_assets m WHERE m.user_id = u.id AND m.kind IN ('voice', 'photo', 'video', 'model3d')
            ) AS media_count, (
                SELECT COUNT(*) FROM chat_messages c WHERE c.user_id = u.id
            ) AS message_count
            FROM users u
            ORDER BY u.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            **serialize_user(row),
            "loved_one_count": row["loved_one_count"],
            "media_count": row["media_count"],
            "message_count": row["message_count"],
        }
        for row in rows
    ]




@router.get("/api/admin/users")
async def admin_list_users(limit: int = 50, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    limit = max(1, min(200, int(limit)))
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT u.*, (
                SELECT COUNT(*) FROM loved_ones l WHERE l.user_id = u.id
            ) AS loved_one_count, (
                SELECT COUNT(*) FROM media_assets m WHERE m.user_id = u.id AND m.kind IN ('voice', 'photo', 'video', 'model3d')
            ) AS media_count, (
                SELECT COUNT(*) FROM chat_messages c WHERE c.user_id = u.id
            ) AS message_count
            FROM users u
            ORDER BY u.created_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            **serialize_user(row),
            "loved_one_count": row["loved_one_count"],
            "media_count": row["media_count"],
            "message_count": row["message_count"],
        }
        for row in rows
    ]


@router.get("/api/admin/loved-ones")
async def admin_list_loved_ones(limit: int = 50, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    limit = max(1, min(200, int(limit)))
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT l.*, u.email AS owner_email, (
                SELECT COUNT(*) FROM media_assets m WHERE m.loved_one_id = l.id AND m.kind IN ('voice', 'photo', 'video', 'model3d')
            ) AS media_count, (
                SELECT COUNT(*) FROM memories mem WHERE mem.loved_one_id = l.id
            ) AS memory_count
            FROM loved_ones l
            JOIN users u ON u.id = l.user_id
            ORDER BY l.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "relationship": row["relationship"],
            "owner_email": row["owner_email"],
            "media_count": row["media_count"],
            "memory_count": row["memory_count"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]




@router.get("/api/admin/loved-ones")
async def admin_list_loved_ones(limit: int = 50, current_user: dict = Depends(get_current_user)):
    require_admin(current_user)
    limit = max(1, min(200, int(limit)))
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT l.*, u.email AS owner_email, (
                SELECT COUNT(*) FROM media_assets m WHERE m.loved_one_id = l.id AND m.kind IN ('voice', 'photo', 'video', 'model3d')
            ) AS media_count, (
                SELECT COUNT(*) FROM memories mem WHERE mem.loved_one_id = l.id
            ) AS memory_count
            FROM loved_ones l
            JOIN users u ON u.id = l.user_id
            ORDER BY l.updated_at DESC
            LIMIT ?
            """,
            (limit,),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "name": row["name"],
            "relationship": row["relationship"],
            "owner_email": row["owner_email"],
            "media_count": row["media_count"],
            "memory_count": row["memory_count"],
            "updated_at": row["updated_at"],
        }
        for row in rows
    ]


@router.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user), authorization: Optional[str] = Header(default=None)):
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=400, detail="无有效会话")
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
    return {"status": "logged_out"}




