"""
念念 - media路由
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

router = APIRouter(tags=["media"])

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




@router.post("/api/loved-ones/{loved_one_id}/voice")
async def upload_voice_sample(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    return await handle_media_upload(
        kind="voice",
        loved_one_id=loved_one_id,
        file=file,
        request=request,
        current_user=current_user,
    )




@router.post("/api/loved-ones/{loved_one_id}/photo")
async def upload_photo(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    return await handle_media_upload(
        kind="photo",
        loved_one_id=loved_one_id,
        file=file,
        request=request,
        current_user=current_user,
    )




@router.post("/api/loved-ones/{loved_one_id}/video")
async def upload_video(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    return await handle_media_upload(
        kind="video",
        loved_one_id=loved_one_id,
        file=file,
        request=request,
        current_user=current_user,
    )




@router.post("/api/loved-ones/{loved_one_id}/model-3d")
async def upload_model3d(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...),
    current_user: dict = Depends(get_current_user),
):
    return await handle_media_upload(
        kind="model3d",
        loved_one_id=loved_one_id,
        file=file,
        request=request,
        current_user=current_user,
    )




@router.get("/api/loved-ones/{loved_one_id}/media")
async def get_media_assets(
    loved_one_id: str,
    kind: Optional[str] = None,
    current_user: dict = Depends(get_current_user),
):
    with get_db() as conn:
        ensure_loved_one_owner(conn, current_user["id"], loved_one_id)
        kinds = [kind] if kind in {"voice", "photo", "video", "model3d"} else None
        rows = fetch_media_rows(conn, loved_one_id, kinds=kinds)
        return [serialize_media_asset(row) for row in rows]




@router.post("/api/media/{asset_id}/tags")
async def update_media_tags(
    asset_id: str,
    payload: MediaTagsPayload,
    current_user: dict = Depends(get_current_user),
):
    tags = [item.strip() for item in payload.tags if str(item).strip()]
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM media_assets WHERE id = ? AND user_id = ?",
            (asset_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="素材未找到")
        conn.execute(
            "UPDATE media_assets SET tags_json = ? WHERE id = ?",
            (json.dumps(tags, ensure_ascii=False), asset_id),
        )
        updated = conn.execute("SELECT * FROM media_assets WHERE id = ?", (asset_id,)).fetchone()
    return {"status": "updated", "asset": serialize_media_asset(updated)}




@router.post("/api/media/{asset_id}/primary")
async def set_media_primary(asset_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM media_assets WHERE id = ? AND user_id = ?",
            (asset_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="素材未找到")
        if row["kind"] not in {"voice", "photo", "video", "model3d"}:
            raise HTTPException(status_code=400, detail="当前素材不支持主样本设置")
        conn.execute(
            "UPDATE media_assets SET is_primary = 0 WHERE loved_one_id = ? AND kind = ?",
            (row["loved_one_id"], row["kind"]),
        )
        conn.execute("UPDATE media_assets SET is_primary = 1 WHERE id = ?", (asset_id,))
        updated = conn.execute("SELECT * FROM media_assets WHERE id = ?", (asset_id,)).fetchone()
    return {"status": "updated", "asset": serialize_media_asset(updated)}


@router.post("/api/media/{asset_id}/model3d-stage")
async def update_model3d_stage(
    asset_id: str,
    payload: MediaStagePayload,
    current_user: dict = Depends(get_current_user),
):
    stage = payload.stage.strip()
    if stage not in MODEL3D_STAGE_ORDER:
        raise HTTPException(status_code=400, detail="不支持的 3D 阶段")
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM media_assets WHERE id = ? AND user_id = ?",
            (asset_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="素材未找到")
        if row["kind"] != "model3d":
            raise HTTPException(status_code=400, detail="仅支持 3D 重建素材更新阶段")
        meta = json_object(row["metadata_json"]) if row["metadata_json"] else {}
        meta["stage"] = stage
        conn.execute(
            "UPDATE media_assets SET metadata_json = ? WHERE id = ?",
            (json.dumps(meta, ensure_ascii=False), asset_id),
        )
        updated = conn.execute("SELECT * FROM media_assets WHERE id = ?", (asset_id,)).fetchone()
        refresh_identity_model_summary(conn, row["loved_one_id"], trigger_source="model3d_stage")
    return {"status": "updated", "asset": serialize_media_asset(updated)}




@router.post("/api/media/{asset_id}/model3d-stage")
async def update_model3d_stage(
    asset_id: str,
    payload: MediaStagePayload,
    current_user: dict = Depends(get_current_user),
):
    stage = payload.stage.strip()
    if stage not in MODEL3D_STAGE_ORDER:
        raise HTTPException(status_code=400, detail="不支持的 3D 阶段")
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM media_assets WHERE id = ? AND user_id = ?",
            (asset_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="素材未找到")
        if row["kind"] != "model3d":
            raise HTTPException(status_code=400, detail="仅支持 3D 重建素材更新阶段")
        meta = json_object(row["metadata_json"]) if row["metadata_json"] else {}
        meta["stage"] = stage
        conn.execute(
            "UPDATE media_assets SET metadata_json = ? WHERE id = ?",
            (json.dumps(meta, ensure_ascii=False), asset_id),
        )
        updated = conn.execute("SELECT * FROM media_assets WHERE id = ?", (asset_id,)).fetchone()
        refresh_identity_model_summary(conn, row["loved_one_id"], trigger_source="model3d_stage")
    return {"status": "updated", "asset": serialize_media_asset(updated)}




@router.delete("/api/media/{asset_id}")
async def delete_media_asset(asset_id: str, current_user: dict = Depends(get_current_user)):
    with get_db() as conn:
        row = conn.execute(
            "SELECT * FROM media_assets WHERE id = ? AND user_id = ?",
            (asset_id, current_user["id"]),
        ).fetchone()
        if row is None:
            raise HTTPException(status_code=404, detail="素材未找到")
        if row["kind"] not in {"voice", "photo", "video", "model3d"}:
            raise HTTPException(status_code=403, detail="当前素材不支持手动删除")
        loved_one_id = row["loved_one_id"]
        was_primary = bool(row["is_primary"]) if "is_primary" in row.keys() else False
        was_cover = conn.execute(
            "SELECT 1 FROM loved_ones WHERE id = ? AND cover_photo_asset_id = ?",
            (loved_one_id, asset_id),
        ).fetchone()
        cleanup_path(row["file_path"])
        conn.execute("DELETE FROM media_assets WHERE id = ?", (asset_id,))
        if was_primary:
            next_row = conn.execute(
                """
                SELECT id FROM media_assets
                WHERE loved_one_id = ? AND kind = ?
                ORDER BY created_at DESC
                LIMIT 1
                """,
                (loved_one_id, row["kind"]),
            ).fetchone()
            if next_row:
                conn.execute("UPDATE media_assets SET is_primary = 1 WHERE id = ?", (next_row["id"],))
        if was_cover:
            next_cover = conn.execute(
                """
                SELECT id FROM media_assets
                WHERE loved_one_id = ? AND kind = 'photo'
                ORDER BY is_primary DESC, created_at DESC
                LIMIT 1
                """,
                (loved_one_id,),
            ).fetchone()
            conn.execute(
                "UPDATE loved_ones SET cover_photo_asset_id = ? WHERE id = ?",
                (next_cover["id"] if next_cover else None, loved_one_id),
            )
        refresh_identity_model_summary(conn, loved_one_id, trigger_source="delete_media")
        conn.execute("UPDATE loved_ones SET updated_at = ? WHERE id = ?", (now_iso(), loved_one_id))
    return {"status": "deleted", "asset_id": asset_id}


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




