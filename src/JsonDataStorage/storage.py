"""
JSON Data Storage - Xử lý đọc/ghi dữ liệu task từ file JSON
"""

import json
import os
from datetime import datetime

DATA_FILE = os.path.join(os.path.dirname(__file__), "..", "..", "data", "tasks.json")


def _ensure_data_file():
    """Tạo file data nếu chưa tồn tại."""
    os.makedirs(os.path.dirname(DATA_FILE), exist_ok=True)
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", encoding="utf-8") as f:
            json.dump(
                {
                    "tasks": [],
                    "deleted": [],
                    "meta": {"created_at": datetime.now().isoformat()},
                },
                f,
                ensure_ascii=False,
                indent=2,
            )


def load_tasks() -> list:
    """Đọc danh sách task từ file JSON."""
    _ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("tasks", [])


def save_tasks(tasks: list) -> None:
    """Lưu danh sách task vào file JSON."""
    _ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["tasks"] = tasks
    data["meta"]["last_updated"] = datetime.now().isoformat()
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def load_deleted_tasks() -> list:
    """Đọc danh sách task đã xóa (thùng rác)."""
    _ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    return data.get("deleted", [])


def save_deleted_tasks(deleted: list) -> None:
    """Lưu danh sách task đã xóa vào thùng rác."""
    _ensure_data_file()
    with open(DATA_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
    data["deleted"] = deleted
    with open(DATA_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def get_next_id() -> int:
    """Tạo ID tự động tăng dần."""
    tasks = load_tasks()
    deleted = load_deleted_tasks()
    all_ids = [t.get("id", 0) for t in tasks + deleted]
    return max(all_ids, default=0) + 1
