"""
Cloud Memorial — 祈福服务
虚拟祈福、许愿、祈祷功能
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from config import load_json_data


@dataclass
class Prayer:
    """祈福"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    prayed_by: str = ""
    prayer_type: str = "blessing"  # blessing / wish / remembrance / gratitude
    content: str = ""
    template_id: Optional[str] = None
    candle_count: int = 1
    is_anonymous: bool = False
    like_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class PrayerWall:
    """祈福墙"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    prayer_ids: list[str] = field(default_factory=list)
    theme: str = "warm"  # warm / solemn / nature / stars
    max_display: int = 50

    def to_dict(self) -> dict:
        return asdict(self)


class PrayerService:
    """祈福服务"""

    def __init__(self):
        self.prayers: dict[str, Prayer] = {}
        self.walls: dict[str, PrayerWall] = {}
        self.templates = load_json_data("prayer-templates.json")

    def pray(self, memorial_id: str, prayed_by: str,
             content: str, prayer_type: str = "blessing",
             template_id: str = None,
             candle_count: int = 1,
             is_anonymous: bool = False) -> Prayer:
        """进行祈福"""
        prayer = Prayer(
            memorial_id=memorial_id,
            prayed_by=prayed_by,
            prayer_type=prayer_type,
            content=content,
            template_id=template_id,
            candle_count=candle_count,
            is_anonymous=is_anonymous,
        )
        self.prayers[prayer.id] = prayer
        # 自动添加到祈福墙
        wall = self.get_or_create_wall(memorial_id)
        wall.prayer_ids.append(prayer.id)
        return prayer

    def get_prayer(self, prayer_id: str) -> Optional[Prayer]:
        """获取祈福"""
        return self.prayers.get(prayer_id)

    def list_prayers(self, memorial_id: str, prayer_type: str = None) -> list[Prayer]:
        """列出祈福"""
        prayers = [p for p in self.prayers.values() if p.memorial_id == memorial_id]
        if prayer_type:
            prayers = [p for p in prayers if p.prayer_type == prayer_type]
        return sorted(prayers, key=lambda p: p.created_at, reverse=True)

    def like_prayer(self, prayer_id: str) -> int:
        """点赞祈福"""
        p = self.prayers.get(prayer_id)
        if p:
            p.like_count += 1
            return p.like_count
        return 0

    def get_or_create_wall(self, memorial_id: str) -> PrayerWall:
        """获取或创建祈福墙"""
        wall = self.walls.get(memorial_id)
        if not wall:
            wall = PrayerWall(memorial_id=memorial_id)
            self.walls[memorial_id] = wall
        return wall

    def get_wall_prayers(self, memorial_id: str, limit: int = 50) -> list[Prayer]:
        """获取祈福墙上的祈福"""
        wall = self.get_or_create_wall(memorial_id)
        prayers = []
        for pid in wall.prayer_ids[-limit:]:
            p = self.prayers.get(pid)
            if p:
                prayers.append(p)
        return prayers

    def get_templates(self, category: str = None) -> list[dict]:
        """获取祈福模板"""
        if isinstance(self.templates, dict):
            tpl_list = self.templates.get("prayer_templates", [])
        else:
            tpl_list = self.templates
        if category:
            return [t for t in tpl_list if t.get("category") == category]
        return tpl_list

    def fill_template(self, template_id: str, values: dict) -> Optional[str]:
        """填充祈福模板"""
        templates = self.get_templates()
        for t in templates:
            if t.get("id") == template_id:
                content = t.get("content", "")
                for key, value in values.items():
                    content = content.replace(f"{{{key}}}", value)
                return content
        return None

    def get_prayer_stats(self, memorial_id: str) -> dict:
        """获取祈福统计"""
        prayers = self.list_prayers(memorial_id)
        type_count = {}
        for p in prayers:
            type_count[p.prayer_type] = type_count.get(p.prayer_type, 0) + 1
        return {
            "total_prayers": len(prayers),
            "by_type": type_count,
            "total_candles": sum(p.candle_count for p in prayers),
            "total_likes": sum(p.like_count for p in prayers),
        }

    def get_recent_prayers(self, memorial_id: str, limit: int = 10) -> list[Prayer]:
        """获取最近的祈福"""
        return self.list_prayers(memorial_id)[:limit]

    def delete_prayer(self, prayer_id: str) -> bool:
        """删除祈福"""
        prayer = self.prayers.pop(prayer_id, None)
        if not prayer:
            return False
        # 从祈福墙移除
        wall = self.walls.get(prayer.memorial_id)
        if wall and prayer_id in wall.prayer_ids:
            wall.prayer_ids.remove(prayer_id)
        return True
