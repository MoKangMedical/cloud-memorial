"""
念念 - chat路由
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

router = APIRouter(tags=["chat"])

@router.post("/api/chat", response_model=ChatResponse)
async def chat_with_loved_one(
    msg: ChatMessage,
    request: Request,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        loved_one_row = ensure_loved_one_owner(conn, current_user["id"], msg.loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        requested_mode = (msg.mode or "text").lower()

        if requested_mode == "voice":
            assert_plan_capability(subscription, "voice", "当前套餐不包含语音电话，请先升级套餐。")
        if requested_mode == "video":
            assert_plan_capability(subscription, "video", "当前套餐不包含视频陪伴，请先升级套餐。")

        loved_one = serialize_loved_one(conn, loved_one_row, subscription=subscription).model_dump()
        available_modes = loved_one.get("digital_twin_profile", {}).get("available_modes", ["text"])
        interaction_mode = requested_mode
        if requested_mode == "video" and "video" not in available_modes:
            interaction_mode = "voice" if "voice" in available_modes else "text"
        elif requested_mode == "voice" and "voice" not in available_modes:
            interaction_mode = "text"

        # 使用增强的情感感知系统分析用户消息
        print(f"正在分析用户情感: {msg.message}")
        emotion_analysis = emotion_analyzer.analyze_emotion(
            text=msg.message,
            conversation_history=[]  # 可以从数据库加载历史对话
        )
        detected_emotion = emotion_analysis.primary_emotion
        emotion_intensity = emotion_analysis.intensity.value / 5.0  # 转换为0-1范围
        print(f"情感分析结果: {detected_emotion}, 强度: {emotion_intensity:.2f}")

        # 使用增强的记忆系统选择相关记忆
        print("正在选择相关记忆...")
        memory_rows = conn.execute(
            "SELECT content, memory_type, memory_date, importance FROM memories WHERE loved_one_id = ? ORDER BY created_at DESC LIMIT 20",
            (msg.loved_one_id,),
        ).fetchall()
        
        # 转换为记忆系统需要的格式
        all_memories = []
        for row in memory_rows:
            memory_dict = {
                "content": row["content"],
                "memory_type": row["memory_type"] if "memory_type" in row.keys() else "shared",
                "date": row["memory_date"] if "memory_date" in row.keys() else None,
                "importance": row["importance"] if "importance" in row.keys() else 5,
            }
            all_memories.append(memory_dict)
        
        # 使用增强的记忆系统选择相关记忆
        memory_context = memory_system.select_relevant_memories(
            current_message=msg.message,
            current_emotion=detected_emotion,
            all_memories=all_memories,
            conversation_history=[],
            limit=3
        )
        
        # 构建记忆上下文字符串
        memory_values = [mem.content for mem in memory_context.relevant_memories]
        memory_text = "\\n".join([f"- {value}" for value in memory_values])
        memory_refs = [value[:50] for value in memory_values if value][:3]
        
        print(f"选择的相关记忆: {len(memory_context.relevant_memories)}条")
        print(f"情感共鸣度: {memory_context.emotional_resonance:.2f}")

        # 使用丰富的人格建模系统构建人格画像
        print("正在构建人格画像...")
        personality_traits = loved_one.get("personality_traits", {})
        personality_profile = personality_modeling.build_personality_profile(
            name=loved_one["name"],
            relationship=loved_one.get("relationship", "亲人"),
            personality_traits_dict=personality_traits,
            speaking_style=loved_one.get("speaking_style", "温柔亲切"),
            additional_info=loved_one.get("additional_info")
        )
        
        # 构建增强的提示
        enhanced_prompt = personality_modeling.generate_personality_prompt(personality_profile)
        
        # 添加记忆上下文
        if memory_context.relevant_memories:
            memory_text_for_prompt = "\\n".join([f"- {mem.content}" for mem in memory_context.relevant_memories])
            enhanced_prompt += f"\\n\\n相关记忆：\\n{memory_text_for_prompt}"
        
        # 添加情感分析结果
        enhanced_prompt += f"\\n\\n用户当前情感：{detected_emotion}（强度：{emotion_intensity:.1f}）"
        enhanced_prompt += f"\\n建议回应风格：{emotion_analysis.suggested_response_style}"
        enhanced_prompt += f"\\n情感共鸣度：{memory_context.emotional_resonance:.2f}"

        # 生成AI回应
        if MIMO_API_KEY:
            try:
                # 使用增强的提示生成回应
                ai_response = await generate_text_response_with_mimo(
                    loved_one=loved_one,
                    user_message=msg.message,
                    emotion=detected_emotion,  # 使用检测到的情感
                    memory_context=memory_text_for_prompt if memory_context.relevant_memories else "",
                    request=request,
                    mode=interaction_mode,
                    intensity=msg.intensity or int(emotion_intensity * 5),  # 使用情感强度
                )
                print(f"使用MIMO API生成回应成功")
            except Exception as e:
                print(f"MIMO API调用失败，使用回退回应: {e}")
                ai_response = build_fallback_response(
                    loved_one=loved_one,
                    user_message=msg.message,
                    emotion=detected_emotion,
                    memory_context=memory_text_for_prompt if memory_context.relevant_memories else "",
                    intensity=msg.intensity or int(emotion_intensity * 5),
                )
        else:
            print("MIMO API未配置，使用回退回应")
            ai_response = build_fallback_response(
                loved_one=loved_one,
                user_message=msg.message,
                emotion=detected_emotion,
                memory_context=memory_text_for_prompt if memory_context.relevant_memories else "",
                intensity=msg.intensity or int(emotion_intensity * 5),
            )

        response_audio_url = None
        response_audio_asset_id = None
        audio_result = None
        if interaction_mode in {"voice", "video"}:
            audio_result = await synthesize_speech_with_mimo(
                conn=conn,
                user_id=current_user["id"],
                loved_one_id=msg.loved_one_id,
                text=ai_response,
                emotion=msg.emotion,
            )
            if audio_result:
                response_audio_url = audio_result["url"]
                response_audio_asset_id = audio_result["asset_id"]

        response_video_url = None
        response_video_asset_id = None
        video_mode_note = None
        if interaction_mode == "video":
            video_result = await synthesize_video_with_mimo(
                conn=conn,
                user_id=current_user["id"],
                loved_one_id=msg.loved_one_id,
                loved_one=loved_one,
                user_message=msg.message,
                ai_response=ai_response,
                emotion=msg.emotion,
                memory_context=memory_context,
                request=request,
                audio_result=audio_result,
            )
            if video_result:
                response_video_url = video_result["url"]
                response_video_asset_id = video_result["asset_id"]
                video_mode_note = video_result.get("mode_note")
            elif loved_one["video_urls"]:
                response_video_url = loved_one["video_urls"][-1]
                video_row = conn.execute(
                    """
                    SELECT id FROM media_assets
                    WHERE loved_one_id = ? AND kind = 'video'
                    ORDER BY created_at DESC
                    LIMIT 1
                    """,
                    (msg.loved_one_id,),
                ).fetchone()
                response_video_asset_id = video_row["id"] if video_row else None
                video_mode_note = "MIMO 旁白生成已完成；当前视频画面先回退到你上传的原始影像素材。"

        conn.execute(
            """
            INSERT INTO chat_messages (
                id, user_id, loved_one_id, user_message, ai_response, emotion, mode,
                response_audio_asset_id, response_video_asset_id, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                str(uuid.uuid4()),
                current_user["id"],
                msg.loved_one_id,
                msg.message,
                ai_response,
                msg.emotion,
                interaction_mode,
                response_audio_asset_id,
                response_video_asset_id,
                now_iso(),
            ),
        )
        conn.execute("UPDATE loved_ones SET updated_at = ? WHERE id = ?", (now_iso(), msg.loved_one_id))

    # 使用对话自然度系统调整回应
    print("正在调整对话自然度...")
    dialogue_context = DialogueContext(
        current_state=DialogueState.DEEP_CONVERSATION,  # 可以根据实际情况调整
        state_turns=1,  # 可以从数据库加载
        conversation_history=[],  # 可以从数据库加载
        user_intent="general_chat",  # 可以从情感分析中获取
        emotional_tone=detected_emotion,
        topics_discussed=[],
        memory_references=[mem.content[:20] for mem in memory_context.relevant_memories],
        last_response_time=datetime.now()
    )
    
    natural_response = dialogue_naturalness.generate_natural_response(
        dialogue_context=dialogue_context,
        ai_response=ai_response,
        user_emotion=detected_emotion,
        personality_profile=personality_profile
    )
    
    # 使用情感表达系统增强回应
    print("正在添加情感表达细节...")
    enhanced_response = emotional_expression.add_emotional_expressions(
        text=natural_response,
        emotion=detected_emotion,
        intensity=emotion_intensity,
        personality_traits=personality_traits,
        context={}
    )
    
    print(f"最终回应: {enhanced_response[:100]}...")

    return ChatResponse(
        loved_one_id=msg.loved_one_id,
        loved_one_name=loved_one["name"],
        response_text=enhanced_response,  # 使用增强后的回应
        response_audio_url=response_audio_url,
        response_video_url=response_video_url,
        interaction_mode=interaction_mode,
        mode_note=video_mode_note or build_mode_note(requested_mode, available_modes),
        available_modes=available_modes,
        emotion_detected=detected_emotion,  # 使用检测到的情感
        memory_triggered=memory_context.relevant_memories[0].content[:100] if memory_context.relevant_memories else None,
        memory_refs=memory_refs,
    )




@router.get("/api/chat-history/{loved_one_id}")
async def get_chat_history(
    loved_one_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        rows = conn.execute(
            """
            SELECT created_at, user_message, ai_response, emotion, mode,
                   response_audio_asset_id, response_video_asset_id
            FROM chat_messages
            WHERE loved_one_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (loved_one_id, current_user["id"], limit),
        ).fetchall()
        items = []
        for row in reversed(rows):
            audio_ref = get_media_asset_reference(conn, row["response_audio_asset_id"])
            video_ref = get_media_asset_reference(conn, row["response_video_asset_id"])
            items.append(
                {
                    "timestamp": row["created_at"],
                    "user_message": row["user_message"],
                    "ai_response": row["ai_response"],
                    "emotion": row["emotion"],
                    "mode": row["mode"],
                    "response_audio_url": audio_ref["url"] if audio_ref else None,
                    "response_audio_kind": audio_ref["kind"] if audio_ref else None,
                    "response_video_url": video_ref["url"] if video_ref else None,
                    "response_video_kind": video_ref["kind"] if video_ref else None,
                }
            )
    return items




@router.post("/api/memories")
async def add_memory(memory: MemoryEntry, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], memory.loved_one_id)
        subscription = get_subscription_snapshot(conn, current_user["id"])
        assert_memory_limit(conn, current_user["id"], memory.loved_one_id, subscription)
        memory_id = str(uuid.uuid4())
        conn.execute(
            """
            INSERT INTO memories (
                id, user_id, loved_one_id, content, memory_type, memory_date, importance, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                memory_id,
                current_user["id"],
                memory.loved_one_id,
                memory.content.strip(),
                memory.memory_type,
                memory.date,
                memory.importance,
                now_iso(),
            ),
        )
        refresh_identity_model_summary(conn, memory.loved_one_id, trigger_source="add_memory")
        conn.execute("UPDATE loved_ones SET updated_at = ? WHERE id = ?", (now_iso(), memory.loved_one_id))
    return {"status": "saved", "memory_id": memory_id}


@router.get("/api/memories/{loved_one_id}")
async def get_memories(
    loved_one_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        rows = conn.execute(
            """
            SELECT id, loved_one_id, content, memory_type, memory_date, importance, created_at
            FROM memories
            WHERE loved_one_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (loved_one_id, current_user["id"], limit),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "loved_one_id": row["loved_one_id"],
            "content": row["content"],
            "memory_type": row["memory_type"],
            "date": row["memory_date"],
            "importance": row["importance"],
            "created_at": row["created_at"],
        }
        for row in reversed(rows)
    ]




@router.get("/api/memories/{loved_one_id}")
async def get_memories(
    loved_one_id: str,
    limit: int = 50,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        rows = conn.execute(
            """
            SELECT id, loved_one_id, content, memory_type, memory_date, importance, created_at
            FROM memories
            WHERE loved_one_id = ? AND user_id = ?
            ORDER BY created_at DESC
            LIMIT ?
            """,
            (loved_one_id, current_user["id"], limit),
        ).fetchall()
    return [
        {
            "id": row["id"],
            "loved_one_id": row["loved_one_id"],
            "content": row["content"],
            "memory_type": row["memory_type"],
            "date": row["memory_date"],
            "importance": row["importance"],
            "created_at": row["created_at"],
        }
        for row in reversed(rows)
    ]




@router.delete("/api/memories/{loved_one_id}/{memory_id}")
async def delete_memory(loved_one_id: str, memory_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        deleted = conn.execute(
            "DELETE FROM memories WHERE id = ? AND loved_one_id = ? AND user_id = ?",
            (memory_id, loved_one_id, current_user["id"]),
        ).rowcount
        if not deleted:
            raise HTTPException(status_code=404, detail="回忆未找到")
        refresh_identity_model_summary(conn, loved_one_id, trigger_source="delete_memory")
        conn.execute("UPDATE loved_ones SET updated_at = ? WHERE id = ?", (now_iso(), loved_one_id))
    return {"status": "deleted", "memory_id": memory_id}


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




