"""
Cloud Memorial — 哀伤辅导
提供哀伤支持资源和心理辅导功能
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from config import load_json_data


@dataclass
class CounselorProfile:
    """心理咨询师"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    title: str = ""
    specialty: str = ""
    bio: str = ""
    contact_info: str = ""
    available: bool = True
    rating: float = 5.0
    consultation_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class GriefAssessment:
    """哀伤评估"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    memorial_id: str = ""
    score: int = 0  # 哀伤程度 0-100
    stage: str = ""  # denial / anger / bargaining / depression / acceptance
    answers: dict = field(default_factory=dict)
    recommendations: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class CounselingSession:
    """辅导会话"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    memorial_id: str = ""
    counselor_id: Optional[str] = None
    session_type: str = "ai"  # ai / human / self_help
    topic: str = ""
    notes: str = ""
    duration_minutes: int = 0
    mood_before: str = ""
    mood_after: str = ""
    satisfaction: int = 0  # 1-5
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


# 哀伤阶段说明
GRIEF_STAGES = {
    "denial": {
        "name": "否认",
        "description": "难以接受亲人离世的现实",
        "suggestions": [
            "允许自己慢慢接受",
            "与亲友分享感受",
            "不必强迫自己立刻面对",
        ]
    },
    "anger": {
        "name": "愤怒",
        "description": "对命运、疾病或自己感到愤怒",
        "suggestions": [
            "愤怒是正常的情绪反应",
            "找到安全的方式表达愤怒",
            "运动、写日记可以帮助释放",
        ]
    },
    "bargaining": {
        "name": "讨价还价",
        "description": "反复思考'如果当时...'的情景",
        "suggestions": [
            "不要过度自责",
            "接受无法改变的事实",
            "专注于当下能做的事",
        ]
    },
    "depression": {
        "name": "抑郁",
        "description": "感到深深的悲伤和空虚",
        "suggestions": [
            "允许自己悲伤",
            "保持基本的日常作息",
            "必要时寻求专业帮助",
        ]
    },
    "acceptance": {
        "name": "接受",
        "description": "逐渐接受现实，学会与失去共处",
        "suggestions": [
            "接受不等于遗忘",
            "找到纪念亲人的新方式",
            "重新发现生活的意义",
        ]
    },
}


class GriefCounselingService:
    """哀伤辅导服务"""

    def __init__(self):
        self.assessments: dict[str, GriefAssessment] = {}
        self.sessions: dict[str, CounselingSession] = {}
        self.counselors: dict[str, CounselorProfile] = {}
        self.resources = load_json_data("grief-resources.json")
        self._init_sample_counselors()

    def _init_sample_counselors(self):
        """初始化示例咨询师"""
        samples = [
            CounselorProfile(
                name="张医生",
                title="主任心理咨询师",
                specialty="丧亲哀伤、创伤后应激",
                bio="从事心理咨询20年，专注于丧亲辅导领域",
            ),
            CounselorProfile(
                name="李老师",
                title="心理治疗师",
                specialty="家庭哀伤、儿童心理",
                bio="擅长家庭系统治疗，帮助家庭成员共同度过哀伤",
            ),
        ]
        for c in samples:
            self.counselors[c.id] = c

    def take_assessment(self, user_id: str, memorial_id: str,
                        answers: dict) -> GriefAssessment:
        """进行哀伤评估"""
        # 简化评分逻辑
        score = min(100, sum(answers.values()) * 10) if answers else 50
        if score < 20:
            stage = "acceptance"
        elif score < 40:
            stage = "depression"
        elif score < 60:
            stage = "bargaining"
        elif score < 80:
            stage = "anger"
        else:
            stage = "denial"

        stage_info = GRIEF_STAGES.get(stage, {})
        assessment = GriefAssessment(
            user_id=user_id,
            memorial_id=memorial_id,
            score=score,
            stage=stage,
            answers=answers,
            recommendations=stage_info.get("suggestions", []),
        )
        self.assessments[assessment.id] = assessment
        return assessment

    def get_assessment(self, assessment_id: str) -> Optional[GriefAssessment]:
        """获取评估结果"""
        return self.assessments.get(assessment_id)

    def get_user_assessments(self, user_id: str) -> list[GriefAssessment]:
        """获取用户的所有评估"""
        return sorted(
            [a for a in self.assessments.values() if a.user_id == user_id],
            key=lambda a: a.created_at, reverse=True,
        )

    def start_session(self, user_id: str, memorial_id: str,
                      session_type: str = "ai", topic: str = "") -> CounselingSession:
        """开始辅导会话"""
        session = CounselingSession(
            user_id=user_id,
            memorial_id=memorial_id,
            session_type=session_type,
            topic=topic,
        )
        self.sessions[session.id] = session
        return session

    def end_session(self, session_id: str, notes: str = "",
                    mood_after: str = "",
                    satisfaction: int = 0) -> Optional[CounselingSession]:
        """结束辅导会话"""
        session = self.sessions.get(session_id)
        if session:
            session.notes = notes
            session.mood_after = mood_after
            session.satisfaction = satisfaction
            session.duration_minutes = int(
                (datetime.now() - datetime.fromisoformat(session.created_at)).total_seconds() / 60
            )
        return session

    def get_user_sessions(self, user_id: str) -> list[CounselingSession]:
        """获取用户的会话历史"""
        return sorted(
            [s for s in self.sessions.values() if s.user_id == user_id],
            key=lambda s: s.created_at, reverse=True,
        )

    def get_counselors(self, specialty: str = None) -> list[CounselorProfile]:
        """获取咨询师列表"""
        counselors = list(self.counselors.values())
        if specialty:
            counselors = [c for c in counselors if specialty in c.specialty]
        return counselors

    def get_grief_stage_info(self, stage: str) -> Optional[dict]:
        """获取哀伤阶段信息"""
        return GRIEF_STAGES.get(stage)

    def get_all_stages(self) -> dict:
        """获取所有哀伤阶段"""
        return GRIEF_STAGES

    def get_resources(self, category: str = None) -> list[dict]:
        """获取哀伤资源"""
        if isinstance(self.resources, dict):
            resource_list = self.resources.get("resources", [])
        else:
            resource_list = self.resources
        if category:
            return [r for r in resource_list if r.get("category") == category]
        return resource_list

    def get_ai_response(self, user_message: str, stage: str = "") -> str:
        """获取AI辅导回复（模拟）"""
        responses = {
            "denial": "我理解这很难接受。给自己一些时间，不必急着面对一切。",
            "anger": "你的愤怒是完全正常的。这种不公平感是哀伤的一部分。",
            "bargaining": "我们都会想'如果...'，但请不要苛责自己。你已经尽力了。",
            "depression": "悲伤是你对亲人爱的证明。允许自己感受这份悲伤，但也要照顾好自己。",
            "acceptance": "你正在学会与失去共处。这需要勇气，你做得很棒。",
        }
        if stage and stage in responses:
            return responses[stage]
        return "我在这里陪伴你。每个人的哀伤都是独特的，没有对错之分。你想聊聊吗？"

    def get_stats(self) -> dict:
        """获取服务统计"""
        return {
            "total_assessments": len(self.assessments),
            "total_sessions": len(self.sessions),
            "available_counselors": len([c for c in self.counselors.values() if c.available]),
        }
