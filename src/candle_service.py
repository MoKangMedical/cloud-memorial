"""
Cloud Memorial — 虚拟祭扫
提供虚拟点蜡烛、祭扫场景等功能
"""

import uuid
import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from config import load_json_data, CANDLE_EFFECTS


@dataclass
class Candle:
    """蜡烛"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    lit_by: str = ""
    candle_type: str = "white"  # white / red / eternal / lotus / star
    message: str = ""
    duration_hours: int = 24
    lit_at: str = field(default_factory=lambda: datetime.now().isoformat())
    expires_at: str = ""
    is_eternal: bool = False
    like_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Offering:
    """祭品"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    offered_by: str = ""
    offering_type: str = ""  # fruit / wine / food / incense
    name: str = ""
    message: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class SweepRecord:
    """祭扫记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    visitor_name: str = ""
    visit_type: str = "virtual"  # virtual / onsite
    candles_lit: int = 0
    offerings_made: int = 0
    message: str = ""
    duration_minutes: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class CandleService:
    """虚拟祭扫服务"""

    def __init__(self):
        self.candles: dict[str, Candle] = {}
        self.offerings: dict[str, Offering] = {}
        self.sweep_records: dict[str, SweepRecord] = {}
        self.candle_types = load_json_data("candle-types.json")

    def light_candle(self, memorial_id: str, lit_by: str,
                     candle_type: str = "white", message: str = "",
                     is_eternal: bool = False) -> Candle:
        """点蜡烛"""
        candle = Candle(
            memorial_id=memorial_id,
            lit_by=lit_by,
            candle_type=candle_type,
            message=message,
            is_eternal=is_eternal,
        )
        if not is_eternal:
            from datetime import timedelta
            expires = datetime.now() + timedelta(hours=candle.duration_hours)
            candle.expires_at = expires.isoformat()
        self.candles[candle.id] = candle
        return candle

    def get_active_candles(self, memorial_id: str) -> list[Candle]:
        """获取纪念馆当前亮着的蜡烛"""
        now = datetime.now()
        active = []
        for c in self.candles.values():
            if c.memorial_id != memorial_id:
                continue
            if c.is_eternal:
                active.append(c)
            elif c.expires_at:
                expires = datetime.fromisoformat(c.expires_at)
                if now < expires:
                    active.append(c)
        return active

    def get_candle_count(self, memorial_id: str) -> int:
        """获取蜡烛总数"""
        return len([c for c in self.candles.values() if c.memorial_id == memorial_id])

    def like_candle(self, candle_id: str) -> int:
        """点赞蜡烛"""
        c = self.candles.get(candle_id)
        if c:
            c.like_count += 1
            return c.like_count
        return 0

    def place_offering(self, memorial_id: str, offered_by: str,
                       offering_type: str, name: str,
                       message: str = "") -> Offering:
        """放置祭品"""
        offering = Offering(
            memorial_id=memorial_id,
            offered_by=offered_by,
            offering_type=offering_type,
            name=name,
            message=message,
        )
        self.offerings[offering.id] = offering
        return offering

    def get_offerings(self, memorial_id: str) -> list[Offering]:
        """获取所有祭品"""
        return sorted(
            [o for o in self.offerings.values() if o.memorial_id == memorial_id],
            key=lambda o: o.created_at, reverse=True,
        )

    def record_sweep(self, memorial_id: str, visitor_name: str,
                     message: str = "", visit_type: str = "virtual") -> SweepRecord:
        """记录祭扫"""
        candles = self.get_active_candles(memorial_id)
        record = SweepRecord(
            memorial_id=memorial_id,
            visitor_name=visitor_name,
            visit_type=visit_type,
            candles_lit=len(candles),
            offerings_made=len(self.get_offerings(memorial_id)),
            message=message,
        )
        self.sweep_records[record.id] = record
        return record

    def get_sweep_history(self, memorial_id: str) -> list[SweepRecord]:
        """获取祭扫历史"""
        return sorted(
            [r for r in self.sweep_records.values() if r.memorial_id == memorial_id],
            key=lambda r: r.created_at, reverse=True,
        )

    def get_candle_types(self) -> list[dict]:
        """获取蜡烛类型列表"""
        if isinstance(self.candle_types, dict):
            return self.candle_types.get("candle_types", [])
        return self.candle_types

    def get_memorial_stats(self, memorial_id: str) -> dict:
        """获取纪念馆祭扫统计"""
        return {
            "total_candles": self.get_candle_count(memorial_id),
            "active_candles": len(self.get_active_candles(memorial_id)),
            "total_offerings": len(self.get_offerings(memorial_id)),
            "total_sweeps": len(self.get_sweep_history(memorial_id)),
        }
