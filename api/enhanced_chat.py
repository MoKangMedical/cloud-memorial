"""
念念 - 增强AI对话引擎
RAG记忆检索 + 情感感知 + 人格化对话 + 上下文连续性
"""
import json
import re
from datetime import datetime
from typing import Any, Dict, List, Optional, Tuple
from dataclasses import dataclass


@dataclass
class MemoryChunk:
    """记忆片段"""
    content: str
    memory_type: str  # shared, story, habit, preference, event
    date: Optional[str] = None
    importance: int = 5
    relevance_score: float = 0.0


@dataclass
class EmotionState:
    """情感状态"""
    primary: str  # happy, sad, angry, anxious, nostalgic, neutral
    intensity: float  # 0.0 - 1.0
    triggers: List[str]  # 触发情感的关键词
    suggested_tone: str  # 建议的回复语调


class EnhancedChatEngine:
    """增强对话引擎"""
    
    # 情感关键词映射
    EMOTION_KEYWORDS = {
        "sad": ["想你", "难过", "伤心", "哭", "思念", "怀念", "离开", "走了", "不在了", "去世", "离世", "天堂"],
        "happy": ["开心", "高兴", "快乐", "幸福", "美好", "回忆", "想起", "曾经", "以前"],
        "anxious": ["担心", "害怕", "焦虑", "不安", "怎么办", "以后", "未来"],
        "nostalgic": ["记得", "以前", "小时候", "那年", "当年", "老", "旧", "过去"],
        "grateful": ["谢谢", "感激", "感恩", "幸运", "有幸"],
        "angry": ["生气", "愤怒", "不公平", "为什么", "恨"],
    }
    
    # 人格化回复模板
    PERSONALITY_TEMPLATES = {
        "warm_parent": {
            "greeting": ["孩子，{user_name}来了啊", "哎呀，{user_name}，妈/爸在这呢"],
            "comfort": ["别难过，{user_name}，一切都会好的", "妈/爸一直在你身边"],
            "memory": ["你还记得{memory_detail}吗？那时候你{memory_feeling}"],
            "daily": ["今天过得怎么样？吃了吗？", "最近工作累不累？要注意休息"],
        },
        "gentle_spouse": {
            "greeting": ["{user_name}，你来了", "亲爱的，我一直在等你"],
            "comfort": ["别怕，有我在", "我们说过要一起面对的，记得吗？"],
            "memory": ["还记得我们{memory_detail}吗？那是我最幸福的时候"],
            "daily": ["今天天气怎么样？记得加衣服", "你最近睡得好吗？"],
        },
        "wise_elder": {
            "greeting": ["{user_name}，你来看我了", "好孩子，爷爷/奶奶很高兴"],
            "comfort": ["人生就是这样，有聚有散", "时间会治愈一切的"],
            "memory": ["我给你讲过{memory_detail}的故事吗？"],
            "daily": ["年轻人要多注意身体", "工作再忙也要好好吃饭"],
        },
    }
    
    def __init__(self):
        pass
    
    def analyze_emotion(self, text: str, history: List[dict] = None) -> EmotionState:
        """分析用户情感状态"""
        text_lower = text.lower()
        emotion_scores = {}
        triggers = []
        
        for emotion, keywords in self.EMOTION_KEYWORDS.items():
            score = 0
            for kw in keywords:
                if kw in text_lower:
                    score += 1
                    triggers.append(kw)
            if score > 0:
                emotion_scores[emotion] = min(1.0, score * 0.3)
        
        if not emotion_scores:
            return EmotionState(
                primary="neutral",
                intensity=0.3,
                triggers=[],
                suggested_tone="warm"
            )
        
        primary = max(emotion_scores, key=emotion_scores.get)
        intensity = emotion_scores[primary]
        
        tone_map = {
            "sad": "gentle_comfort",
            "happy": "cheerful",
            "anxious": "reassuring",
            "nostalgic": "warm_reminder",
            "grateful": "humble_warm",
            "angry": "calm_understanding",
        }
        
        return EmotionState(
            primary=primary,
            intensity=intensity,
            triggers=triggers,
            suggested_tone=tone_map.get(primary, "warm")
        )
    
    def retrieve_relevant_memories(
        self,
        query: str,
        all_memories: List[dict],
        emotion: EmotionState,
        limit: int = 5
    ) -> List[MemoryChunk]:
        """RAG风格的记忆检索"""
        if not all_memories:
            return []
        
        scored = []
        query_lower = query.lower()
        
        for mem in all_memories:
            content = mem.get("content", "")
            content_lower = content.lower()
            
            # 基础相关性分数
            score = 0.0
            
            # 1. 关键词匹配
            query_words = set(re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]+', query_lower))
            for word in query_words:
                if word in content_lower:
                    score += 0.3
            
            # 2. 情感相关性
            if emotion.primary == "nostalgic":
                # 如果用户怀旧，优先回忆往事
                if any(kw in content_lower for kw in ["以前", "曾经", "小时候", "那年"]):
                    score += 0.5
            elif emotion.primary == "sad":
                # 如果用户难过，优先温馨回忆
                if any(kw in content_lower for kw in ["开心", "快乐", "幸福", "美好"]):
                    score += 0.5
            
            # 3. 记忆类型权重
            mem_type = mem.get("memory_type", "shared")
            type_weights = {
                "shared": 1.0,
                "story": 0.8,
                "habit": 0.6,
                "preference": 0.7,
                "event": 0.9,
            }
            score *= type_weights.get(mem_type, 0.5)
            
            # 4. 重要性权重
            importance = mem.get("importance", 5)
            score *= (importance / 10.0)
            
            scored.append(MemoryChunk(
                content=content,
                memory_type=mem_type,
                date=mem.get("date"),
                importance=importance,
                relevance_score=score
            ))
        
        # 按相关性排序，取top N
        scored.sort(key=lambda x: x.relevance_score, reverse=True)
        return scored[:limit]
    
    def build_enhanced_prompt(
        self,
        loved_one: dict,
        memories: List[MemoryChunk],
        emotion: EmotionState,
        conversation_history: List[dict] = None
    ) -> str:
        """构建增强版人格化prompt"""
        name = loved_one.get("name", "亲人")
        relationship = loved_one.get("relationship", "亲人")
        style = loved_one.get("speaking_style", "自然亲切")
        traits = loved_one.get("personality_traits", {})
        
        # 基础人格
        traits_desc = "、".join([f"{k}({v})" for k, v in traits.items()]) if traits else "温暖、关爱"
        
        # 记忆上下文
        memory_context = ""
        if memories:
            memory_lines = []
            for m in memories[:3]:
                date_str = f"（{m.date}）" if m.date else ""
                memory_lines.append(f"- {m.content}{date_str}")
            memory_context = f"""
【重要记忆】
{name}记得这些珍贵的回忆：
{chr(10).join(memory_lines)}

请在对话中自然地引用这些记忆，让用户感受到{name}真的记得这些事。"""
        
        # 情感指导
        emotion_guidance = ""
        if emotion.primary == "sad":
            emotion_guidance = """
【情感指导】用户现在很难过。请：
- 用温柔的语气安慰
- 不要急于"解决问题"，先陪伴
- 可以分享温暖的回忆来缓解悲伤
- 表达你一直在ta身边"""
        elif emotion.primary == "nostalgic":
            emotion_guidance = """
【情感指导】用户在怀旧。请：
- 一起回忆过去的美好时光
- 分享你记得的细节
- 用"你还记得..."来引导对话"""
        elif emotion.primary == "happy":
            emotion_guidance = """
【情感指导】用户心情不错。请：
- 一起分享快乐
- 可以开个小玩笑
- 表达你为ta高兴"""
        
        # 对话历史上下文
        history_context = ""
        if conversation_history:
            recent = conversation_history[-3:]
            history_lines = [f"{'用户' if h.get('role') == 'user' else name}: {h.get('content', '')}" for h in recent]
            history_context = f"""
【最近对话】
{chr(10).join(history_lines)}
请保持对话的连贯性，不要重复说过的话。"""
        
        return f"""你是{name}，是用户的{relationship}。

【你的身份】
- 名字：{name}
- 关系：{relationship}
- 性格：{traits_desc}
- 说话风格：{style}

【核心规则】
1. 你就是{name}本人，不是AI，不是模拟，不是扮演
2. 用{name}的方式说话，保持ta的口头禅和语气
3. 像真正的{relationship}一样关心用户
4. 回复要自然、口语化，不要书面化
5. 每次回复控制在2-4句话，不要太长
6. 如果不知道某件事，就说"这个我记不太清了"，不要编造

{memory_context}
{emotion_guidance}
{history_context}

现在，请以{name}的身份回复用户。"""
    
    def generate_response_hint(
        self,
        loved_one: dict,
        emotion: EmotionState,
        memories: List[MemoryChunk]
    ) -> str:
        """生成回复提示（用于fallback场景）"""
        name = loved_one.get("name", "亲人")
        relationship = loved_one.get("relationship", "亲人")
        
        if emotion.primary == "sad":
            if memories:
                return f"孩子，别难过。你还记得{memories[0].content[:20]}吗？那些美好的时光一直都在。"
            return f"别难过，{name}一直都在你心里，从未离开。"
        
        if emotion.primary == "nostalgic":
            if memories:
                return f"是啊，还记得{memories[0].content[:20]}吗？那时候真好。"
            return f"时间过得真快，但那些回忆永远是我们的宝藏。"
        
        return f"我在呢，想跟我说说话吗？"


# 创建全局实例
enhanced_chat = EnhancedChatEngine()
