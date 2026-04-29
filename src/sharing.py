"""
Cloud Memorial — 分享功能
纪念馆分享、社交媒体分享、链接分享
"""

import uuid
import hashlib
from datetime import datetime, timedelta
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class ShareLink:
    """分享链接"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    share_code: str = ""
    share_type: str = "public"  # public / private / password / temporary
    password: Optional[str] = None
    expires_at: Optional[str] = None
    max_visits: int = 0  # 0 = 无限
    visit_count: int = 0
    created_by: str = ""
    permissions: list[str] = field(default_factory=lambda: ["view"])  # view / comment / edit
    is_active: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ShareRecord:
    """分享记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    share_code: str = ""
    visitor_ip: str = ""
    visitor_name: str = ""
    visited_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class SharingService:
    """分享服务"""

    def __init__(self):
        self.share_links: dict[str, ShareLink] = {}
        self.share_records: list[ShareRecord] = []

    def _generate_code(self, memorial_id: str) -> str:
        """生成分享码"""
        raw = f"{memorial_id}-{datetime.now().isoformat()}-{uuid.uuid4()}"
        return hashlib.md5(raw.encode()).hexdigest()[:10]

    def create_share_link(self, memorial_id: str, created_by: str,
                          share_type: str = "public",
                          password: str = None,
                          expires_hours: int = 0,
                          max_visits: int = 0,
                          permissions: list = None) -> ShareLink:
        """创建分享链接"""
        link = ShareLink(
            memorial_id=memorial_id,
            share_code=self._generate_code(memorial_id),
            share_type=share_type,
            password=password,
            max_visits=max_visits,
            created_by=created_by,
            permissions=permissions or ["view"],
        )
        if expires_hours > 0:
            expires = datetime.now() + timedelta(hours=expires_hours)
            link.expires_at = expires.isoformat()
        if share_type == "password" and password:
            link.password = hashlib.sha256(password.encode()).hexdigest()
        self.share_links[link.share_code] = link
        return link

    def get_share_link(self, share_code: str) -> Optional[ShareLink]:
        """获取分享链接"""
        return self.share_links.get(share_code)

    def validate_access(self, share_code: str,
                        password: str = None) -> dict:
        """验证访问权限"""
        link = self.share_links.get(share_code)
        if not link:
            return {"valid": False, "reason": "链接不存在"}
        if not link.is_active:
            return {"valid": False, "reason": "链接已禁用"}
        if link.expires_at:
            expires = datetime.fromisoformat(link.expires_at)
            if datetime.now() > expires:
                return {"valid": False, "reason": "链接已过期"}
        if link.max_visits > 0 and link.visit_count >= link.max_visits:
            return {"valid": False, "reason": "访问次数已达上限"}
        if link.share_type == "password":
            if not password:
                return {"valid": False, "reason": "需要密码", "requires_password": True}
            hashed = hashlib.sha256(password.encode()).hexdigest()
            if hashed != link.password:
                return {"valid": False, "reason": "密码错误"}
        return {
            "valid": True,
            "memorial_id": link.memorial_id,
            "permissions": link.permissions,
        }

    def record_visit(self, share_code: str, visitor_ip: str = "",
                     visitor_name: str = "") -> bool:
        """记录访问"""
        link = self.share_links.get(share_code)
        if not link:
            return False
        link.visit_count += 1
        record = ShareRecord(
            memorial_id=link.memorial_id,
            share_code=share_code,
            visitor_ip=visitor_ip,
            visitor_name=visitor_name,
        )
        self.share_records.append(record)
        return True

    def get_memorial_links(self, memorial_id: str) -> list[ShareLink]:
        """获取纪念馆的所有分享链接"""
        return [
            l for l in self.share_links.values()
            if l.memorial_id == memorial_id
        ]

    def disable_link(self, share_code: str) -> bool:
        """禁用分享链接"""
        link = self.share_links.get(share_code)
        if link:
            link.is_active = False
            return True
        return False

    def enable_link(self, share_code: str) -> bool:
        """启用分享链接"""
        link = self.share_links.get(share_code)
        if link:
            link.is_active = True
            return True
        return False

    def delete_link(self, share_code: str) -> bool:
        """删除分享链接"""
        return self.share_links.pop(share_code, None) is not None

    def get_share_stats(self, memorial_id: str) -> dict:
        """获取分享统计"""
        links = self.get_memorial_links(memorial_id)
        records = [r for r in self.share_records if r.memorial_id == memorial_id]
        return {
            "total_links": len(links),
            "active_links": len([l for l in links if l.is_active]),
            "total_visits": len(records),
            "unique_visitors": len(set(r.visitor_ip for r in records if r.visitor_ip)),
            "by_type": {
                t: len([l for l in links if l.share_type == t])
                for t in set(l.share_type for l in links)
            },
        }

    def generate_social_share_text(self, memorial_id: str,
                                   deceased_name: str,
                                   platform: str = "wechat") -> str:
        """生成社交媒体分享文本"""
        templates = {
            "wechat": f"🌸 {deceased_name}的纪念馆 — 永远的思念\n在这里，我们可以一起回忆{deceased_name}的点点滴滴。\n🔗 {{link}}",
            "weibo": f"#云思园# 🌸 纪念{deceased_name} — {deceased_name}虽然离开了，但永远活在我们心里。🔗 {{link}}",
            "qq": f"🌸 {deceased_name}的纪念空间\n一起来看看{deceased_name}的故事吧~\n{{link}}",
        }
        return templates.get(platform, templates["wechat"]).format(
            link="https://memorial.example.com/m/" + memorial_id[:8]
        )
