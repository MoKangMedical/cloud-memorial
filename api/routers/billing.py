"""
念念 - billing路由
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

router = APIRouter(tags=["billing"])

def extract_plan_code_from_subscription_item(price_id: Optional[str]) -> Optional[str]:
    if not price_id:
        return None
    for code, configured_price_id in STRIPE_PRICE_IDS.items():
        if configured_price_id and configured_price_id == price_id:
            return code
    return None


def sync_subscription_from_stripe_object(conn: sqlite3.Connection, stripe_subscription: Any, fallback_user_id: Optional[str] = None):
    item = stripe_subscription["items"]["data"][0] if stripe_subscription["items"]["data"] else {}
    price_id = item.get("price", {}).get("id")
    plan_code = extract_plan_code_from_subscription_item(price_id)
    if not plan_code:
        return

    customer_id = stripe_subscription.get("customer")
    user_row = find_user_by_customer_id(conn, customer_id) if customer_id else None
    user_id = user_row["id"] if user_row else fallback_user_id
    if not user_id:
        return

    period_end = stripe_subscription.get("current_period_end")
    current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc).isoformat() if period_end else None
    sync_subscription_record(
        conn,
        user_id=user_id,
        plan_code=plan_code,
        status=stripe_subscription.get("status", "active"),
        stripe_subscription_id=stripe_subscription.get("id"),
        stripe_price_id=price_id,
        current_period_end=current_period_end,
        cancel_at_period_end=bool(stripe_subscription.get("cancel_at_period_end")),
    )




def sync_subscription_from_stripe_object(conn: sqlite3.Connection, stripe_subscription: Any, fallback_user_id: Optional[str] = None):
    item = stripe_subscription["items"]["data"][0] if stripe_subscription["items"]["data"] else {}
    price_id = item.get("price", {}).get("id")
    plan_code = extract_plan_code_from_subscription_item(price_id)
    if not plan_code:
        return

    customer_id = stripe_subscription.get("customer")
    user_row = find_user_by_customer_id(conn, customer_id) if customer_id else None
    user_id = user_row["id"] if user_row else fallback_user_id
    if not user_id:
        return

    period_end = stripe_subscription.get("current_period_end")
    current_period_end = datetime.fromtimestamp(period_end, tz=timezone.utc).isoformat() if period_end else None
    sync_subscription_record(
        conn,
        user_id=user_id,
        plan_code=plan_code,
        status=stripe_subscription.get("status", "active"),
        stripe_subscription_id=stripe_subscription.get("id"),
        stripe_price_id=price_id,
        current_period_end=current_period_end,
        cancel_at_period_end=bool(stripe_subscription.get("cancel_at_period_end")),
    )


@router.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    ensure_stripe_configured()
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="支付服务尚未配置 STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=STRIPE_WEBHOOK_SECRET)
    except Exception as exc:  # pragma: no cover - signature errors are environment specific
        raise HTTPException(status_code=400, detail=f"Webhook 验证失败: {exc}") from exc

    with get_db() as conn:
        already_seen = conn.execute("SELECT id FROM stripe_events WHERE id = ?", (event["id"],)).fetchone()
        if already_seen:
            return {"status": "ignored", "reason": "duplicate"}

        event_type = event["type"]
        data_object = event["data"]["object"]

        if event_type == "checkout.session.completed":
            if data_object.get("mode") == "subscription" and data_object.get("subscription"):
                subscription_obj = stripe.Subscription.retrieve(data_object["subscription"])
                sync_subscription_from_stripe_object(
                    conn,
                    subscription_obj,
                    fallback_user_id=data_object.get("client_reference_id") or data_object.get("metadata", {}).get("user_id"),
                )
                customer_id = data_object.get("customer")
                user_id = data_object.get("client_reference_id") or data_object.get("metadata", {}).get("user_id")
                if customer_id and user_id:
                    conn.execute(
                        "UPDATE users SET stripe_customer_id = ?, updated_at = ? WHERE id = ?",
                        (customer_id, now_iso(), user_id),
                    )

        elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
            sync_subscription_from_stripe_object(conn, data_object)

        conn.execute(
            "INSERT INTO stripe_events (id, event_type, created_at) VALUES (?, ?, ?)",
            (event["id"], event_type, now_iso()),
        )

    return {"status": "processed"}




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




@router.post("/api/billing/portal")
async def create_billing_portal(request: Request, current_user: dict = Depends(get_current_user)):
    ensure_stripe_configured()
    with get_db() as conn:
        user_row = conn.execute("SELECT * FROM users WHERE id = ?", (current_user["id"],)).fetchone()
        customer_id = user_row["stripe_customer_id"]
        if not customer_id:
            raise HTTPException(status_code=400, detail="当前账号还没有 Stripe 客户档案")

    session = stripe.billing_portal.Session.create(
        customer=customer_id,
        return_url=f"{resolve_checkout_base_url(request)}#pricing",
    )
    return {"url": session["url"]}


def extract_plan_code_from_subscription_item(price_id: Optional[str]) -> Optional[str]:
    if not price_id:
        return None
    for code, configured_price_id in STRIPE_PRICE_IDS.items():
        if configured_price_id and configured_price_id == price_id:
            return code
    return None




@router.post("/api/billing/webhook")
async def stripe_webhook(request: Request):
    ensure_stripe_configured()
    payload = await request.body()
    signature = request.headers.get("stripe-signature")
    if not STRIPE_WEBHOOK_SECRET:
        raise HTTPException(status_code=503, detail="支付服务尚未配置 STRIPE_WEBHOOK_SECRET")

    try:
        event = stripe.Webhook.construct_event(payload=payload, sig_header=signature, secret=STRIPE_WEBHOOK_SECRET)
    except Exception as exc:  # pragma: no cover - signature errors are environment specific
        raise HTTPException(status_code=400, detail=f"Webhook 验证失败: {exc}") from exc

    with get_db() as conn:
        already_seen = conn.execute("SELECT id FROM stripe_events WHERE id = ?", (event["id"],)).fetchone()
        if already_seen:
            return {"status": "ignored", "reason": "duplicate"}

        event_type = event["type"]
        data_object = event["data"]["object"]

        if event_type == "checkout.session.completed":
            if data_object.get("mode") == "subscription" and data_object.get("subscription"):
                subscription_obj = stripe.Subscription.retrieve(data_object["subscription"])
                sync_subscription_from_stripe_object(
                    conn,
                    subscription_obj,
                    fallback_user_id=data_object.get("client_reference_id") or data_object.get("metadata", {}).get("user_id"),
                )
                customer_id = data_object.get("customer")
                user_id = data_object.get("client_reference_id") or data_object.get("metadata", {}).get("user_id")
                if customer_id and user_id:
                    conn.execute(
                        "UPDATE users SET stripe_customer_id = ?, updated_at = ? WHERE id = ?",
                        (customer_id, now_iso(), user_id),
                    )

        elif event_type in {"customer.subscription.updated", "customer.subscription.deleted"}:
            sync_subscription_from_stripe_object(conn, data_object)

        conn.execute(
            "INSERT INTO stripe_events (id, event_type, created_at) VALUES (?, ?, ?)",
            (event["id"], event_type, now_iso()),
        )

    return {"status": "processed"}


# ===== 启动 =====
if __name__ == "__main__":
    import uvicorn

    print("念念启动中...")
    print("念念不忘，ta一直在")
    uvicorn.run(app, host="0.0.0.0", port=8102)


