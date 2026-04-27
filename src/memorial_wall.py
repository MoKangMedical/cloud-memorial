"""
Cloud Memorial — 纪念墙
公共纪念墙、留言墙功能
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class WallMessage:
    """纪念墙留言"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    wall_type: str = "memorial"  # memorial / prayer / memory / public
    author_name: str = ""
    author_avatar: str = ""
    content: str = ""
    message_type: str = "text"  # text / image / video / audio / candle
    media_url: str = ""
    position_x: float = 0.0
    position_y: float = 0.0
    color: str = "#8b5e3c"
    font_size: int = 14
    is_pinned: bool = False
    is_anonymous: bool = False
    like_count: int = 0
    reply_to_id: Optional[str] = None
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class MemorialWall:
    """纪念墙"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    name: str = ""
    description: str = ""
    wall_type: str = "memorial"  # memorial / prayer / public
    theme: str = "classic"  # classic / modern / nature / night_sky
    background_url: str = ""
    max_messages: int = 1000
    message_count: int = 0
    is_public: bool = True
    allow_anonymous: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class MemorialWallService:
    """纪念墙服务"""

    def __init__(self):
        self.walls: dict[str, MemorialWall] = {}
        self.messages: dict[str, WallMessage] = {}

    def create_wall(self, memorial_id: str, name: str,
                    description: str = "", wall_type: str = "memorial",
                    theme: str = "classic",
                    is_public: bool = True) -> MemorialWall:
        """创建纪念墙"""
        wall = MemorialWall(
            memorial_id=memorial_id,
            name=name,
            description=description,
            wall_type=wall_type,
            theme=theme,
            is_public=is_public,
        )
        self.walls[wall.id] = wall
        return wall

    def get_wall(self, wall_id: str) -> Optional[MemorialWall]:
        """获取纪念墙"""
        return self.walls.get(wall_id)

    def get_memorial_walls(self, memorial_id: str) -> list[MemorialWall]:
        """获取纪念馆的所有纪念墙"""
        return [w for w in self.walls.values() if w.memorial_id == memorial_id]

    def update_wall(self, wall_id: str, **kwargs) -> Optional[MemorialWall]:
        """更新纪念墙"""
        wall = self.walls.get(wall_id)
        if not wall:
            return None
        for key, value in kwargs.items():
            if hasattr(wall, key):
                setattr(wall, key, value)
        return wall

    def delete_wall(self, wall_id: str) -> bool:
        """删除纪念墙"""
        if wall_id not in self.walls:
            return False
        # 删除所有留言
        msg_ids = [m.id for m in self.messages.values() if m.memorial_id == wall_id]
        for mid in msg_ids:
            self.messages.pop(mid, None)
        self.walls.pop(wall_id, None)
        return True

    def leave_message(self, wall_id: str, author_name: str,
                      content: str, message_type: str = "text",
                      media_url: str = "", color: str = "#8b5e3c",
                      is_anonymous: bool = False,
                      position_x: float = 0, position_y: float = 0) -> Optional[WallMessage]:
        """在纪念墙留言"""
        wall = self.walls.get(wall_id)
        if not wall:
            return None
        if not wall.allow_anonymous and is_anonymous:
            return None
        msg = WallMessage(
            memorial_id=wall_id,
            wall_type=wall.wall_type,
            author_name="匿名" if is_anonymous else author_name,
            content=content,
            message_type=message_type,
            media_url=media_url,
            color=color,
            position_x=position_x,
            position_y=position_y,
            is_anonymous=is_anonymous,
        )
        self.messages[msg.id] = msg
        wall.message_count = len([m for m in self.messages.values() if m.memorial_id == wall_id])
        return msg

    def get_messages(self, wall_id: str, limit: int = 50,
                     offset: int = 0) -> list[WallMessage]:
        """获取纪念墙留言"""
        msgs = sorted(
            [m for m in self.messages.values() if m.memorial_id == wall_id],
            key=lambda m: m.created_at, reverse=True,
        )
        # 固定置顶消息
        pinned = [m for m in msgs if m.is_pinned]
        regular = [m for m in msgs if not m.is_pinned]
        return (pinned + regular)[offset:offset + limit]

    def like_message(self, msg_id: str) -> int:
        """点赞留言"""
        msg = self.messages.get(msg_id)
        if msg:
            msg.like_count += 1
            return msg.like_count
        return 0

    def pin_message(self, msg_id: str) -> bool:
        """置顶留言"""
        msg = self.messages.get(msg_id)
        if msg:
            msg.is_pinned = True
            return True
        return False

    def unpin_message(self, msg_id: str) -> bool:
        """取消置顶"""
        msg = self.messages.get(msg_id)
        if msg:
            msg.is_pinned = False
            return True
        return False

    def reply_to_message(self, msg_id: str, author_name: str,
                         content: str) -> Optional[WallMessage]:
        """回复留言"""
        original = self.messages.get(msg_id)
        if not original:
            return None
        return self.leave_message(
            wall_id=original.memorial_id,
            author_name=author_name,
            content=content,
            position_x=original.position_x + 20,
            position_y=original.position_y + 20,
        )

    def delete_message(self, msg_id: str) -> bool:
        """删除留言"""
        return self.messages.pop(msg_id, None) is not None

    def search_messages(self, wall_id: str, keyword: str) -> list[WallMessage]:
        """搜索留言"""
        keyword_lower = keyword.lower()
        return [
            m for m in self.get_messages(wall_id, limit=9999)
            if keyword_lower in m.content.lower()
            or keyword_lower in m.author_name.lower()
        ]

    def get_wall_stats(self, wall_id: str) -> dict:
        """获取纪念墙统计"""
        msgs = [m for m in self.messages.values() if m.memorial_id == wall_id]
        return {
            "total_messages": len(msgs),
            "pinned": len([m for m in msgs if m.is_pinned]),
            "total_likes": sum(m.like_count for m in msgs),
            "by_type": {
                t: len([m for m in msgs if m.message_type == t])
                for t in set(m.message_type for m in msgs)
            },
        }
