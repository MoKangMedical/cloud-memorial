"""
Cloud Memorial — 家族树管理
构建和维护家族谱系关系图
"""

import json
import uuid
from datetime import datetime, date
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class FamilyMember:
    """家族成员"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    name: str = ""
    gender: str = ""  # male / female / unknown
    birth_date: Optional[str] = None
    death_date: Optional[str] = None
    birth_place: str = ""
    photo_url: str = ""
    bio: str = ""
    generation: int = 0  # 世代编号，0为根节点
    parent_id: Optional[str] = None
    spouse_id: Optional[str] = None
    is_alive: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class FamilyTree:
    """家族树管理器"""

    def __init__(self, tree_id: str = None, family_name: str = ""):
        self.tree_id = tree_id or str(uuid.uuid4())[:12]
        self.family_name = family_name
        self.members: dict[str, FamilyMember] = {}
        self.root_id: Optional[str] = None
        self.created_at = datetime.now().isoformat()
        self.updated_at = self.created_at

    def add_member(self, member: FamilyMember, parent_id: str = None) -> str:
        """添加家族成员"""
        if parent_id:
            member.parent_id = parent_id
            parent = self.members.get(parent_id)
            if parent:
                member.generation = parent.generation + 1
        self.members[member.id] = member
        if self.root_id is None:
            self.root_id = member.id
        self.updated_at = datetime.now().isoformat()
        return member.id

    def remove_member(self, member_id: str) -> bool:
        """移除家族成员（级联移除后代）"""
        if member_id not in self.members:
            return False
        # 找到所有后代
        descendants = self._get_descendants(member_id)
        for did in descendants:
            self.members.pop(did, None)
        self.members.pop(member_id, None)
        if self.root_id == member_id:
            self.root_id = None
        self.updated_at = datetime.now().isoformat()
        return True

    def _get_descendants(self, member_id: str) -> list[str]:
        """获取所有后代ID"""
        result = []
        for mid, m in self.members.items():
            if m.parent_id == member_id:
                result.append(mid)
                result.extend(self._get_descendants(mid))
        return result

    def get_children(self, member_id: str) -> list[FamilyMember]:
        """获取子女"""
        return [m for m in self.members.values() if m.parent_id == member_id]

    def get_siblings(self, member_id: str) -> list[FamilyMember]:
        """获取兄弟姐妹"""
        member = self.members.get(member_id)
        if not member or not member.parent_id:
            return []
        return [
            m for m in self.members.values()
            if m.parent_id == member.parent_id and m.id != member_id
        ]

    def get_spouse(self, member_id: str) -> Optional[FamilyMember]:
        """获取配偶"""
        member = self.members.get(member_id)
        if member and member.spouse_id:
            return self.members.get(member.spouse_id)
        return None

    def get_ancestors(self, member_id: str) -> list[FamilyMember]:
        """获取祖先链"""
        ancestors = []
        member = self.members.get(member_id)
        while member and member.parent_id:
            parent = self.members.get(member.parent_id)
            if parent:
                ancestors.append(parent)
                member = parent
            else:
                break
        return ancestors

    def get_generation(self, gen: int) -> list[FamilyMember]:
        """获取指定世代的所有成员"""
        return [m for m in self.members.values() if m.generation == gen]

    def get_tree_depth(self) -> int:
        """获取树的深度"""
        if not self.members:
            return 0
        return max(m.generation for m in self.members.values()) + 1

    def to_dict(self) -> dict:
        """导出为字典"""
        return {
            "tree_id": self.tree_id,
            "family_name": self.family_name,
            "root_id": self.root_id,
            "members": {mid: m.to_dict() for mid, m in self.members.items()},
            "created_at": self.created_at,
            "updated_at": self.updated_at,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "FamilyTree":
        """从字典恢复"""
        tree = cls(tree_id=data["tree_id"], family_name=data.get("family_name", ""))
        tree.root_id = data.get("root_id")
        tree.created_at = data.get("created_at", "")
        tree.updated_at = data.get("updated_at", "")
        for mid, mdata in data.get("members", {}).items():
            tree.members[mid] = FamilyMember(**mdata)
        return tree

    def generate_mermaid(self) -> str:
        """生成 Mermaid 流程图语法"""
        lines = ["graph TD"]
        for mid, m in self.members.items():
            label = f"{m.name}"
            if not m.is_alive:
                label += " †"
            lines.append(f"    {mid}[\"{label}\"]")
        for mid, m in self.members.items():
            if m.parent_id and m.parent_id in self.members:
                lines.append(f"    {m.parent_id} --> {mid}")
            if m.spouse_id and m.spouse_id in self.members:
                lines.append(f"    {mid} ---|配偶| {m.spouse_id}")
        return "\n".join(lines)


class FamilyTreeManager:
    """家族树管理服务"""

    def __init__(self):
        self.trees: dict[str, FamilyTree] = {}

    def create_tree(self, family_name: str) -> FamilyTree:
        """创建新的家族树"""
        tree = FamilyTree(family_name=family_name)
        self.trees[tree.tree_id] = tree
        return tree

    def get_tree(self, tree_id: str) -> Optional[FamilyTree]:
        """获取家族树"""
        return self.trees.get(tree_id)

    def list_trees(self) -> list[dict]:
        """列出所有家族树"""
        return [
            {"tree_id": t.tree_id, "family_name": t.family_name,
             "member_count": len(t.members), "depth": t.get_tree_depth()}
            for t in self.trees.values()
        ]

    def delete_tree(self, tree_id: str) -> bool:
        """删除家族树"""
        return self.trees.pop(tree_id, None) is not None

    def export_tree(self, tree_id: str) -> Optional[str]:
        """导出为JSON"""
        tree = self.get_tree(tree_id)
        if tree:
            return json.dumps(tree.to_dict(), ensure_ascii=False, indent=2)
        return None

    def import_tree(self, json_str: str) -> Optional[FamilyTree]:
        """从JSON导入"""
        try:
            data = json.loads(json_str)
            tree = FamilyTree.from_dict(data)
            self.trees[tree.tree_id] = tree
            return tree
        except (json.JSONDecodeError, KeyError):
            return None
