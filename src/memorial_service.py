"""
纪念服务模块 (Memorial Service)
数字纪念堂创建、管理、虚拟祭扫、家族树
"""

import json
import logging
import hashlib
from typing import List, Dict, Optional
from dataclasses import dataclass, field
from pathlib import Path
from datetime import datetime

logger = logging.getLogger(__name__)

# ============================================================
# 数据模型
# ============================================================

@dataclass
class MemorialProfile:
    """纪念人物档案"""
    memorial_id: str
    name: str
    relation: str             # 关系：父亲、母亲、爷爷...
    birth_date: str
    death_date: str
    birthplace: str = ""
    occupation: str = ""
    photo_url: str = ""
    biography: str = ""
    personality_traits: List[str] = field(default_factory=list)
    catchphrases: List[str] = field(default_factory=list)
    created_by: str = ""
    created_at: str = ""
    privacy: str = "private"  # private | family | public

    def to_dict(self) -> Dict:
        return {
            "memorial_id": self.memorial_id,
            "name": self.name,
            "relation": self.relation,
            "birth_date": self.birth_date,
            "death_date": self.death_date,
            "birthplace": self.birthplace,
            "occupation": self.occupation,
            "photo_url": self.photo_url,
            "biography": self.biography,
            "personality_traits": self.personality_traits,
            "catchphrases": self.catchphrases,
            "created_by": self.created_by,
            "created_at": self.created_at,
            "privacy": self.privacy,
        }


@dataclass
class MemorialOffering:
    """虚拟祭品"""
    offering_id: str
    memorial_id: str
    user_name: str
    offering_type: str        # flower | candle | incense | food | message
    message: str = ""
    created_at: str = ""

    def to_dict(self) -> Dict:
        return {
            "offering_id": self.offering_id,
            "memorial_id": self.memorial_id,
            "user_name": self.user_name,
            "offering_type": self.offering_type,
            "message": self.message,
            "created_at": self.created_at,
        }


@dataclass
class FamilyTreeNode:
    """家族树节点"""
    node_id: str
    name: str
    relation: str
    generation: int           # 世代（0=本人，1=父母，-1=子女）
    parent_id: Optional[str] = None
    spouse_id: Optional[str] = None
    memorial_id: Optional[str] = None  # 关联纪念堂
    birth_year: Optional[int] = None
    death_year: Optional[int] = None
    photo_url: str = ""

    def to_dict(self) -> Dict:
        return {
            "node_id": self.node_id,
            "name": self.name,
            "relation": self.relation,
            "generation": self.generation,
            "parent_id": self.parent_id,
            "spouse_id": self.spouse_id,
            "memorial_id": self.memorial_id,
            "birth_year": self.birth_year,
            "death_year": self.death_year,
            "photo_url": self.photo_url,
        }


# ============================================================
# 纪念服务
# ============================================================

class MemorialService:
    """纪念堂管理服务"""

    OFFERING_ICONS = {
        "flower": "💐",
        "candle": "🕯️",
        "incense": "🪔",
        "food": "🍎",
        "message": "💌",
        "music": "🎵",
    }

    def __init__(self):
        self.memorials: Dict[str, MemorialProfile] = {}
        self.offerings: Dict[str, List[MemorialOffering]] = {}  # memorial_id -> offerings
        self.family_trees: Dict[str, List[FamilyTreeNode]] = {}  # user_id -> nodes
        logger.info("MemorialService 初始化完成")

    # ----------------------------------------------------------
    # 纪念堂 CRUD
    # ----------------------------------------------------------

    def create_memorial(self, profile: MemorialProfile) -> MemorialProfile:
        """创建纪念堂"""
        if not profile.memorial_id:
            profile.memorial_id = hashlib.md5(
                f"{profile.name}:{profile.birth_date}".encode()
            ).hexdigest()[:12]
        if not profile.created_at:
            profile.created_at = datetime.now().isoformat()

        self.memorials[profile.memorial_id] = profile
        self.offerings[profile.memorial_id] = []
        logger.info(f"纪念堂创建: {profile.name} ({profile.memorial_id})")
        return profile

    def get_memorial(self, memorial_id: str) -> Optional[MemorialProfile]:
        """获取纪念堂"""
        return self.memorials.get(memorial_id)

    def list_memorials(self, user_id: Optional[str] = None) -> List[MemorialProfile]:
        """列出纪念堂"""
        memorials = list(self.memorials.values())
        if user_id:
            memorials = [m for m in memorials if m.created_by == user_id]
        return memorials

    def update_memorial(self, memorial_id: str, updates: Dict) -> Optional[MemorialProfile]:
        """更新纪念堂"""
        memorial = self.memorials.get(memorial_id)
        if not memorial:
            return None
        for key, val in updates.items():
            if hasattr(memorial, key):
                setattr(memorial, key, val)
        return memorial

    def delete_memorial(self, memorial_id: str) -> bool:
        """删除纪念堂"""
        if memorial_id in self.memorials:
            del self.memorials[memorial_id]
            self.offerings.pop(memorial_id, None)
            return True
        return False

    # ----------------------------------------------------------
    # 虚拟祭扫
    # ----------------------------------------------------------

    def add_offering(self, memorial_id: str, user_name: str,
                     offering_type: str, message: str = "") -> Optional[MemorialOffering]:
        """添加虚拟祭品"""
        if memorial_id not in self.memorials:
            return None

        offering = MemorialOffering(
            offering_id=f"OFF-{len(self.offerings.get(memorial_id, [])) + 1:04d}",
            memorial_id=memorial_id,
            user_name=user_name,
            offering_type=offering_type,
            message=message,
            created_at=datetime.now().isoformat(),
        )
        self.offerings.setdefault(memorial_id, []).append(offering)
        logger.info(f"祭品添加: {user_name} -> {memorial_id} ({offering_type})")
        return offering

    def get_offerings(self, memorial_id: str) -> List[MemorialOffering]:
        """获取纪念堂所有祭品"""
        return self.offerings.get(memorial_id, [])

    def get_offering_stats(self, memorial_id: str) -> Dict:
        """祭品统计"""
        offerings = self.offerings.get(memorial_id, [])
        type_counts: Dict[str, int] = {}
        for o in offerings:
            type_counts[o.offering_type] = type_counts.get(o.offering_type, 0) + 1
        return {
            "total": len(offerings),
            "by_type": type_counts,
            "unique_visitors": len(set(o.user_name for o in offerings)),
        }

    # ----------------------------------------------------------
    # 家族树
    # ----------------------------------------------------------

    def create_family_tree(self, user_id: str) -> List[FamilyTreeNode]:
        """初始化家族树"""
        self.family_trees[user_id] = []
        return self.family_trees[user_id]

    def add_family_member(self, user_id: str, node: FamilyTreeNode) -> FamilyTreeNode:
        """添加家族成员"""
        if user_id not in self.family_trees:
            self.create_family_tree(user_id)

        if not node.node_id:
            node.node_id = hashlib.md5(
                f"{user_id}:{node.name}:{node.generation}".encode()
            ).hexdigest()[:10]

        self.family_trees[user_id].append(node)
        logger.info(f"家族成员添加: {node.name} (第{node.generation}代)")
        return node

    def get_family_tree(self, user_id: str) -> List[Dict]:
        """获取家族树（按世代排序）"""
        nodes = self.family_trees.get(user_id, [])
        sorted_nodes = sorted(nodes, key=lambda n: -n.generation)  # 长辈在前
        return [n.to_dict() for n in sorted_nodes]

    def link_memorial_to_tree(self, user_id: str, node_id: str,
                               memorial_id: str) -> bool:
        """将纪念堂关联到家族树节点"""
        nodes = self.family_trees.get(user_id, [])
        for n in nodes:
            if n.node_id == node_id:
                n.memorial_id = memorial_id
                return True
        return False

    # ----------------------------------------------------------
    # 纪念模板
    # ----------------------------------------------------------

    def load_templates(self, path: str) -> Dict:
        """加载纪念模板"""
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    def apply_template(self, memorial_id: str, template: Dict) -> None:
        """将模板应用到纪念堂"""
        memorial = self.memorials.get(memorial_id)
        if not memorial:
            return
        if "personality_traits" in template and not memorial.personality_traits:
            memorial.personality_traits = template["personality_traits"]
        if "catchphrases" in template and not memorial.catchphrases:
            memorial.catchphrases = template["catchphrases"]

    # ----------------------------------------------------------
    # 统计
    # ----------------------------------------------------------

    def statistics(self) -> Dict:
        """服务统计"""
        total_offerings = sum(len(v) for v in self.offerings.values())
        return {
            "total_memorials": len(self.memorials),
            "total_offerings": total_offerings,
            "total_family_trees": len(self.family_trees),
            "privacy_distribution": {
                p: sum(1 for m in self.memorials.values() if m.privacy == p)
                for p in ["private", "family", "public"]
            },
        }


# ============================================================
# CLI 入口
# ============================================================

def main():
    service = MemorialService()

    # 创建示例纪念堂
    profile = MemorialProfile(
        memorial_id="MEM-001",
        name="奶奶",
        relation="祖母",
        birth_date="1935-03-15",
        death_date="2023-08-20",
        birthplace="浙江绍兴",
        occupation="教师",
        personality_traits=["慈祥", "勤劳", "善良"],
        catchphrases=["孩子，吃饭了吗", "奶奶给你留了好吃的"],
        created_by="user-001",
    )
    service.create_memorial(profile)

    # 添加祭品
    service.add_offering("MEM-001", "小明", "flower", "奶奶，我很想您")
    service.add_offering("MEM-001", "小红", "candle", "")

    print(json.dumps(service.statistics(), ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
