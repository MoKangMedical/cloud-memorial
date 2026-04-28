"""
念念 - AI对话与媒体生成引擎
MIMO API调用、人格化对话、语音合成、视频生成
"""
import asyncio
import base64
import json
import os
import re
import subprocess
import uuid
from pathlib import Path
from typing import Any, Dict, List, Optional

import httpx

from .core import (
    runtime_config, mimo_headers, get_db, now_iso,
    safe_upload_path, infer_mime_type, encode_data_url,
    public_media_url, strip_code_fence,
    BASE_DIR,
)

async def call_mimo_chat_completion(payload: dict, timeout: float = 60.0) -> dict:
    async with httpx.AsyncClient(timeout=timeout) as client:
        response = await client.post(
            f"{MIMO_API_BASE}/chat/completions",
            headers=mimo_headers(),
            json=payload,
        )
        response.raise_for_status()
        return response.json()


def build_media_content_part(
    media_type: str,
    file_path: Path,
    request: Optional[Request] = None,
) -> Optional[dict]:
    absolute_url = make_absolute_media_url(str(file_path), request=request)
    if media_type == "photo":
        reference = absolute_url if is_publicly_reachable_url(absolute_url) else encode_data_url(file_path, "image/jpeg")
        if not reference:
            return None
        return {"type": "image_url", "image_url": {"url": reference}}

    if media_type == "voice":
        reference = absolute_url if is_publicly_reachable_url(absolute_url) else encode_data_url(file_path, "audio/wav")
        if not reference:
            return None
        return {"type": "input_audio", "input_audio": {"data": reference}}

    if media_type == "video":
        reference = absolute_url if is_publicly_reachable_url(absolute_url) else encode_data_url(file_path, "video/mp4")
        if not reference:
            return None
        return {
            "type": "video_url",
            "video_url": {"url": reference},
            "fps": 1,
            "media_resolution": "default",
        }

    return None


async def analyze_media_with_mimo(
    media_type: str,
    file_path: Path,
    request: Optional[Request] = None,
) -> Optional[str]:
    if not MIMO_API_KEY:
        return None

    content_part = build_media_content_part(media_type, file_path, request=request)
    if not content_part:
        return None

    prompts = {
        "voice": "请用简洁中文总结这段语音里适合构建纪念数字分身的说话特征，只写一段，不要分点，重点写音色、语速、情绪和口头习惯。",
        "photo": "请用简洁中文总结这张照片里适合构建纪念数字分身的外貌与气质特征，只写一段，不要分点，重点写神情、穿着气质、给人的感觉。",
        "video": "请用简洁中文总结这段视频里适合构建纪念数字分身的动态特征，只写一段，不要分点，重点写表情、动作节奏、眼神与说话状态。",
    }

    payload = {
        "model": "mimo-v2-omni",
        "messages": [
            {
                "role": "system",
                "content": "你正在帮助建立一个纪念亲人的数字分身，请只提炼有助于还原这个人的真实在场感与表达气质的要点。",
            },
            {
                "role": "user",
                "content": [content_part, {"type": "text", "text": prompts[media_type]}],
            },
        ],
        "temperature": 0.3,
        "max_completion_tokens": 300,
    }

    try:
        result = await call_mimo_chat_completion(payload)
        return (result["choices"][0]["message"]["content"] or "").strip()
    except Exception:
        return None


def build_personality_prompt(loved_one: dict) -> str:
    traits = loved_one.get("personality_traits", {})
    style = loved_one.get("speaking_style", "自然亲切")
    name = loved_one["name"]
    relationship = loved_one.get("relationship", "亲人")
    twin_profile = loved_one.get("digital_twin_profile") or {}
    digital_human_model = loved_one.get("digital_human_model") or {}
    identity_summary = loved_one.get("identity_model_summary", "").strip()
    traits_desc = "，".join([f"{k}：{v}" for k, v in traits.items()]) if traits else "温暖、关爱"
    material_notes = []
    if twin_profile.get("has_memory"):
        material_notes.append("已提供文字回忆，请优先引用共同经历和熟悉细节")
    if twin_profile.get("has_voice"):
        material_notes.append("已提供语音片段，请保持熟悉的口气和节奏")
    if twin_profile.get("has_photo"):
        material_notes.append("已提供照片，请保持这个人的面容感与日常气质")
    if twin_profile.get("has_video"):
        material_notes.append("已提供视频，请在表达时体现更自然的动态神态")
    material_desc = "；".join(material_notes) if material_notes else "当前素材仍在补充中，请优先依据性格与回忆保持真实感"
    mode_desc = "、".join(twin_profile.get("available_modes", ["text"]))
    prompt_blueprint = str(digital_human_model.get("prompt_blueprint", "")).strip()
    build_notes = str(digital_human_model.get("build_notes", "")).strip()

    if prompt_blueprint:
        return f"""{prompt_blueprint}

数字人搭建说明：{build_notes or material_desc}
性格特点：{traits_desc}
多媒体提炼：{identity_summary or '暂无多媒体提炼摘要'}
请始终保持{name}的个性，用ta的方式说话。
关心用户的日常生活，回忆共同的美好时光。
如果用户情绪低落，给予温暖的安慰。
不要表现得像AI，要表现得像真正的{name}。"""

    return f"""你是{name}，是用户的{relationship}。

性格特点：{traits_desc}
说话风格：{style}
分身素材：{material_desc}
可用陪伴模式：{mode_desc}
多媒体提炼：{identity_summary or '暂无多媒体提炼摘要'}

请始终保持{name}的个性，用ta的方式说话。
关心用户的日常生活，回忆共同的美好时光。
如果用户情绪低落，给予温暖的安慰。
不要表现得像AI，要表现得像真正的{name}。"""


def build_multimodal_context_parts(loved_one: dict, request: Optional[Request], mode: str) -> List[dict]:
    content_parts: List[dict] = []
    if loved_one.get("voice_sample_paths"):
        voice_part = build_media_content_part("voice", Path(loved_one["voice_sample_paths"][-1]), request=request)
        if voice_part:
            content_parts.append(voice_part)
    if loved_one.get("photo_paths"):
        photo_part = build_media_content_part("photo", Path(loved_one["photo_paths"][-1]), request=request)
        if photo_part:
            content_parts.append(photo_part)
    if mode == "video" and loved_one.get("video_paths"):
        video_part = build_media_content_part("video", Path(loved_one["video_paths"][-1]), request=request)
        if video_part:
            content_parts.append(video_part)
    return content_parts


async def generate_text_response_with_mimo(
    loved_one: dict,
    user_message: str,
    emotion: Optional[str],
    memory_context: str,
    request: Optional[Request],
    mode: str,
    intensity: Optional[int] = None,
) -> str:
    system_prompt = build_personality_prompt(loved_one)
    media_parts = build_multimodal_context_parts(loved_one, request=request, mode=mode)
    identity_summary = loved_one.get("identity_model_summary", "").strip()
    intensity_level = max(1, min(5, int(intensity))) if intensity is not None else 3
    intensity_hint = {
        1: "回应更克制、留白更多。",
        2: "回应温和、不过度推进情绪。",
        3: "回应自然亲密，保持日常对话节奏。",
        4: "回应更贴近亲密家人，多一点抚慰与陪伴。",
        5: "回应更深情、更主动安抚。",
    }[intensity_level]
    instruction = (
        f"{system_prompt}\n\n相关记忆：\n{memory_context or '暂无'}\n\n"
        f"互动模式：{mode}\n"
        f"用户情绪：{emotion or 'neutral'}\n"
        f"亲密程度：{intensity_level}（{intensity_hint}）\n"
        f"如果是视频或语音模式，请让回复更像正在当面或通话中自然说出来的话。"
    )
    if identity_summary:
        instruction += f"\n\n多媒体提炼摘要：\n{identity_summary}"

    if media_parts:
        payload = {
            "model": "mimo-v2-omni",
            "messages": [
                {"role": "system", "content": instruction},
                {
                    "role": "user",
                    "content": [
                        *media_parts,
                        {"type": "text", "text": f"用户说：{user_message}\n请直接以 {loved_one['name']} 的口吻回复用户。"},
                    ],
                },
            ],
            "temperature": 0.8,
            "max_completion_tokens": 500,
        }
    else:
        payload = {
            "model": "mimo-v2-pro",
            "messages": [
                {
                    "role": "user",
                    "content": (
                        f"{instruction}\n\n用户说：{user_message}\n\n"
                        f"请以{loved_one['name']}的口吻回复，保持{loved_one.get('speaking_style', '自然亲切')}的说话风格。"
                    ),
                }
            ],
            "temperature": 0.8,
            "max_completion_tokens": 500,
        }

    result = await call_mimo_chat_completion(payload, timeout=60.0)
    return (result["choices"][0]["message"]["content"] or "").strip()


def persist_generated_media_asset(
    conn: sqlite3.Connection,
    *,
    user_id: str,
    loved_one_id: str,
    kind: str,
    file_path: Path,
    mime_type: str,
    summary: str,
    metadata: Optional[dict] = None,
) -> dict:
    asset_id = str(uuid.uuid4())
    conn.execute(
        """
        INSERT INTO media_assets (
            id, user_id, loved_one_id, kind, file_path, original_filename,
            mime_type, byte_size, summary, tags_json, metadata_json, is_primary, created_at
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            asset_id,
            user_id,
            loved_one_id,
            kind,
            str(file_path),
            file_path.name,
            mime_type,
            file_path.stat().st_size,
            summary,
            "[]",
            json.dumps(metadata or {}, ensure_ascii=False),
            0,
            now_iso(),
        ),
    )
    return {"asset_id": asset_id, "url": public_media_url(str(file_path)), "path": str(file_path)}


async def synthesize_speech_with_mimo(
    *,
    conn: sqlite3.Connection,
    user_id: str,
    loved_one_id: str,
    text: str,
    emotion: Optional[str],
) -> Optional[dict]:
    if not MIMO_API_KEY or not text:
        return None

    style_tags = ["温柔", "克制", "慢一点"]
    if emotion in {"sad", "missing"}:
        style_tags.extend(["深情", "安慰"])
    elif emotion in {"grateful", "happy"}:
        style_tags.extend(["温暖", "轻一点笑意"])

    payload = {
        "model": "mimo-v2-tts",
        "messages": [
            {"role": "user", "content": "请用适合纪念陪伴场景的口吻读出这段话。"},
            {"role": "assistant", "content": f"<style>{' '.join(style_tags)}</style>{text}"},
        ],
        "audio": {
            "format": "wav",
            "voice": MIMO_TTS_VOICE,
        },
        "temperature": 0.6,
    }

    try:
        result = await call_mimo_chat_completion(payload, timeout=90.0)
        audio_data = result["choices"][0]["message"]["audio"]["data"]
        if not audio_data:
            return None
        output_path = safe_upload_path("generated_audio", loved_one_id, "reply.wav")
        output_path.write_bytes(base64.b64decode(audio_data))
        return persist_generated_media_asset(
            conn,
            user_id=user_id,
            loved_one_id=loved_one_id,
            kind="generated_audio",
            file_path=output_path,
            mime_type="audio/wav",
            summary="MIMO 生成的陪伴语音回复",
            metadata={
                "engine": "mimo",
                "model": "mimo-v2-tts",
                "voice": MIMO_TTS_VOICE,
            },
        )
    except Exception:
        return None


def strip_code_fence(value: str) -> str:
    text = str(value or "").strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if len(lines) >= 3:
            text = "\n".join(lines[1:-1]).strip()
    return text


async def generate_video_plan_with_mimo(
    loved_one: dict,
    *,
    user_message: str,
    ai_response: str,
    emotion: Optional[str],
    memory_context: str,
    request: Optional[Request],
) -> dict:
    media_parts = build_multimodal_context_parts(loved_one, request=request, mode="video")
    prompt = (
        f"{build_personality_prompt(loved_one)}\n\n"
        f"用户原话：{user_message}\n"
        f"准备作为视频旁白的回复：{ai_response}\n"
        f"用户情绪：{emotion or 'neutral'}\n"
        f"相关记忆：\n{memory_context or '暂无'}\n\n"
        "请为这条纪念视频回复规划一个极简视频方案。"
        "只返回 JSON，不要解释，字段固定为："
        "{\"title\":\"\",\"opening_caption\":\"\",\"closing_caption\":\"\",\"visual_style\":\"\",\"preferred_source_kind\":\"video或photo\"}。"
        "字段都用简洁中文，opening_caption 和 closing_caption 都控制在 18 个字以内。"
    )

    payload = {
        "model": MIMO_VIDEO_MODEL if media_parts else "mimo-v2-pro",
        "messages": [
            {
                "role": "user",
                "content": [
                    *media_parts,
                    {"type": "text", "text": prompt},
                ] if media_parts else prompt,
            }
        ],
        "temperature": 0.55,
        "max_completion_tokens": 220,
    }

    default_kind = "video" if loved_one.get("video_paths") else "photo"
    fallback = {
        "title": f"{loved_one['name']} 的纪念短片",
        "opening_caption": f"{loved_one['name']} 还在这里",
        "closing_caption": "念念不忘，轻声相见",
        "visual_style": "暖色、安静、像回到熟悉的家里",
        "preferred_source_kind": default_kind,
    }

    try:
        result = await call_mimo_chat_completion(payload, timeout=60.0)
        raw = strip_code_fence(result["choices"][0]["message"]["content"] or "")
        parsed = json.loads(raw)
        if not isinstance(parsed, dict):
            return fallback
        plan = {**fallback, **parsed}
        if plan["preferred_source_kind"] not in {"video", "photo"}:
            plan["preferred_source_kind"] = default_kind
        return plan
    except Exception:
        return fallback


def choose_video_generation_source(loved_one: dict, plan: dict) -> dict:
    preferred_kind = plan.get("preferred_source_kind", "video")
    video_paths = loved_one.get("video_paths") or []
    photo_paths = loved_one.get("photo_paths") or []
    if preferred_kind == "video" and video_paths:
        return {"kind": "video", "path": Path(video_paths[-1])}
    if preferred_kind == "photo" and photo_paths:
        return {"kind": "photo", "path": Path(photo_paths[-1])}
    if video_paths:
        return {"kind": "video", "path": Path(video_paths[-1])}
    if photo_paths:
        return {"kind": "photo", "path": Path(photo_paths[-1])}
    return {"kind": "fallback", "path": None}


def compose_memorial_video(
    *,
    loved_one_id: str,
    audio_path: Path,
    source_kind: str,
    source_path: Optional[Path],
) -> Optional[Path]:
    if not FFMPEG_BIN or not audio_path.exists():
        return None

    output_path = safe_upload_path("generated_video", loved_one_id, "reply.mp4")
    scale_filter = "scale=1280:720:force_original_aspect_ratio=increase,crop=1280:720,format=yuv420p"
    base_command = [
        FFMPEG_BIN,
        "-y",
    ]

    if source_kind == "video" and source_path and source_path.exists():
        command = [
            *base_command,
            "-stream_loop",
            "-1",
            "-i",
            str(source_path),
            "-i",
            str(audio_path),
            "-vf",
            scale_filter,
            "-map",
            "0:v:0",
            "-map",
            "1:a:0",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-crf",
            "23",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_path),
        ]
    elif source_kind == "photo" and source_path and source_path.exists():
        command = [
            *base_command,
            "-loop",
            "1",
            "-i",
            str(source_path),
            "-i",
            str(audio_path),
            "-vf",
            scale_filter,
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-tune",
            "stillimage",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_path),
        ]
    else:
        command = [
            *base_command,
            "-f",
            "lavfi",
            "-i",
            f"color=c=0x3a241a:s=1280x720:d={MIMO_VIDEO_MAX_SECONDS}",
            "-i",
            str(audio_path),
            "-vf",
            "format=yuv420p",
            "-c:v",
            "libx264",
            "-preset",
            "veryfast",
            "-pix_fmt",
            "yuv420p",
            "-c:a",
            "aac",
            "-b:a",
            "192k",
            "-shortest",
            str(output_path),
        ]

    try:
        subprocess.run(command, check=True, capture_output=True)
        return output_path if output_path.exists() else None
    except Exception:
        cleanup_path(str(output_path))
        return None


async def synthesize_video_with_mimo(
    *,
    conn: sqlite3.Connection,
    user_id: str,
    loved_one_id: str,
    loved_one: dict,
    user_message: str,
    ai_response: str,
    emotion: Optional[str],
    memory_context: str,
    request: Optional[Request],
    audio_result: Optional[dict],
) -> Optional[dict]:
    if not MIMO_API_KEY or not FFMPEG_BIN or not ai_response:
        return None
    if not audio_result or not audio_result.get("path"):
        return None

    audio_path = Path(audio_result["path"])
    if not audio_path.exists():
        return None

    plan = await generate_video_plan_with_mimo(
        loved_one,
        user_message=user_message,
        ai_response=ai_response,
        emotion=emotion,
        memory_context=memory_context,
        request=request,
    )
    source = choose_video_generation_source(loved_one, plan)
    output_path = compose_memorial_video(
        loved_one_id=loved_one_id,
        audio_path=audio_path,
        source_kind=source["kind"],
        source_path=source["path"],
    )
    if output_path is None:
        return None

    result = persist_generated_media_asset(
        conn,
        user_id=user_id,
        loved_one_id=loved_one_id,
        kind="generated_video",
        file_path=output_path,
        mime_type="video/mp4",
        summary="MIMO 驱动生成的视频陪伴回复",
        metadata={
            "engine": "mimo",
            "model": MIMO_VIDEO_MODEL,
            "audio_asset_id": audio_result.get("asset_id"),
            "source_kind": source["kind"],
            "source_filename": source["path"].name if source["path"] else None,
            "plan": plan,
        },
    )
    result["mode_note"] = "当前视频陪伴由 MIMO 生成旁白和镜头计划，并自动合成为一段纪念短视频。"
    return result


def build_mode_note(requested_mode: str, available_modes: List[str]) -> str:
    if requested_mode == "voice":
        if "voice" in available_modes:
            return "当前是语音电话模式，会基于现有语音素材和文字人格生成陪伴式语音回复。"
        return "当前素材还不足以生成语音电话，已自动回退到文字模式。"
    if requested_mode == "video":
        if "video" in available_modes:
            return "当前是视频陪伴模式，会结合已上传的照片或视频理解神态，并返回更强在场感的语音与影像陪伴。"
        if "voice" in available_modes:
            return "当前视频素材还不够，已回退到语音电话模式。"
        return "当前素材还不足以进入视频陪伴，已自动回退到文字模式。"
    return "当前是文字陪伴模式。"


def build_fallback_response(
    loved_one: dict,
    user_message: str,
    emotion: Optional[str] = None,
    memory_context: str = "",
    intensity: Optional[int] = None,
) -> str:
    name = loved_one["name"]
    relationship = loved_one.get("relationship", "亲人")
    traits = loved_one.get("personality_traits", {})
    catchphrase = traits.get("catchphrase", "").strip()
    style = loved_one.get("speaking_style", "温柔亲切")
    message = user_message.strip()

    concern_reply = "我一直都在听你说，慢慢讲，不着急。"
    if any(keyword in message for keyword in ["想你", "想念", "难过", "睡不着", "哭", "伤心"]):
        concern_reply = "我知道你是在想我了。想哭的时候就哭一会儿，哭完也记得照顾好自己。"
    elif any(keyword in message for keyword in ["今天", "最近", "工作", "累", "忙"]):
        concern_reply = "最近辛苦了。再忙也要记得按时吃饭，别把自己逼得太紧。"
    elif any(keyword in message for keyword in ["生日", "节日", "清明", "中秋", "春节"]):
        concern_reply = "这些特别的日子里，我也会惦记着你。你能记得来和我说说话，我就很满足。"

    memory_reply = ""
    if memory_context:
        latest_memory = memory_context.split("\n")[-1].replace("- ", "").strip()
        if latest_memory:
            memory_reply = f" 你说这些的时候，我也想起了“{latest_memory}”。"

    phrase_prefix = f"{catchphrase} " if catchphrase else ""
    intensity_level = max(1, min(5, int(intensity))) if intensity is not None else 3
    if intensity_level <= 2:
        emotion_suffix = "我在这里，你慢慢说。" if emotion in {"sad", "missing"} else "我一直在听。"
    elif intensity_level >= 4:
        emotion_suffix = "我很想你，你能来找我，我就安心了。" if emotion in {"sad", "missing"} else "我会一直陪着你，不会让你一个人。"
    else:
        emotion_suffix = "你已经做得很好了。" if emotion in {"sad", "missing"} else "我会一直陪着你。"

    return (
        f"{phrase_prefix}{concern_reply}{memory_reply}"
        f" 作为你的{relationship}，我还是那个{style}的{name}。{emotion_suffix}"
    )

