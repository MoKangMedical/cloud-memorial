"""
Cloud Memorial — 语音记忆
录制、存储和播放逝者的语音回忆
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict


@dataclass
class VoiceRecording:
    """语音录音"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    file_path: str = ""
    title: str = ""
    description: str = ""
    duration_seconds: int = 0
    recorded_by: str = ""  # 录制人
    recorded_date: Optional[str] = None
    transcript: str = ""  # 语音转文字
    mood: str = ""  # 情绪标签
    people_mentioned: list[str] = field(default_factory=list)
    tags: list[str] = field(default_factory=list)
    is_public: bool = True
    play_count: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class VoiceStory:
    """语音故事（多段录音组合）"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    title: str = ""
    description: str = ""
    recording_ids: list[str] = field(default_factory=list)
    narrator: str = ""
    total_duration: int = 0
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class VoiceMemoryService:
    """语音记忆服务"""

    def __init__(self):
        self.recordings: dict[str, VoiceRecording] = {}
        self.stories: dict[str, VoiceStory] = {}

    def upload_recording(self, memorial_id: str, file_path: str,
                         title: str, description: str = "",
                         duration_seconds: int = 0,
                         recorded_by: str = "",
                         recorded_date: str = None,
                         transcript: str = "",
                         mood: str = "",
                         people: list = None,
                         tags: list = None) -> VoiceRecording:
        """上传语音录音"""
        rec = VoiceRecording(
            memorial_id=memorial_id,
            file_path=file_path,
            title=title,
            description=description,
            duration_seconds=duration_seconds,
            recorded_by=recorded_by,
            recorded_date=recorded_date,
            transcript=transcript,
            mood=mood,
            people_mentioned=people or [],
            tags=tags or [],
        )
        self.recordings[rec.id] = rec
        return rec

    def get_recording(self, rec_id: str) -> Optional[VoiceRecording]:
        """获取录音"""
        return self.recordings.get(rec_id)

    def list_recordings(self, memorial_id: str, mood: str = None) -> list[VoiceRecording]:
        """列出录音"""
        recs = [r for r in self.recordings.values() if r.memorial_id == memorial_id]
        if mood:
            recs = [r for r in recs if r.mood == mood]
        return sorted(recs, key=lambda r: r.recorded_date or r.created_at, reverse=True)

    def delete_recording(self, rec_id: str) -> bool:
        """删除录音"""
        return self.recordings.pop(rec_id, None) is not None

    def play_recording(self, rec_id: str) -> Optional[str]:
        """播放录音（返回文件路径）"""
        rec = self.recordings.get(rec_id)
        if rec:
            rec.play_count += 1
            return rec.file_path
        return None

    def update_transcript(self, rec_id: str, transcript: str) -> bool:
        """更新语音转文字"""
        rec = self.recordings.get(rec_id)
        if rec:
            rec.transcript = transcript
            return True
        return False

    def create_story(self, memorial_id: str, title: str,
                     recording_ids: list[str],
                     narrator: str = "",
                     description: str = "") -> Optional[VoiceStory]:
        """创建语音故事"""
        total = 0
        for rid in recording_ids:
            rec = self.recordings.get(rid)
            if rec:
                total += rec.duration_seconds
        story = VoiceStory(
            memorial_id=memorial_id,
            title=title,
            description=description,
            recording_ids=recording_ids,
            narrator=narrator,
            total_duration=total,
        )
        self.stories[story.id] = story
        return story

    def get_story(self, story_id: str) -> Optional[VoiceStory]:
        """获取语音故事"""
        return self.stories.get(story_id)

    def list_stories(self, memorial_id: str) -> list[VoiceStory]:
        """列出所有语音故事"""
        return [s for s in self.stories.values() if s.memorial_id == memorial_id]

    def delete_story(self, story_id: str) -> bool:
        """删除语音故事"""
        return self.stories.pop(story_id, None) is not None

    def get_story_playlist(self, story_id: str) -> Optional[list[dict]]:
        """获取故事播放列表"""
        story = self.stories.get(story_id)
        if not story:
            return None
        playlist = []
        for rid in story.recording_ids:
            rec = self.recordings.get(rid)
            if rec:
                playlist.append({
                    "id": rec.id,
                    "title": rec.title,
                    "file_path": rec.file_path,
                    "duration": rec.duration_seconds,
                    "transcript": rec.transcript,
                })
        return playlist

    def search_recordings(self, memorial_id: str, keyword: str) -> list[VoiceRecording]:
        """搜索录音"""
        keyword_lower = keyword.lower()
        return [
            r for r in self.list_recordings(memorial_id)
            if keyword_lower in r.title.lower()
            or keyword_lower in r.description.lower()
            or keyword_lower in r.transcript.lower()
            or keyword_lower in " ".join(r.tags).lower()
        ]

    def get_mood_stats(self, memorial_id: str) -> dict[str, int]:
        """获取情绪统计"""
        recs = self.list_recordings(memorial_id)
        stats = {}
        for r in recs:
            mood = r.mood or "未分类"
            stats[mood] = stats.get(mood, 0) + 1
        return stats
