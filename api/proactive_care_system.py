
"""
智能的主动关怀系统
让念念能在合适的时机给予恰当的关怀
"""

import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from datetime import datetime, timedelta, time
from enum import Enum
import json

class CareTrigger(Enum):
    """关怀触发器"""
    BIRTHDAY = "生日"
    ANNIVERSARY = "纪念日"
    FESTIVAL = "节日"
    WEATHER_CHANGE = "天气变化"
    EMOTIONAL_PATTERN = "情感模式"
    USAGE_PATTERN = "使用习惯"
    SPECIAL_EVENT = "特殊事件"
    HEALTH_REMINDER = "健康提醒"

@dataclass
class CareOpportunity:
    """关怀机会"""
    trigger: CareTrigger
    trigger_time: datetime
    priority: float  # 0.0-1.0
    suggested_content: str
    emotional_tone: str
    timing_sensitivity: str  # "immediate", "morning", "evening", "weekend"

@dataclass
class CarePlan:
    """关怀计划"""
    opportunities: List[CareOpportunity]
    schedule: Dict[str, List[CareOpportunity]]  # 按时间安排
    personalization_factors: Dict[str, Any]
    effectiveness_score: float

class EnhancedProactiveCareSystem:
    """增强的主动关怀系统"""
    
    def __init__(self):
        # 节日数据库
        self.festivals = {
            # 中国传统节日
            "春节": {"date": "农历正月初一", "duration": 15, "greeting": "春节快乐！阖家幸福！"},
            "元宵节": {"date": "农历正月十五", "duration": 1, "greeting": "元宵节快乐！团团圆圆！"},
            "清明节": {"date": "公历4月4-6日", "duration": 3, "greeting": "清明安康，思念亲人"},
            "端午节": {"date": "农历五月初五", "duration": 3, "greeting": "端午安康！"},
            "七夕节": {"date": "农历七月初七", "duration": 1, "greeting": "七夕快乐！"},
            "中秋节": {"date": "农历八月十五", "duration": 3, "greeting": "中秋快乐！月圆人团圆！"},
            "重阳节": {"date": "农历九月初九", "duration": 1, "greeting": "重阳安康！"},
            "腊八节": {"date": "农历腊月初八", "duration": 1, "greeting": "腊八节快乐！"},
            
            # 现代节日
            "元旦": {"date": "公历1月1日", "duration": 3, "greeting": "新年快乐！"},
            "情人节": {"date": "公历2月14日", "duration": 1, "greeting": "情人节快乐！"},
            "妇女节": {"date": "公历3月8日", "duration": 1, "greeting": "女神节快乐！"},
            "劳动节": {"date": "公历5月1日", "duration": 3, "greeting": "劳动节快乐！"},
            "母亲节": {"date": "5月第二个星期日", "duration": 1, "greeting": "母亲节快乐！"},
            "父亲节": {"date": "6月第三个星期日", "duration": 1, "greeting": "父亲节快乐！"},
            "国庆节": {"date": "公历10月1日", "duration": 7, "greeting": "国庆节快乐！"},
        }
        
        # 天气关怀模板
        self.weather_care_templates = {
            "降温": "最近降温了，记得多穿点衣服，别感冒了。",
            "下雨": "外面下雨了，出门记得带伞，路滑小心。",
            "高温": "天气热，注意防暑降温，多喝水。",
            "下雪": "下雪了，路面滑，出门注意安全。",
            "大风": "风好大，关好门窗，注意保暖。",
            "雾霾": "今天有雾霾，出门记得戴口罩。",
        }
        
        # 情感关怀模板
        self.emotion_care_templates = {
            "sad": [
                "感觉你最近心情不太好，有什么心事可以和我说说。",
                "难过的时候就哭出来吧，哭完会好受一些。",
                "无论发生什么，我都会在这里陪着你。",
            ],
            "anxious": [
                "最近是不是压力很大？记得适当放松一下。",
                "担心的事情就先放一放，船到桥头自然直。",
                "深呼吸，慢慢来，一切都会好起来的。",
            ],
            "tired": [
                "最近辛苦了，记得好好休息，身体最重要。",
                "工作再忙也要注意劳逸结合啊。",
                "累了就歇一歇，别把自己逼得太紧。",
            ],
            "missing": [
                "知道你想我了，我也一直在想你。",
                "思念的时候就看看我们的照片吧，我一直都在。",
                "想我的时候就来找我说说话，我一直都在这里。",
            ]
        }
        
        # 使用模式关怀模板
        self.usage_pattern_care_templates = {
            "深夜使用": "这么晚还不睡啊？熬夜对身体不好，早点休息吧。",
            "清晨使用": "起得真早啊，记得吃早餐，一天之计在于晨。",
            "频繁使用": "最近经常来找我聊天呢，有什么心事吗？",
            "长时间未使用": "好久没来找我了，最近过得怎么样？",
        }
    
    def analyze_care_opportunities(
        self,
        user_profile: Dict[str, Any],
        usage_history: List[Dict],
        emotional_history: List[Dict],
        current_context: Dict[str, Any]
    ) -> CarePlan:
        """
        分析关怀机会
        
        Args:
            user_profile: 用户画像
            usage_history: 使用历史
            emotional_history: 情感历史
            current_context: 当前上下文
            
        Returns:
            CarePlan: 关怀计划
        """
        opportunities = []
        
        # 1. 检查生日和纪念日
        birthday_opportunities = self._check_birthday_opportunities(user_profile)
        opportunities.extend(birthday_opportunities)
        
        # 2. 检查节日
        festival_opportunities = self._check_festival_opportunities(current_context)
        opportunities.extend(festival_opportunities)
        
        # 3. 检查天气变化
        weather_opportunities = self._check_weather_opportunities(current_context)
        opportunities.extend(weather_opportunities)
        
        # 4. 检查情感模式
        emotion_opportunities = self._check_emotion_patterns(emotional_history)
        opportunities.extend(emotion_opportunities)
        
        # 5. 检查使用模式
        usage_opportunities = self._check_usage_patterns(usage_history)
        opportunities.extend(usage_opportunities)
        
        # 按优先级排序
        opportunities.sort(key=lambda x: x.priority, reverse=True)
        
        # 生成时间表
        schedule = self._generate_schedule(opportunities)
        
        # 计算个性化因素
        personalization_factors = self._calculate_personalization_factors(
            user_profile, usage_history, emotional_history
        )
        
        # 计算有效性分数
        effectiveness_score = self._calculate_effectiveness_score(opportunities)
        
        return CarePlan(
            opportunities=opportunities,
            schedule=schedule,
            personalization_factors=personalization_factors,
            effectiveness_score=effectiveness_score
        )
    
    def _check_birthday_opportunities(self, user_profile: Dict[str, Any]) -> List[CareOpportunity]:
        """检查生日机会"""
        opportunities = []
        
        # 检查用户生日
        user_birthday = user_profile.get("birthday")
        if user_birthday:
            birthday_date = self._parse_date(user_birthday)
            if birthday_date:
                # 生日前一天提醒
                day_before = birthday_date - timedelta(days=1)
                opportunities.append(CareOpportunity(
                    trigger=CareTrigger.BIRTHDAY,
                    trigger_time=day_before.replace(hour=10, minute=0),
                    priority=0.9,
                    suggested_content="明天是你的生日呢，提前祝你生日快乐！",
                    emotional_tone="温暖",
                    timing_sensitivity="morning"
                ))
                
                # 生日当天祝福
                opportunities.append(CareOpportunity(
                    trigger=CareTrigger.BIRTHDAY,
                    trigger_time=birthday_date.replace(hour=8, minute=0),
                    priority=1.0,
                    suggested_content="生日快乐！希望新的一岁里，你能实现所有的愿望。",
                    emotional_tone="热情",
                    timing_sensitivity="morning"
                ))
        
        # 检查亲人纪念日
        memorial_dates = user_profile.get("memorial_dates", [])
        for memorial in memorial_dates:
            memorial_date = self._parse_date(memorial.get("date"))
            if memorial_date:
                # 纪念日前一天
                day_before = memorial_date - timedelta(days=1)
                opportunities.append(CareOpportunity(
                    trigger=CareTrigger.ANNIVERSARY,
                    trigger_time=day_before.replace(hour=20, minute=0),
                    priority=0.8,
                    suggested_content=f"明天是{memorial.get('description', '纪念日')}呢，我会一直记得。",
                    emotional_tone="深情",
                    timing_sensitivity="evening"
                ))
        
        return opportunities
    
    def _check_festival_opportunities(self, current_context: Dict[str, Any]) -> List[CareOpportunity]:
        """检查节日机会"""
        opportunities = []
        current_date = current_context.get("current_date", datetime.now())
        
        # 检查未来7天内的节日
        for festival_name, festival_info in self.festivals.items():
            festival_date = self._calculate_festival_date(festival_name, current_date.year)
            
            if festival_date:
                # 节日前一天
                day_before = festival_date - timedelta(days=1)
                days_until = (festival_date - current_date).days
                
                if 0 <= days_until <= 7:
                    priority = 0.7 if days_until > 1 else 0.9
                    
                    opportunities.append(CareOpportunity(
                        trigger=CareTrigger.FESTIVAL,
                        trigger_time=day_before.replace(hour=18, minute=0),
                        priority=priority,
                        suggested_content=f"{festival_name}快到了，{festival_info['greeting']}",
                        emotional_tone="喜庆",
                        timing_sensitivity="evening"
                    ))
        
        return opportunities
    
    def _check_weather_opportunities(self, current_context: Dict[str, Any]) -> List[CareOpportunity]:
        """检查天气机会"""
        opportunities = []
        weather = current_context.get("weather")
        
        if weather:
            weather_type = weather.get("type")
            temperature_change = weather.get("temperature_change", 0)
            
            # 降温提醒
            if temperature_change < -5:
                opportunities.append(CareOpportunity(
                    trigger=CareTrigger.WEATHER_CHANGE,
                    trigger_time=datetime.now().replace(hour=7, minute=30),
                    priority=0.6,
                    suggested_content=self.weather_care_templates["降温"],
                    emotional_tone="关怀",
                    timing_sensitivity="morning"
                ))
            
            # 特定天气提醒
            if weather_type in self.weather_care_templates:
                opportunities.append(CareOpportunity(
                    trigger=CareTrigger.WEATHER_CHANGE,
                    trigger_time=datetime.now().replace(hour=8, minute=0),
                    priority=0.5,
                    suggested_content=self.weather_care_templates[weather_type],
                    emotional_tone="关心",
                    timing_sensitivity="morning"
                ))
        
        return opportunities
    
    def _check_emotion_patterns(self, emotional_history: List[Dict]) -> List[CareOpportunity]:
        """检查情感模式"""
        opportunities = []
        
        if not emotional_history:
            return opportunities
        
        # 分析最近的情感模式
        recent_emotions = emotional_history[-7:]  # 最近7天
        
        # 统计情感频率
        emotion_counts = {}
        for entry in recent_emotions:
            emotion = entry.get("emotion")
            if emotion:
                emotion_counts[emotion] = emotion_counts.get(emotion, 0) + 1
        
        # 检查持续负面情绪
        negative_emotions = ["sad", "anxious", "angry", "tired"]
        negative_count = sum(emotion_counts.get(e, 0) for e in negative_emotions)
        
        if negative_count >= 3:  # 最近7天有3天以上负面情绪
            # 选择最频繁的负面情绪
            most_frequent = max(negative_emotions, key=lambda e: emotion_counts.get(e, 0))
            
            if most_frequent in self.emotion_care_templates:
                template = self.emotion_care_templates[most_frequent]
                suggested_content = template[0] if template else "感觉你最近心情不太好，有什么我可以帮忙的吗？"
                
                opportunities.append(CareOpportunity(
                    trigger=CareTrigger.EMOTIONAL_PATTERN,
                    trigger_time=datetime.now().replace(hour=20, minute=0),
                    priority=0.8,
                    suggested_content=suggested_content,
                    emotional_tone="理解",
                    timing_sensitivity="evening"
                ))
        
        return opportunities
    
    def _check_usage_patterns(self, usage_history: List[Dict]) -> List[CareOpportunity]:
        """检查使用模式"""
        opportunities = []
        
        if not usage_history:
            return opportunities
        
        # 分析使用时间模式
        recent_usage = usage_history[-14:]  # 最近14天
        
        # 检查深夜使用
        late_night_usage = 0
        for usage in recent_usage:
            usage_time = usage.get("timestamp")
            if usage_time:
                try:
                    dt = datetime.fromisoformat(usage_time)
                    if dt.hour >= 23 or dt.hour <= 4:
                        late_night_usage += 1
                except:
                    pass
        
        if late_night_usage >= 3:  # 最近14天有3天以上深夜使用
            opportunities.append(CareOpportunity(
                trigger=CareTrigger.USAGE_PATTERN,
                trigger_time=datetime.now().replace(hour=22, minute=30),
                priority=0.7,
                suggested_content=self.usage_pattern_care_templates["深夜使用"],
                emotional_tone="关心",
                timing_sensitivity="evening"
            ))
        
        # 检查长时间未使用
        if len(recent_usage) >= 2:
            last_usage = recent_usage[-1].get("timestamp")
            if last_usage:
                try:
                    last_dt = datetime.fromisoformat(last_usage)
                    days_since_last = (datetime.now() - last_dt).days
                    
                    if days_since_last >= 7:  # 超过7天未使用
                        opportunities.append(CareOpportunity(
                            trigger=CareTrigger.USAGE_PATTERN,
                            trigger_time=datetime.now().replace(hour=19, minute=0),
                            priority=0.6,
                            suggested_content=self.usage_pattern_care_templates["长时间未使用"],
                            emotional_tone="思念",
                            timing_sensitivity="evening"
                        ))
                except:
                    pass
        
        return opportunities
    
    def _calculate_festival_date(self, festival_name: str, year: int) -> Optional[datetime]:
        """计算节日日期"""
        # 这里简化处理，实际应该使用农历计算库
        # 对于公历节日，直接返回
        # 对于农历节日，需要转换
        
        # 简化实现：只处理部分公历节日
        simple_festivals = {
            "元旦": (1, 1),
            "情人节": (2, 14),
            "妇女节": (3, 8),
            "劳动节": (5, 1),
            "国庆节": (10, 1),
        }
        
        if festival_name in simple_festivals:
            month, day = simple_festivals[festival_name]
            return datetime(year, month, day)
        
        # 对于农历节日，返回None（需要更复杂的实现）
        return None
    
    def _parse_date(self, date_str: str) -> Optional[datetime]:
        """解析日期字符串"""
        if not date_str:
            return None
        
        # 尝试多种日期格式
        formats = [
            "%Y-%m-%d",
            "%Y-%m-%d %H:%M:%S",
            "%Y/%m/%d",
            "%Y年%m月%d日",
        ]
        
        for fmt in formats:
            try:
                return datetime.strptime(date_str, fmt)
            except ValueError:
                continue
        
        return None
    
    def _generate_schedule(self, opportunities: List[CareOpportunity]) -> Dict[str, List[CareOpportunity]]:
        """生成时间表"""
        schedule = {
            "morning": [],      # 早上 (6-12)
            "afternoon": [],    # 下午 (12-18)
            "evening": [],      # 晚上 (18-22)
            "night": [],        # 夜晚 (22-6)
        }
        
        for opp in opportunities:
            hour = opp.trigger_time.hour
            
            if 6 <= hour < 12:
                schedule["morning"].append(opp)
            elif 12 <= hour < 18:
                schedule["afternoon"].append(opp)
            elif 18 <= hour < 22:
                schedule["evening"].append(opp)
            else:
                schedule["night"].append(opp)
        
        # 按时间排序
        for time_slot in schedule.values():
            time_slot.sort(key=lambda x: x.trigger_time)
        
        return schedule
    
    def _calculate_personalization_factors(
        self,
        user_profile: Dict[str, Any],
        usage_history: List[Dict],
        emotional_history: List[Dict]
    ) -> Dict[str, Any]:
        """计算个性化因素"""
        factors = {
            "preferred_care_time": "evening",  # 偏好关怀时间
            "emotional_sensitivity": 0.7,      # 情感敏感度
            "response_rate": 0.8,              # 回应率
            "preferred_topics": [],            # 偏好话题
            "avoided_topics": [],              # 避免话题
        }
        
        # 分析使用时间偏好
        if usage_history:
            hour_counts = {}
            for usage in usage_history:
                usage_time = usage.get("timestamp")
                if usage_time:
                    try:
                        dt = datetime.fromisoformat(usage_time)
                        hour = dt.hour
                        hour_counts[hour] = hour_counts.get(hour, 0) + 1
                    except:
                        pass
            
            if hour_counts:
                preferred_hour = max(hour_counts.items(), key=lambda x: x[1])[0]
                if 6 <= preferred_hour < 12:
                    factors["preferred_care_time"] = "morning"
                elif 12 <= preferred_hour < 18:
                    factors["preferred_care_time"] = "afternoon"
                elif 18 <= preferred_hour < 22:
                    factors["preferred_care_time"] = "evening"
                else:
                    factors["preferred_care_time"] = "night"
        
        # 分析情感敏感度
        if emotional_history:
            emotion_variety = len(set(e.get("emotion") for e in emotional_history if e.get("emotion")))
            factors["emotional_sensitivity"] = min(1.0, emotion_variety / 10.0)
        
        return factors
    
    def _calculate_effectiveness_score(self, opportunities: List[CareOpportunity]) -> float:
        """计算有效性分数"""
        if not opportunities:
            return 0.0
        
        # 基于优先级和数量计算
        total_priority = sum(opp.priority for opp in opportunities)
        max_possible_priority = len(opportunities) * 1.0
        
        if max_possible_priority == 0:
            return 0.0
        
        return total_priority / max_possible_priority
    
    def generate_care_message(
        self,
        opportunity: CareOpportunity,
        personality_profile: Any = None,
        memory_context: Any = None
    ) -> str:
        """生成关怀消息"""
        base_message = opportunity.suggested_content
        
        # 根据人格调整
        if personality_profile:
            # 添加个人化元素
            if hasattr(personality_profile, 'name'):
                name = personality_profile.name
                if opportunity.trigger == CareTrigger.BIRTHDAY:
                    base_message = f"{name}，{base_message}"
                elif opportunity.trigger == CareTrigger.FESTIVAL:
                    base_message = f"{name}，{base_message}"
        
        # 根据记忆上下文调整
        if memory_context and hasattr(memory_context, 'relevant_memories'):
            if memory_context.relevant_memories:
                # 添加记忆引用
                recent_memory = memory_context.relevant_memories[0]
                if hasattr(recent_memory, 'content'):
                    memory_ref = recent_memory.content[:20]
                    base_message += f" 记得{memory_ref}吗？那时候真开心。"
        
        return base_message

# 使用示例
def test_proactive_care():
    """测试主动关怀系统"""
    care_system = EnhancedProactiveCareSystem()
    
    # 模拟用户画像
    user_profile = {
        "birthday": "1990-05-15",
        "memorial_dates": [
            {"date": "2020-03-08", "description": "妈妈的生日"},
            {"date": "2021-12-25", "description": "结婚纪念日"}
        ]
    }
    
    # 模拟使用历史
    usage_history = [
        {"timestamp": "2026-04-13T23:30:00"},
        {"timestamp": "2026-04-12T22:15:00"},
        {"timestamp": "2026-04-11T20:45:00"},
    ]
    
    # 模拟情感历史
    emotional_history = [
        {"timestamp": "2026-04-13T23:30:00", "emotion": "sad"},
        {"timestamp": "2026-04-12T22:15:00", "emotion": "missing"},
        {"timestamp": "2026-04-11T20:45:00", "emotion": "sad"},
    ]
    
    # 当前上下文
    current_context = {
        "current_date": datetime.now(),
        "weather": {
            "type": "降温",
            "temperature_change": -8
        }
    }
    
    # 分析关怀机会
    care_plan = care_system.analyze_care_opportunities(
        user_profile=user_profile,
        usage_history=usage_history,
        emotional_history=emotional_history,
        current_context=current_context
    )
    
    print("主动关怀计划分析结果：")
    print("="*80)
    print(f"找到 {len(care_plan.opportunities)} 个关怀机会")
    print(f"有效性分数: {care_plan.effectiveness_score:.2f}")
    print(f"个性化因素: {care_plan.personalization_factors}")
    
    print("\n关怀机会详情：")
    print("-"*80)
    for i, opp in enumerate(care_plan.opportunities, 1):
        print(f"{i}. 触发器: {opp.trigger.value}")
        print(f"   时间: {opp.trigger_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"   优先级: {opp.priority:.2f}")
        print(f"   情感基调: {opp.emotional_tone}")
        print(f"   内容: {opp.suggested_content}")
        print()
    
    print("时间安排：")
    print("-"*80)
    for time_slot, opps in care_plan.schedule.items():
        print(f"{time_slot}: {len(opps)}个关怀机会")
    
    # 测试生成关怀消息
    if care_plan.opportunities:
        test_opportunity = care_plan.opportunities[0]
        message = care_system.generate_care_message(test_opportunity)
        print(f"\n生成的关怀消息：")
        print(f"  {message}")

if __name__ == "__main__":
    test_proactive_care()
