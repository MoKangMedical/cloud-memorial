"""
念念 - auth路由
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

router = APIRouter(tags=["auth"])

@router.post("/api/auth/register", response_model=AuthEnvelope)
async def register(payload: RegisterPayload):
    email = normalize_email(payload.email)
    if "@" not in email:
        raise HTTPException(status_code=400, detail="请输入有效邮箱")
    if len(payload.password) < 8:
        raise HTTPException(status_code=400, detail="密码至少需要 8 位")
    display_name = payload.display_name.strip()
    if not display_name:
        raise HTTPException(status_code=400, detail="请填写你的称呼")

    with get_db() as conn:
        existing = conn.execute("SELECT id FROM users WHERE email = ?", (email,)).fetchone()
        if existing:
            raise HTTPException(status_code=409, detail="该邮箱已注册")

        timestamp = now_iso()
        user_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO users (
                id, email, password_hash, display_name, phone_number, proactive_opt_in,
                preferred_contact_channel, preferred_contact_time, timezone, created_at, updated_at
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                user_id,
                email,
                hash_password(payload.password),
                display_name,
                "",
                0,
                "app",
                "20:30",
                DEFAULT_TIMEZONE,
                timestamp,
                timestamp,
            ),
        )
        sync_admin_flag(conn, user_id, email)
        create_trial_subscription(conn, user_id)
        import_legacy_json_data(conn, user_id)
        session = create_session(conn, user_id)
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (user_id,)).fetchone()
        subscription = get_subscription_snapshot(conn, user_id)
        stats = get_user_stats(conn, user_id)

    return AuthEnvelope(
        token=session["token"],
        user=UserSummary(**serialize_user(user_row)),
        subscription=SubscriptionSnapshot(**subscription),
        stats=stats,
    )


@router.post("/api/auth/login", response_model=AuthEnvelope)
async def login(payload: LoginPayload):
    email = normalize_email(payload.email)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="邮箱或密码错误")

        sync_admin_flag(conn, row["id"], row["email"])
        session = create_session(conn, row["id"])
        subscription = get_subscription_snapshot(conn, row["id"])
        stats = get_user_stats(conn, row["id"])

    return AuthEnvelope(
        token=session["token"],
        user=UserSummary(**serialize_user(row)),
        subscription=SubscriptionSnapshot(**subscription),
        stats=stats,
    )




@router.post("/api/auth/login", response_model=AuthEnvelope)
async def login(payload: LoginPayload):
    email = normalize_email(payload.email)
    with get_db() as conn:
        row = conn.execute("SELECT * FROM users WHERE email = ?", (email,)).fetchone()
        if row is None or not verify_password(payload.password, row["password_hash"]):
            raise HTTPException(status_code=401, detail="邮箱或密码错误")

        sync_admin_flag(conn, row["id"], row["email"])
        session = create_session(conn, row["id"])
        subscription = get_subscription_snapshot(conn, row["id"])
        stats = get_user_stats(conn, row["id"])

    return AuthEnvelope(
        token=session["token"],
        user=UserSummary(**serialize_user(row)),
        subscription=SubscriptionSnapshot(**subscription),
        stats=stats,
    )


@router.get("/api/auth/me", response_model=AuthEnvelope)
async def get_me(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        sync_admin_flag(conn, current_user["id"], current_user["email"])
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],)).fetchone()
        subscription = get_subscription_snapshot(conn, current_user["id"])
        stats = get_user_stats(conn, current_user["id"])
    return AuthEnvelope(
        user=UserSummary(**serialize_user(user_row)),
        subscription=SubscriptionSnapshot(**subscription),
        stats=stats,
    )




@router.get("/api/auth/me", response_model=AuthEnvelope)
async def get_me(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        sync_admin_flag(conn, current_user["id"], current_user["email"])
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],)).fetchone()
        subscription = get_subscription_snapshot(conn, current_user["id"])
        stats = get_user_stats(conn, current_user["id"])
    return AuthEnvelope(
        user=UserSummary(**serialize_user(user_row)),
        subscription=SubscriptionSnapshot(**subscription),
        stats=stats,
    )


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




@router.post("/api/auth/logout")
async def logout(current_user: dict = Depends(get_current_user), authorization: Optional[str] = Header(default=None)):
    token = extract_bearer_token(authorization)
    if not token:
        raise HTTPException(status_code=400, detail="无有效会话")
    with get_db() as conn:
        conn.execute("DELETE FROM sessions WHERE token_hash = ?", (hash_token(token),))
    return {"status": "logged_out"}


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




