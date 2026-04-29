"""
念念 - memorial路由
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

router = APIRouter(tags=["memorial"])

@router.get("/health")
async def health():
    bridge = build_call_bridge_status()
    return {
        "status": "healthy",
        "service": "念念",
        "version": "2.0.0",
        "timestamp": now_iso(),
        "database": str(DB_PATH),
        "stripe_configured": bool(STRIPE_SECRET_KEY),
        "mimo_configured": bool(MIMO_API_KEY),
        "mimo_video_model": MIMO_VIDEO_MODEL,
        "ffmpeg_configured": bool(FFMPEG_BIN),
        "mimo_video_pipeline_ready": bool(MIMO_API_KEY and FFMPEG_BIN),
        "call_bridge_provider": bridge["provider"],
        "call_bridge_configured": bridge["configured"],
    }


@router.get("/")
async def index():
    if FRONTEND_FILE.exists():
        return FileResponse(FRONTEND_FILE)
    raise HTTPException(status_code=404, detail="前端页面未找到")




@router.get("/")
async def index():
    if FRONTEND_FILE.exists():
        return FileResponse(FRONTEND_FILE)
    raise HTTPException(status_code=404, detail="前端页面未找到")


@router.get("/api/plans")
async def list_plans(authorization: Optional[str] = Header(default=None)):
    current_user = get_optional_user_from_authorization(authorization)
    with get_db() as conn:
        plans = [build_plan_view(dict(row)) for row in conn.execute("SELECT * FROM plans WHERE code != 'trial' ORDER BY price_cny")]
        current_subscription = get_subscription_snapshot(conn, current_user["id"]) if current_user else None
    return {
        "plans": plans,
        "current_plan_code": current_subscription["plan_code"] if current_subscription else None,
        "stripe_configured": bool(STRIPE_SECRET_KEY),
    }




@router.get("/api/plans")
async def list_plans(authorization: Optional[str] = Header(default=None)):
    current_user = get_optional_user_from_authorization(authorization)
    with get_db() as conn:
        plans = [build_plan_view(dict(row)) for row in conn.execute("SELECT * FROM plans WHERE code != 'trial' ORDER BY price_cny")]
        current_subscription = get_subscription_snapshot(conn, current_user["id"]) if current_user else None
    return {
        "plans": plans,
        "current_plan_code": current_subscription["plan_code"] if current_subscription else None,
        "stripe_configured": bool(STRIPE_SECRET_KEY),
    }


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




@router.post("/api/greetings/schedule")
async def schedule_greeting(greeting: GreetingSchedule, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], greeting.loved_one_id)
        greeting_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO greetings (
                id, user_id, loved_one_id, greeting_type, trigger_date, message_template, status, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                greeting_id,
                current_user["id"],
                greeting.loved_one_id,
                greeting.greeting_type,
                greeting.trigger_date,
                greeting.message_template,
                "scheduled",
                now_iso(),
            ),
        )
    return {"status": "scheduled", "greeting_id": greeting_id}


@router.get("/api/greetings/upcoming")
async def upcoming_greetings(days: int = 7, current_user: dict = Depends(get_current_user)):
    start = now_utc()
    end = start + timedelta(days=days)
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM greetings
            WHERE user_id = ? AND status = 'scheduled'
            ORDER BY trigger_date ASC
            """,
            (current_user["id"],),
        ).fetchall()
    upcoming = []
    for row in rows:
        trigger = parse_iso(row["trigger_date"])
        if trigger and start <= trigger <= end:
            upcoming.append(dict(row))
    return upcoming




@router.get("/api/greetings/upcoming")
async def upcoming_greetings(days: int = 7, current_user: dict = Depends(get_current_user)):
    start = now_utc()
    end = start + timedelta(days=days)
    with get_db() as conn:
        rows = conn.execute(
            """
            SELECT * FROM greetings
            WHERE user_id = ? AND status = 'scheduled'
            ORDER BY trigger_date ASC
            """,
            (current_user["id"],),
        ).fetchall()
    upcoming = []
    for row in rows:
        trigger = parse_iso(row["trigger_date"])
        if trigger and start <= trigger <= end:
            upcoming.append(dict(row))
    return upcoming


@router.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        return get_user_stats(conn, current_user["id"])




@router.get("/api/stats")
async def get_stats(current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        return get_user_stats(conn, current_user["id"])


@router.post("/api/billing/checkout")
async def create_checkout_session(
    payload: CheckoutPayload,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    ensure_stripe_configured()
    if payload.plan_code not in STRIPE_PRICE_IDS or not STRIPE_PRICE_IDS[payload.plan_code]:
        raise HTTPException(status_code=400, detail="该套餐尚未配置 Stripe Price ID")

    with get_db() as conn:
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],)).fetchone()
        base_url = resolve_checkout_base_url(request)
        customer_id = user_row["stripe_customer_id"]
        if not customer_id:
            customer = stripe.Customer.create(
                email=user_row["email"],
                name=user_row["display_name"],
                metadata={"user_id": user_row["id"]},
            )
            customer_id = customer["id"]
            conn.execute(
                "UPDATE users SET stripe_customer_id = ?, updated_at = ? WHERE id = ?",
                (customer_id, now_iso(), user_row["id"]),
            )

    session = stripe.checkout.Session.create(
        mode="subscription",
        customer=customer_id,
        line_items=[{"price": STRIPE_PRICE_IDS[payload.plan_code], "quantity": 1}],
        client_reference_id=current_user["id"],
        metadata={"user_id": current_user["id"], "plan_code": payload.plan_code},
        allow_promotion_codes=True,
        success_url=f"{base_url}?checkout=success",
        cancel_url=f"{base_url}?checkout=cancelled",
    )
    return {"url": session["url"]}




