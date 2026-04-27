
"""
增强的记忆系统
让念念能更自然地回忆和引用共同记忆
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta
import json

@dataclass
class Memory:
    """记忆条目"""
    id: str
    content: str
    memory_type: str  # "shared", "personal", "event", "feeling"
    date: Optional[str]
    importance: int  # 1-10
    tags: List[str]
    emotion_associated: Optional[str]
    related_memories: List[str]  # 相关记忆ID
    
@dataclass
class MemoryContext:
    """记忆上下文"""
    relevant_memories: List[Memory]  # 相关记忆
    memory_chain: List[Memory]       # 记忆链条
    emotional_resonance: float       # 情感共鸣度
    time_context: str                # 时间背景
    suggested_references: List[str]  # 建议的引用方式

class EnhancedMemorySystem:
    """增强的记忆系统"""
    
    def __init__(self):
        # 记忆类型权重
        self.memory_type_weights = {
            "shared": 1.0,      # 共同记忆最重要
            "event": 0.8,       # 事件记忆
            "feeling": 0.7,     # 情感记忆
            "personal": 0.5,    # 个人记忆
        }
        
        # 时间衰减系数
        self.time_decay_factors = {
            "today": 1.0,
            "yesterday": 0.9,
            "this_week": 0.8,
            "this_month": 0.6,
            "this_year": 0.4,
            "long_ago": 0.2,
        }
        
        # 情感关联强度
        self.emotion_association_strength = {
            "sad": 0.9,
            "missing": 1.0,
            "happy": 0.8,
            "grateful": 0.7,
            "anxious": 0.6,
        }
    
    def select_relevant_memories(
        self,
        current_message: str,
        current_emotion: str,
        all_memories: List[Dict],
        conversation_history: List[str] = None,
        limit: int = 3
    ) -> MemoryContext:
        """
        选择与当前对话相关的记忆
        
        Args:
            current_message: 当前用户消息
            current_emotion: 当前情感
            all_memories: 所有可用记忆
            conversation_history: 对话历史
            limit: 返回的记忆数量限制
            
        Returns:
            MemoryContext: 记忆上下文
        """
        if not all_memories:
            return MemoryContext(
                relevant_memories=[],
                memory_chain=[],
                emotional_resonance=0.0,
                time_context="现在",
                suggested_references=[]
            )
        
        # 将字典转换为Memory对象
        memories = self._convert_to_memory_objects(all_memories)
        
        # 计算每个记忆的相关性分数
        scored_memories = []
        for memory in memories:
            score = self._calculate_memory_relevance(
                memory, current_message, current_emotion, conversation_history
            )
            scored_memories.append((memory, score))
        
        # 按分数排序
        scored_memories.sort(key=lambda x: x[1], reverse=True)
        
        # 选择最相关的记忆
        relevant_memories = [memory for memory, score in scored_memories[:limit]]
        
        # 构建记忆链条
        memory_chain = self._build_memory_chain(relevant_memories, memories)
        
        # 计算情感共鸣度
        emotional_resonance = self._calculate_emotional_resonance(
            relevant_memories, current_emotion
        )
        
        # 确定时间背景
        time_context = self._determine_time_context(relevant_memories)
        
        # 生成建议的引用方式
        suggested_references = self._generate_reference_suggestions(
            relevant_memories, current_message, current_emotion
        )
        
        return MemoryContext(
            relevant_memories=relevant_memories,
            memory_chain=memory_chain,
            emotional_resonance=emotional_resonance,
            time_context=time_context,
            suggested_references=suggested_references
        )
    
    def _convert_to_memory_objects(self, memory_dicts: List[Dict]) -> List[Memory]:
        """将字典转换为Memory对象"""
        memories = []
        for mem_dict in memory_dicts:
            memory = Memory(
                id=mem_dict.get("id", ""),
                content=mem_dict.get("content", ""),
                memory_type=mem_dict.get("memory_type", "shared"),
                date=mem_dict.get("date"),
                importance=mem_dict.get("importance", 5),
                tags=mem_dict.get("tags", []),
                emotion_associated=mem_dict.get("emotion_associated"),
                related_memories=mem_dict.get("related_memories", [])
            )
            memories.append(memory)
        return memories
    
    def _calculate_memory_relevance(
        self,
        memory: Memory,
        current_message: str,
        current_emotion: str,
        conversation_history: List[str] = None
    ) -> float:
        """计算记忆的相关性分数"""
        score = 0.0
        
        # 1. 关键词匹配
        keyword_score = self._calculate_keyword_similarity(memory.content, current_message)
        score += keyword_score * 0.4
        
        # 2. 情感匹配
        emotion_score = self._calculate_emotion_similarity(memory.emotion_associated, current_emotion)
        score += emotion_score * 0.3
        
        # 3. 记忆类型权重
        type_weight = self.memory_type_weights.get(memory.memory_type, 0.5)
        score += type_weight * 0.15
        
        # 4. 时间衰减
        time_score = self._calculate_time_relevance(memory.date)
        score += time_score * 0.1
        
        # 5. 重要性权重
        importance_score = memory.importance / 10.0
        score += importance_score * 0.05
        
        return score
    
    def _calculate_keyword_similarity(self, memory_content: str, current_message: str) -> float:
        """计算关键词相似度"""
        # 简单实现：计算共同词数量
        memory_words = set(re.findall(r'\w+', memory_content))
        message_words = set(re.findall(r'\w+', current_message))
        
        if not memory_words or not message_words:
            return 0.0
        
        common_words = memory_words.intersection(message_words)
        similarity = len(common_words) / max(len(memory_words), len(message_words))
        
        return similarity
    
    def _calculate_emotion_similarity(self, memory_emotion: Optional[str], current_emotion: str) -> float:
        """计算情感相似度"""
        if not memory_emotion or not current_emotion:
            return 0.0
        
        if memory_emotion == current_emotion:
            return 1.0
        
        # 情感相似度矩阵
        emotion_similarity_matrix = {
            ("sad", "missing"): 0.8,
            ("sad", "anxious"): 0.6,
            ("happy", "grateful"): 0.7,
            ("anxious", "tired"): 0.5,
        }
        
        # 检查两种顺序
        key1 = (memory_emotion, current_emotion)
        key2 = (current_emotion, memory_emotion)
        
        return emotion_similarity_matrix.get(key1, emotion_similarity_matrix.get(key2, 0.0))
    
    def _calculate_time_relevance(self, memory_date: Optional[str]) -> float:
        """计算时间相关性"""
        if not memory_date:
            return 0.5
        
        try:
            # 解析记忆日期
            if isinstance(memory_date, str):
                # 尝试解析不同格式
                for fmt in ["%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%Y-%m-%dT%H:%M:%S"]:
                    try:
                        memory_dt = datetime.strptime(memory_date, fmt)
                        break
                    except ValueError:
                        continue
                else:
                    # 如果无法解析，返回中等分数
                    return 0.5
            else:
                memory_dt = memory_date
            
            # 计算时间差
            now = datetime.now()
            time_diff = now - memory_dt
            
            # 根据时间差返回分数
            if time_diff.days == 0:
                return self.time_decay_factors["today"]
            elif time_diff.days == 1:
                return self.time_decay_factors["yesterday"]
            elif time_diff.days <= 7:
                return self.time_decay_factors["this_week"]
            elif time_diff.days <= 30:
                return self.time_decay_factors["this_month"]
            elif time_diff.days <= 365:
                return self.time_decay_factors["this_year"]
            else:
                return self.time_decay_factors["long_ago"]
                
        except Exception:
            return 0.5
    
    def _build_memory_chain(
        self,
        relevant_memories: List[Memory],
        all_memories: List[Memory]
    ) -> List[Memory]:
        """构建记忆链条"""
        if not relevant_memories:
            return []
        
        # 以最相关的记忆为起点
        start_memory = relevant_memories[0]
        chain = [start_memory]
        
        # 查找相关记忆
        for related_id in start_memory.related_memories:
            for memory in all_memories:
                if memory.id == related_id and memory not in chain:
                    chain.append(memory)
                    break
        
        # 按时间排序
        chain.sort(key=lambda x: x.date or "")
        
        return chain
    
    def _calculate_emotional_resonance(
        self,
        relevant_memories: List[Memory],
        current_emotion: str
    ) -> float:
        """计算情感共鸣度"""
        if not relevant_memories:
            return 0.0
        
        resonance_scores = []
        for memory in relevant_memories:
            if memory.emotion_associated:
                # 计算情感匹配度
                emotion_match = 1.0 if memory.emotion_associated == current_emotion else 0.5
                # 考虑记忆重要性
                importance_factor = memory.importance / 10.0
                # 考虑情感关联强度
                emotion_strength = self.emotion_association_strength.get(memory.emotion_associated, 0.5)
                
                resonance = emotion_match * importance_factor * emotion_strength
                resonance_scores.append(resonance)
        
        if not resonance_scores:
            return 0.0
        
        return sum(resonance_scores) / len(resonance_scores)
    
    def _determine_time_context(self, relevant_memories: List[Memory]) -> str:
        """确定时间背景"""
        if not relevant_memories:
            return "现在"
        
        # 找到最新的记忆
        latest_memory = max(relevant_memories, key=lambda x: x.date or "")
        
        if not latest_memory.date:
            return "过去"
        
        try:
            memory_dt = datetime.strptime(latest_memory.date, "%Y-%m-%d")
            now = datetime.now()
            days_diff = (now - memory_dt).days
            
            if days_diff == 0:
                return "今天"
            elif days_diff == 1:
                return "昨天"
            elif days_diff <= 7:
                return "这周"
            elif days_diff <= 30:
                return "这个月"
            elif days_diff <= 365:
                return "今年"
            else:
                return "很久以前"
                
        except Exception:
            return "过去"
    
    def _generate_reference_suggestions(
        self,
        relevant_memories: List[Memory],
        current_message: str,
        current_emotion: str
    ) -> List[str]:
        """生成建议的引用方式"""
        suggestions = []
        
        for memory in relevant_memories[:2]:  # 只为前两个记忆生成建议
            # 根据记忆类型和情感生成不同的引用方式
            if memory.memory_type == "shared":
                if current_emotion in ["sad", "missing"]:
                    suggestions.append(f"记得我们一起{memory.content[:20]}...的时候吗？")
                elif current_emotion in ["happy", "grateful"]:
                    suggestions.append(f"想起那次{memory.content[:20]}...真的很开心。")
                else:
                    suggestions.append(f"你记得{memory.content[:20]}...吗？")
            
            elif memory.memory_type == "event":
                suggestions.append(f"那次{memory.content[:20]}...让我印象深刻。")
            
            elif memory.memory_type == "feeling":
                if current_emotion == memory.emotion_associated:
                    suggestions.append(f"你现在的感觉让我想起了{memory.content[:20]}...")
                else:
                    suggestions.append(f"我记得你曾经{memory.content[:20]}...")
        
        return suggestions

# 使用示例
def test_memory_system():
    """测试记忆系统"""
    memory_system = EnhancedMemorySystem()
    
    # 模拟记忆数据
    sample_memories = [
        {
            "id": "1",
            "content": "去年春节我们一起包饺子，你包的饺子总是露馅",
            "memory_type": "shared",
            "date": "2025-01-29",
            "importance": 8,
            "tags": ["春节", "家庭", "传统"],
            "emotion_associated": "happy",
            "related_memories": ["2"]
        },
        {
            "id": "2",
            "content": "你教我做红烧肉，说火候是关键",
            "memory_type": "shared",
            "date": "2024-12-15",
            "importance": 7,
            "tags": ["烹饪", "学习", "生活"],
            "emotion_associated": "grateful",
            "related_memories": ["1"]
        },
        {
            "id": "3",
            "content": "那次我生病，你整夜守在我床边",
            "memory_type": "shared",
            "date": "2024-11-20",
            "importance": 9,
            "tags": ["生病", "照顾", "亲情"],
            "emotion_associated": "grateful",
            "related_memories": []
        }
    ]
    
    # 测试不同场景
    test_cases = [
        {
            "message": "春节快到了，好想吃你包的饺子",
            "emotion": "missing",
            "history": []
        },
        {
            "message": "今天尝试做红烧肉，但火候没掌握好",
            "emotion": "disappointed",
            "history": []
        },
        {
            "message": "最近总是想起你，特别是生病的时候",
            "emotion": "sad",
            "history": []
        }
    ]
    
    for case in test_cases:
        print(f"\n用户消息：{case['message']}")
        print(f"用户情感：{case['emotion']}")
        
        context = memory_system.select_relevant_memories(
            current_message=case["message"],
            current_emotion=case["emotion"],
            all_memories=sample_memories,
            conversation_history=case["history"]
        )
        
        print(f"相关记忆数量：{len(context.relevant_memories)}")
        print(f"情感共鸣度：{context.emotional_resonance:.2f}")
        print(f"时间背景：{context.time_context}")
        print(f"建议引用：")
        for suggestion in context.suggested_references:
            print(f"  - {suggestion}")

if __name__ == "__main__":
    test_memory_system()
