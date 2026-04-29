"""
Cloud Memorial — 纪念日提醒
管理逝者忌日、生日、重要纪念日的提醒
"""

import uuid
from datetime import datetime, date, timedelta
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Anniversary:
    """纪念日"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    title: str = ""
    date: str = ""  # MM-DD 格式（每年重复）或 YYYY-MM-DD（一次性）
    year: Optional[int] = None  # 如果有年份则为一次性，否则每年重复
    category: str = "other"  # birthday / death_anniversary / holiday / custom / other
    description: str = ""
    reminder_days_before: int = 7  # 提前几天提醒
    is_lunar: bool = False  # 是否农历
    is_recurring: bool = True
    notification_sent: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Reminder:
    """提醒记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    anniversary_id: str = ""
    memorial_id: str = ""
    title: str = ""
    message: str = ""
    remind_date: str = ""
    is_sent: bool = False
    channel: str = "app"  # app / email / sms / wechat
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class AnniversaryService:
    """纪念日提醒服务"""

    def __init__(self):
        self.anniversaries: dict[str, Anniversary] = {}
        self.reminders: dict[str, Reminder] = {}

    def add_anniversary(self, memorial_id: str, title: str,
                        date_str: str, category: str = "other",
                        description: str = "",
                        reminder_days: int = 7,
                        is_lunar: bool = False,
                        is_recurring: bool = True,
                        year: int = None) -> Anniversary:
        """添加纪念日"""
        ann = Anniversary(
            memorial_id=memorial_id,
            title=title,
            date=date_str,
            year=year,
            category=category,
            description=description,
            reminder_days_before=reminder_days,
            is_lunar=is_lunar,
            is_recurring=is_recurring,
        )
        self.anniversaries[ann.id] = ann
        return ann

    def get_anniversary(self, ann_id: str) -> Optional[Anniversary]:
        """获取纪念日"""
        return self.anniversaries.get(ann_id)

    def list_anniversaries(self, memorial_id: str, category: str = None) -> list[Anniversary]:
        """列出纪念日"""
        anns = [a for a in self.anniversaries.values() if a.memorial_id == memorial_id]
        if category:
            anns = [a for a in anns if a.category == category]
        return sorted(anns, key=lambda a: a.date)

    def update_anniversary(self, ann_id: str, **kwargs) -> Optional[Anniversary]:
        """更新纪念日"""
        ann = self.anniversaries.get(ann_id)
        if not ann:
            return None
        for key, value in kwargs.items():
            if hasattr(ann, key):
                setattr(ann, key, value)
        return ann

    def delete_anniversary(self, ann_id: str) -> bool:
        """删除纪念日"""
        return self.anniversaries.pop(ann_id, None) is not None

    def get_upcoming(self, memorial_id: str, days: int = 30) -> list[dict]:
        """获取未来 N 天内的纪念日"""
        today = date.today()
        upcoming = []
        for ann in self.anniversaries.values():
            if ann.memorial_id != memorial_id:
                continue
            try:
                mm, dd = map(int, ann.date.split("-")[:2])
                this_year = date(today.year, mm, dd)
                if this_year < today:
                    this_year = date(today.year + 1, mm, dd)
                delta = (this_year - today).days
                if 0 <= delta <= days:
                    upcoming.append({
                        "anniversary": ann.to_dict(),
                        "days_until": delta,
                        "date": this_year.isoformat(),
                    })
            except (ValueError, IndexError):
                continue
        return sorted(upcoming, key=lambda x: x["days_until"])

    def generate_reminders(self, memorial_id: str) -> list[Reminder]:
        """生成未来提醒"""
        today = date.today()
        new_reminders = []
        for ann in self.anniversaries.values():
            if ann.memorial_id != memorial_id:
                continue
            try:
                mm, dd = map(int, ann.date.split("-")[:2])
                this_year = date(today.year, mm, dd)
                if this_year < today:
                    this_year = date(today.year + 1, mm, dd)
                remind_date = this_year - timedelta(days=ann.reminder_days_before)
                if remind_date < today:
                    remind_date = today
                # 检查是否已存在
                existing = [
                    r for r in self.reminders.values()
                    if r.anniversary_id == ann.id and r.remind_date == remind_date.isoformat()
                ]
                if not existing:
                    reminder = Reminder(
                        anniversary_id=ann.id,
                        memorial_id=memorial_id,
                        title=f"纪念日提醒：{ann.title}",
                        message=f"{ann.title} 将在 {(this_year - remind_date).days} 天后到来（{this_year.isoformat()}）",
                        remind_date=remind_date.isoformat(),
                    )
                    self.reminders[reminder.id] = reminder
                    new_reminders.append(reminder)
            except (ValueError, IndexError):
                continue
        return new_reminders

    def get_pending_reminders(self, memorial_id: str) -> list[Reminder]:
        """获取待发送的提醒"""
        today_str = date.today().isoformat()
        return [
            r for r in self.reminders.values()
            if r.memorial_id == memorial_id
            and not r.is_sent
            and r.remind_date <= today_str
        ]

    def mark_reminder_sent(self, reminder_id: str) -> bool:
        """标记提醒已发送"""
        r = self.reminders.get(reminder_id)
        if r:
            r.is_sent = True
            return True
        return False

    def get_calendar_view(self, memorial_id: str, year: int) -> dict[str, list[dict]]:
        """获取日历视图"""
        calendar = {}
        for ann in self.anniversaries.values():
            if ann.memorial_id != memorial_id:
                continue
            try:
                mm, dd = map(int, ann.date.split("-")[:2])
                key = f"{year:04d}-{mm:02d}-{dd:02d}"
                calendar.setdefault(key, []).append({
                    "title": ann.title,
                    "category": ann.category,
                    "description": ann.description,
                })
            except (ValueError, IndexError):
                continue
        return calendar

    def get_stats(self, memorial_id: str) -> dict:
        """获取统计信息"""
        anns = self.list_anniversaries(memorial_id)
        return {
            "total": len(anns),
            "by_category": {
                cat: len([a for a in anns if a.category == cat])
                for cat in set(a.category for a in anns)
            },
            "recurring": len([a for a in anns if a.is_recurring]),
            "one_time": len([a for a in anns if not a.is_recurring]),
        }
