
"""
情感表达细节系统
让念念的对话包含更多情感表达细节
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import random

class EmotionalExpression(Enum):
    """情感表达类型"""
    TONE_WORDS = "语气词"
    PAUSES = "停顿"
    REPETITION = "重复"
    EXAGGERATION = "夸张"
    UNDERSTATEMENT = "低调"
    METAPHOR = "比喻"
    ONOMATOPOEIA = "拟声词"
    ELLIPSIS = "省略"

@dataclass
class EmotionalMarker:
    """情感标记"""
    expression_type: EmotionalExpression
    content: str
    position: str  # "beginning", "middle", "end"
    intensity: float  # 0.0-1.0
    emotion_associated: str

class EmotionalExpressionSystem:
    """情感表达细节系统"""
    
    def __init__(self):
        # 语气词库
        self.tone_words = {
            # 开心类语气词
            "happy": {
                "beginning": ["哇", "呀", "哈", "嘿", "哎呀"],
                "middle": ["呢", "啊", "哦", "嘛", "啦"],
                "end": ["呢", "啊", "哦", "嘛", "啦", "咯", "哟"],
                "examples": ["哇，真好！", "哎呀，太棒了！", "嘿，不错哦！"]
            },
            
            # 悲伤类语气词
            "sad": {
                "beginning": ["唉", "哎", "唔", "嗯"],
                "middle": ["啊", "呢", "哦", "嘛"],
                "end": ["了", "啊", "呢", "哦"],
                "examples": ["唉，好难过", "哎，真伤心", "唔，想哭"]
            },
            
            # 思念类语气词
            "missing": {
                "beginning": ["嗯", "啊", "哦", "哎"],
                "middle": ["呢", "啊", "哦", "嘛"],
                "end": ["了", "啊", "呢", "哦"],
                "examples": ["嗯，想你了", "啊，好想你", "哦，想念你"]
            },
            
            # 惊讶类语气词
            "surprised": {
                "beginning": ["哇", "呀", "啊", "咦", "哎呀"],
                "middle": ["呢", "啊", "哦", "嘛"],
                "end": ["呢", "啊", "哦", "嘛", "啦"],
                "examples": ["哇，真的吗？", "呀，太意外了！", "咦，怎么会这样？"]
            },
            
            # 关心类语气词
            "caring": {
                "beginning": ["乖", "听话", "宝贝"],
                "middle": ["呢", "啊", "哦", "嘛"],
                "end": ["哦", "啊", "呢", "吧"],
                "examples": ["乖，别担心", "听话，慢慢来", "宝贝，小心点"]
            }
        }
        
        # 停顿模式
        self.pause_patterns = {
            "思考性停顿": ["嗯...", "这个...", "那个...", "让我想想..."],
            "情感性停顿": ["...", "……", "（停顿）", "（沉默）"],
            "强调性停顿": ["——", "—", "（强调）", "（重音）"],
            "省略性停顿": ["...", "…", "（省略）", "（不言而喻）"]
        }
        
        # 重复表达
        self.repetition_patterns = {
            "强调重复": ["真的真的", "非常非常", "特别特别", "好好好"],
            "情感重复": ["想你了想你了", "开心开心", "难过难过", "担心担心"],
            "口吃重复": ["我我我", "你你你", "他他他", "这这这"],
            "可爱重复": ["吃饭饭", "睡觉觉", "喝水水", "洗手手"]
        }
        
        # 夸张表达
        self.exaggeration_patterns = {
            "程度夸张": ["太...了", "超级...", "特别...", "极其..."],
            "时间夸张": ["永远...", "一直...", "每时每刻...", "天天..."],
            "数量夸张": ["无数...", "千万...", "一万...", "一百万..."],
            "情感夸张": ["爱死了", "想疯了", "开心到爆炸", "难过到极点"]
        }
        
        # 比喻表达
        self.metaphor_patterns = {
            "温暖比喻": ["像阳光一样", "像春风一样", "像家一样", "像港湾一样"],
            "思念比喻": ["像星星一样", "像月亮一样", "像大海一样", "像天空一样"],
            "时间比喻": ["像流水一样", "像飞箭一样", "像闪电一样", "像蜗牛一样"],
            "情感比喻": ["像蜜一样甜", "像药一样苦", "像冰一样冷", "像火一样热"]
        }
        
        # 拟声词
        self.onomatopoeia_patterns = {
            "笑声": ["哈哈", "呵呵", "嘿嘿", "嘻嘻", "咯咯"],
            "哭声": ["呜呜", "嘤嘤", "啜泣", "抽泣", "哽咽"],
            "叹息": ["唉", "哎", "呼", " sigh"],
            "自然声": ["哗啦", "滴答", "呼呼", "沙沙", "簌簌"]
        }
    
    def add_emotional_expressions(
        self,
        text: str,
        emotion: str,
        intensity: float,
        personality_traits: Dict[str, Any] = None,
        context: Dict[str, Any] = None
    ) -> str:
        """
        添加情感表达细节
        
        Args:
            text: 原始文本
            emotion: 情感类型
            intensity: 情感强度 0.0-1.0
            personality_traits: 人格特质
            context: 上下文信息
            
        Returns:
            str: 添加情感表达后的文本
        """
        processed_text = text
        
        # 1. 根据情感强度决定添加多少表达细节
        expression_count = self._determine_expression_count(intensity, personality_traits)
        
        # 2. 选择要添加的表达类型
        expression_types = self._select_expression_types(emotion, intensity, personality_traits)
        
        # 3. 添加各种表达
        for expr_type in expression_types:
            if expression_count <= 0:
                break
            
            if expr_type == EmotionalExpression.TONE_WORDS:
                processed_text = self._add_tone_words(processed_text, emotion, intensity)
                expression_count -= 1
            
            elif expr_type == EmotionalExpression.PAUSES:
                processed_text = self._add_pauses(processed_text, emotion, intensity)
                expression_count -= 1
            
            elif expr_type == EmotionalExpression.REPETITION:
                processed_text = self._add_repetition(processed_text, emotion, intensity)
                expression_count -= 1
            
            elif expr_type == EmotionalExpression.EXAGGERATION:
                processed_text = self._add_exaggeration(processed_text, emotion, intensity)
                expression_count -= 1
            
            elif expr_type == EmotionalExpression.METAPHOR:
                processed_text = self._add_metaphor(processed_text, emotion, intensity)
                expression_count -= 1
            
            elif expr_type == EmotionalExpression.ONOMATOPOEIA:
                processed_text = self._add_onomatopoeia(processed_text, emotion, intensity)
                expression_count -= 1
        
        # 4. 根据人格特质调整表达风格
        if personality_traits:
            processed_text = self._adjust_by_personality(processed_text, personality_traits)
        
        return processed_text
    
    def _determine_expression_count(self, intensity: float, personality_traits: Dict[str, Any] = None) -> int:
        """确定要添加的表达数量"""
        # 基础数量：根据情感强度
        base_count = int(intensity * 3)  # 0-3个表达
        
        # 根据人格特质调整
        if personality_traits:
            # 外向的人可能使用更多表达
            extraversion = personality_traits.get("extraversion", 0.5)
            if extraversion > 0.7:
                base_count += 1
            elif extraversion < 0.3:
                base_count = max(0, base_count - 1)
            
            # 神经质高的人可能使用更多情感表达
            neuroticism = personality_traits.get("neuroticism", 0.5)
            if neuroticism > 0.7:
                base_count += 1
        
        return min(base_count, 3)  # 最多3个表达
    
    def _select_expression_types(
        self,
        emotion: str,
        intensity: float,
        personality_traits: Dict[str, Any] = None
    ) -> List[EmotionalExpression]:
        """选择要添加的表达类型"""
        expression_types = []
        
        # 根据情感选择表达类型
        if emotion in ["happy", "grateful"]:
            # 开心情感：语气词、夸张、比喻
            expression_types = [
                EmotionalExpression.TONE_WORDS,
                EmotionalExpression.EXAGGERATION,
                EmotionalExpression.METAPHOR
            ]
        
        elif emotion in ["sad", "missing"]:
            # 悲伤/思念：语气词、停顿、重复
            expression_types = [
                EmotionalExpression.TONE_WORDS,
                EmotionalExpression.PAUSES,
                EmotionalExpression.REPETITION
            ]
        
        elif emotion in ["anxious", "angry"]:
            # 焦虑/生气：重复、夸张、拟声词
            expression_types = [
                EmotionalExpression.REPETITION,
                EmotionalExpression.EXAGGERATION,
                EmotionalExpression.ONOMATOPOEIA
            ]
        
        elif emotion in ["surprised"]:
            # 惊讶：语气词、夸张、拟声词
            expression_types = [
                EmotionalExpression.TONE_WORDS,
                EmotionalExpression.EXAGGERATION,
                EmotionalExpression.ONOMATOPOEIA
            ]
        
        else:
            # 默认：语气词、停顿
            expression_types = [
                EmotionalExpression.TONE_WORDS,
                EmotionalExpression.PAUSES
            ]
        
        # 根据强度调整
        if intensity < 0.3:
            # 低强度：减少表达类型
            expression_types = expression_types[:1]
        elif intensity > 0.7:
            # 高强度：增加表达类型
            if EmotionalExpression.REPETITION not in expression_types:
                expression_types.append(EmotionalExpression.REPETITION)
        
        # 根据人格特质调整
        if personality_traits:
            # 内向的人可能更少使用夸张表达
            extraversion = personality_traits.get("extraversion", 0.5)
            if extraversion < 0.3:
                if EmotionalExpression.EXAGGERATION in expression_types:
                    expression_types.remove(EmotionalExpression.EXAGGERATION)
        
        return expression_types[:3]  # 最多3种类型
    
    def _add_tone_words(self, text: str, emotion: str, intensity: float) -> str:
        """添加语气词"""
        if emotion not in self.tone_words:
            emotion = "happy"  # 默认使用开心语气词
        
        tone_data = self.tone_words[emotion]
        
        # 根据强度选择位置
        if intensity > 0.7:
            position = "beginning"
        elif intensity > 0.3:
            position = "middle"
        else:
            position = "end"
        
        # 选择语气词
        available_words = tone_data.get(position, [])
        if not available_words:
            available_words = tone_data.get("end", [])
        
        if not available_words:
            return text
        
        tone_word = random.choice(available_words)
        
        # 添加语气词
        if position == "beginning":
            # 在开头添加
            if not text.startswith(tone_word):
                text = f"{tone_word}，{text}"
        
        elif position == "middle":
            # 在中间添加
            sentences = re.split(r'[。！？]', text)
            if len(sentences) > 1:
                # 在第一个句子后添加
                first_sentence = sentences[0]
                if len(first_sentence) > 5:
                    # 在合适的位置添加
                    insert_pos = len(first_sentence) // 2
                    text = first_sentence[:insert_pos] + tone_word + first_sentence[insert_pos:] + "。".join(sentences[1:])
        
        else:  # position == "end"
            # 在结尾添加
            if text.endswith(("。", "！", "？")):
                text = text[:-1] + tone_word + text[-1]
            else:
                text = text + tone_word
        
        return text
    
    def _add_pauses(self, text: str, emotion: str, intensity: float) -> str:
        """添加停顿"""
        # 根据情感选择停顿类型
        if emotion in ["sad", "missing"]:
            pause_type = "情感性停顿"
        elif emotion in ["anxious", "angry"]:
            pause_type = "强调性停顿"
        else:
            pause_type = "思考性停顿"
        
        available_pauses = self.pause_patterns.get(pause_type, ["..."])
        pause = random.choice(available_pauses)
        
        # 根据强度决定添加几个停顿
        pause_count = 1
        if intensity > 0.7:
            pause_count = 2
        
        # 添加停顿
        sentences = re.split(r'([。！？])', text)
        new_sentences = []
        
        for i, sentence in enumerate(sentences):
            new_sentences.append(sentence)
            
            # 在句子之间添加停顿
            if i % 2 == 0 and i < len(sentences) - 2 and pause_count > 0:
                # 随机决定是否添加停顿
                if random.random() < 0.5:
                    new_sentences.append(pause)
                    pause_count -= 1
        
        return "".join(new_sentences)
    
    def _add_repetition(self, text: str, emotion: str, intensity: float) -> str:
        """添加重复表达"""
        # 根据情感选择重复类型
        if emotion in ["happy", "grateful"]:
            repetition_type = "强调重复"
        elif emotion in ["sad", "missing"]:
            repetition_type = "情感重复"
        elif emotion in ["anxious"]:
            repetition_type = "口吃重复"
        else:
            repetition_type = "可爱重复"
        
        available_repetitions = self.repetition_patterns.get(repetition_type, ["真的真的"])
        repetition = random.choice(available_repetitions)
        
        # 查找可以添加重复的词汇
        words = re.findall(r'\w+', text)
        if not words:
            return text
        
        # 选择要重复的词汇
        target_word = random.choice(words)
        
        # 添加重复
        if intensity > 0.7:
            # 高强度：重复整个短语
            text = text.replace(target_word, repetition, 1)
        else:
            # 低强度：在合适位置添加重复
            sentences = re.split(r'([。！？])', text)
            if len(sentences) > 0:
                first_sentence = sentences[0]
                if len(first_sentence) > 10:
                    # 在句子开头添加重复
                    text = repetition + "，" + text
        
        return text
    
    def _add_exaggeration(self, text: str, emotion: str, intensity: float) -> str:
        """添加夸张表达"""
        # 根据情感选择夸张类型
        if emotion in ["happy", "grateful"]:
            exaggeration_type = "情感夸张"
        elif emotion in ["sad", "missing"]:
            exaggeration_type = "程度夸张"
        elif emotion in ["anxious", "angry"]:
            exaggeration_type = "程度夸张"
        else:
            exaggeration_type = "程度夸张"
        
        available_exaggerations = self.exaggeration_patterns.get(exaggeration_type, ["太...了"])
        exaggeration_template = random.choice(available_exaggerations)
        
        # 查找可以夸张的词汇
        words = re.findall(r'\w+', text)
        if not words:
            return text
        
        # 选择要夸张的词汇
        target_word = random.choice(words)
        
        # 应用夸张
        if "..." in exaggeration_template:
            exaggeration = exaggeration_template.replace("...", target_word)
        else:
            exaggeration = exaggeration_template + target_word
        
        # 替换原文中的词汇
        text = text.replace(target_word, exaggeration, 1)
        
        return text
    
    def _add_metaphor(self, text: str, emotion: str, intensity: float) -> str:
        """添加比喻表达"""
        # 根据情感选择比喻类型
        if emotion in ["happy", "grateful"]:
            metaphor_type = "温暖比喻"
        elif emotion in ["sad", "missing"]:
            metaphor_type = "思念比喻"
        elif emotion in ["anxious", "angry"]:
            metaphor_type = "情感比喻"
        else:
            metaphor_type = "温暖比喻"
        
        available_metaphors = self.metaphor_patterns.get(metaphor_type, ["像阳光一样"])
        metaphor = random.choice(available_metaphors)
        
        # 在句子中添加比喻
        sentences = re.split(r'([。！？])', text)
        if len(sentences) > 0:
            # 在第一个句子后添加比喻
            first_sentence = sentences[0]
            if len(first_sentence) > 10:
                text = first_sentence + f"，{metaphor}" + "".join(sentences[1:])
        
        return text
    
    def _add_onomatopoeia(self, text: str, emotion: str, intensity: float) -> str:
        """添加拟声词"""
        # 根据情感选择拟声词类型
        if emotion in ["happy", "grateful"]:
            onomatopoeia_type = "笑声"
        elif emotion in ["sad", "missing"]:
            onomatopoeia_type = "哭声"
        elif emotion in ["anxious", "angry"]:
            onomatopoeia_type = "叹息"
        else:
            onomatopoeia_type = "自然声"
        
        available_onomatopoeia = self.onomatopoeia_patterns.get(omatopoeia_type, ["哈哈"])
        onomatopoeia = random.choice(available_onomatopoeia)
        
        # 在句子中添加拟声词
        if intensity > 0.7:
            # 高强度：在开头添加
            text = f"{omatopoeia}，{text}"
        else:
            # 低强度：在合适位置添加
            sentences = re.split(r'([。！？])', text)
            if len(sentences) > 0:
                first_sentence = sentences[0]
                if len(first_sentence) > 15:
                    # 在句子中间添加
                    insert_pos = len(first_sentence) * 2 // 3
                    text = first_sentence[:insert_pos] + f"，{omatopoeia}" + first_sentence[insert_pos:] + "".join(sentences[1:])
        
        return text
    
    def _adjust_by_personality(self, text: str, personality_traits: Dict[str, Any]) -> str:
        """根据人格特质调整表达"""
        # 外向的人可能使用更多感叹号
        extraversion = personality_traits.get("extraversion", 0.5)
        if extraversion > 0.7:
            # 添加更多感叹号
            text = text.replace("。", "！")
        
        # 内向的人可能使用更多省略号
        if extraversion < 0.3:
            # 添加省略号
            if not text.endswith("..."):
                text = text.rstrip("。！？") + "..."
        
        # 神经质高的人可能使用更多问号
        neuroticism = personality_traits.get("neuroticism", 0.5)
        if neuroticism > 0.7:
            # 添加问号
            text = text.replace("。", "？")
        
        return text

# 使用示例
def test_emotional_expression():
    """测试情感表达系统"""
    expression_system = EmotionalExpressionSystem()
    
    # 测试不同情感和强度
    test_cases = [
        {
            "text": "我很开心",
            "emotion": "happy",
            "intensity": 0.8,
            "personality": {"extraversion": 0.8, "neuroticism": 0.3}
        },
        {
            "text": "我好难过",
            "emotion": "sad",
            "intensity": 0.9,
            "personality": {"extraversion": 0.3, "neuroticism": 0.8}
        },
        {
            "text": "我想你了",
            "emotion": "missing",
            "intensity": 0.7,
            "personality": {"extraversion": 0.5, "neuroticism": 0.6}
        },
        {
            "text": "我有点担心",
            "emotion": "anxious",
            "intensity": 0.5,
            "personality": {"extraversion": 0.4, "neuroticism": 0.7}
        }
    ]
    
    print("情感表达系统测试：")
    print("="*80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"原始文本: {case['text']}")
        print(f"情感: {case['emotion']}, 强度: {case['intensity']}")
        print(f"人格特质: {case['personality']}")
        
        # 添加情感表达
        enhanced_text = expression_system.add_emotional_expressions(
            text=case["text"],
            emotion=case["emotion"],
            intensity=case["intensity"],
            personality_traits=case["personality"]
        )
        
        print(f"增强后: {enhanced_text}")
        print("-"*80)

if __name__ == "__main__":
    test_emotional_expression()
