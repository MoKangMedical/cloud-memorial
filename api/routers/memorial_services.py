"""
念念 - 纪念服务路由
集成 src/ 模块：家族树、蜡烛、献花、祈福、哀伤辅导、信件、故事
"""
from fastapi import APIRouter, Depends, HTTPException, Request
from typing import Any, Dict, List, Optional
import sqlite3
import json
import uuid
from datetime import datetime

from ..app_helpers import get_db, get_current_user, now_iso

router = APIRouter(tags=["纪念服务"])

# ===== 家族树 =====
@router.get("/api/family-tree/{loved_one_id}")
async def get_family_tree(loved_one_id: str, current_user: dict = Depends(get_current_user)):
    """获取家族树"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM family_members WHERE loved_one_id = ? ORDER BY generation, created_at",
            (loved_one_id,)
        ).fetchall()
        members = [dict(r) for r in rows]
    return {"members": members}

@router.post("/api/family-tree/{loved_one_id}")
async def add_family_member(
    loved_one_id: str,
    member: dict,
    current_user: dict = Depends(get_current_user)
):
    """添加家族成员"""
    member_id = str(uuid.uuid4())[:8]
    with get_db() as conn:
        conn.execute(
            """INSERT INTO family_members 
               (id, loved_one_id, user_id, name, gender, birth_date, death_date, 
                bio, generation, parent_id, spouse_id, is_alive, created_at)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (member_id, loved_one_id, current_user["id"],
             member.get("name", ""), member.get("gender", ""),
             member.get("birth_date"), member.get("death_date"),
             member.get("bio", ""), member.get("generation", 0),
             member.get("parent_id"), member.get("spouse_id"),
             member.get("is_alive", True), now_iso())
        )
    return {"id": member_id, "status": "created"}

# ===== 虚拟蜡烛 =====
@router.post("/api/candles/{loved_one_id}")
async def light_candle(
    loved_one_id: str,
    candle: dict,
    current_user: dict = Depends(get_current_user)
):
    """点燃蜡烛"""
    candle_id = str(uuid.uuid4())[:8]
    with get_db() as conn:
        conn.execute(
            """INSERT INTO candles 
               (id, loved_one_id, user_id, candle_type, message, lit_at, is_eternal)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (candle_id, loved_one_id, current_user["id"],
             candle.get("candle_type", "white"),
             candle.get("message", ""),
             now_iso(),
             candle.get("is_eternal", False))
        )
    return {"id": candle_id, "status": "lit"}

@router.get("/api/candles/{loved_one_id}")
async def get_candles(loved_one_id: str):
    """获取蜡烛列表"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM candles WHERE loved_one_id = ? ORDER BY lit_at DESC LIMIT 50",
            (loved_one_id,)
        ).fetchall()
    return {"candles": [dict(r) for r in rows]}

# ===== 虚拟献花 =====
@router.post("/api/flowers/{loved_one_id}")
async def offer_flowers(
    loved_one_id: str,
    flower: dict,
    current_user: dict = Depends(get_current_user)
):
    """献花"""
    flower_id = str(uuid.uuid4())[:8]
    with get_db() as conn:
        conn.execute(
            """INSERT INTO flower_offerings 
               (id, loved_one_id, user_id, flower_type, message, offered_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (flower_id, loved_one_id, current_user["id"],
             flower.get("flower_type", "chrysanthemum"),
             flower.get("message", ""),
             now_iso())
        )
    return {"id": flower_id, "status": "offered"}

@router.get("/api/flowers/{loved_one_id}")
async def get_flowers(loved_one_id: str):
    """获取献花列表"""
    with get_db() as conn:
        rows = conn.execute(
            "SELECT * FROM flower_offerings WHERE loved_one_id = ? ORDER BY offered_at DESC LIMIT 50",
            (loved_one_id,)
        ).fetchall()
    return {"flowers": [dict(r) for r in rows]}

# ===== 祈福 =====
@router.post("/api/prayers/{loved_one_id}")
async def send_prayer(
    loved_one_id: str,
    prayer: dict,
    current_user: dict = Depends(get_current_user)
):
    """发送祈福"""
    prayer_id = str(uuid.uuid4())[:8]
    with get_db() as conn:
        conn.execute(
            """INSERT INTO prayers 
               (id, loved_one_id, user_id, prayer_type, message, sent_at)
               VALUES (?, ?, ?, ?, ?, ?)""",
            (prayer_id, loved_one_id, current_user["id"],
             prayer.get("prayer_type", "blessing"),
             prayer.get("message", ""),
             now_iso())
        )
    return {"id": prayer_id, "status": "sent"}

# ===== AI信件 =====
@router.post("/api/letters/{loved_one_id}")
async def generate_letter(
    loved_one_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """生成AI信件"""
    # Get loved one info for context
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM loved_ones WHERE id = ? AND user_id = ?",
            (loved_one_id, current_user["id"])
        ).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="亲人未找到")
    
    letter_type = request.get("type", "miss_you")  # miss_you, birthday, holiday
    # AI letter generation would go here
    # For now, return a template
    templates = {
        "miss_you": f"亲爱的{dict(row)['name']}：\n\n好久不见，甚是想念...",
        "birthday": f"亲爱的{dict(row)['name']}：\n\n今天是你的生日...",
        "holiday": f"亲爱的{dict(row)['name']}：\n\n节日快乐...",
    }
    
    return {
        "letter": templates.get(letter_type, templates["miss_you"]),
        "type": letter_type
    }

# ===== AI故事 =====
@router.post("/api/stories/{loved_one_id}")
async def generate_story(
    loved_one_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """生成AI故事"""
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM loved_ones WHERE id = ? AND user_id = ?",
            (loved_one_id, current_user["id"])
        ).fetchone()
    
    if not row:
        raise HTTPException(status_code=404, detail="亲人未找到")
    
    # Get memories for context
    with get_db() as conn:
        memories = conn.execute(
            "SELECT content FROM memories WHERE loved_one_id = ? ORDER BY created_at DESC LIMIT 5",
            (loved_one_id,)
        ).fetchall()
    
    return {
        "story": f"这是关于{dict(row)['name']}的故事...",
        "memories_used": len(memories)
    }

# ===== 纪念墙 =====
@router.get("/api/memorial-wall/{loved_one_id}")
async def get_memorial_wall(loved_one_id: str):
    """获取纪念墙数据"""
    with get_db() as conn:
        candles = conn.execute(
            "SELECT COUNT(*) as count FROM candles WHERE loved_one_id = ?",
            (loved_one_id,)
        ).fetchone()
        flowers = conn.execute(
            "SELECT COUNT(*) as count FROM flower_offerings WHERE loved_one_id = ?",
            (loved_one_id,)
        ).fetchone()
        prayers = conn.execute(
            "SELECT COUNT(*) as count FROM prayers WHERE loved_one_id = ?",
            (loved_one_id,)
        ).fetchone()
    
    return {
        "candle_count": dict(candles)["count"] if candles else 0,
        "flower_count": dict(flowers)["count"] if flowers else 0,
        "prayer_count": dict(prayers)["count"] if prayers else 0,
    }

# ===== 哀伤辅导资源 =====
@router.get("/api/grief-resources")
async def get_grief_resources():
    """获取哀伤辅导资源"""
    resources = [
        {"id": "1", "title": "如何面对失去亲人的痛苦", "type": "article", "url": "#"},
        {"id": "2", "title": "哀伤的五个阶段", "type": "article", "url": "#"},
        {"id": "3", "title": "心理咨询热线", "type": "hotline", "phone": "400-161-9995"},
        {"id": "4", "title": "线上哀伤支持小组", "type": "group", "url": "#"},
    ]
    return {"resources": resources}

# ===== 分享 =====
@router.post("/api/share/{loved_one_id}")
async def create_share_link(
    loved_one_id: str,
    request: dict,
    current_user: dict = Depends(get_current_user)
):
    """创建分享链接"""
    share_id = str(uuid.uuid4())[:8]
    share_type = request.get("type", "link")  # link, qrcode, wechat
    
    return {
        "share_id": share_id,
        "share_url": f"/memorial/{loved_one_id}?share={share_id}",
        "share_type": share_type,
        "qr_code_url": f"/api/share/{share_id}/qr" if share_type == "qrcode" else None
    }
