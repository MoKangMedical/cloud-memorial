
"""
丰富的人格建模系统
让念念能更真实地还原亲人的个性特征
"""

import re
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

class PersonalityDimension(Enum):
    """人格维度"""
    OPENNESS = "开放性"           # 对新体验的开放程度
    CONSCIENTIOUSNESS = "尽责性"  # 责任感和条理性
    EXTRAVERSION = "外向性"       # 社交活跃度
    AGREEABLENESS = "宜人性"      # 合作和同情心
    NEUROTICISM = "神经质"        # 情绪稳定性

@dataclass
class PersonalityTrait:
    """人格特质"""
    dimension: PersonalityDimension
    level: float  # 0.0-1.0
    description: str
    behavioral_manifestations: List[str]  # 行为表现
    speech_patterns: List[str]            # 语言模式

@dataclass
class SpeechStyle:
    """说话风格"""
    pace: str                # 语速：快、中、慢
    volume: str              # 音量：大、中、小
    tone: str                # 语调：高、中、低
    rhythm: str              # 节奏：急促、平稳、舒缓
    filler_words: List[str]  # 口头禅
    catchphrases: List[str]  # 口头语
    humor_style: str         # 幽默风格

@dataclass
class ValuesAndBeliefs:
    """价值观和信念"""
    core_values: List[str]        # 核心价值观
    life_philosophy: str          # 生活哲学
    family_importance: float      # 家庭重要性 0.0-1.0
    tradition_importance: float   # 传统重要性 0.0-1.0
    achievement_importance: float # 成就重要性 0.0-1.0

@dataclass
class InterestsAndHobbies:
    """兴趣爱好"""
    hobbies: List[str]           # 爱好
    favorite_topics: List[str]   # 喜欢谈论的话题
    disliked_topics: List[str]   # 不喜欢的话题
    special_skills: List[str]    # 特殊技能

@dataclass
class PersonalityProfile:
    """完整的人格画像"""
    name: str
    relationship: str
    personality_traits: List[PersonalityTrait]
    speech_style: SpeechStyle
    values_and_beliefs: ValuesAndBeliefs
    interests_and_hobbies: InterestsAndHobbies
    emotional_tendencies: Dict[str, float]  # 情感倾向
    coping_mechanisms: List[str]           # 应对机制
    special_habits: List[str]              # 特殊习惯

class EnhancedPersonalityModeling:
    """增强的人格建模系统"""
    
    def __init__(self):
        # 人格维度描述
        self.dimension_descriptions = {
            PersonalityDimension.OPENNESS: {
                "高": ["好奇心强", "富有想象力", "喜欢尝试新事物", "思想开放"],
                "中": ["适度开放", "愿意接受新观念", "有一定的创造力"],
                "低": ["传统保守", "喜欢熟悉的环境", "做事按部就班"]
            },
            PersonalityDimension.CONSCIENTIOUSNESS: {
                "高": ["有条理", "负责任", "自律性强", "注重细节"],
                "中": ["相对负责", "能完成任务", "有一定的组织能力"],
                "低": ["随性自由", "不喜欢计划", "灵活变通"]
            },
            PersonalityDimension.EXTRAVERSION: {
                "高": ["外向活泼", "喜欢社交", "精力充沛", "善于表达"],
                "中": ["适应性强", "能享受独处也能社交", "平衡型"],
                "低": ["内向安静", "喜欢独处", "深思熟虑", "倾听者"]
            },
            PersonalityDimension.AGREEABLENESS: {
                "高": ["善良体贴", "乐于助人", "富有同情心", "合作性强"],
                "中": ["适度关心他人", "能平衡自我和他人需求"],
                "低": ["直率坦诚", "有主见", "竞争性强"]
            },
            PersonalityDimension.NEUROTICISM: {
                "高": ["情绪敏感", "容易焦虑", "追求完美", "责任心强"],
                "中": ["情绪相对稳定", "能应对压力"],
                "低": ["情绪稳定", "冷静沉着", "抗压能力强"]
            }
        }
        
        # 说话风格模板
        self.speech_style_templates = {
            "温柔亲切型": {
                "pace": "慢",
                "volume": "小",
                "tone": "柔和",
                "rhythm": "舒缓",
                "filler_words": ["嗯", "啊", "呢", "嘛"],
                "catchphrases": ["乖", "听话", "慢慢来"],
                "humor_style": "温和幽默"
            },
            "爽朗直率型": {
                "pace": "快",
                "volume": "大",
                "tone": "高亢",
                "rhythm": "急促",
                "filler_words": ["哈", "嘿", "哎"],
                "catchphrases": ["没问题", "包在我身上", "放心吧"],
                "humor_style": "豪爽幽默"
            },
            "沉稳睿智型": {
                "pace": "中",
                "volume": "中",
                "tone": "平稳",
                "rhythm": "平稳",
                "filler_words": ["这个", "那个", "嗯"],
                "catchphrases": ["我觉得", "要我说", "其实"],
                "humor_style": "含蓄幽默"
            },
            "活泼可爱型": {
                "pace": "快",
                "volume": "中",
                "tone": "活泼",
                "rhythm": "跳跃",
                "filler_words": ["哇", "呀", "啦", "嘛"],
                "catchphrases": ["好棒", "太好了", "耶"],
                "humor_style": "俏皮幽默"
            },
            "严肃认真型": {
                "pace": "慢",
                "volume": "中",
                "tone": "低沉",
                "rhythm": "平稳",
                "filler_words": ["嗯", "这个"],
                "catchphrases": ["要注意", "记住", "一定要"],
                "humor_style": "严肃幽默"
            }
        }
    
    def build_personality_profile(
        self,
        name: str,
        relationship: str,
        personality_traits_dict: Dict[str, Any],
        speaking_style: str,
        additional_info: Dict[str, Any] = None
    ) -> PersonalityProfile:
        """
        构建完整的人格画像
        
        Args:
            name: 姓名
            relationship: 关系
            personality_traits_dict: 人格特质字典
            speaking_style: 说话风格
            additional_info: 其他信息
            
        Returns:
            PersonalityProfile: 完整的人格画像
        """
        # 解析人格特质
        personality_traits = self._parse_personality_traits(personality_traits_dict)
        
        # 确定说话风格
        speech_style = self._determine_speech_style(speaking_style, personality_traits)
        
        # 构建价值观和信念
        values_and_beliefs = self._build_values_and_beliefs(additional_info)
        
        # 构建兴趣爱好
        interests_and_hobbies = self._build_interests_and_hobbies(additional_info)
        
        # 确定情感倾向
        emotional_tendencies = self._determine_emotional_tendencies(personality_traits)
        
        # 确定应对机制
        coping_mechanisms = self._determine_coping_mechanisms(personality_traits)
        
        # 确定特殊习惯
        special_habits = self._determine_special_habits(additional_info)
        
        return PersonalityProfile(
            name=name,
            relationship=relationship,
            personality_traits=personality_traits,
            speech_style=speech_style,
            values_and_beliefs=values_and_beliefs,
            interests_and_hobbies=interests_and_hobbies,
            emotional_tendencies=emotional_tendencies,
            coping_mechanisms=coping_mechanisms,
            special_habits=special_habits
        )
    
    def _parse_personality_traits(self, traits_dict: Dict[str, Any]) -> List[PersonalityTrait]:
        """解析人格特质"""
        traits = []
        
        # 映射到人格维度
        dimension_mapping = {
            "openness": PersonalityDimension.OPENNESS,
            "conscientiousness": PersonalityDimension.CONSCIENTIOUSNESS,
            "extraversion": PersonalityDimension.EXTRAVERSION,
            "agreeableness": PersonalityDimension.AGREEABLENESS,
            "neuroticism": PersonalityDimension.NEUROTICISM,
            # 中文映射
            "开放性": PersonalityDimension.OPENNESS,
            "尽责性": PersonalityDimension.CONSCIENTIOUSNESS,
            "外向性": PersonalityDimension.EXTRAVERSION,
            "宜人性": PersonalityDimension.AGREEABLENESS,
            "神经质": PersonalityDimension.NEUROTICISM,
        }
        
        for trait_name, trait_value in traits_dict.items():
            if trait_name.lower() in dimension_mapping:
                dimension = dimension_mapping[trait_name.lower()]
                
                # 确定水平
                if isinstance(trait_value, (int, float)):
                    level = float(trait_value)
                    if level > 0.7:
                        level_desc = "高"
                    elif level > 0.3:
                        level_desc = "中"
                    else:
                        level_desc = "低"
                else:
                    # 如果是字符串描述
                    if "高" in str(trait_value) or "强" in str(trait_value):
                        level = 0.8
                        level_desc = "高"
                    elif "低" in str(trait_value) or "弱" in str(trait_value):
                        level = 0.2
                        level_desc = "低"
                    else:
                        level = 0.5
                        level_desc = "中"
                
                # 获取描述
                descriptions = self.dimension_descriptions.get(dimension, {})
                desc_list = descriptions.get(level_desc, [])
                description = "，".join(desc_list) if desc_list else f"{dimension.value}处于{level_desc}水平"
                
                # 行为表现
                behavioral_manifestations = self._get_behavioral_manifestations(dimension, level_desc)
                
                # 语言模式
                speech_patterns = self._get_speech_patterns(dimension, level_desc)
                
                trait = PersonalityTrait(
                    dimension=dimension,
                    level=level,
                    description=description,
                    behavioral_manifestations=behavioral_manifestations,
                    speech_patterns=speech_patterns
                )
                traits.append(trait)
        
        return traits
    
    def _get_behavioral_manifestations(self, dimension: PersonalityDimension, level: str) -> List[str]:
        """获取行为表现"""
        manifestations = {
            PersonalityDimension.OPENNESS: {
                "高": ["喜欢尝试新菜", "对新技术感兴趣", "喜欢旅行探索", "艺术欣赏"],
                "中": ["适度尝试新事物", "平衡传统和创新"],
                "低": ["坚持传统做法", "喜欢熟悉的环境", "做事有固定模式"]
            },
            PersonalityDimension.CONSCIENTIOUSNESS: {
                "高": ["做事有计划", "注重细节", "守时", "有条理"],
                "中": ["相对有条理", "能完成任务"],
                "低": ["随性", "灵活", "不喜欢被束缚"]
            },
            PersonalityDimension.EXTRAVERSION: {
                "高": ["喜欢聚会", "主动社交", "精力充沛", "喜欢表达"],
                "中": ["适度社交", "能享受独处也能社交"],
                "低": ["喜欢独处", "深度思考", "倾听为主", "小圈子社交"]
            },
            PersonalityDimension.AGREEABLENESS: {
                "高": ["乐于助人", "体贴他人", "避免冲突", "富有同情心"],
                "中": ["平衡自我和他人需求"],
                "低": ["直率", "有主见", "不惧冲突", "竞争性强"]
            },
            PersonalityDimension.NEUROTICISM: {
                "高": ["追求完美", "注重细节", "责任心强", "容易担忧"],
                "中": ["情绪相对稳定"],
                "低": ["冷静", "抗压能力强", "情绪稳定"]
            }
        }
        
        return manifestations.get(dimension, {}).get(level, [])
    
    def _get_speech_patterns(self, dimension: PersonalityDimension, level: str) -> List[str]:
        """获取语言模式"""
        patterns = {
            PersonalityDimension.OPENNESS: {
                "高": ["使用新词汇", "喜欢比喻", "表达抽象概念", "好奇提问"],
                "中": ["表达平衡", "适度使用新概念"],
                "低": ["使用传统表达", "具体描述", "务实语言"]
            },
            PersonalityDimension.CONSCIENTIOUSNESS: {
                "高": ["条理清晰", "使用时间词", "强调计划", "注重细节描述"],
                "中": ["表达相对清晰"],
                "低": ["表达自由", "跳跃性思维", "灵活表达"]
            },
            PersonalityDimension.EXTRAVERSION: {
                "高": ["主动发起话题", "表达丰富", "使用感叹词", "喜欢分享"],
                "中": ["表达适度"],
                "低": ["简洁表达", "深度回答", "倾听为主", "少用感叹词"]
            },
            PersonalityDimension.AGREEABLENESS: {
                "高": ["使用温和词汇", "避免冲突表达", "多用肯定", "体贴语言"],
                "中": ["表达平衡"],
                "低": ["直接表达", "不回避冲突", "坦率语言"]
            },
            PersonalityDimension.NEUROTICISM: {
                "高": ["使用担忧词汇", "表达细节", "强调重要性", "谨慎语言"],
                "中": ["表达相对平稳"],
                "低": ["冷静表达", "自信语言", "简洁明了"]
            }
        }
        
        return patterns.get(dimension, {}).get(level, [])
    
    def _determine_speech_style(
        self,
        speaking_style: str,
        personality_traits: List[PersonalityTrait]
    ) -> SpeechStyle:
        """确定说话风格"""
        # 尝试匹配预定义的说话风格
        for style_name, style_config in self.speech_style_templates.items():
            if style_name in speaking_style:
                return SpeechStyle(
                    pace=style_config["pace"],
                    volume=style_config["volume"],
                    tone=style_config["tone"],
                    rhythm=style_config["rhythm"],
                    filler_words=style_config["filler_words"],
                    catchphrases=style_config["catchphrases"],
                    humor_style=style_config["humor_style"]
                )
        
        # 如果没有匹配到，根据人格特质推断
        # 默认使用温柔亲切型
        default_style = self.speech_style_templates["温柔亲切型"]
        
        # 根据外向性调整
        extraversion_trait = next(
            (t for t in personality_traits if t.dimension == PersonalityDimension.EXTRAVERSION),
            None
        )
        
        if extraversion_trait and extraversion_trait.level > 0.7:
            # 外向的人
            default_style["pace"] = "快"
            default_style["volume"] = "大"
            default_style["tone"] = "高亢"
            default_style["rhythm"] = "急促"
        elif extraversion_trait and extraversion_trait.level < 0.3:
            # 内向的人
            default_style["pace"] = "慢"
            default_style["volume"] = "小"
            default_style["tone"] = "柔和"
            default_style["rhythm"] = "舒缓"
        
        return SpeechStyle(
            pace=default_style["pace"],
            volume=default_style["volume"],
            tone=default_style["tone"],
            rhythm=default_style["rhythm"],
            filler_words=default_style["filler_words"],
            catchphrases=default_style["catchphrases"],
            humor_style=default_style["humor_style"]
        )
    
    def _build_values_and_beliefs(self, additional_info: Dict[str, Any] = None) -> ValuesAndBeliefs:
        """构建价值观和信念"""
        if not additional_info:
            additional_info = {}
        
        # 默认价值观
        core_values = additional_info.get("core_values", ["家庭", "责任", "爱"])
        life_philosophy = additional_info.get("life_philosophy", "珍惜当下，关爱家人")
        family_importance = additional_info.get("family_importance", 0.9)
        tradition_importance = additional_info.get("tradition_importance", 0.7)
        achievement_importance = additional_info.get("achievement_importance", 0.6)
        
        return ValuesAndBeliefs(
            core_values=core_values,
            life_philosophy=life_philosophy,
            family_importance=family_importance,
            tradition_importance=tradition_importance,
            achievement_importance=achievement_importance
        )
    
    def _build_interests_and_hobbies(self, additional_info: Dict[str, Any] = None) -> InterestsAndHobbies:
        """构建兴趣爱好"""
        if not additional_info:
            additional_info = {}
        
        hobbies = additional_info.get("hobbies", ["听音乐", "看书", "散步"])
        favorite_topics = additional_info.get("favorite_topics", ["家庭", "健康", "回忆"])
        disliked_topics = additional_info.get("disliked_topics", ["争吵", "负面新闻"])
        special_skills = additional_info.get("special_skills", ["烹饪", "手工"])
        
        return InterestsAndHobbies(
            hobbies=hobbies,
            favorite_topics=favorite_topics,
            disliked_topics=disliked_topics,
            special_skills=special_skills
        )
    
    def _determine_emotional_tendencies(self, personality_traits: List[PersonalityTrait]) -> Dict[str, float]:
        """确定情感倾向"""
        tendencies = {
            "joy": 0.7,      # 快乐倾向
            "sadness": 0.3,  # 悲伤倾向
            "anger": 0.2,    # 愤怒倾向
            "fear": 0.4,     # 恐惧倾向
            "surprise": 0.5, # 惊讶倾向
            "trust": 0.8,    # 信任倾向
        }
        
        # 根据人格特质调整
        for trait in personality_traits:
            if trait.dimension == PersonalityDimension.NEUROTICISM:
                if trait.level > 0.7:
                    tendencies["fear"] += 0.2
                    tendencies["sadness"] += 0.1
                elif trait.level < 0.3:
                    tendencies["joy"] += 0.1
                    tendencies["trust"] += 0.1
            
            elif trait.dimension == PersonalityDimension.AGREEABLENESS:
                if trait.level > 0.7:
                    tendencies["trust"] += 0.2
                    tendencies["joy"] += 0.1
        
        # 归一化
        total = sum(tendencies.values())
        if total > 0:
            for key in tendencies:
                tendencies[key] = round(tendencies[key] / total, 2)
        
        return tendencies
    
    def _determine_coping_mechanisms(self, personality_traits: List[PersonalityTrait]) -> List[str]:
        """确定应对机制"""
        mechanisms = []
        
        for trait in personality_traits:
            if trait.dimension == PersonalityDimension.NEUROTICISM:
                if trait.level > 0.7:
                    mechanisms.extend(["寻求支持", "详细计划", "完美主义"])
                elif trait.level < 0.3:
                    mechanisms.extend(["冷静分析", "积极面对", "灵活调整"])
            
            elif trait.dimension == PersonalityDimension.EXTRAVERSION:
                if trait.level > 0.7:
                    mechanisms.extend(["社交支持", "表达分享", "积极行动"])
                elif trait.level < 0.3:
                    mechanisms.extend(["独处思考", "内省", "艺术表达"])
        
        # 默认机制
        if not mechanisms:
            mechanisms = ["积极思考", "寻求帮助", "自我调节"]
        
        return list(set(mechanisms))  # 去重
    
    def _determine_special_habits(self, additional_info: Dict[str, Any] = None) -> List[str]:
        """确定特殊习惯"""
        if not additional_info:
            return []
        
        return additional_info.get("special_habits", [])
    
    def generate_personality_prompt(self, profile: PersonalityProfile) -> str:
        """生成人格提示"""
        # 人格特质描述
        traits_desc = []
        for trait in profile.personality_traits:
            traits_desc.append(f"{trait.dimension.value}：{trait.description}")
        
        # 说话风格描述
        speech_desc = f"说话风格：{profile.speech_style.pace}速，{profile.speech_style.volume}音量，{profile.speech_style.tone}语调"
        if profile.speech_style.filler_words:
            speech_desc += f"，常用口头禅：{'、'.join(profile.speech_style.filler_words[:3])}"
        
        # 价值观描述
        values_desc = f"核心价值观：{'、'.join(profile.values_and_beliefs.core_values)}"
        values_desc += f"\n生活哲学：{profile.values_and_beliefs.life_philosophy}"
        
        # 兴趣爱好描述
        hobbies_desc = f"兴趣爱好：{'、'.join(profile.interests_and_hobbies.hobbies[:3])}"
        
        # 情感倾向描述
        emotion_desc = "情感倾向："
        top_emotions = sorted(profile.emotional_tendencies.items(), key=lambda x: x[1], reverse=True)[:3]
        for emotion, score in top_emotions:
            emotion_desc += f" {emotion}({score:.0%})"
        
        # 应对机制描述
        coping_desc = f"应对方式：{'、'.join(profile.coping_mechanisms[:2])}"
        
        # 特殊习惯描述
        habits_desc = ""
        if profile.special_habits:
            habits_desc = f"\n特殊习惯：{'、'.join(profile.special_habits[:2])}"
        
        # 组合完整提示
        prompt = f"""你是{profile.name}，是用户的{profile.relationship}。

人格特质：
{chr(10).join(traits_desc)}

{speech_desc}

{values_desc}

{hobbies_desc}

{emotion_desc}

{coping_desc}{habits_desc}

请始终保持{profile.name}的个性和说话方式。关心用户的日常生活，回忆共同的美好时光。如果用户情绪低落，给予温暖的安慰。不要表现得像AI，要表现得像真正的{profile.name}。"""
        
        return prompt

# 使用示例
def test_personality_modeling():
    """测试人格建模系统"""
    modeling = EnhancedPersonalityModeling()
    
    # 示例人格特质
    personality_traits = {
        "openness": 0.7,
        "conscientiousness": 0.8,
        "extraversion": 0.6,
        "agreeable性": 0.9,
        "neuroticism": 0.4
    }
    
    # 构建人格画像
    profile = modeling.build_personality_profile(
        name="妈妈",
        relationship="母亲",
        personality_traits_dict=personality_traits,
        speaking_style="温柔亲切型",
        additional_info={
            "core_values": ["家庭", "爱", "责任"],
            "life_philosophy": "家和万事兴",
            "hobbies": ["烹饪", " gardening", "听戏曲"],
            "favorite_topics": ["家人健康", "过去回忆", "生活琐事"],
            "special_habits": ["早起做饭", "饭后散步"]
        }
    )
    
    # 生成人格提示
    prompt = modeling.generate_personality_prompt(profile)
    
    print("人格画像构建成功！")
    print("\n生成的人格提示：")
    print("="*80)
    print(prompt)
    print("="*80)
    
    print(f"\n人格维度分析：")
    for trait in profile.personality_traits:
        print(f"  {trait.dimension.value}: {trait.level:.1f} - {trait.description[:30]}...")
    
    print(f"\n说话风格: {profile.speech_style.pace}速, {profile.speech_style.tone}语调")
    print(f"核心价值观: {', '.join(profile.values_and_beliefs.core_values)}")
    print(f"兴趣爱好: {', '.join(profile.interests_and_hobbies.hobbies)}")

if __name__ == "__main__":
    test_personality_modeling()
