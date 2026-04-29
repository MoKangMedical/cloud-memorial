"""
Cloud Memorial — AI 信件生成
生成写给逝者的信件、虚拟回信
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Letter:
    """信件"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    sender_name: str = ""
    recipient_name: str = ""
    title: str = ""
    content: str = ""
    letter_type: str = "to_deceased"  # to_deceased / ai_reply / memorial
    mood: str = ""  # 思念 / 感恩 / 告别 / 分享
    is_public: bool = False
    is_ai_generated: bool = False
    like_count: int = 0
    reply_to_id: Optional[str] = None
    tags: list[str] = field(default_factory=list)
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class LetterTemplate:
    """信件模板"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    category: str = ""  # 节日 / 生日 / 忌日 / 日常
    content_template: str = ""
    placeholders: list[str] = field(default_factory=list)
    tone: str = ""  # 温馨 / 庄重 / 轻松 / 深情

    def to_dict(self) -> dict:
        return asdict(self)


# 预设信件模板
DEFAULT_TEMPLATES = [
    LetterTemplate(
        name="清明节思念",
        category="节日",
        content_template="亲爱的{name}，又是一年清明时。{memory}。愿您在天堂安好，我们会永远记得您。",
        placeholders=["name", "memory"],
        tone="深情",
    ),
    LetterTemplate(
        name="生日祝福",
        category="生日",
        content_template="今天是您的生日，{name}。{wish}。虽然您不在身边，但我们从未忘记这个特别的日子。",
        placeholders=["name", "wish"],
        tone="温馨",
    ),
    LetterTemplate(
        name="日常思念",
        category="日常",
        content_template="{name}，今天{event}，让我想起了您。{feeling}。您一直活在我们心里。",
        placeholders=["name", "event", "feeling"],
        tone="温馨",
    ),
    LetterTemplate(
        name="告别信",
        category="告别",
        content_template="亲爱的{name}，这封信写了很久，一直不知道怎么寄出。{content}。愿您安息，我们终会再见。",
        placeholders=["name", "content"],
        tone="庄重",
    ),
    LetterTemplate(
        name="分享近况",
        category="日常",
        content_template="{name}，好久没跟您说话了。最近{news}。{feeling}。想您了。",
        placeholders=["name", "news", "feeling"],
        tone="轻松",
    ),
]


class LetterGeneratorService:
    """AI信件生成服务"""

    def __init__(self):
        self.letters: dict[str, Letter] = {}
        self.templates: list[LetterTemplate] = DEFAULT_TEMPLATES.copy()

    def send_letter(self, memorial_id: str, sender_name: str,
                    recipient_name: str, title: str, content: str,
                    mood: str = "", letter_type: str = "to_deceased",
                    is_public: bool = False,
                    tags: list = None) -> Letter:
        """发送信件"""
        letter = Letter(
            memorial_id=memorial_id,
            sender_name=sender_name,
            recipient_name=recipient_name,
            title=title,
            content=content,
            letter_type=letter_type,
            mood=mood,
            is_public=is_public,
            tags=tags or [],
        )
        self.letters[letter.id] = letter
        return letter

    def get_letter(self, letter_id: str) -> Optional[Letter]:
        """获取信件"""
        return self.letters.get(letter_id)

    def list_letters(self, memorial_id: str, letter_type: str = None,
                     mood: str = None) -> list[Letter]:
        """列出信件"""
        letters = [l for l in self.letters.values() if l.memorial_id == memorial_id]
        if letter_type:
            letters = [l for l in letters if l.letter_type == letter_type]
        if mood:
            letters = [l for l in letters if l.mood == mood]
        return sorted(letters, key=lambda l: l.created_at, reverse=True)

    def delete_letter(self, letter_id: str) -> bool:
        """删除信件"""
        return self.letters.pop(letter_id, None) is not None

    def like_letter(self, letter_id: str) -> int:
        """点赞信件"""
        letter = self.letters.get(letter_id)
        if letter:
            letter.like_count += 1
            return letter.like_count
        return 0

    def generate_ai_reply(self, letter_id: str,
                          deceased_name: str,
                          deceased_personality: str = "慈祥、温暖",
                          relationship: str = "亲人") -> Optional[Letter]:
        """AI 生成虚拟回信"""
        original = self.letters.get(letter_id)
        if not original:
            return None

        # 模拟 AI 生成回复（实际应调用 AI API）
        reply_content = (
            f"亲爱的{original.sender_name}，\n\n"
            f"收到你的来信，我非常感动。你说的{original.title}，我一直都记得。\n"
            f"看到你过得好，我就放心了。不要太牵挂我，好好生活就是对我最好的纪念。\n"
            f"我一直都在你身边，只是换了一种方式陪伴。\n\n"
            f"永远爱你的{deceased_name}"
        )

        reply = Letter(
            memorial_id=original.memorial_id,
            sender_name=deceased_name,
            recipient_name=original.sender_name,
            title=f"Re: {original.title}",
            content=reply_content,
            letter_type="ai_reply",
            mood=original.mood,
            is_ai_generated=True,
            reply_to_id=letter_id,
        )
        self.letters[reply.id] = reply
        return reply

    def get_templates(self, category: str = None) -> list[LetterTemplate]:
        """获取信件模板"""
        if category:
            return [t for t in self.templates if t.category == category]
        return self.templates

    def fill_template(self, template_id: str, values: dict) -> Optional[str]:
        """填充模板"""
        for t in self.templates:
            if t.id == template_id:
                content = t.content_template
                for placeholder in t.placeholders:
                    value = values.get(placeholder, f"[{placeholder}]")
                    content = content.replace(f"{{{placeholder}}}", value)
                return content
        return None

    def get_letter_stats(self, memorial_id: str) -> dict:
        """获取信件统计"""
        letters = self.list_letters(memorial_id)
        return {
            "total": len(letters),
            "by_type": {
                lt: len([l for l in letters if l.letter_type == lt])
                for lt in set(l.letter_type for l in letters)
            },
            "by_mood": {
                m: len([l for l in letters if l.mood == m])
                for m in set(l.mood for l in letters if l.mood)
            },
            "ai_replies": len([l for l in letters if l.is_ai_generated]),
            "total_likes": sum(l.like_count for l in letters),
        }
