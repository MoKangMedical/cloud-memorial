"""
Cloud Memorial — AI 故事讲述
生成逝者的生平故事、回忆录
"""

import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from config import load_json_data


@dataclass
class Story:
    """故事"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    title: str = ""
    content: str = ""
    story_type: str = "life"  # life / memory / anecdote / letter / custom
    author: str = ""
    people_mentioned: list[str] = field(default_factory=list)
    time_period: str = ""  # 时间段描述
    location: str = ""
    mood: str = ""  # 温馨 / 感人 / 幽默 / 怀旧
    is_ai_generated: bool = False
    source_memories: list[str] = field(default_factory=list)  # 基于的记忆ID
    word_count: int = 0
    like_count: int = 0
    is_public: bool = True
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class StoryChapter:
    """故事章节"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    story_id: str = ""
    chapter_number: int = 0
    title: str = ""
    content: str = ""
    time_period: str = ""
    photos: list[str] = field(default_factory=list)

    def to_dict(self) -> dict:
        return asdict(self)


class StoryTellerService:
    """AI故事讲述服务"""

    def __init__(self):
        self.stories: dict[str, Story] = {}
        self.chapters: dict[str, StoryChapter] = {}
        self.prompts = load_json_data("story-prompts.json")

    def create_story(self, memorial_id: str, title: str,
                     content: str, story_type: str = "memory",
                     author: str = "", people: list = None,
                     time_period: str = "", location: str = "",
                     mood: str = "") -> Story:
        """创建故事"""
        story = Story(
            memorial_id=memorial_id,
            title=title,
            content=content,
            story_type=story_type,
            author=author,
            people_mentioned=people or [],
            time_period=time_period,
            location=location,
            mood=mood,
            word_count=len(content),
        )
        self.stories[story.id] = story
        return story

    def get_story(self, story_id: str) -> Optional[Story]:
        """获取故事"""
        return self.stories.get(story_id)

    def list_stories(self, memorial_id: str, story_type: str = None,
                     mood: str = None) -> list[Story]:
        """列出故事"""
        stories = [s for s in self.stories.values() if s.memorial_id == memorial_id]
        if story_type:
            stories = [s for s in stories if s.story_type == story_type]
        if mood:
            stories = [s for s in stories if s.mood == mood]
        return sorted(stories, key=lambda s: s.created_at, reverse=True)

    def update_story(self, story_id: str, **kwargs) -> Optional[Story]:
        """更新故事"""
        story = self.stories.get(story_id)
        if not story:
            return None
        for key, value in kwargs.items():
            if hasattr(story, key):
                setattr(story, key, value)
        if "content" in kwargs:
            story.word_count = len(kwargs["content"])
        return story

    def delete_story(self, story_id: str) -> bool:
        """删除故事"""
        # 删除相关章节
        chapter_ids = [c.id for c in self.chapters.values() if c.story_id == story_id]
        for cid in chapter_ids:
            self.chapters.pop(cid, None)
        return self.stories.pop(story_id, None) is not None

    def like_story(self, story_id: str) -> int:
        """点赞故事"""
        s = self.stories.get(story_id)
        if s:
            s.like_count += 1
            return s.like_count
        return 0

    def add_chapter(self, story_id: str, title: str, content: str,
                    chapter_number: int = None,
                    time_period: str = "",
                    photos: list = None) -> Optional[StoryChapter]:
        """添加章节"""
        story = self.stories.get(story_id)
        if not story:
            return None
        if chapter_number is None:
            existing = [c for c in self.chapters.values() if c.story_id == story_id]
            chapter_number = len(existing) + 1
        chapter = StoryChapter(
            story_id=story_id,
            chapter_number=chapter_number,
            title=title,
            content=content,
            time_period=time_period,
            photos=photos or [],
        )
        self.chapters[chapter.id] = chapter
        return chapter

    def get_chapters(self, story_id: str) -> list[StoryChapter]:
        """获取故事的所有章节"""
        return sorted(
            [c for c in self.chapters.values() if c.story_id == story_id],
            key=lambda c: c.chapter_number,
        )

    def generate_ai_story(self, memorial_id: str,
                          deceased_name: str,
                          key_facts: list[str],
                          story_type: str = "life",
                          tone: str = "温馨") -> Story:
        """AI 生成故事"""
        # 模拟 AI 生成（实际应调用 AI API）
        facts_text = "；".join(key_facts[:5]) if key_facts else "一生平凡而伟大"
        content = (
            f"## {deceased_name}的故事\n\n"
            f"在这个世界上，有这样一个人——{deceased_name}。\n\n"
            f"{facts_text}。\n\n"
            f"岁月流转，时光荏苒，但那些珍贵的记忆永远不会褪色。"
            f"每一个微笑、每一次拥抱、每一句叮咛，都深深刻在我们心里。\n\n"
            f"虽然{deceased_name}已经离开了我们，但TA的精神和爱永远与我们同在。"
            f"让我们一起回忆那些美好的时光，让爱延续。\n\n"
            f"——由AI根据家人回忆自动生成"
        )
        story = Story(
            memorial_id=memorial_id,
            title=f"{deceased_name}的故事",
            content=content,
            story_type=story_type,
            author="AI",
            is_ai_generated=True,
            mood=tone,
            word_count=len(content),
        )
        self.stories[story.id] = story
        return story

    def get_story_prompts(self, category: str = None) -> list[dict]:
        """获取故事创作提示"""
        if isinstance(self.prompts, dict):
            prompt_list = self.prompts.get("story_prompts", [])
        else:
            prompt_list = self.prompts
        if category:
            return [p for p in prompt_list if p.get("category") == category]
        return prompt_list

    def search_stories(self, memorial_id: str, keyword: str) -> list[Story]:
        """搜索故事"""
        keyword_lower = keyword.lower()
        return [
            s for s in self.list_stories(memorial_id)
            if keyword_lower in s.title.lower()
            or keyword_lower in s.content.lower()
            or keyword_lower in " ".join(s.people_mentioned).lower()
        ]

    def get_story_stats(self, memorial_id: str) -> dict:
        """获取故事统计"""
        stories = self.list_stories(memorial_id)
        return {
            "total_stories": len(stories),
            "total_words": sum(s.word_count for s in stories),
            "by_type": {
                t: len([s for s in stories if s.story_type == t])
                for t in set(s.story_type for s in stories)
            },
            "by_mood": {
                m: len([s for s in stories if s.mood == m])
                for m in set(s.mood for s in stories if s.mood)
            },
            "ai_generated": len([s for s in stories if s.is_ai_generated]),
        }
