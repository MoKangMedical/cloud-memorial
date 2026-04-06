"""
念念 - AI思念亲人平台
核心API服务
"""
import base64
import json
import mimetypes
import os
import uuid
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any, Dict, List, Optional

from fastapi import FastAPI, HTTPException, UploadFile, File, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field
import httpx

app = FastAPI(
    title="念念 API",
    description="AI思念亲人平台 - 念念不忘，ta一直在",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== 配置 =====
BASE_DIR = Path(__file__).resolve().parent.parent
FRONTEND_FILE = BASE_DIR / "frontend" / "index.html"
ASSETS_DIR = BASE_DIR / "frontend" / "assets"


def load_runtime_settings() -> Dict[str, str]:
    settings: Dict[str, str] = {}
    candidates = [
        BASE_DIR / ".runtime-secrets.json",
        BASE_DIR / ".env.local",
    ]

    for candidate in candidates:
        if not candidate.exists():
            continue
        if candidate.suffix == ".json":
            try:
                raw = json.loads(candidate.read_text(encoding="utf-8"))
                if isinstance(raw, dict):
                    settings.update({str(key): str(value) for key, value in raw.items() if value is not None})
            except json.JSONDecodeError:
                continue
            continue

        for line in candidate.read_text(encoding="utf-8").splitlines():
            stripped = line.strip()
            if not stripped or stripped.startswith("#") or "=" not in stripped:
                continue
            key, value = stripped.split("=", 1)
            settings[key.strip()] = value.strip().strip("'\"")
    return settings


RUNTIME_SETTINGS = load_runtime_settings()


def runtime_config(name: str, default: str = "") -> str:
    return os.getenv(name) or str(RUNTIME_SETTINGS.get(name, default))


MIMO_API_BASE = runtime_config("MIMO_API_BASE", "https://api.xiaomimimo.com/v1")
MIMO_API_KEY = runtime_config("MIMO_API_KEY", "")
MIMO_TTS_VOICE = runtime_config("MIMO_TTS_VOICE", "default_zh")
PUBLIC_BASE_URL = runtime_config("PUBLIC_BASE_URL", "").rstrip("/")
DEFAULT_DATA_DIR = Path("/tmp/memorial_data") if os.getenv("VERCEL") else BASE_DIR / "memorial_data"
DATA_DIR = Path(os.getenv("DATA_DIR", str(DEFAULT_DATA_DIR)))
DATA_DIR.mkdir(parents=True, exist_ok=True)
GENERATED_AUDIO_DIR = DATA_DIR / "generated_audio"
GENERATED_AUDIO_DIR.mkdir(parents=True, exist_ok=True)

if ASSETS_DIR.exists():
    app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
app.mount("/media", StaticFiles(directory=DATA_DIR), name="media")

# ===== 数据模型 =====
class LovedOne(BaseModel):
    id: Optional[str] = None
    name: str
    relationship: str  # 父亲/母亲/配偶/子女/...
    birth_date: Optional[str] = None
    pass_away_date: Optional[str] = None
    personality_traits: Dict = Field(default_factory=dict)
    speaking_style: str = ""
    memories: List[str] = Field(default_factory=list)
    voice_sample_path: Optional[str] = None
    voice_sample_paths: List[str] = Field(default_factory=list)
    voice_sample_urls: List[str] = Field(default_factory=list)
    photo_paths: List[str] = Field(default_factory=list)
    photo_urls: List[str] = Field(default_factory=list)
    video_paths: List[str] = Field(default_factory=list)
    video_urls: List[str] = Field(default_factory=list)
    media_insights: Dict = Field(default_factory=dict)
    identity_model_summary: str = ""
    digital_twin_profile: Dict = Field(default_factory=dict)

class ChatMessage(BaseModel):
    loved_one_id: str
    message: str
    emotion: Optional[str] = None  # happy/sad/missing/grateful
    mode: str = "text"  # text/voice/video

class ChatResponse(BaseModel):
    loved_one_id: str
    loved_one_name: str
    response_text: str
    response_audio_url: Optional[str] = None
    response_video_url: Optional[str] = None
    interaction_mode: str = "text"
    mode_note: Optional[str] = None
    available_modes: List[str] = Field(default_factory=list)
    emotion_detected: str
    memory_triggered: Optional[str] = None

class MemoryEntry(BaseModel):
    loved_one_id: str
    content: str
    memory_type: str  # event/feeling/conversation/photo
    date: Optional[str] = None
    importance: int = 5  # 1-10

class GreetingSchedule(BaseModel):
    loved_one_id: str
    greeting_type: str  # birthday/holiday/weather/daily
    trigger_date: str
    message_template: str

# ===== 存储 =====
def load_data(filename: str) -> dict:
    filepath = DATA_DIR / filename
    if filepath.exists():
        try:
            return json.loads(filepath.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return {}
    return {}

def save_data(filename: str, data: dict):
    filepath = DATA_DIR / filename
    filepath.write_text(
        json.dumps(data, ensure_ascii=False, indent=2),
        encoding="utf-8"
    )


def get_memory_entries(loved_one_id: Optional[str]) -> List[dict]:
    if not loved_one_id:
        return []
    memories = load_data("memories.json")
    return memories.get(loved_one_id, [])


def mimo_headers() -> Dict[str, str]:
    return {
        "Authorization": f"Bearer {MIMO_API_KEY}",
        "api-key": MIMO_API_KEY,
        "Content-Type": "application/json",
    }


def unique_preserve_order(values: List[str]) -> List[str]:
    seen = set()
    normalized = []
    for value in values:
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def public_media_url(path_str: str) -> Optional[str]:
    if not path_str:
        return None

    path = Path(path_str)
    try:
        relative = path.resolve().relative_to(DATA_DIR.resolve())
    except ValueError:
        return None
    return f"/media/{relative.as_posix()}"


def make_absolute_media_url(path_str: str, request: Optional[Request] = None) -> Optional[str]:
    relative = public_media_url(path_str)
    if not relative:
        return None

    base_url = PUBLIC_BASE_URL
    if not base_url and request is not None:
        base_url = str(request.base_url).rstrip("/")

    if not base_url:
        return None
    return f"{base_url}{relative}"


def is_publicly_reachable_url(url: Optional[str]) -> bool:
    if not url:
        return False
    return not any(local in url for local in ["127.0.0.1", "localhost", "0.0.0.0"])


def infer_mime_type(path: Path, fallback: str) -> str:
    guessed, _ = mimetypes.guess_type(path.name)
    return guessed or fallback


def encode_data_url(path: Path, fallback_mime: str, max_bytes: int = 10 * 1024 * 1024) -> Optional[str]:
    if not path.exists() or path.stat().st_size > max_bytes:
        return None
    mime_type = infer_mime_type(path, fallback_mime)
    return f"data:{mime_type};base64,{base64.b64encode(path.read_bytes()).decode('ascii')}"


def ensure_media_insights(record: dict) -> Dict[str, List[dict]]:
    insights = record.setdefault("media_insights", {})
    insights.setdefault("voice", [])
    insights.setdefault("photo", [])
    insights.setdefault("video", [])
    return insights


def build_available_modes(loved_one: dict) -> List[str]:
    voice_count = len(loved_one.get("voice_sample_paths", []) or [])
    photo_count = len(loved_one.get("photo_paths", []) or [])
    video_count = len(loved_one.get("video_paths", []) or [])
    modes = ["text"]
    if voice_count > 0:
        modes.append("voice")
    if voice_count > 0 and (photo_count > 0 or video_count > 0):
        modes.append("video")
    return modes


def build_digital_twin_profile(loved_one: dict, memory_count: int = 0) -> dict:
    voice_paths = loved_one.get("voice_sample_paths", [])
    photo_paths = loved_one.get("photo_paths", [])
    video_paths = loved_one.get("video_paths", [])
    text_memory_count = memory_count or len([item for item in loved_one.get("memories", []) if str(item).strip()])

    voice_count = len(voice_paths)
    photo_count = len(photo_paths)
    video_count = len(video_paths)
    coverage = sum(1 for count in [text_memory_count, voice_count, photo_count, video_count] if count > 0)
    profile_signal_count = sum(
        1
        for signal in [
            loved_one.get("name"),
            loved_one.get("relationship"),
            loved_one.get("speaking_style"),
            loved_one.get("personality_traits"),
        ]
        if signal
    )
    coverage_score = coverage / 4 * 0.55
    depth_score = (
        min(text_memory_count, 8) / 8 * 0.15
        + min(voice_count, 3) / 3 * 0.12
        + min(photo_count, 4) / 4 * 0.08
        + min(video_count, 2) / 2 * 0.06
        + profile_signal_count / 4 * 0.04
    )
    completion_percent = round((coverage_score + depth_score) * 100)

    if coverage == 0:
        label = "待补充分身素材"
        summary = "先留下几段文字记忆，再补充语音、照片和视频，数字分身才会逐渐像 ta。"
    elif completion_percent < 55:
        label = "分身轮廓已开始成形"
        summary = "已经留住了一部分辨识度，继续补充回忆、声音和影像，这个分身会更接近 ta。"
    elif completion_percent < 82:
        label = "立体分身正在成形"
        summary = "文字记忆、声音和影像已经开始互相校准，数字分身会更接近 ta 的真实感觉。"
    else:
        label = "完整数字分身已就绪"
        summary = "文字、声音、照片和动态影像都已具备，这个数字分身已经有了更完整的在场感。"

    return {
        "memory_count": text_memory_count,
        "voice_count": voice_count,
        "photo_count": photo_count,
        "video_count": video_count,
        "has_memory": text_memory_count > 0,
        "has_voice": voice_count > 0,
        "has_photo": photo_count > 0,
        "has_video": video_count > 0,
        "coverage": coverage,
        "completion_percent": completion_percent,
        "completeness_label": label,
        "summary": summary,
        "available_modes": build_available_modes({
            "voice_sample_paths": voice_paths,
            "photo_paths": photo_paths,
            "video_paths": video_paths,
        }),
    }


def normalize_loved_one_record(record: dict) -> dict:
    normalized = dict(record)
    normalized.pop("voice_sample_urls", None)
    normalized.pop("photo_urls", None)
    normalized.pop("video_urls", None)
    normalized.pop("digital_twin_profile", None)

    normalized.setdefault("personality_traits", {})
    normalized.setdefault("memories", [])
    normalized.setdefault("photo_paths", [])
    normalized.setdefault("video_paths", [])
    normalized.setdefault("media_insights", {})
    normalized.setdefault("identity_model_summary", "")
    normalized["memories"] = unique_preserve_order(
        [str(item).strip() for item in normalized.get("memories", []) if str(item).strip()]
    )

    voice_paths = normalized.get("voice_sample_paths", []) or []
    primary_voice = normalized.get("voice_sample_path")
    if primary_voice and primary_voice not in voice_paths:
        voice_paths.insert(0, primary_voice)
    voice_paths = unique_preserve_order(voice_paths)
    normalized["voice_sample_paths"] = voice_paths
    if voice_paths:
        normalized["voice_sample_path"] = voice_paths[0]

    normalized["photo_paths"] = unique_preserve_order(normalized.get("photo_paths", []))
    normalized["video_paths"] = unique_preserve_order(normalized.get("video_paths", []))
    ensure_media_insights(normalized)
    return normalized


def serialize_loved_one(record: dict) -> LovedOne:
    normalized = normalize_loved_one_record(record)
    memory_count = len(get_memory_entries(normalized.get("id")))
    normalized["voice_sample_urls"] = [
        url for url in (public_media_url(path) for path in normalized.get("voice_sample_paths", [])) if url
    ]
    normalized["photo_urls"] = [
        url for url in (public_media_url(path) for path in normalized.get("photo_paths", [])) if url
    ]
    normalized["video_urls"] = [
        url for url in (public_media_url(path) for path in normalized.get("video_paths", [])) if url
    ]
    normalized["digital_twin_profile"] = build_digital_twin_profile(normalized, memory_count=memory_count)
    return LovedOne(**normalized)


def safe_upload_path(kind: str, loved_one_id: str, filename: Optional[str]) -> Path:
    ext = Path(filename or "").suffix or ""
    safe_name = f"{datetime.now().strftime('%Y%m%d%H%M%S')}-{uuid.uuid4().hex[:8]}{ext}"
    target_dir = DATA_DIR / kind / loved_one_id
    target_dir.mkdir(parents=True, exist_ok=True)
    return target_dir / safe_name


def latest_media_summary(loved_one: dict, kind: str) -> str:
    insights = loved_one.get("media_insights", {}).get(kind, [])
    if not insights:
        return ""
    return "；".join(item.get("summary", "").strip() for item in insights[-2:] if item.get("summary"))


def compose_identity_model_summary(loved_one: dict) -> str:
    parts = []
    voice_summary = latest_media_summary(loved_one, "voice")
    photo_summary = latest_media_summary(loved_one, "photo")
    video_summary = latest_media_summary(loved_one, "video")
    if voice_summary:
        parts.append(f"语音特征：{voice_summary}")
    if photo_summary:
        parts.append(f"面容与气质：{photo_summary}")
    if video_summary:
        parts.append(f"动态神态：{video_summary}")
    return "\n".join(parts)


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
    loved_one: dict,
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
                "content": [
                    content_part,
                    {"type": "text", "text": prompts[media_type]},
                ],
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


async def enrich_media_insights(
    loved_one_id: str,
    request: Optional[Request] = None,
) -> dict:
    data = load_data("loved_ones.json")
    loved_one = normalize_loved_one_record(data[loved_one_id])
    media_insights = ensure_media_insights(loved_one)
    changed = False

    path_map = {
        "voice": loved_one.get("voice_sample_paths", []),
        "photo": loved_one.get("photo_paths", []),
        "video": loved_one.get("video_paths", []),
    }

    for media_type, paths in path_map.items():
        analyzed_paths = {item.get("path") for item in media_insights.get(media_type, [])}
        for path_str in paths:
            if path_str in analyzed_paths:
                continue
            summary = await analyze_media_with_mimo(loved_one, media_type, Path(path_str), request=request)
            if summary:
                media_insights[media_type].append({
                    "path": path_str,
                    "summary": summary,
                    "created_at": datetime.now().isoformat(),
                })
                changed = True

    if changed:
        loved_one["identity_model_summary"] = compose_identity_model_summary(loved_one)
        data[loved_one_id] = normalize_loved_one_record(loved_one)
        data[loved_one_id]["media_insights"] = loved_one["media_insights"]
        data[loved_one_id]["identity_model_summary"] = loved_one["identity_model_summary"]
        save_data("loved_ones.json", data)

    return data[loved_one_id]


async def synthesize_speech_with_mimo(
    loved_one: dict,
    text: str,
    emotion: Optional[str],
    loved_one_id: str,
) -> Optional[str]:
    if not MIMO_API_KEY or not text:
        return None

    style_tags = ["温柔", "克制", "慢一点"]
    if emotion in {"sad", "missing"}:
        style_tags.extend(["深情", "安慰"])
    elif emotion in {"grateful", "happy"}:
        style_tags.extend(["温暖", "轻一点笑意"])

    role_prefix = f"<style>{' '.join(style_tags)}</style>"
    payload = {
        "model": "mimo-v2-tts",
        "messages": [
            {"role": "user", "content": f"请用适合纪念陪伴场景的口吻读出这段话。"},
            {"role": "assistant", "content": f"{role_prefix}{text}"},
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
        audio_bytes = base64.b64decode(audio_data)
        output_path = safe_upload_path("generated_audio", loved_one_id, "reply.wav")
        output_path.write_bytes(audio_bytes)
        return public_media_url(str(output_path))
    except Exception:
        return None


def build_mode_note(mode: str, twin_profile: dict) -> str:
    available_modes = twin_profile.get("available_modes", ["text"])
    if mode == "voice":
        if "voice" in available_modes:
            return "当前是语音电话模式，会基于现有语音素材和文字人格生成陪伴式语音回复。"
        return "当前素材还不足以生成语音电话，已自动回退到文字模式。"
    if mode == "video":
        if "video" in available_modes:
            return "当前是视频陪伴模式，会结合已上传的照片或视频理解神态，并返回更强在场感的语音与影像陪伴。"
        if "voice" in available_modes:
            return "当前视频素材还不够，已回退到语音电话模式。"
        return "当前素材还不足以进入视频陪伴，已自动回退到文字模式。"
    return "当前是文字陪伴模式。"


def select_video_presence_url(loved_one: dict) -> Optional[str]:
    video_urls = loved_one.get("video_urls", [])
    if video_urls:
        return video_urls[-1]
    return None


def build_multimodal_context_parts(
    loved_one: dict,
    request: Optional[Request],
    mode: str,
) -> List[dict]:
    content_parts: List[dict] = []
    candidate_assets = [
        ("voice", loved_one.get("voice_sample_paths", [])[-1:] if loved_one.get("voice_sample_paths") else []),
        ("photo", loved_one.get("photo_paths", [])[-1:] if loved_one.get("photo_paths") else []),
    ]
    if mode == "video":
        candidate_assets.append(("video", loved_one.get("video_paths", [])[-1:] if loved_one.get("video_paths") else []))

    for media_type, paths in candidate_assets:
        for path_str in paths:
            part = build_media_content_part(media_type, Path(path_str), request=request)
            if part:
                content_parts.append(part)
    return content_parts


async def generate_text_response_with_mimo(
    loved_one: dict,
    user_message: str,
    emotion: Optional[str],
    memory_context: str,
    request: Optional[Request],
    mode: str,
) -> str:
    system_prompt = build_personality_prompt(loved_one)
    media_parts = build_multimodal_context_parts(loved_one, request=request, mode=mode)
    identity_summary = loved_one.get("identity_model_summary", "").strip()
    instruction = (
        f"{system_prompt}\n\n相关记忆：\n{memory_context or '暂无'}\n\n"
        f"互动模式：{mode}\n"
        f"用户情绪：{emotion or 'neutral'}\n"
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

# ===== API 端点 =====

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "念念",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.get("/")
async def index():
    if FRONTEND_FILE.exists():
        return FileResponse(FRONTEND_FILE)
    raise HTTPException(status_code=404, detail="前端页面未找到")

@app.post("/api/loved-ones", response_model=LovedOne)
async def create_loved_one(loved_one: LovedOne):
    """创建亲人档案"""
    loved_one.id = str(uuid.uuid4())
    data = load_data("loved_ones.json")
    initial_memories = unique_preserve_order([item.strip() for item in loved_one.memories if item and item.strip()])
    payload = loved_one.model_dump()
    payload["memories"] = initial_memories
    data[loved_one.id] = normalize_loved_one_record(payload)
    save_data("loved_ones.json", data)

    if initial_memories:
        memories = load_data("memories.json")
        bucket = memories.setdefault(loved_one.id, [])
        existing_contents = {item.get("content") for item in bucket}
        for content in initial_memories:
            if content in existing_contents:
                continue
            bucket.append({
                "id": str(uuid.uuid4()),
                "loved_one_id": loved_one.id,
                "content": content,
                "memory_type": "conversation",
                "importance": 7,
                "created_at": datetime.now().isoformat(),
            })
        save_data("memories.json", memories)

    return serialize_loved_one(data[loved_one.id])

@app.get("/api/loved-ones", response_model=List[LovedOne])
async def list_loved_ones():
    """列出所有亲人"""
    data = load_data("loved_ones.json")
    return [serialize_loved_one(v) for v in data.values()]

@app.get("/api/loved-ones/{loved_one_id}", response_model=LovedOne)
async def get_loved_one(loved_one_id: str):
    """获取亲人详情"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")
    return serialize_loved_one(data[loved_one_id])

@app.post("/api/loved-ones/{loved_one_id}/voice")
async def upload_voice_sample(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...)
):
    """上传亲人的语音样本（用于声音电话与分身语气建模）"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    # 保存语音文件
    voice_path = safe_upload_path("voices", loved_one_id, file.filename)

    content = await file.read()
    voice_path.write_bytes(content)

    # 更新档案
    loved_one = normalize_loved_one_record(data[loved_one_id])
    loved_one["voice_sample_path"] = str(voice_path)
    loved_one.setdefault("voice_sample_paths", []).append(str(voice_path))
    data[loved_one_id] = normalize_loved_one_record(loved_one)
    save_data("loved_ones.json", data)
    enriched = await enrich_media_insights(loved_one_id, request=request)

    return {
        "status": "uploaded",
        "path": str(voice_path),
        "url": public_media_url(str(voice_path)),
        "message": "语音样本已上传，正在为这个数字分身校准声音与通话语气...",
        "loved_one": serialize_loved_one(enriched).model_dump()
    }

@app.post("/api/loved-ones/{loved_one_id}/photo")
async def upload_photo(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...)
):
    """上传亲人的照片（用于形成更完整的视觉分身）"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    # 保存照片
    photo_path = safe_upload_path("photos", loved_one_id, file.filename)

    content = await file.read()
    photo_path.write_bytes(content)

    # 更新档案
    loved_one = normalize_loved_one_record(data[loved_one_id])
    loved_one.setdefault("photo_paths", []).append(str(photo_path))
    data[loved_one_id] = normalize_loved_one_record(loved_one)
    save_data("loved_ones.json", data)
    enriched = await enrich_media_insights(loved_one_id, request=request)

    return {
        "status": "uploaded",
        "path": str(photo_path),
        "url": public_media_url(str(photo_path)),
        "message": "照片已上传，分身的面容正在变得更清晰。",
        "loved_one": serialize_loved_one(enriched).model_dump()
    }


@app.post("/api/loved-ones/{loved_one_id}/video")
async def upload_video(
    loved_one_id: str,
    request: Request,
    file: UploadFile = File(...)
):
    """上传亲人的视频（用于形成更完整的动态分身）"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    video_path = safe_upload_path("videos", loved_one_id, file.filename)

    content = await file.read()
    video_path.write_bytes(content)

    loved_one = normalize_loved_one_record(data[loved_one_id])
    loved_one.setdefault("video_paths", []).append(str(video_path))
    data[loved_one_id] = normalize_loved_one_record(loved_one)
    save_data("loved_ones.json", data)
    enriched = await enrich_media_insights(loved_one_id, request=request)

    return {
        "status": "uploaded",
        "path": str(video_path),
        "url": public_media_url(str(video_path)),
        "message": "视频已上传，分身开始拥有更完整的动态神态。",
        "loved_one": serialize_loved_one(enriched).model_dump()
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_loved_one(msg: ChatMessage, request: Request):
    """与亲人的AI分身对话"""
    data = load_data("loved_ones.json")
    if msg.loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    loved_one = normalize_loved_one_record(data[msg.loved_one_id])
    loved_one = serialize_loved_one(loved_one).model_dump()
    twin_profile = loved_one.get("digital_twin_profile", {})
    requested_mode = (msg.mode or "text").lower()
    interaction_mode = requested_mode
    available_modes = twin_profile.get("available_modes", ["text"])
    if requested_mode == "video" and "video" not in available_modes:
        interaction_mode = "voice" if "voice" in available_modes else "text"
    elif requested_mode == "voice" and "voice" not in available_modes:
        interaction_mode = "text"

    # 加载相关记忆
    memories = load_data("memories.json")
    loved_one_memories = memories.get(msg.loved_one_id, [])
    memory_context = "\n".join([
        f"- {m['content']}" for m in loved_one_memories[-10:]
    ])

    if MIMO_API_KEY:
        try:
            ai_response = await generate_text_response_with_mimo(
                loved_one=loved_one,
                user_message=msg.message,
                emotion=msg.emotion,
                memory_context=memory_context,
                request=request,
                mode=interaction_mode,
            )
        except Exception:
            ai_response = build_fallback_response(
                loved_one=loved_one,
                user_message=msg.message,
                emotion=msg.emotion,
                memory_context=memory_context
            )
    else:
        ai_response = build_fallback_response(
            loved_one=loved_one,
            user_message=msg.message,
            emotion=msg.emotion,
            memory_context=memory_context
        )

    response_audio_url = None
    response_video_url = None
    if interaction_mode in {"voice", "video"}:
        response_audio_url = await synthesize_speech_with_mimo(
            loved_one=loved_one,
            text=ai_response,
            emotion=msg.emotion,
            loved_one_id=msg.loved_one_id,
        )

    if interaction_mode == "video":
        response_video_url = select_video_presence_url(loved_one)

    # 保存对话记录
    chat_history = load_data("chat_history.json")
    if msg.loved_one_id not in chat_history:
        chat_history[msg.loved_one_id] = []
    chat_history[msg.loved_one_id].append({
        "timestamp": datetime.now().isoformat(),
        "user_message": msg.message,
        "ai_response": ai_response,
        "emotion": msg.emotion,
        "mode": interaction_mode,
    })
    save_data("chat_history.json", chat_history)

    return ChatResponse(
        loved_one_id=msg.loved_one_id,
        loved_one_name=loved_one["name"],
        response_text=ai_response,
        response_audio_url=response_audio_url,
        response_video_url=response_video_url,
        interaction_mode=interaction_mode,
        mode_note=build_mode_note(requested_mode, twin_profile),
        available_modes=available_modes,
        emotion_detected=msg.emotion or "neutral",
        memory_triggered=memory_context[:100] if memory_context else None
    )

@app.post("/api/memories")
async def add_memory(memory: MemoryEntry):
    """添加回忆"""
    memories = load_data("memories.json")
    if memory.loved_one_id not in memories:
        memories[memory.loved_one_id] = []

    memory_dict = memory.dict()
    memory_dict["id"] = str(uuid.uuid4())
    memory_dict["created_at"] = datetime.now().isoformat()
    memories[memory.loved_one_id].append(memory_dict)
    save_data("memories.json", memories)

    return {"status": "saved", "memory_id": memory_dict["id"]}

@app.get("/api/memories/{loved_one_id}")
async def get_memories(loved_one_id: str, limit: int = 50):
    """获取亲人的回忆"""
    memories = load_data("memories.json")
    loved_one_memories = memories.get(loved_one_id, [])
    return loved_one_memories[-limit:]

@app.post("/api/greetings/schedule")
async def schedule_greeting(greeting: GreetingSchedule):
    """设置问候提醒"""
    greetings = load_data("greetings.json")
    greeting_id = str(uuid.uuid4())
    greetings[greeting_id] = {
        **greeting.dict(),
        "id": greeting_id,
        "status": "scheduled",
        "created_at": datetime.now().isoformat()
    }
    save_data("greetings.json", greetings)
    return {"status": "scheduled", "greeting_id": greeting_id}

@app.get("/api/greetings/upcoming")
async def upcoming_greetings(days: int = 7):
    """获取即将到来的问候"""
    greetings = load_data("greetings.json")
    today = datetime.now()
    upcoming = []
    for g in greetings.values():
        try:
            trigger = datetime.fromisoformat(g["trigger_date"])
            if today <= trigger <= today + timedelta(days=days):
                upcoming.append(g)
        except:
            pass
    return upcoming

@app.get("/api/stats")
async def get_stats():
    """获取平台统计"""
    loved_ones = load_data("loved_ones.json")
    memories = load_data("memories.json")
    chat_history = load_data("chat_history.json")

    total_messages = sum(len(msgs) for msgs in chat_history.values())

    return {
        "total_loved_ones": len(loved_ones),
        "total_memories": sum(len(m) for m in memories.values()),
        "total_messages": total_messages,
        "active_families": len(loved_ones)
    }

# ===== 辅助函数 =====

def build_personality_prompt(loved_one: dict) -> str:
    """构建人格提示词"""
    traits = loved_one.get("personality_traits", {})
    style = loved_one.get("speaking_style", "自然亲切")
    name = loved_one["name"]
    relationship = loved_one.get("relationship", "亲人")

    traits_desc = "，".join([f"{k}：{v}" for k, v in traits.items()]) if traits else "温暖、关爱"
    twin_profile = build_digital_twin_profile(
        normalize_loved_one_record(loved_one),
        memory_count=len(get_memory_entries(loved_one.get("id"))),
    )
    identity_summary = loved_one.get("identity_model_summary", "").strip()
    material_notes = []
    if twin_profile["has_memory"]:
        material_notes.append("已提供文字回忆，请优先引用共同经历和熟悉细节")
    if twin_profile["has_voice"]:
        material_notes.append("已提供语音片段，请保持熟悉的口气和节奏")
    if twin_profile["has_photo"]:
        material_notes.append("已提供照片，请保持这个人的面容感与日常气质")
    if twin_profile["has_video"]:
        material_notes.append("已提供视频，请在表达时体现更自然的动态神态")
    material_desc = "；".join(material_notes) if material_notes else "当前素材仍在补充中，请优先依据性格与回忆保持真实感"
    mode_desc = "、".join(twin_profile.get("available_modes", ["text"]))

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

def build_fallback_response(
    loved_one: dict,
    user_message: str,
    emotion: Optional[str] = None,
    memory_context: str = ""
) -> str:
    """在外部模型不可用时，生成一个带人情味的本地回复。"""
    name = loved_one["name"]
    relationship = loved_one.get("relationship", "亲人")
    traits = loved_one.get("personality_traits", {})
    catchphrase = traits.get("catchphrase", "").strip()
    style = loved_one.get("speaking_style", "温柔亲切")
    message = user_message.strip()

    concern_reply = f"我一直都在听你说，慢慢讲，不着急。"
    if any(keyword in message for keyword in ["想你", "想念", "难过", "睡不着", "哭", "伤心"]):
        concern_reply = f"我知道你是在想我了。想哭的时候就哭一会儿，哭完也记得照顾好自己。"
    elif any(keyword in message for keyword in ["今天", "最近", "工作", "累", "忙"]):
        concern_reply = f"最近辛苦了。再忙也要记得按时吃饭，别把自己逼得太紧。"
    elif any(keyword in message for keyword in ["生日", "节日", "清明", "中秋", "春节"]):
        concern_reply = f"这些特别的日子里，我也会惦记着你。你能记得来和我说说话，我就很满足。"

    memory_reply = ""
    if memory_context:
        latest_memory = memory_context.split("\n")[-1].replace("- ", "").strip()
        if latest_memory:
            memory_reply = f" 你说这些的时候，我也想起了“{latest_memory}”。"

    phrase_prefix = f"{catchphrase} " if catchphrase else ""
    emotion_suffix = "你已经做得很好了。" if emotion in {"sad", "missing"} else "我会一直陪着你。"

    return (
        f"{phrase_prefix}{concern_reply}{memory_reply}"
        f" 作为你的{relationship}，我还是那个{style}的{name}。{emotion_suffix}"
    )

# ===== 启动 =====
if __name__ == "__main__":
    import uvicorn
    print("🌸 念念启动中...")
    print("📍 念念不忘，ta一直在")
    uvicorn.run(app, host="0.0.0.0", port=8097)
