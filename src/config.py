"""
Cloud Memorial — 配置管理
全局配置、环境变量、常量定义
"""

import os
import json
from pathlib import Path
from dataclasses import dataclass, field
from typing import Optional

# 项目根目录
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
SRC_DIR = BASE_DIR / "src"
UPLOAD_DIR = BASE_DIR / "uploads"
BACKUP_DIR = BASE_DIR / "backups"

# 确保目录存在
for d in [DATA_DIR, UPLOAD_DIR, BACKUP_DIR]:
    d.mkdir(parents=True, exist_ok=True)


@dataclass
class AppConfig:
    """应用配置"""
    app_name: str = "云思园"
    app_title: str = "🌸 云思园 — AI 思念亲人平台"
    version: str = "1.0.0"
    debug: bool = False

    # 服务端口
    host: str = "0.0.0.0"
    port: int = 8501

    # AI 配置
    ai_model: str = "gpt-4"
    ai_temperature: float = 0.7
    ai_max_tokens: int = 2048

    # 文件上传限制
    max_upload_size_mb: int = 50
    allowed_image_types: tuple = (".jpg", ".jpeg", ".png", ".gif", ".webp")
    allowed_video_types: tuple = (".mp4", ".mov", ".avi", ".webm")
    allowed_audio_types: tuple = (".mp3", ".wav", ".ogg", ".m4a")

    # 数据库
    db_path: str = str(BASE_DIR / "memorial.db")

    # 备份配置
    backup_interval_hours: int = 24
    max_backups: int = 30

    # 通知配置
    notification_enabled: bool = True
    email_smtp_host: str = ""
    email_smtp_port: int = 587

    # 安全配置
    secret_key: str = os.getenv("MEMORIAL_SECRET_KEY", "memorial-dev-key-change-in-production")
    jwt_expiry_hours: int = 72


@dataclass
class MemorialTheme:
    """纪念主题配置"""
    primary_color: str = "#8b5e3c"
    secondary_color: str = "#a0845c"
    background_gradient: str = "linear-gradient(180deg, #fef9f0 0%, #f5ebe0 100%)"
    font_family: str = "serif"
    border_radius: str = "16px"


def load_json_data(filename: str) -> dict:
    """加载 JSON 数据文件"""
    filepath = DATA_DIR / filename
    if filepath.exists():
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}


def get_config() -> AppConfig:
    """获取应用配置（单例）"""
    if not hasattr(get_config, "_instance"):
        get_config._instance = AppConfig()
    return get_config._instance


# 全局常量
RELATIONSHIP_TYPES = [
    "父亲", "母亲", "爷爷", "奶奶", "外公", "外婆",
    "丈夫", "妻子", "儿子", "女儿", "兄弟", "姐妹",
    "伯伯", "叔叔", "姑姑", "舅舅", "姨妈",
    "堂兄弟", "表兄弟", "侄子", "侄女", "外甥", "外甥女",
    "好友", "恩师", "其他"
]

MEMORIAL_STATUS = ["active", "archived", "private", "public"]

CANDLE_EFFECTS = ["温暖", "宁静", "思念", "永恒", "安详"]

FLOWER_MEANINGS = {
    "白菊花": "高洁、哀悼",
    "白百合": "纯洁、庄严",
    "黄菊花": "思念、怀念",
    "白玫瑰": "尊敬、纯洁",
    "康乃馨": "母爱、感恩",
    "勿忘我": "永恒的记忆",
    "满天星": "思念、关怀",
    "马蹄莲": "永恒、优雅",
}
