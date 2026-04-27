"""
Cloud Memorial — 相册管理
管理逝者照片、相册、图片回忆
"""

import uuid
import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path


@dataclass
class Photo:
    """照片"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    album_id: str = ""
    file_path: str = ""
    thumbnail_path: str = ""
    title: str = ""
    description: str = ""
    date_taken: Optional[str] = None
    location: str = ""
    people: list[str] = field(default_factory=list)  # 照片中的人物
    tags: list[str] = field(default_factory=list)
    is_cover: bool = False
    width: int = 0
    height: int = 0
    file_size_kb: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class Album:
    """相册"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""  # 关联的纪念馆
    title: str = ""
    description: str = ""
    cover_photo_id: Optional[str] = None
    photo_count: int = 0
    is_public: bool = True
    sort_order: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())
    updated_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class PhotoAlbumManager:
    """相册管理服务"""

    def __init__(self):
        self.albums: dict[str, Album] = {}
        self.photos: dict[str, Photo] = {}

    # ---- 相册操作 ----

    def create_album(self, memorial_id: str, title: str, description: str = "") -> Album:
        """创建相册"""
        album = Album(memorial_id=memorial_id, title=title, description=description)
        self.albums[album.id] = album
        return album

    def get_album(self, album_id: str) -> Optional[Album]:
        """获取相册"""
        return self.albums.get(album_id)

    def list_albums(self, memorial_id: str) -> list[Album]:
        """列出某纪念馆的所有相册"""
        return sorted(
            [a for a in self.albums.values() if a.memorial_id == memorial_id],
            key=lambda a: a.sort_order
        )

    def update_album(self, album_id: str, **kwargs) -> Optional[Album]:
        """更新相册信息"""
        album = self.albums.get(album_id)
        if not album:
            return None
        for key, value in kwargs.items():
            if hasattr(album, key):
                setattr(album, key, value)
        album.updated_at = datetime.now().isoformat()
        return album

    def delete_album(self, album_id: str) -> bool:
        """删除相册（同时删除照片）"""
        if album_id not in self.albums:
            return False
        # 删除相册内所有照片
        photo_ids = [p.id for p in self.photos.values() if p.album_id == album_id]
        for pid in photo_ids:
            self.photos.pop(pid, None)
        self.albums.pop(album_id, None)
        return True

    # ---- 照片操作 ----

    def add_photo(self, album_id: str, file_path: str, title: str = "",
                  description: str = "", date_taken: str = None,
                  location: str = "", people: list = None,
                  tags: list = None) -> Optional[Photo]:
        """添加照片到相册"""
        if album_id not in self.albums:
            return None
        photo = Photo(
            album_id=album_id,
            file_path=file_path,
            title=title,
            description=description,
            date_taken=date_taken,
            location=location,
            people=people or [],
            tags=tags or [],
        )
        self.photos[photo.id] = photo
        # 更新相册计数
        album = self.albums[album_id]
        album.photo_count = sum(1 for p in self.photos.values() if p.album_id == album_id)
        if not album.cover_photo_id:
            album.cover_photo_id = photo.id
            photo.is_cover = True
        album.updated_at = datetime.now().isoformat()
        return photo

    def get_photo(self, photo_id: str) -> Optional[Photo]:
        """获取照片"""
        return self.photos.get(photo_id)

    def list_photos(self, album_id: str) -> list[Photo]:
        """列出相册中的所有照片"""
        return sorted(
            [p for p in self.photos.values() if p.album_id == album_id],
            key=lambda p: p.date_taken or p.created_at
        )

    def delete_photo(self, photo_id: str) -> bool:
        """删除照片"""
        photo = self.photos.pop(photo_id, None)
        if not photo:
            return False
        # 更新相册计数
        album = self.albums.get(photo.album_id)
        if album:
            album.photo_count = sum(1 for p in self.photos.values() if p.album_id == photo.album_id)
            if album.cover_photo_id == photo_id:
                remaining = self.list_photos(photo.album_id)
                album.cover_photo_id = remaining[0].id if remaining else None
        return True

    def set_cover(self, album_id: str, photo_id: str) -> bool:
        """设置相册封面"""
        album = self.albums.get(album_id)
        photo = self.photos.get(photo_id)
        if not album or not photo or photo.album_id != album_id:
            return False
        # 取消旧封面
        for p in self.photos.values():
            if p.album_id == album_id:
                p.is_cover = False
        photo.is_cover = True
        album.cover_photo_id = photo_id
        return True

    def search_photos(self, memorial_id: str, keyword: str) -> list[Photo]:
        """搜索照片"""
        album_ids = {a.id for a in self.albums.values() if a.memorial_id == memorial_id}
        results = []
        for p in self.photos.values():
            if p.album_id not in album_ids:
                continue
            keyword_lower = keyword.lower()
            if (keyword_lower in p.title.lower() or
                keyword_lower in p.description.lower() or
                keyword_lower in " ".join(p.tags).lower() or
                keyword_lower in " ".join(p.people).lower()):
                results.append(p)
        return results

    def get_timeline(self, memorial_id: str) -> list[dict]:
        """按时间线排列所有照片"""
        album_ids = {a.id for a in self.albums.values() if a.memorial_id == memorial_id}
        photos = sorted(
            [p for p in self.photos.values() if p.album_id in album_ids],
            key=lambda p: p.date_taken or "9999"
        )
        timeline = {}
        for p in photos:
            year = (p.date_taken or "未知年份")[:4]
            timeline.setdefault(year, []).append(p.to_dict())
        return [{"year": y, "photos": ps} for y, ps in timeline.items()]

    def export_album(self, album_id: str) -> Optional[str]:
        """导出相册数据"""
        album = self.albums.get(album_id)
        if not album:
            return None
        photos = self.list_photos(album_id)
        return json.dumps({
            "album": album.to_dict(),
            "photos": [p.to_dict() for p in photos],
        }, ensure_ascii=False, indent=2)
