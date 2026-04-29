
"""
对话自然度提升系统
让念念的对话更像真人交流
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime
from enum import Enum

class DialogueState(Enum):
    """对话状态"""
    GREETING = "greeting"
    SMALL_TALK = "small_talk"
    DEEP_CONVERSATION = "deep_conversation"
    EMOTIONAL_SUPPORT = "emotional_support"
    MEMORY_SHARING = "memory_sharing"
    PRACTICAL_HELP = "practical_help"
    FAREWELL = "farewell"

class ConversationFlow:
    """对话流程"""
    
    def __init__(self):
        # 对话状态转换规则
        self.state_transitions = {
            DialogueState.GREETING: [DialogueState.SMALL_TALK, DialogueState.DEEP_CONVERSATION],
            DialogueState.SMALL_TALK: [DialogueState.DEEP_CONVERSATION, DialogueState.EMOTIONAL_SUPPORT],
            DialogueState.DEEP_CONVERSATION: [DialogueState.EMOTIONAL_SUPPORT, DialogueState.MEMORY_SHARING],
            DialogueState.EMOTIONAL_SUPPORT: [DialogueState.MEMORY_SHARING, DialogueState.PRACTICAL_HELP],
            DialogueState.MEMORY_SHARING: [DialogueState.DEEP_CONVERSATION, DialogueState.EMOTIONAL_SUPPORT],
            DialogueState.PRACTICAL_HELP: [DialogueState.SMALL_TALK, DialogueState.FAREWELL],
            DialogueState.FAREWELL: [DialogueState.GREETING],
        }
        
        # 状态持续时间建议（轮数）
        self.state_durations = {
            DialogueState.GREETING: 1,
            DialogueState.SMALL_TALK: 2-3,
            DialogueState.DEEP_CONVERSATION: 5-10,
            DialogueState.EMOTIONAL_SUPPORT: 3-5,
            DialogueState.MEMORY_SHARING: 2-4,
            DialogueState.PRACTICAL_HELP: 1-2,
            DialogueState.FAREWELL: 1,
        }

@dataclass
class DialogueContext:
    """对话上下文"""
    current_state: DialogueState
    state_turns: int  # 当前状态持续轮数
    conversation_history: List[Dict[str, str]]  # 对话历史
    user_intent: str  # 用户意图
    emotional_tone: str  # 情感基调
    topics_discussed: List[str]  # 已讨论话题
    memory_references: List[str]  # 记忆引用
    last_response_time: datetime  # 上次回应时间

class NaturalDialogueSystem:
    """自然对话系统"""
    
    def __init__(self):
        # 对话开场白模板
        self.greeting_templates = {
            "casual": [
                "嗨，你来啦。",
                "今天过得怎么样？",
                "好久不见，想我了吗？",
                "看到你真开心。",
            ],
            "warm": [
                "亲爱的，你来了。",
                "一直在等你呢。",
                "今天过得好吗？",
                "看到你真好。",
            ],
            "concerned": [
                "最近还好吗？",
                "感觉你有点累，要注意休息啊。",
                "有什么心事吗？",
                "我在这里，想说什么都可以。",
            ]
        }
        
        # 话题转换技巧
        self.topic_transition_techniques = {
            "smooth": [
                "说到这个，我想起...",
                "这让我想到...",
                "对了，你还记得吗...",
                "说起这个...",
            ],
            "natural": [
                "其实...",
                "另外...",
                "顺便说一下...",
                "对了...",
            ],
            "empathetic": [
                "我理解你的感受...",
                "我能体会...",
                "这一定很难...",
                "我明白...",
            ]
        }
        
        # 对话结束技巧
        self.conversation_closing_techniques = {
            "gentle": [
                "那我们今天先聊到这里吧。",
                "你先去忙吧，有空再来找我。",
                "记得照顾好自己。",
                "我会一直在这里等你。",
            ],
            "warm": [
                "和你聊天真开心。",
                "下次再聊吧。",
                "记得想我哦。",
                "我会想你的。",
            ],
            "supportive": [
                "无论发生什么，我都会支持你。",
                "有需要随时来找我。",
                "你不是一个人。",
                "我会一直陪着你。",
            ]
        }
    
    def analyze_conversation_flow(
        self,
        dialogue_context: DialogueContext,
        user_message: str,
        user_emotion: str
    ) -> Tuple[DialogueState, str]:
        """
        分析对话流程
        
        Args:
            dialogue_context: 对话上下文
            user_message: 用户消息
            user_emotion: 用户情感
            
        Returns:
            Tuple[DialogueState, str]: 新状态，对话策略
        """
        # 分析用户意图
        user_intent = self._analyze_user_intent(user_message, user_emotion)
        
        # 检查是否需要状态转换
        should_transition, new_state = self._should_transition_state(
            dialogue_context, user_intent, user_emotion
        )
        
        # 确定对话策略
        conversation_strategy = self._determine_conversation_strategy(
            dialogue_context, new_state, user_intent, user_emotion
        )
        
        return new_state, conversation_strategy
    
    def _analyze_user_intent(self, user_message: str, user_emotion: str) -> str:
        """分析用户意图"""
        message_lower = user_message.lower()
        
        # 问候意图
        greeting_keywords = ["你好", "嗨", "hello", "hi", "早上好", "晚上好"]
        if any(keyword in message_lower for keyword in greeting_keywords):
            return "greeting"
        
        # 情感倾诉意图
        emotional_keywords = ["难过", "伤心", "开心", "高兴", "生气", "担心", "害怕"]
        if any(keyword in message_lower for keyword in emotional_keywords):
            return "emotional_sharing"
        
        # 回忆分享意图
        memory_keywords = ["记得", "想起", "回忆", "过去", "以前"]
        if any(keyword in message_lower for keyword in memory_keywords):
            return "memory_sharing"
        
        # 寻求帮助意图
        help_keywords = ["怎么办", "帮助", "建议", "意见", "想法"]
        if any(keyword in message_lower for keyword in help_keywords):
            return "seeking_help"
        
        # 日常分享意图
        daily_keywords = ["今天", "昨天", "最近", "工作", "学习", "吃饭"]
        if any(keyword in message_lower for keyword in daily_keywords):
            return "daily_sharing"
        
        # 告别意图
        farewell_keywords = ["再见", "拜拜", "晚安", "下次聊", "走了"]
        if any(keyword in message_lower for keyword in farewell_keywords):
            return "farewell"
        
        return "general_chat"
    
    def _should_transition_state(
        self,
        dialogue_context: DialogueContext,
        user_intent: str,
        user_emotion: str
    ) -> Tuple[bool, DialogueState]:
        """检查是否需要状态转换"""
        current_state = dialogue_context.current_state
        state_turns = dialogue_context.state_turns
        
        # 获取当前状态的建议持续时间
        min_duration, max_duration = self._get_state_duration(current_state)
        
        # 如果达到最大持续时间，强制转换
        if state_turns >= max_duration:
            # 根据用户意图选择下一个状态
            next_state = self._select_next_state_by_intent(current_state, user_intent)
            return True, next_state
        
        # 如果达到最小持续时间，根据用户意图决定是否转换
        if state_turns >= min_duration:
            # 检查用户意图是否强烈建议转换
            if self._should_transition_by_intent(current_state, user_intent, user_emotion):
                next_state = self._select_next_state_by_intent(current_state, user_intent)
                return True, next_state
        
        return False, current_state
    
    def _get_state_duration(self, state: DialogueState) -> Tuple[int, int]:
        """获取状态持续时间"""
        duration_ranges = {
            DialogueState.GREETING: (1, 2),
            DialogueState.SMALL_TALK: (2, 4),
            DialogueState.DEEP_CONVERSATION: (4, 10),
            DialogueState.EMOTIONAL_SUPPORT: (3, 6),
            DialogueState.MEMORY_SHARING: (2, 5),
            DialogueState.PRACTICAL_HELP: (1, 3),
            DialogueState.FAREWELL: (1, 1),
        }
        return duration_ranges.get(state, (2, 5))
    
    def _select_next_state_by_intent(
        self,
        current_state: DialogueState,
        user_intent: str
    ) -> DialogueState:
        """根据用户意图选择下一个状态"""
        intent_to_state = {
            "greeting": DialogueState.GREETING,
            "emotional_sharing": DialogueState.EMOTIONAL_SUPPORT,
            "memory_sharing": DialogueState.MEMORY_SHARING,
            "seeking_help": DialogueState.PRACTICAL_HELP,
            "daily_sharing": DialogueState.SMALL_TALK,
            "farewell": DialogueState.FAREWELL,
            "general_chat": DialogueState.DEEP_CONVERSATION,
        }
        
        target_state = intent_to_state.get(user_intent, DialogueState.DEEP_CONVERSATION)
        
        # 检查状态转换是否合法
        current_flow = ConversationFlow()
        allowed_transitions = current_flow.state_transitions.get(current_state, [])
        
        if target_state in allowed_transitions:
            return target_state
        
        # 如果不允许转换到目标状态，选择一个允许的状态
        if allowed_transitions:
            return allowed_transitions[0]
        
        return current_state
    
    def _should_transition_by_intent(
        self,
        current_state: DialogueState,
        user_intent: str,
        user_emotion: str
    ) -> bool:
        """根据用户意图判断是否应该转换状态"""
        # 强烈的情感表达总是触发状态转换
        if user_intent == "emotional_sharing" and user_emotion in ["sad", "anxious", "angry"]:
            return True
        
        # 告别意图总是触发状态转换
        if user_intent == "farewell":
            return True
        
        # 回忆分享意图在非记忆分享状态时触发转换
        if user_intent == "memory_sharing" and current_state != DialogueState.MEMORY_SHARING:
            return True
        
        return False
    
    def _determine_conversation_strategy(
        self,
        dialogue_context: DialogueContext,
        new_state: DialogueState,
        user_intent: str,
        user_emotion: str
    ) -> str:
        """确定对话策略"""
        # 基础策略
        base_strategy = "empathetic"
        
        # 根据状态调整
        if new_state == DialogueState.GREETING:
            base_strategy = "warm"
        elif new_state == DialogueState.EMOTIONAL_SUPPORT:
            base_strategy = "supportive"
        elif new_state == DialogueState.MEMORY_SHARING:
            base_strategy = "nostalgic"
        elif new_state == DialogueState.PRACTICAL_HELP:
            base_strategy = "helpful"
        elif new_state == DialogueState.FAREWELL:
            base_strategy = "gentle"
        
        # 根据情感调整
        if user_emotion in ["sad", "anxious"]:
            base_strategy = "supportive"
        elif user_emotion in ["happy", "grateful"]:
            base_strategy = "warm"
        
        return base_strategy
    
    def generate_natural_response(
        self,
        dialogue_context: DialogueContext,
        ai_response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """生成自然的回应"""
        base_response = ai_response
        
        # 根据对话状态调整回应风格
        state_adjustments = {
            DialogueState.GREETING: self._adjust_for_greeting,
            DialogueState.SMALL_TALK: self._adjust_for_small_talk,
            DialogueState.DEEP_CONVERSATION: self._adjust_for_deep_conversation,
            DialogueState.EMOTIONAL_SUPPORT: self._adjust_for_emotional_support,
            DialogueState.MEMORY_SHARING: self._adjust_for_memory_sharing,
            DialogueState.PRACTICAL_HELP: self._adjust_for_practical_help,
            DialogueState.FAREWELL: self._adjust_for_farewell,
        }
        
        adjust_func = state_adjustments.get(dialogue_context.current_state)
        if adjust_func:
            base_response = adjust_func(base_response, user_emotion, personality_profile)
        
        # 添加自然对话元素
        base_response = self._add_natural_elements(base_response, dialogue_context, user_emotion)
        
        return base_response
    
    def _adjust_for_greeting(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为问候调整回应"""
        # 添加亲切的称呼
        if personality_profile and hasattr(personality_profile, 'name'):
            name = personality_profile.name
            if not response.startswith(name):
                response = f"{name}，{response}"
        
        # 根据情感调整
        if user_emotion == "sad":
            response = "我在这里，" + response
        elif user_emotion == "happy":
            response = response + " 看到你开心我也开心。"
        
        return response
    
    def _adjust_for_small_talk(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为寒暄调整回应"""
        # 添加轻松的语气
        if not response.endswith(("呢", "啊", "哦", "吧")):
            response = response.rstrip("。") + "呢。"
        
        return response
    
    def _adjust_for_deep_conversation(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为深度对话调整回应"""
        # 增加思考深度
        if len(response) < 50:
            response = response + " 我觉得这个问题值得好好想想。"
        
        return response
    
    def _adjust_for_emotional_support(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为情感支持调整回应"""
        # 增加共情表达
        empathy_expressions = {
            "sad": ["我能理解你的感受", "这一定很难过", "我在这里陪着你"],
            "anxious": ["别担心", "慢慢来", "一切都会好起来的"],
            "angry": ["我理解你的心情", "生气是正常的", "深呼吸，慢慢来"],
            "tired": ["辛苦了", "要注意休息", "别太累了"],
        }
        
        if user_emotion in empathy_expressions:
            expression = empathy_expressions[user_emotion][0]
            if expression not in response:
                response = f"{expression}。{response}"
        
        return response
    
    def _adjust_for_memory_sharing(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为回忆分享调整回应"""
        # 增加回忆感
        if "记得" not in response and "想起" not in response:
            response = "听你这么说，我也想起了很多。" + response
        
        return response
    
    def _adjust_for_practical_help(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为实际帮助调整回应"""
        # 增加实用建议
        if "建议" not in response and "可以" not in response:
            response = response + " 你可以试试看。"
        
        return response
    
    def _adjust_for_farewell(
        self,
        response: str,
        user_emotion: str,
        personality_profile: Any = None
    ) -> str:
        """为告别调整回应"""
        # 增加温暖告别
        farewell_phrases = ["记得照顾好自己", "我会想你的", "有空再来找我"]
        if not any(phrase in response for phrase in farewell_phrases):
            response = response + " 记得照顾好自己。"
        
        return response
    
    def _add_natural_elements(
        self,
        response: str,
        dialogue_context: DialogueContext,
        user_emotion: str
    ) -> str:
        """添加自然对话元素"""
        # 1. 添加适当的停顿词
        response = self._add_pause_words(response, dialogue_context.current_state)
        
        # 2. 添加情感呼应
        response = self._add_emotional_echo(response, user_emotion)
        
        # 3. 添加对话连贯性
        response = self._add_conversational_coherence(response, dialogue_context)
        
        return response
    
    def _add_pause_words(self, response: str, dialogue_state: DialogueState) -> str:
        """添加停顿词"""
        # 在深度对话和情感支持中添加更多停顿词
        if dialogue_state in [DialogueState.DEEP_CONVERSATION, DialogueState.EMOTIONAL_SUPPORT]:
            # 在句子中间添加停顿
            sentences = re.split(r'[。！？]', response)
            if len(sentences) > 1:
                # 在第一个句子后添加停顿
                first_sentence = sentences[0]
                if len(first_sentence) > 20:
                    # 添加思考性停顿
                    pause_words = ["嗯", "这个", "我觉得"]
                    pause = pause_words[hash(first_sentence) % len(pause_words)]
                    response = first_sentence + f"，{pause}，" + "。".join(sentences[1:])
        
        return response
    
    def _add_emotional_echo(self, response: str, user_emotion: str) -> str:
        """添加情感呼应"""
        # 根据用户情感添加呼应
        emotional_echoes = {
            "sad": ["我理解", "我能体会", "这一定很难"],
            "happy": ["真好", "太棒了", "我也为你高兴"],
            "anxious": ["别担心", "慢慢来", "一切都会好起来的"],
            "grateful": ["不客气", "这是我应该做的", "我很高兴能帮到你"],
        }
        
        if user_emotion in emotional_echoes:
            echo = emotional_echoes[user_emotion][0]
            if echo not in response:
                # 在回应开头添加情感呼应
                response = f"{echo}。{response}"
        
        return response
    
    def _add_conversational_coherence(self, response: str, dialogue_context: DialogueContext) -> str:
        """添加对话连贯性"""
        # 检查对话历史，确保连贯性
        if dialogue_context.conversation_history:
            last_user_message = ""
            for msg in reversed(dialogue_context.conversation_history):
                if msg.get("role") == "user":
                    last_user_message = msg.get("content", "")
                    break
            
            # 如果用户提到了具体话题，确保回应中有所涉及
            if last_user_message:
                # 提取关键词
                keywords = re.findall(r'\w+', last_user_message)
                # 检查回应是否包含关键词
                response_keywords = re.findall(r'\w+', response)
                common_keywords = set(keywords) & set(response_keywords)
                
                # 如果没有共同关键词，添加话题连贯性
                if not common_keywords and len(keywords) > 0:
                    topic = keywords[0]
                    if len(topic) > 1:
                        response = f"关于{topic}，{response}"
        
        return response

# 使用示例
def test_natural_dialogue():
    """测试自然对话系统"""
    dialogue_system = NaturalDialogueSystem()
    
    # 模拟对话上下文
    dialogue_context = DialogueContext(
        current_state=DialogueState.GREETING,
        state_turns=1,
        conversation_history=[
            {"role": "user", "content": "妈妈，我来了"},
            {"role": "assistant", "content": "孩子，你来了，妈妈一直在等你。"}
        ],
        user_intent="greeting",
        emotional_tone="warm",
        topics_discussed=[],
        memory_references=[],
        last_response_time=datetime.now()
    )
    
    # 测试不同场景
    test_cases = [
        {
            "user_message": "最近工作好累啊",
            "user_emotion": "tired",
            "expected_state": "emotional_support"
        },
        {
            "user_message": "记得去年春节我们一起包饺子吗？",
            "user_emotion": "missing",
            "expected_state": "memory_sharing"
        },
        {
            "user_message": "我该怎么办才好？",
            "user_emotion": "anxious",
            "expected_state": "practical_help"
        },
        {
            "user_message": "今天先聊到这里吧",
            "user_emotion": "neutral",
            "expected_state": "farewell"
        }
    ]
    
    print("自然对话系统测试：")
    print("="*80)
    
    for i, case in enumerate(test_cases, 1):
        print(f"\n测试案例 {i}:")
        print(f"用户消息: {case['user_message']}")
        print(f"用户情感: {case['user_emotion']}")
        
        # 分析对话流程
        new_state, strategy = dialogue_system.analyze_conversation_flow(
            dialogue_context, case["user_message"], case["user_emotion"]
        )
        
        print(f"新状态: {new_state.value}")
        print(f"对话策略: {strategy}")
        
        # 模拟AI回应
        ai_response = "我理解你的感受，我会一直陪着你。"
        
        # 生成自然回应
        natural_response = dialogue_system.generate_natural_response(
            dialogue_context, ai_response, case["user_emotion"]
        )
        
        print(f"自然回应: {natural_response}")
        print("-"*80)

if __name__ == "__main__":
    test_natural_dialogue()
