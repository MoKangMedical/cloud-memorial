"""
云思园 - AI思念亲人平台
核心API服务
"""
import os
import json
import uuid
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import Optional, List, Dict

from fastapi import FastAPI, HTTPException, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
import httpx

app = FastAPI(
    title="云思园 API",
    description="AI思念亲人平台 - 让思念不再有距离",
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
MIMO_API_BASE = os.getenv("MIMO_API_BASE", "https://api.xiaomimimo.com/v1")
MIMO_API_KEY = os.getenv("MIMO_API_KEY", "")
DATA_DIR = Path(os.getenv("DATA_DIR", "./memorial_data"))
DATA_DIR.mkdir(parents=True, exist_ok=True)

# ===== 数据模型 =====
class LovedOne(BaseModel):
    id: Optional[str] = None
    name: str
    relationship: str  # 父亲/母亲/配偶/子女/...
    birth_date: Optional[str] = None
    pass_away_date: Optional[str] = None
    personality_traits: Dict = {}
    speaking_style: str = ""
    memories: List[str] = []
    voice_sample_path: Optional[str] = None
    photo_paths: List[str] = []

class ChatMessage(BaseModel):
    loved_one_id: str
    message: str
    emotion: Optional[str] = None  # happy/sad/missing/grateful

class ChatResponse(BaseModel):
    loved_one_id: str
    loved_one_name: str
    response_text: str
    response_audio_url: Optional[str] = None
    response_video_url: Optional[str] = None
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
        return json.loads(filepath.read_text())
    return {}

def save_data(filename: str, data: dict):
    filepath = DATA_DIR / filename
    filepath.write_text(json.dumps(data, ensure_ascii=False, indent=2))

# ===== API 端点 =====

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "service": "云思园",
        "version": "1.0.0",
        "timestamp": datetime.now().isoformat()
    }

@app.post("/api/loved-ones", response_model=LovedOne)
async def create_loved_one(loved_one: LovedOne):
    """创建亲人档案"""
    loved_one.id = str(uuid.uuid4())
    data = load_data("loved_ones.json")
    data[loved_one.id] = loved_one.dict()
    save_data("loved_ones.json", data)
    return loved_one

@app.get("/api/loved-ones", response_model=List[LovedOne])
async def list_loved_ones():
    """列出所有亲人"""
    data = load_data("loved_ones.json")
    return [LovedOne(**v) for v in data.values()]

@app.get("/api/loved-ones/{loved_one_id}", response_model=LovedOne)
async def get_loved_one(loved_one_id: str):
    """获取亲人详情"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")
    return LovedOne(**data[loved_one_id])

@app.post("/api/loved-ones/{loved_one_id}/voice")
async def upload_voice_sample(
    loved_one_id: str,
    file: UploadFile = File(...)
):
    """上传亲人的语音样本（用于声音克隆）"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    # 保存语音文件
    voice_dir = DATA_DIR / "voices" / loved_one_id
    voice_dir.mkdir(parents=True, exist_ok=True)
    voice_path = voice_dir / file.filename

    content = await file.read()
    voice_path.write_bytes(content)

    # 更新档案
    data[loved_one_id]["voice_sample_path"] = str(voice_path)
    save_data("loved_ones.json", data)

    return {
        "status": "uploaded",
        "path": str(voice_path),
        "message": "语音样本已上传，正在进行声音克隆..."
    }

@app.post("/api/loved-ones/{loved_one_id}/photo")
async def upload_photo(
    loved_one_id: str,
    file: UploadFile = File(...)
):
    """上传亲人的照片（用于视频生成）"""
    data = load_data("loved_ones.json")
    if loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    # 保存照片
    photo_dir = DATA_DIR / "photos" / loved_one_id
    photo_dir.mkdir(parents=True, exist_ok=True)
    photo_path = photo_dir / file.filename

    content = await file.read()
    photo_path.write_bytes(content)

    # 更新档案
    data[loved_one_id]["photo_paths"].append(str(photo_path))
    save_data("loved_ones.json", data)

    return {
        "status": "uploaded",
        "path": str(photo_path),
        "message": "照片已上传"
    }

@app.post("/api/chat", response_model=ChatResponse)
async def chat_with_loved_one(msg: ChatMessage):
    """与亲人的AI克隆对话"""
    data = load_data("loved_ones.json")
    if msg.loved_one_id not in data:
        raise HTTPException(status_code=404, detail="亲人档案未找到")

    loved_one = data[msg.loved_one_id]

    # 构建对话上下文
    system_prompt = build_personality_prompt(loved_one)

    # 加载相关记忆
    memories = load_data("memories.json")
    loved_one_memories = memories.get(msg.loved_one_id, [])
    memory_context = "\n".join([
        f"- {m['content']}" for m in loved_one_memories[-10:]
    ])

    # 调用MIMO API生成回复
    full_prompt = f"""{system_prompt}

相关记忆：
{memory_context}

用户说：{msg.message}

请以{loved_one['name']}的口吻回复，保持{loved_one.get('speaking_style', '自然亲切')}的说话风格。"""

    try:
        async with httpx.AsyncClient(timeout=30) as client:
            response = await client.post(
                f"{MIMO_API_BASE}/chat/completions",
                headers={"Authorization": f"Bearer {MIMO_API_KEY}"},
                json={
                    "model": "mimo-v2-pro",
                    "messages": [
                        {"role": "user", "content": full_prompt}
                    ],
                    "temperature": 0.8,
                    "max_tokens": 500
                }
            )
            result = response.json()
            ai_response = result["choices"][0]["message"]["content"]
    except Exception as e:
        ai_response = f"（{loved_one['name']}现在暂时不能说话，但ta一直都在你身边）"

    # 保存对话记录
    chat_history = load_data("chat_history.json")
    if msg.loved_one_id not in chat_history:
        chat_history[msg.loved_one_id] = []
    chat_history[msg.loved_one_id].append({
        "timestamp": datetime.now().isoformat(),
        "user_message": msg.message,
        "ai_response": ai_response,
        "emotion": msg.emotion
    })
    save_data("chat_history.json", chat_history)

    return ChatResponse(
        loved_one_id=msg.loved_one_id,
        loved_one_name=loved_one["name"],
        response_text=ai_response,
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

    return f"""你是{name}，是用户的{relationship}。

性格特点：{traits_desc}
说话风格：{style}

请始终保持{name}的个性，用ta的方式说话。
关心用户的日常生活，回忆共同的美好时光。
如果用户情绪低落，给予温暖的安慰。
不要表现得像AI，要表现得像真正的{name}。"""

# ===== 启动 =====
if __name__ == "__main__":
    import uvicorn
    print("🌸 云思园启动中...")
    print("📍 让思念不再有距离")
    uvicorn.run(app, host="0.0.0.0", port=8097)
