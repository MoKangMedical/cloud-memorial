"""
Cloud Memorial — REST API 接口
提供 RESTful API 供前端调用
"""

import json
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field
from flask import Flask, jsonify, request, abort

# 导入各服务模块
from config import get_config, AppConfig
from family_tree import FamilyTreeManager
from photo_album import PhotoAlbumManager
from video_memorial import VideoMemorialService
from voice_memory import VoiceMemoryService
from letter_generator import LetterGeneratorService
from anniversary import AnniversaryService
from candle_service import CandleService
from flower_service import FlowerService
from prayer_service import PrayerService
from story_teller import StoryTellerService
from grief_counseling import GriefCounselingService
from memorial_wall import MemorialWallService
from sharing import SharingService
from backup import BackupService
from notification import NotificationService


# 创建 Flask 应用
app = Flask(__name__)
app.config["SECRET_KEY"] = get_config().secret_key

# 初始化所有服务
services = {
    "family_tree": FamilyTreeManager(),
    "photo_album": PhotoAlbumManager(),
    "video_memorial": VideoMemorialService(),
    "voice_memory": VoiceMemoryService(),
    "letter_generator": LetterGeneratorService(),
    "anniversary": AnniversaryService(),
    "candle": CandleService(),
    "flower": FlowerService(),
    "prayer": PrayerService(),
    "story_teller": StoryTellerService(),
    "grief_counseling": GriefCounselingService(),
    "memorial_wall": MemorialWallService(),
    "sharing": SharingService(),
    "backup": BackupService(),
    "notification": NotificationService(),
}


def success_response(data=None, message="success"):
    """成功响应"""
    return jsonify({"code": 0, "message": message, "data": data})


def error_response(message="error", code=400):
    """错误响应"""
    return jsonify({"code": code, "message": message, "data": None}), code


# ==================== 纪念馆管理 ====================

@app.route("/api/v1/health", methods=["GET"])
def health_check():
    """健康检查"""
    return success_response({
        "status": "healthy",
        "version": get_config().version,
        "timestamp": datetime.now().isoformat(),
    })


@app.route("/api/v1/config", methods=["GET"])
def get_app_config():
    """获取应用配置"""
    cfg = get_config()
    return success_response({
        "app_name": cfg.app_name,
        "version": cfg.version,
        "max_upload_size_mb": cfg.max_upload_size_mb,
    })


# ==================== 家族树 ====================

@app.route("/api/v1/family-tree", methods=["POST"])
def create_family_tree():
    """创建家族树"""
    data = request.get_json()
    tree = services["family_tree"].create_tree(data.get("family_name", ""))
    return success_response(tree.to_dict())


@app.route("/api/v1/family-tree/<tree_id>", methods=["GET"])
def get_family_tree(tree_id):
    """获取家族树"""
    tree = services["family_tree"].get_tree(tree_id)
    if not tree:
        return error_response("家族树不存在", 404)
    return success_response(tree.to_dict())


@app.route("/api/v1/family-tree/<tree_id>/member", methods=["POST"])
def add_family_member(tree_id):
    """添加家族成员"""
    tree = services["family_tree"].get_tree(tree_id)
    if not tree:
        return error_response("家族树不存在", 404)
    data = request.get_json()
    from family_tree import FamilyMember
    member = FamilyMember(**{k: v for k, v in data.items() if hasattr(FamilyMember, k)})
    member_id = tree.add_member(member, data.get("parent_id"))
    return success_response({"member_id": member_id})


# ==================== 相册 ====================

@app.route("/api/v1/album", methods=["POST"])
def create_album():
    """创建相册"""
    data = request.get_json()
    album = services["photo_album"].create_album(
        data.get("memorial_id", ""),
        data.get("title", ""),
        data.get("description", ""),
    )
    return success_response(album.to_dict())


@app.route("/api/v1/album/<album_id>/photo", methods=["POST"])
def add_photo(album_id):
    """添加照片"""
    data = request.get_json()
    photo = services["photo_album"].add_photo(
        album_id=album_id,
        file_path=data.get("file_path", ""),
        title=data.get("title", ""),
        description=data.get("description", ""),
        date_taken=data.get("date_taken"),
        location=data.get("location", ""),
        people=data.get("people", []),
        tags=data.get("tags", []),
    )
    if not photo:
        return error_response("相册不存在", 404)
    return success_response(photo.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/albums", methods=["GET"])
def list_albums(memorial_id):
    """列出相册"""
    albums = services["photo_album"].list_albums(memorial_id)
    return success_response([a.to_dict() for a in albums])


# ==================== 视频纪念 ====================

@app.route("/api/v1/video", methods=["POST"])
def upload_video():
    """上传视频"""
    data = request.get_json()
    clip = services["video_memorial"].upload_clip(
        memorial_id=data.get("memorial_id", ""),
        file_path=data.get("file_path", ""),
        title=data.get("title", ""),
        description=data.get("description", ""),
        duration_seconds=data.get("duration_seconds", 0),
    )
    return success_response(clip.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/videos", methods=["GET"])
def list_videos(memorial_id):
    """列出视频"""
    clips = services["video_memorial"].list_clips(memorial_id)
    return success_response([c.to_dict() for c in clips])


# ==================== 语音记忆 ====================

@app.route("/api/v1/voice", methods=["POST"])
def upload_voice():
    """上传语音"""
    data = request.get_json()
    rec = services["voice_memory"].upload_recording(
        memorial_id=data.get("memorial_id", ""),
        file_path=data.get("file_path", ""),
        title=data.get("title", ""),
        description=data.get("description", ""),
        duration_seconds=data.get("duration_seconds", 0),
        recorded_by=data.get("recorded_by", ""),
    )
    return success_response(rec.to_dict())


# ==================== 信件 ====================

@app.route("/api/v1/letter", methods=["POST"])
def send_letter():
    """发送信件"""
    data = request.get_json()
    letter = services["letter_generator"].send_letter(
        memorial_id=data.get("memorial_id", ""),
        sender_name=data.get("sender_name", ""),
        recipient_name=data.get("recipient_name", ""),
        title=data.get("title", ""),
        content=data.get("content", ""),
        mood=data.get("mood", ""),
    )
    return success_response(letter.to_dict())


@app.route("/api/v1/letter/<letter_id>/ai-reply", methods=["POST"])
def ai_reply_letter(letter_id):
    """AI回信"""
    data = request.get_json()
    reply = services["letter_generator"].generate_ai_reply(
        letter_id=letter_id,
        deceased_name=data.get("deceased_name", ""),
        deceased_personality=data.get("personality", "慈祥"),
    )
    if not reply:
        return error_response("原信不存在", 404)
    return success_response(reply.to_dict())


# ==================== 纪念日 ====================

@app.route("/api/v1/anniversary", methods=["POST"])
def add_anniversary():
    """添加纪念日"""
    data = request.get_json()
    ann = services["anniversary"].add_anniversary(
        memorial_id=data.get("memorial_id", ""),
        title=data.get("title", ""),
        date_str=data.get("date", ""),
        category=data.get("category", "other"),
        description=data.get("description", ""),
    )
    return success_response(ann.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/anniversaries/upcoming", methods=["GET"])
def upcoming_anniversaries(memorial_id):
    """获取即将到来的纪念日"""
    days = request.args.get("days", 30, type=int)
    upcoming = services["anniversary"].get_upcoming(memorial_id, days)
    return success_response(upcoming)


# ==================== 虚拟祭扫 ====================

@app.route("/api/v1/candle", methods=["POST"])
def light_candle():
    """点蜡烛"""
    data = request.get_json()
    candle = services["candle"].light_candle(
        memorial_id=data.get("memorial_id", ""),
        lit_by=data.get("lit_by", ""),
        candle_type=data.get("candle_type", "white"),
        message=data.get("message", ""),
    )
    return success_response(candle.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/candles", methods=["GET"])
def list_candles(memorial_id):
    """列出蜡烛"""
    candles = services["candle"].get_active_candles(memorial_id)
    return success_response([c.to_dict() for c in candles])


# ==================== 虚拟献花 ====================

@app.route("/api/v1/flower", methods=["POST"])
def place_flower():
    """献花"""
    data = request.get_json()
    flower = services["flower"].place_flower(
        memorial_id=data.get("memorial_id", ""),
        placed_by=data.get("placed_by", ""),
        flower_type=data.get("flower_type", "chrysanthemum"),
        color=data.get("color", "white"),
        quantity=data.get("quantity", 1),
        message=data.get("message", ""),
    )
    return success_response(flower.to_dict())


# ==================== 祈福 ====================

@app.route("/api/v1/prayer", methods=["POST"])
def pray():
    """祈福"""
    data = request.get_json()
    prayer = services["prayer"].pray(
        memorial_id=data.get("memorial_id", ""),
        prayed_by=data.get("prayed_by", ""),
        content=data.get("content", ""),
        prayer_type=data.get("prayer_type", "blessing"),
    )
    return success_response(prayer.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/prayer-wall", methods=["GET"])
def prayer_wall(memorial_id):
    """祈福墙"""
    prayers = services["prayer"].get_wall_prayers(memorial_id)
    return success_response([p.to_dict() for p in prayers])


# ==================== 故事 ====================

@app.route("/api/v1/story", methods=["POST"])
def create_story():
    """创建故事"""
    data = request.get_json()
    story = services["story_teller"].create_story(
        memorial_id=data.get("memorial_id", ""),
        title=data.get("title", ""),
        content=data.get("content", ""),
        story_type=data.get("story_type", "memory"),
        author=data.get("author", ""),
    )
    return success_response(story.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/stories", methods=["GET"])
def list_stories(memorial_id):
    """列出故事"""
    stories = services["story_teller"].list_stories(memorial_id)
    return success_response([s.to_dict() for s in stories])


# ==================== 哀伤辅导 ====================

@app.route("/api/v1/grief/assessment", methods=["POST"])
def grief_assessment():
    """哀伤评估"""
    data = request.get_json()
    assessment = services["grief_counseling"].take_assessment(
        user_id=data.get("user_id", ""),
        memorial_id=data.get("memorial_id", ""),
        answers=data.get("answers", {}),
    )
    return success_response(assessment.to_dict())


@app.route("/api/v1/grief/stages", methods=["GET"])
def grief_stages():
    """获取哀伤阶段信息"""
    return success_response(services["grief_counseling"].get_all_stages())


# ==================== 纪念墙 ====================

@app.route("/api/v1/wall", methods=["POST"])
def create_wall():
    """创建纪念墙"""
    data = request.get_json()
    wall = services["memorial_wall"].create_wall(
        memorial_id=data.get("memorial_id", ""),
        name=data.get("name", ""),
        description=data.get("description", ""),
    )
    return success_response(wall.to_dict())


@app.route("/api/v1/wall/<wall_id>/message", methods=["POST"])
def leave_wall_message(wall_id):
    """纪念墙留言"""
    data = request.get_json()
    msg = services["memorial_wall"].leave_message(
        wall_id=wall_id,
        author_name=data.get("author_name", ""),
        content=data.get("content", ""),
    )
    if not msg:
        return error_response("纪念墙不存在", 404)
    return success_response(msg.to_dict())


# ==================== 分享 ====================

@app.route("/api/v1/share", methods=["POST"])
def create_share():
    """创建分享链接"""
    data = request.get_json()
    link = services["sharing"].create_share_link(
        memorial_id=data.get("memorial_id", ""),
        created_by=data.get("created_by", ""),
        share_type=data.get("share_type", "public"),
    )
    return success_response(link.to_dict())


@app.route("/api/v1/share/<share_code>/validate", methods=["GET"])
def validate_share(share_code):
    """验证分享链接"""
    password = request.args.get("password")
    result = services["sharing"].validate_access(share_code, password)
    return success_response(result)


# ==================== 备份 ====================

@app.route("/api/v1/backup", methods=["POST"])
def create_backup():
    """创建备份"""
    data = request.get_json()
    record = services["backup"].create_backup(
        memorial_id=data.get("memorial_id", ""),
        data=data.get("data", {}),
    )
    return success_response(record.to_dict())


@app.route("/api/v1/memorial/<memorial_id>/backups", methods=["GET"])
def list_backups(memorial_id):
    """列出备份"""
    backups = services["backup"].list_backups(memorial_id)
    return success_response([b.to_dict() for b in backups])


# ==================== 通知 ====================

@app.route("/api/v1/notifications/<user_id>", methods=["GET"])
def get_notifications(user_id):
    """获取通知"""
    notifs = services["notification"].get_notifications(user_id)
    return success_response([n.to_dict() for n in notifs])


@app.route("/api/v1/notifications/<user_id>/unread-count", methods=["GET"])
def unread_count(user_id):
    """未读通知数"""
    count = services["notification"].get_unread_count(user_id)
    return success_response({"count": count})


def run_api_server(host: str = "0.0.0.0", port: int = 5000, debug: bool = False):
    """启动 API 服务器"""
    app.run(host=host, port=port, debug=debug)


if __name__ == "__main__":
    cfg = get_config()
    run_api_server(host=cfg.host, port=5000, debug=cfg.debug)
