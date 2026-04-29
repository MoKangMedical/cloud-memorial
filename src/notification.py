"""
Cloud Memorial — 通知提醒
管理各类通知和提醒
"""

import uuid
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class Notification:
    """通知"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    user_id: str = ""
    memorial_id: str = ""
    title: str = ""
    message: str = ""
    notification_type: str = "system"  # system / anniversary / prayer / share / candle / flower
    priority: str = "normal"  # low / normal / high / urgent
    is_read: bool = False
    action_url: str = ""
    action_label: str = ""
    channel: str = "app"  # app / email / sms / wechat / push
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    read_at: Optional[str] = None

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class NotificationPreference:
    """通知偏好设置"""
    user_id: str = ""
    anniversary_enabled: bool = True
    anniversary_days_before: int = 7
    prayer_enabled: bool = True
    share_enabled: bool = True
    candle_enabled: bool = True
    flower_enabled: bool = True
    system_enabled: bool = True
    quiet_hours_start: int = 22  # 免打扰开始（小时）
    quiet_hours_end: int = 8  # 免打扰结束（小时）
    channels: list[str] = field(default_factory=lambda: ["app"])

    def to_dict(self) -> dict:
        return asdict(self)


class NotificationService:
    """通知服务"""

    def __init__(self):
        self.notifications: dict[str, Notification] = {}
        self.preferences: dict[str, NotificationPreference] = {}

    def send_notification(self, user_id: str, title: str,
                          message: str, notification_type: str = "system",
                          memorial_id: str = "",
                          priority: str = "normal",
                          action_url: str = "",
                          action_label: str = "",
                          channel: str = "app") -> Notification:
        """发送通知"""
        # 检查免打扰
        pref = self.preferences.get(user_id)
        if pref:
            if not self._is_channel_enabled(pref, notification_type):
                return None
            if self._is_quiet_hours(pref):
                priority = "low"  # 免打扰时段降低优先级

        notification = Notification(
            user_id=user_id,
            memorial_id=memorial_id,
            title=title,
            message=message,
            notification_type=notification_type,
            priority=priority,
            action_url=action_url,
            action_label=action_label,
            channel=channel,
        )
        self.notifications[notification.id] = notification
        return notification

    def _is_channel_enabled(self, pref: NotificationPreference,
                            notification_type: str) -> bool:
        """检查通知渠道是否启用"""
        type_map = {
            "anniversary": pref.anniversary_enabled,
            "prayer": pref.prayer_enabled,
            "share": pref.share_enabled,
            "candle": pref.candle_enabled,
            "flower": pref.flower_enabled,
            "system": pref.system_enabled,
        }
        return type_map.get(notification_type, True)

    def _is_quiet_hours(self, pref: NotificationPreference) -> bool:
        """检查是否在免打扰时段"""
        hour = datetime.now().hour
        if pref.quiet_hours_start > pref.quiet_hours_end:
            return hour >= pref.quiet_hours_start or hour < pref.quiet_hours_end
        return pref.quiet_hours_start <= hour < pref.quiet_hours_end

    def get_notifications(self, user_id: str, is_read: bool = None,
                          notification_type: str = None,
                          limit: int = 50) -> list[Notification]:
        """获取通知列表"""
        notifs = [n for n in self.notifications.values() if n.user_id == user_id]
        if is_read is not None:
            notifs = [n for n in notifs if n.is_read == is_read]
        if notification_type:
            notifs = [n for n in notifs if n.notification_type == notification_type]
        return sorted(notifs, key=lambda n: n.created_at, reverse=True)[:limit]

    def get_unread_count(self, user_id: str) -> int:
        """获取未读通知数"""
        return len([n for n in self.notifications.values()
                    if n.user_id == user_id and not n.is_read])

    def mark_as_read(self, notification_id: str) -> bool:
        """标记通知为已读"""
        n = self.notifications.get(notification_id)
        if n:
            n.is_read = True
            n.read_at = datetime.now().isoformat()
            return True
        return False

    def mark_all_read(self, user_id: str) -> int:
        """标记所有通知为已读"""
        count = 0
        for n in self.notifications.values():
            if n.user_id == user_id and not n.is_read:
                n.is_read = True
                n.read_at = datetime.now().isoformat()
                count += 1
        return count

    def delete_notification(self, notification_id: str) -> bool:
        """删除通知"""
        return self.notifications.pop(notification_id, None) is not None

    def clear_old_notifications(self, user_id: str, days: int = 30) -> int:
        """清理旧通知"""
        cutoff = (datetime.now() - timedelta(days=days)).isoformat()
        old_ids = [
            n.id for n in self.notifications.values()
            if n.user_id == user_id and n.created_at < cutoff
        ]
        for nid in old_ids:
            self.notifications.pop(nid, None)
        return len(old_ids)

    def set_preference(self, user_id: str, **kwargs) -> NotificationPreference:
        """设置通知偏好"""
        pref = self.preferences.get(user_id)
        if not pref:
            pref = NotificationPreference(user_id=user_id)
            self.preferences[user_id] = pref
        for key, value in kwargs.items():
            if hasattr(pref, key):
                setattr(pref, key, value)
        return pref

    def get_preference(self, user_id: str) -> NotificationPreference:
        """获取通知偏好"""
        if user_id not in self.preferences:
            self.preferences[user_id] = NotificationPreference(user_id=user_id)
        return self.preferences[user_id]

    def send_anniversary_reminder(self, user_id: str, memorial_id: str,
                                  anniversary_title: str,
                                  days_until: int) -> Notification:
        """发送纪念日提醒"""
        if days_until == 0:
            message = f"今天是{anniversary_title}，记得纪念。"
        else:
            message = f"{anniversary_title}将在{days_until}天后到来。"
        return self.send_notification(
            user_id=user_id,
            title=f"纪念日提醒",
            message=message,
            notification_type="anniversary",
            memorial_id=memorial_id,
            priority="high" if days_until <= 1 else "normal",
        )

    def send_prayer_notification(self, user_id: str, memorial_id: str,
                                 prayer_by: str) -> Notification:
        """发送祈福通知"""
        return self.send_notification(
            user_id=user_id,
            title="有人为您的纪念馆祈福",
            message=f"{prayer_by}为您的纪念馆送上了祝福。",
            notification_type="prayer",
            memorial_id=memorial_id,
        )

    def send_share_notification(self, user_id: str, memorial_id: str,
                                visitor_name: str) -> Notification:
        """发送分享访问通知"""
        return self.send_notification(
            user_id=user_id,
            title="纪念馆有新的访问",
            message=f"{visitor_name}访问了您的纪念馆。",
            notification_type="share",
            memorial_id=memorial_id,
        )

    def get_stats(self, user_id: str) -> dict:
        """获取通知统计"""
        notifs = self.get_notifications(user_id, limit=9999)
        return {
            "total": len(notifs),
            "unread": self.get_unread_count(user_id),
            "by_type": {
                t: len([n for n in notifs if n.notification_type == t])
                for t in set(n.notification_type for n in notifs)
            },
        }
