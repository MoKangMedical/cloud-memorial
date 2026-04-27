"""
Cloud Memorial — 数据备份
纪念馆数据的备份与恢复
"""

import os
import json
import shutil
import uuid
from datetime import datetime
from typing import Optional
from dataclasses import dataclass, field, asdict
from pathlib import Path
from config import BACKUP_DIR


@dataclass
class BackupRecord:
    """备份记录"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    memorial_id: str = ""
    backup_type: str = "full"  # full / incremental / manual
    file_path: str = ""
    file_size_bytes: int = 0
    includes: list[str] = field(default_factory=list)  # photos / videos / audio / data
    status: str = "completed"  # pending / in_progress / completed / failed
    error_message: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class RestorePoint:
    """恢复点"""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    backup_id: str = ""
    memorial_id: str = ""
    description: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


class BackupService:
    """数据备份服务"""

    def __init__(self, backup_dir: Path = None):
        self.backup_dir = backup_dir or BACKUP_DIR
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.backups: dict[str, BackupRecord] = {}
        self.restore_points: dict[str, RestorePoint] = {}

    def create_backup(self, memorial_id: str, data: dict,
                      backup_type: str = "full",
                      includes: list = None) -> BackupRecord:
        """创建备份"""
        backup_id = str(uuid.uuid4())[:8]
        filename = f"backup_{memorial_id}_{backup_id}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        file_path = self.backup_dir / filename

        # 写入备份数据
        backup_data = {
            "backup_id": backup_id,
            "memorial_id": memorial_id,
            "backup_type": backup_type,
            "created_at": datetime.now().isoformat(),
            "data": data,
        }

        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(backup_data, f, ensure_ascii=False, indent=2)

        file_size = file_path.stat().st_size

        record = BackupRecord(
            id=backup_id,
            memorial_id=memorial_id,
            backup_type=backup_type,
            file_path=str(file_path),
            file_size_bytes=file_size,
            includes=includes or ["data"],
            status="completed",
        )
        self.backups[backup_id] = record

        # 创建恢复点
        restore_point = RestorePoint(
            backup_id=backup_id,
            memorial_id=memorial_id,
            description=f"{backup_type}备份 - {datetime.now().strftime('%Y-%m-%d %H:%M')}",
        )
        self.restore_points[restore_point.id] = restore_point

        return record

    def get_backup(self, backup_id: str) -> Optional[BackupRecord]:
        """获取备份记录"""
        return self.backups.get(backup_id)

    def list_backups(self, memorial_id: str) -> list[BackupRecord]:
        """列出某纪念馆的所有备份"""
        return sorted(
            [b for b in self.backups.values() if b.memorial_id == memorial_id],
            key=lambda b: b.created_at, reverse=True,
        )

    def restore_backup(self, backup_id: str) -> Optional[dict]:
        """从备份恢复数据"""
        record = self.backups.get(backup_id)
        if not record:
            return None
        file_path = Path(record.file_path)
        if not file_path.exists():
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                backup_data = json.load(f)
            return backup_data.get("data")
        except (json.JSONDecodeError, IOError):
            return None

    def delete_backup(self, backup_id: str) -> bool:
        """删除备份"""
        record = self.backups.pop(backup_id, None)
        if not record:
            return False
        file_path = Path(record.file_path)
        if file_path.exists():
            file_path.unlink()
        # 删除相关恢复点
        rp_ids = [rp.id for rp in self.restore_points.values() if rp.backup_id == backup_id]
        for rpid in rp_ids:
            self.restore_points.pop(rpid, None)
        return True

    def get_restore_points(self, memorial_id: str) -> list[RestorePoint]:
        """获取恢复点"""
        return sorted(
            [rp for rp in self.restore_points.values() if rp.memorial_id == memorial_id],
            key=lambda rp: rp.created_at, reverse=True,
        )

    def auto_cleanup(self, memorial_id: str, max_backups: int = 30) -> int:
        """自动清理旧备份"""
        backups = self.list_backups(memorial_id)
        if len(backups) <= max_backups:
            return 0
        to_delete = backups[max_backups:]
        count = 0
        for b in to_delete:
            if self.delete_backup(b.id):
                count += 1
        return count

    def export_memorial(self, memorial_id: str, data: dict,
                        export_format: str = "json") -> Optional[str]:
        """导出纪念馆数据"""
        filename = f"export_{memorial_id}_{datetime.now().strftime('%Y%m%d')}.{export_format}"
        file_path = self.backup_dir / filename
        try:
            if export_format == "json":
                with open(file_path, "w", encoding="utf-8") as f:
                    json.dump(data, f, ensure_ascii=False, indent=2)
            return str(file_path)
        except IOError:
            return None

    def import_memorial(self, file_path: str) -> Optional[dict]:
        """导入纪念馆数据"""
        path = Path(file_path)
        if not path.exists():
            return None
        try:
            with open(path, "r", encoding="utf-8") as f:
                return json.load(f)
        except (json.JSONDecodeError, IOError):
            return None

    def get_backup_stats(self, memorial_id: str) -> dict:
        """获取备份统计"""
        backups = self.list_backups(memorial_id)
        return {
            "total_backups": len(backups),
            "total_size_mb": round(sum(b.file_size_bytes for b in backups) / 1024 / 1024, 2),
            "latest_backup": backups[0].created_at if backups else None,
            "by_type": {
                t: len([b for b in backups if b.backup_type == t])
                for t in set(b.backup_type for b in backups)
            },
        }
