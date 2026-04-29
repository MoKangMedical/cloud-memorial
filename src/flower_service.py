"""
Cloud Memorial — 虚拟献花
提供虚拟鲜花祭奠功能
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from config import load_json_data, FLOWER_MEANINGS


@dataclass
class Flower:
    """鲜花"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    placed_by: str = ""
    flower_type: str = ""  # chrysanthemum / lily / rose / carnation / forgetmenot / custom
    color: str = "white"
    quantity: int = 1
    message: str = ""
    arrangement: str = "bouquet"  # bouquet / wreath / single / basket
    placed_at: str = field(default_factory=lambda: datetime.now().isoformat())
    wilts_at: str = ""
    is_artificial: bool = False  # 是否假花（永不凋谢）
    like_count: int = 0

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class FlowerGarden:
    """花园（纪念馆的虚拟花园）"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    name: str = ""
    description: str = ""
    flower_count: int = 0
    unique_types: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class FlowerService:
    """虚拟献花服务"""

    def __init__(self):
        self.flowers: dict[str, Flower] = {}
        self.gardens: dict[str, FlowerGarden] = {}
        self.flower_types = load_json_data("flower-types.json")

    def place_flower(self, memorial_id: str, placed_by: str,
                     flower_type: str, color: str = "white",
                     quantity: int = 1, message: str = "",
                     arrangement: str = "bouquet",
                     is_artificial: bool = False) -> Flower:
        """献花"""
        flower = Flower(
            memorial_id=memorial_id,
            placed_by=placed_by,
            flower_type=flower_type,
            color=color,
            quantity=quantity,
            message=message,
            arrangement=arrangement,
            is_artificial=is_artificial,
        )
        if not is_artificial:
            from datetime import timedelta
            wilts = datetime.now() + timedelta(days=7)
            flower.wilts_at = wilts.isoformat()
        self.flowers[flower.id] = flower
        self._update_garden(memorial_id)
        return flower

    def get_active_flowers(self, memorial_id: str) -> list[Flower]:
        """获取未凋谢的鲜花"""
        now = datetime.now()
        active = []
        for f in self.flowers.values():
            if f.memorial_id != memorial_id:
                continue
            if f.is_artificial:
                active.append(f)
            elif f.wilts_at:
                wilts = datetime.fromisoformat(f.wilts_at)
                if now < wilts:
                    active.append(f)
        return active

    def get_all_flowers(self, memorial_id: str) -> list[Flower]:
        """获取所有鲜花（含已凋谢）"""
        return sorted(
            [f for f in self.flowers.values() if f.memorial_id == memorial_id],
            key=lambda f: f.placed_at, reverse=True,
        )

    def like_flower(self, flower_id: str) -> int:
        """点赞鲜花"""
        f = self.flowers.get(flower_id)
        if f:
            f.like_count += 1
            return f.like_count
        return 0

    def _update_garden(self, memorial_id: str):
        """更新花园信息"""
        garden = self.gardens.get(memorial_id)
        flowers = self.get_active_flowers(memorial_id)
        types = set(f.flower_type for f in flowers)
        if not garden:
            garden = FlowerGarden(
                memorial_id=memorial_id,
                name=f"{memorial_id}的花园",
            )
            self.gardens[memorial_id] = garden
        garden.flower_count = len(flowers)
        garden.unique_types = len(types)

    def get_garden(self, memorial_id: str) -> Optional[FlowerGarden]:
        """获取花园"""
        self._update_garden(memorial_id)
        return self.gardens.get(memorial_id)

    def get_flower_stats(self, memorial_id: str) -> dict:
        """获取献花统计"""
        all_flowers = self.get_all_flowers(memorial_id)
        active = self.get_active_flowers(memorial_id)
        type_count = {}
        for f in all_flowers:
            type_count[f.flower_type] = type_count.get(f.flower_type, 0) + 1
        return {
            "total_placed": len(all_flowers),
            "currently_active": len(active),
            "unique_types": len(set(f.flower_type for f in all_flowers)),
            "by_type": type_count,
            "total_likes": sum(f.like_count for f in all_flowers),
        }

    def get_flower_meaning(self, flower_type: str) -> str:
        """获取花语"""
        return FLOWER_MEANINGS.get(flower_type, "思念")

    def get_flower_types(self) -> list[dict]:
        """获取可用的鲜花类型"""
        if isinstance(self.flower_types, dict):
            return self.flower_types.get("flower_types", [])
        return self.flower_types

    def create_wreath(self, memorial_id: str, placed_by: str,
                      flowers: list[dict], message: str = "") -> list[Flower]:
        """创建花圈（多种花组合）"""
        result = []
        for f in flowers:
            flower = self.place_flower(
                memorial_id=memorial_id,
                placed_by=placed_by,
                flower_type=f.get("type", "chrysanthemum"),
                color=f.get("color", "white"),
                quantity=f.get("quantity", 1),
                message=message,
                arrangement="wreath",
            )
            result.append(flower)
        return result

    def cleanup_wilted(self, memorial_id: str) -> int:
        """清理已凋谢的花"""
        now = datetime.now()
        wilted_ids = []
        for f in self.flowers.values():
            if f.memorial_id != memorial_id:
                continue
            if not f.is_artificial and f.wilts_at:
                wilts = datetime.fromisoformat(f.wilts_at)
                if now >= wilts:
                    wilted_ids.append(f.id)
        for fid in wilted_ids:
            self.flowers.pop(fid, None)
        self._update_garden(memorial_id)
        return len(wilted_ids)
