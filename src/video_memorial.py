"""
Cloud Memorial — 视频纪念
管理纪念视频、影像回忆
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class VideoClip:
    """视频片段"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    file_path: str = ""
    thumbnail_path: str = ""
    title: str = ""
    description: str = ""
    duration_seconds: int = 0
    date_recorded: Optional[str] = None
    people: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    is_public: bool = True
    view_count: int = 0
    like_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VideoMemorial:
    """视频纪念合集"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    title: str = ""
    description: str = ""
    video_ids: list[str] = field(default_factory=list)
    bgm_path: str = ""
    cover_image: str = ""
    duration_seconds: int = 0
    is_compilation: bool = False
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class VideoMemorialService:
    """视频纪念服务"""

    def __init__(self):
        self.clips: dict[str, VideoClip] = {}
        self.collections: dict[str, VideoMemorial] = {}

    def upload_clip(self, memorial_id: str, file_path: str,
                    title: str, description: str = "",
                    duration_seconds: int = 0,
                    date_recorded: str = None,
                    people: list = None, tags: list = None) -> VideoClip:
        """上传视频片段"""
        clip = VideoClip(
            memorial_id=memorial_id,
            file_path=file_path,
            title=title,
            description=description,
            duration_seconds=duration_seconds,
            date_recorded=date_recorded,
            people=people or [],
            tags=tags or [],
        )
        self.clips[clip.id] = clip
        return clip

    def get_clip(self, clip_id: str) -> Optional[VideoClip]:
        """获取视频片段"""
        return self.clips.get(clip_id)

    def list_clips(self, memorial_id: str) -> list[VideoClip]:
        """列出某纪念馆的所有视频"""
        return sorted(
            [c for c in self.clips.values() if c.memorial_id == memorial_id],
            key=lambda c: c.date_recorded or c.created_at,
            reverse=True,
        )

    def delete_clip(self, clip_id: str) -> bool:
        """删除视频片段"""
        return self.clips.pop(clip_id, None) is not None

    def like_clip(self, clip_id: str) -> int:
        """点赞视频"""
        clip = self.clips.get(clip_id)
        if clip:
            clip.like_count += 1
            return clip.like_count
        return 0

    def view_clip(self, clip_id: str) -> int:
        """记录观看"""
        clip = self.clips.get(clip_id)
        if clip:
            clip.view_count += 1
            return clip.view_count
        return 0

    def create_collection(self, memorial_id: str, title: str,
                          description: str = "", video_ids: list = None,
                          bgm_path: str = "") -> VideoMemorial:
        """创建视频合集"""
        collection = VideoMemorial(
            memorial_id=memorial_id,
            title=title,
            description=description,
            video_ids=video_ids or [],
            bgm_path=bgm_path,
        )
        # 计算总时长
        for vid in collection.video_ids:
            clip = self.clips.get(vid)
            if clip:
                collection.duration_seconds += clip.duration_seconds
        self.collections[collection.id] = collection
        return collection

    def get_collection(self, collection_id: str) -> Optional[VideoMemorial]:
        """获取视频合集"""
        return self.collections.get(collection_id)

    def list_collections(self, memorial_id: str) -> list[VideoMemorial]:
        """列出所有视频合集"""
        return [c for c in self.collections.values() if c.memorial_id == memorial_id]

    def add_to_collection(self, collection_id: str, clip_id: str) -> bool:
        """添加视频到合集"""
        collection = self.collections.get(collection_id)
        clip = self.clips.get(clip_id)
        if not collection or not clip:
            return False
        if clip_id not in collection.video_ids:
            collection.video_ids.append(clip_id)
            collection.duration_seconds += clip.duration_seconds
        return True

    def remove_from_collection(self, collection_id: str, clip_id: str) -> bool:
        """从合集移除视频"""
        collection = self.collections.get(collection_id)
        if not collection or clip_id not in collection.video_ids:
            return False
        clip = self.clips.get(clip_id)
        collection.video_ids.remove(clip_id)
        if clip:
            collection.duration_seconds -= clip.duration_seconds
        return True

    def generate_slideshow_script(self, collection_id: str) -> Optional[list[dict]]:
        """生成幻灯片脚本"""
        collection = self.collections.get(collection_id)
        if not collection:
            return None
        script = []
        for i, vid in enumerate(collection.video_ids):
            clip = self.clips.get(vid)
            if clip:
                script.append({
                    "order": i + 1,
                    "clip_id": clip.id,
                    "title": clip.title,
                    "file_path": clip.file_path,
                    "duration": clip.duration_seconds,
                    "transition": "fade",
                })
        return script

    def search_clips(self, memorial_id: str, keyword: str) -> list[VideoClip]:
        """搜索视频"""
        keyword_lower = keyword.lower()
        return [
            c for c in self.list_clips(memorial_id)
            if keyword_lower in c.title.lower()
            or keyword_lower in c.description.lower()
            or keyword_lower in " ".join(c.tags).lower()
            or keyword_lower in " ".join(c.people).lower()
        ]
