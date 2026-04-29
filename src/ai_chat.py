"""
AI 对话模块 (AI Chat)
基于数字人格的温暖对话系统，支持人格化回复、情感识别、记忆引用
"""

import json
import re
import logging
import random
from typing import List, Dict, Optional, Tuple
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================
# 数据模型
# ============================================================

@dataclass
class ChatMessage:
    """对话消息"""
    role: str                 # user | assistant | system
    content: str
    timestamp: str = ""
    emotion: str = ""         # happy | sad | nostalgic | neutral
    memory_refs: List[str] = field(default_factory=list)

    def to_dict(self) -> Dict:
        return {
            "role": self.role,
            "content": self.content,
            "timestamp": self.timestamp or datetime.now().isoformat(),
            "emotion": self.emotion,
            "memory_refs": self.memory_refs,
        }


@dataclass
class DigitalPersona:
    """数字人格"""
    persona_id: str
    name: str
    relation: str
    voice_profile: Dict = field(default_factory=dict)      # speaking_style, catchphrases
    personality_model: Dict = field(default_factory=dict)   # core_values, traits, responses
    memories: List[Dict] = field(default_factory=list)      # 关键记忆片段
    life_stories: List[Dict] = field(default_factory=list)  # 人生故事

    def to_dict(self) -> Dict:
        return {
            "persona_id": self.persona_id,
            "name": self.name,
            "relation": self.relation,
            "voice_profile": self.voice_profile,
            "personality_model": self.personality_model,
            "memories": self.memories,
            "life_stories": self.life_stories,
        }


# ============================================================
# 情感分析器
# ============================================================

class EmotionAnalyzer:
    """简易情感分析"""

    EMOTION_KEYWORDS = {
        "sad": ["难过", "伤心", "想你", "思念", "哭", "泪", "走", "离开", "不在了", "去世"],
        "happy": ["开心", "高兴", "快乐", "幸福", "笑", "好", "棒", "厉害"],
        "nostalgic": ["以前", "小时候", "记得", "那年", "曾经", "回忆", "过去", "老", "从前"],
        "grateful": ["谢谢", "感谢", "感恩", "感激", "辛苦", "付出"],
        "angry": ["生气", "愤怒", "讨厌", "恨", "烦"],
        "anxious": ["担心", "焦虑", "害怕", "怕", "紧张", "不安"],
    }

    def analyze(self, text: str) -> str:
        """分析文本情感"""
        scores: Dict[str, int] = {}
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = sum(1 for kw in keywords if kw in text)
            if score > 0:
                scores[emotion] = score

        if not scores:
            return "neutral"
        return max(scores, key=scores.get)


# ============================================================
# 记忆检索器
# ============================================================

class MemoryRetriever:
    """基于关键词的记忆检索"""

    def __init__(self, memories: List[Dict]):
        self.memories = memories

    def search(self, query: str, top_k: int = 3) -> List[Dict]:
        """搜索相关记忆"""
        scored = []
        for mem in self.memories:
            score = 0
            text = mem.get("content", "") + " " + mem.get("description", "")
            for word in query:
                if word in text:
                    score += 1
            # 时间衰减（越近越高）
            if score > 0:
                scored.append((score, mem))

        scored.sort(key=lambda x: x[0], reverse=True)
        return [m for _, m in scored[:top_k]]

    def random_memory(self) -> Optional[Dict]:
        """随机回忆"""
        if self.memories:
            return random.choice(self.memories)
        return None


# ============================================================
# AI 对话引擎
# ============================================================

class AIChatEngine:
    """AI 对话引擎 — 数字人格对话"""

    # 通用回复模板
    RESPONSE_TEMPLATES = {
        "greeting": [
            "{name}在呢，{catchphrase}",
            "哎呀，{catchphrase}，看到你真高兴",
            "孩子来了，{catchphrase}",
        ],
        "farewell": [
            "好的，{name}先走了，记得照顾好自己",
            "{catchphrase}，有空再来看{name}",
            "去吧，{name}永远在这里等你",
        ],
        "comfort": [
            "别难过，{catchphrase}，一切都会好起来的",
            "孩子，{name}一直在你身边，只是你看不到而已",
            "哭出来就好了，{catchphrase}",
        ],
        "encouragement": [
            "加油！{catchphrase}，你一定行的",
            "{name}相信你，{catchphrase}",
            "你已经做得很好了，{catchphrase}",
        ],
        "nostalgic": [
            "是啊，那时候{memory_ref}",
            "你还记得{memory_ref}，{name}好开心",
            "那些日子{memory_ref}，真是美好的回忆",
        ],
        "daily": [
            "{catchphrase}，今天过得怎么样？",
            "嗯，{catchphrase}，{name}在听呢",
            "你说，{catchphrase}",
        ],
    }

    def __init__(self, persona: DigitalPersona):
        self.persona = persona
        self.emotion_analyzer = EmotionAnalyzer()
        self.memory_retriever = MemoryRetriever(persona.memories)
        self.history: List[ChatMessage] = []
        logger.info(f"AI 对话引擎初始化: {persona.name}")

    def _get_catchphrase(self) -> str:
        """获取口头禅"""
        phrases = self.persona.voice_profile.get("catchphrases", [])
        if phrases:
            return random.choice(phrases)
        return f"{self.persona.name}在呢"

    def _get_memory_ref(self) -> str:
        """获取记忆引用"""
        mem = self.memory_retriever.random_memory()
        if mem:
            return mem.get("description", mem.get("content", "")[:30])
        return "那些年的日子"

    def _build_response(self, template_key: str) -> str:
        """基于模板构建回复"""
        templates = self.RESPONSE_TEMPLATES.get(template_key, self.RESPONSE_TEMPLATES["daily"])
        template = random.choice(templates)
        return template.format(
            name=self.persona.name,
            catchphrase=self._get_catchphrase(),
            memory_ref=self._get_memory_ref(),
        )

    def _should_reference_memory(self, user_input: str) -> bool:
        """判断是否需要引用记忆"""
        triggers = ["记得", "以前", "那时候", "小时候", "曾经", "回忆", "过去"]
        return any(t in user_input for t in triggers)

    def generate_response(self, user_input: str) -> ChatMessage:
        """生成回复"""
        # 情感分析
        emotion = self.emotion_analyzer.analyze(user_input)

        # 记忆检索
        memory_refs = []
        if self._should_reference_memory(user_input):
            related = self.memory_retriever.search(user_input, top_k=1)
            memory_refs = [m.get("description", "") for m in related]

        # 选择回复策略
        if any(kw in user_input for kw in ["你好", "嗨", "在吗", "来了"]):
            reply = self._build_response("greeting")
        elif any(kw in user_input for kw in ["再见", "走了", "拜拜", "先这样"]):
            reply = self._build_response("farewell")
        elif emotion == "sad" or any(kw in user_input for kw in ["难过", "伤心", "想你", "哭"]):
            reply = self._build_response("comfort")
        elif emotion == "happy" or any(kw in user_input for kw in ["开心", "高兴", "好消息"]):
            reply = self._build_response("encouragement")
        elif emotion == "nostalgic" or self._should_reference_memory(user_input):
            if memory_refs:
                reply = f"是啊，你还记得{memory_refs[0]}，{self.persona.name}好开心。{self._get_catchphrase()}。"
            else:
                reply = self._build_response("nostalgic")
        else:
            # 通用回复 + 尝试添加记忆
            reply = self._build_response("daily")
            related = self.memory_retriever.search(user_input, top_k=1)
            if related:
                reply += f"对了，{related[0].get('description', '')}，你还记得吗？"

        # 人格特质注入
        core_values = self.persona.personality_model.get("core_values", [])
        if core_values and random.random() > 0.7:
            reply += f" {random.choice(core_values)}，这是{self.persona.name}一直相信的。"

        msg = ChatMessage(
            role="assistant",
            content=reply,
            emotion=emotion,
            memory_refs=memory_refs,
        )
        self.history.append(msg)
        return msg

    def chat(self, user_input: str) -> Dict:
        """对话入口（返回字典）"""
        # 记录用户消息
        user_msg = ChatMessage(role="user", content=user_input)
        self.history.append(user_msg)

        # 生成回复
        reply = self.generate_response(user_input)

        return {
            "user_input": user_input,
            "reply": reply.content,
            "emotion_detected": reply.emotion,
            "memory_referenced": reply.memory_refs,
            "persona": self.persona.name,
        }

    def get_history(self) -> List[Dict]:
        """获取对话历史"""
        return [m.to_dict() for m in self.history]

    def clear_history(self) -> None:
        """清空对话历史"""
        self.history = []


# ============================================================
# 对话管理器（多人格）
# ============================================================

class ChatManager:
    """多人格对话管理"""

    def __init__(self):
        self.personas: Dict[str, DigitalPersona] = {}
        self.engines: Dict[str, AIChatEngine] = {}

    def load_persona(self, persona_data: Dict) -> DigitalPersona:
        """加载数字人格"""
        persona = DigitalPersona(
            persona_id=persona_data.get("id", ""),
            name=persona_data.get("name", ""),
            relation=persona_data.get("relation", ""),
            voice_profile=persona_data.get("voice_profile", {}),
            personality_model=persona_data.get("personality_model", {}),
            memories=persona_data.get("memories", []),
            life_stories=persona_data.get("life_stories", []),
        )
        self.personas[persona.persona_id] = persona
        self.engines[persona.persona_id] = AIChatEngine(persona)
        return persona

    def load_from_file(self, path: str) -> int:
        """从 sample-personas.json 加载"""
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        count = 0
        for p in data.get("personas", []):
            self.load_persona(p)
            count += 1
        logger.info(f"加载 {count} 个数字人格")
        return count

    def chat(self, persona_id: str, user_input: str) -> Dict:
        """对话"""
        engine = self.engines.get(persona_id)
        if not engine:
            return {"error": f"人格不存在: {persona_id}"}
        return engine.chat(user_input)

    def list_personas(self) -> List[Dict]:
        """列出所有人格"""
        return [
            {"id": p.persona_id, "name": p.name, "relation": p.relation}
            for p in self.personas.values()
        ]


# ============================================================
# CLI 入口
# ============================================================

def main():
    manager = ChatManager()
    personas_path = Path(__file__).parent.parent / "data" / "sample-personas.json"
    if personas_path.exists():
        manager.load_from_file(str(personas_path))

    personas = manager.list_personas()
    if not personas:
        print("未找到数字人格数据")
        return

    pid = personas[0]["id"]
    print(f"与 {personas[0]['name']} 对话中...")

    # 演示对话
    test_inputs = ["你好", "我好想你", "记得小时候你给我做饭", "再见"]
    for text in test_inputs:
        result = manager.chat(pid, text)
        print(f"\n我: {text}")
        print(f"{result['persona']}: {result['reply']}")


if __name__ == "__main__":
    main()
