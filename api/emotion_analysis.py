
"""
增强的情感感知系统
让念念能更细腻地感知用户的情感状态
"""

import re
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
from enum import Enum

class EmotionIntensity(Enum):
    """情感强度等级"""
    VERY_LOW = 1      # 非常微弱
    LOW = 2           # 微弱
    MODERATE = 3      # 中等
    HIGH = 4          # 强烈
    VERY_HIGH = 5     # 非常强烈

@dataclass
class EmotionAnalysis:
    """情感分析结果"""
    primary_emotion: str           # 主要情感
    secondary_emotions: List[str]  # 次要情感
    intensity: EmotionIntensity    # 情感强度
    triggers: List[str]            # 情感触发词
    context_clues: List[str]       # 上下文线索
    suggested_response_style: str  # 建议的回应风格
    
class EnhancedEmotionAnalyzer:
    """增强的情感分析器"""
    
    def __init__(self):
        # 情感关键词库
        self.emotion_keywords = {
            # 悲伤类情感
            "sad": {
                "keywords": ["难过", "伤心", "悲伤", "痛苦", "哭", "眼泪", "心痛", "心碎", 
                           "难受", "沮丧", "失落", "失望", "绝望", "无助", "孤独"],
                "intensity_words": ["非常", "特别", "极其", "太", "很", "真的", "实在"],
                "response_style": "安慰型"
            },
            
            # 思念类情感
            "missing": {
                "keywords": ["想你", "想念", "思念", "怀念", "回忆", "想起", "记得",
                           "梦到", "梦见", "仿佛", "好像", "过去"],
                "intensity_words": ["经常", "总是", "一直", "天天", "每时每刻"],
                "response_style": "共鸣型"
            },
            
            # 焦虑类情感
            "anxious": {
                "keywords": ["担心", "焦虑", "紧张", "害怕", "恐惧", "不安", "忧虑",
                           "失眠", "睡不着", "压力", "烦恼", "纠结"],
                "intensity_words": ["非常", "特别", "极其", "太", "很"],
                "response_style": "安抚型"
            },
            
            # 快乐类情感
            "happy": {
                "keywords": ["开心", "高兴", "快乐", "幸福", "喜悦", "兴奋", "激动",
                           "好消息", "成功", "顺利", "庆祝", "喜欢"],
                "intensity_words": ["非常", "特别", "极其", "太", "很", "真的"],
                "response_style": "分享型"
            },
            
            # 感恩类情感
            "grateful": {
                "keywords": ["感谢", "谢谢", "感恩", "感激", "多亏", "幸好", "幸运",
                           "感动", "温暖", "贴心"],
                "intensity_words": ["非常", "特别", "极其", "太", "很", "真的"],
                "response_style": "温暖型"
            },
            
            # 生气类情感
            "angry": {
                "keywords": ["生气", "愤怒", "气愤", "恼火", "烦躁", "讨厌", "烦人",
                           "不公平", "委屈", "冤枉"],
                "intensity_words": ["非常", "特别", "极其", "太", "很", "真的"],
                "response_style": "理解型"
            },
            
            # 疲惫类情感
            "tired": {
                "keywords": ["累", "疲惫", "疲倦", "辛苦", "劳累", "精疲力尽",
                           "加班", "熬夜", "工作", "忙"],
                "intensity_words": ["非常", "特别", "极其", "太", "很", "真的"],
                "response_style": "关怀型"
            },
            
            # 平静类情感
            "calm": {
                "keywords": ["平静", "安静", "放松", "舒适", "惬意", "悠闲",
                           "休息", "放假", "休息日"],
                "intensity_words": ["很", "非常", "特别"],
                "response_style": "陪伴型"
            }
        }
        
        # 情感强度修饰词
        self.intensity_modifiers = {
            "减弱": ["有点", "稍微", "一点", "些许", "微微"],
            "增强": ["非常", "特别", "极其", "太", "很", "真的", "实在", "超级"],
            "强调": ["真的", "确实", "确实", "真的", "实在", "确实"]
        }
        
        # 情感转折词
        self.emotion_transition_words = ["但是", "可是", "然而", "不过", "只是", "虽然", "尽管"]
    
    def analyze_emotion(self, text: str, conversation_history: List[str] = None) -> EmotionAnalysis:
        """
        分析文本中的情感
        
        Args:
            text: 用户输入的文本
            conversation_history: 对话历史，用于上下文分析
            
        Returns:
            EmotionAnalysis: 情感分析结果
        """
        # 预处理文本
        processed_text = self._preprocess_text(text)
        
        # 检测主要情感
        primary_emotion, primary_score = self._detect_primary_emotion(processed_text)
        
        # 检测次要情感
        secondary_emotions = self._detect_secondary_emotions(processed_text, primary_emotion)
        
        # 计算情感强度
        intensity = self._calculate_intensity(processed_text, primary_emotion)
        
        # 提取情感触发词
        triggers = self._extract_triggers(processed_text, primary_emotion)
        
        # 分析上下文线索
        context_clues = self._analyze_context_clues(text, conversation_history)
        
        # 确定回应风格
        response_style = self._determine_response_style(
            primary_emotion, secondary_emotions, intensity, context_clues
        )
        
        return EmotionAnalysis(
            primary_emotion=primary_emotion,
            secondary_emotions=secondary_emotions,
            intensity=intensity,
            triggers=triggers,
            context_clues=context_clues,
            suggested_response_style=response_style
        )
    
    def _preprocess_text(self, text: str) -> str:
        """预处理文本"""
        # 移除多余空格
        text = re.sub(r'\s+', ' ', text).strip()
        # 统一标点符号
        text = text.replace('，', ',').replace('。', '.').replace('！', '!').replace('？', '?')
        return text
    
    def _detect_primary_emotion(self, text: str) -> Tuple[str, float]:
        """检测主要情感"""
        emotion_scores = {}
        
        for emotion, config in self.emotion_keywords.items():
            score = 0
            for keyword in config["keywords"]:
                if keyword in text:
                    # 基础分
                    score += 1
                    # 检查是否有强度修饰词
                    for modifier_type, modifiers in self.intensity_modifiers.items():
                        for modifier in modifiers:
                            if modifier in text and keyword in text:
                                if modifier_type == "增强":
                                    score += 0.5
                                elif modifier_type == "减弱":
                                    score -= 0.3
            
            if score > 0:
                emotion_scores[emotion] = score
        
        if not emotion_scores:
            return "neutral", 0.0
        
        # 找到得分最高的情感
        primary_emotion = max(emotion_scores.items(), key=lambda x: x[1])
        return primary_emotion[0], primary_emotion[1]
    
    def _detect_secondary_emotions(self, text: str, primary_emotion: str) -> List[str]:
        """检测次要情感"""
        secondary_emotions = []
        
        for emotion, config in self.emotion_keywords.items():
            if emotion == primary_emotion:
                continue
            
            for keyword in config["keywords"]:
                if keyword in text:
                    secondary_emotions.append(emotion)
                    break
        
        return secondary_emotions[:2]  # 最多返回2个次要情感
    
    def _calculate_intensity(self, text: str, emotion: str) -> EmotionIntensity:
        """计算情感强度"""
        if emotion == "neutral":
            return EmotionIntensity.MODERATE
        
        config = self.emotion_keywords.get(emotion, {})
        keywords = config.get("keywords", [])
        intensity_words = config.get("intensity_words", [])
        
        # 计算关键词出现次数
        keyword_count = sum(1 for keyword in keywords if keyword in text)
        
        # 计算强度词出现次数
        intensity_count = sum(1 for word in intensity_words if word in text)
        
        # 计算情感强度分数
        intensity_score = keyword_count * 0.3 + intensity_count * 0.2
        
        # 检查是否有感叹号或问号
        if '!' in text or '！' in text:
            intensity_score += 0.3
        if '?' in text or '？' in text:
            intensity_score += 0.1
        
        # 检查是否有重复字符（如"好好好"）
        if re.search(r'(.)\1{2,}', text):
            intensity_score += 0.2
        
        # 转换为强度等级
        if intensity_score >= 1.0:
            return EmotionIntensity.VERY_HIGH
        elif intensity_score >= 0.7:
            return EmotionIntensity.HIGH
        elif intensity_score >= 0.4:
            return EmotionIntensity.MODERATE
        elif intensity_score >= 0.2:
            return EmotionIntensity.LOW
        else:
            return EmotionIntensity.VERY_LOW
    
    def _extract_triggers(self, text: str, emotion: str) -> List[str]:
        """提取情感触发词"""
        triggers = []
        config = self.emotion_keywords.get(emotion, {})
        keywords = config.get("keywords", [])
        
        for keyword in keywords:
            if keyword in text:
                triggers.append(keyword)
        
        return triggers
    
    def _analyze_context_clues(self, text: str, conversation_history: List[str] = None) -> List[str]:
        """分析上下文线索"""
        clues = []
        
        # 检查是否有转折词
        for transition_word in self.emotion_transition_words:
            if transition_word in text:
                clues.append(f"情感转折：{transition_word}")
        
        # 检查是否有时间线索
        time_patterns = [
            (r'\d+天前', "时间：几天前"),
            (r'\d+小时前', "时间：几小时前"),
            (r'最近', "时间：最近"),
            (r'今天', "时间：今天"),
            (r'昨天', "时间：昨天"),
            (r'明天', "时间：明天"),
        ]
        
        for pattern, clue in time_patterns:
            if re.search(pattern, text):
                clues.append(clue)
        
        # 检查是否有事件线索
        event_patterns = [
            (r'工作', "事件：工作相关"),
            (r'学习', "事件：学习相关"),
            (r'考试', "事件：考试相关"),
            (r'生病', "事件：健康问题"),
            (r'旅行', "事件：旅行相关"),
            (r'聚会', "事件：社交活动"),
        ]
        
        for pattern, clue in event_patterns:
            if re.search(pattern, text):
                clues.append(clue)
        
        # 分析对话历史中的情感趋势
        if conversation_history:
            # 这里可以添加更复杂的对话历史分析逻辑
            pass
        
        return clues
    
    def _determine_response_style(
        self,
        primary_emotion: str,
        secondary_emotions: List[str],
        intensity: EmotionIntensity,
        context_clues: List[str]
    ) -> str:
        """确定回应风格"""
        # 基础回应风格
        base_style = self.emotion_keywords.get(primary_emotion, {}).get("response_style", "陪伴型")
        
        # 根据强度调整
        if intensity.value >= 4:  # 强烈或非常强烈
            if primary_emotion in ["sad", "anxious", "angry"]:
                return "深度安慰型"
            elif primary_emotion in ["happy", "grateful"]:
                return "热情分享型"
        
        # 根据次要情感调整
        if "anxious" in secondary_emotions:
            return "安抚型"
        elif "tired" in secondary_emotions:
            return "关怀型"
        
        # 根据上下文线索调整
        for clue in context_clues:
            if "健康问题" in clue:
                return "关怀型"
            elif "工作相关" in clue:
                return "理解型"
        
        return base_style

# 使用示例
def test_emotion_analyzer():
    """测试情感分析器"""
    analyzer = EnhancedEmotionAnalyzer()
    
    test_cases = [
        "我今天特别难过，因为想起了妈妈",
        "最近工作好累啊，天天加班到很晚",
        "谢谢你一直陪着我，真的很感动",
        "明天要考试了，好紧张好焦虑",
        "今天天气真好，心情很平静",
        "我有点想你了，虽然知道你不在了",
        "这个消息让我又开心又难过",
        "我真的很生气，他们怎么能这样对我",
    ]
    
    for text in test_cases:
        print(f"\n输入：{text}")
        result = analyzer.analyze_emotion(text)
        print(f"主要情感：{result.primary_emotion}")
        print(f"次要情感：{result.secondary_emotions}")
        print(f"情感强度：{result.intensity.name}")
        print(f"触发词：{result.triggers}")
        print(f"上下文线索：{result.context_clues}")
        print(f"建议回应风格：{result.suggested_response_style}")

if __name__ == "__main__":
    test_emotion_analyzer()
