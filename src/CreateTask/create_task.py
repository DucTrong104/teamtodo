"""
CreateTask - Tạo task mới với giao diện CLI sáng tạo có màu sắc + animation
"""

import sys
import os
import time
import uuid
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from JsonDataStorage.storage import load_tasks, save_tasks, get_next_id

# ─── ANSI Color Codes ───────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
ORANGE  = "\033[38;5;208m"

# ─── Hằng số ────────────────────────────────────────────────────────────────
PRIORITY_LEVELS = {
    "1": {"label": "URGENT",  "color": RED,     "value": "urgent",  "icon": "🔴"},
    "2": {"label": "HIGH",    "color": ORANGE,   "value": "high",    "icon": "🟠"},
    "3": {"label": "MEDIUM",  "color": YELLOW,   "value": "medium",  "icon": "🟡"},
    "4": {"label": "LOW",     "color": GREEN,    "value": "low",     "icon": "🟢"},
}

CATEGORIES = {
    "1": {"label": "Công việc", "icon": "💼", "value": "work"},
    "2": {"label": "Cá nhân",   "icon": "🏠", "value": "personal"},
    "3": {"label": "Học tập",   "icon": "📚", "value": "study"},
    "4": {"label": "Sức khỏe", "icon": "🏃", "value": "health"},
    "5": {"label": "Ý tưởng",   "icon": "💡", "value": "idea"},
    "6": {"label": "Khác",      "icon": "⚙️",  "value": "other"},
}


# ─── UI Helpers ─────────────────────────────────────────────────────────────

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")


def typing_effect(text: str, delay: float = 0.025):
    """Hiệu ứng gõ chữ từng ký tự."""
    for ch in text:
        print(ch, end="", flush=True)
        time.sleep(delay)
    print()


def loading_bar(label: str = "Đang lưu", duration: float = 0.8):
    """Thanh tiến trình giả lập khi lưu."""
    total = 25
    for i in range(total + 1):
        filled = "█" * i
        empty  = "░" * (total - i)
        pct    = int(i / total * 100)
        print(
            f"\r  {CYAN}{label}...{RESET} [{GREEN}{filled}{DIM}{empty}{RESET}] {BOLD}{pct}%{RESET}",
            end="",
            flush=True,
        )
        time.sleep(duration / total)
    print(f"\r  {GREEN}✔ Lưu thành công!{RESET}{' ' * 40}")


def print_banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════╗
║  {BOLD}{MAGENTA}      ✦  TẠO TASK MỚI  ✦      {RESET}{CYAN}                     ║
║  {DIM}  TeamTodo · Create Task Module                  {RESET}{CYAN}  ║
╚══════════════════════════════════════════════════════╝{RESET}
""")


def section_header(title: str):
    line = "─" * (44 - len(title))
    print(f"\n  {BLUE}┌─ {BOLD}{title} {RESET}{BLUE}{line}┐{RESET}")


def ask(label: str, required: bool = True, hint: str = "") -> str:
    """Nhận input từ user với giao diện đẹp."""
    hint_str = f" {DIM}({hint}){RESET}" if hint else ""
    req_str  = f" {RED}*{RESET}" if required else f" {DIM}(tùy chọn){RESET}"
    while True:
        print(f"  {YELLOW}▶{RESET} {BOLD}{label}{req_str}{hint_str}")
        val = input(f"    {CYAN}→ {RESET}").strip()
        if val or not required:
            return val
        print(f"  {RED}✗ Trường này bắt buộc! Vui lòng nhập lại.{RESET}")


def choose_priority() -> dict:
    section_header("Mức độ ưu tiên")
    for k, v in PRIORITY_LEVELS.items():
        print(f"    {BOLD}{k}.{RESET} {v['color']}{v['icon']} {v['label']}{RESET}")
    while True:
        c = input(f"\n  {CYAN}→ Chọn (1-4): {RESET}").strip()
        if c in PRIORITY_LEVELS:
            return PRIORITY_LEVELS[c]
        print(f"  {RED}✗ Chọn từ 1 đến 4.{RESET}")


def choose_category() -> dict:
    section_header("Danh mục")
    for k, v in CATEGORIES.items():
        print(f"    {BOLD}{k}.{RESET} {v['icon']}  {v['label']}")
    while True:
        c = input(f"\n  {CYAN}→ Chọn (1-6): {RESET}").strip()
        if c in CATEGORIES:
            return CATEGORIES[c]
        print(f"  {RED}✗ Chọn từ 1 đến 6.{RESET}")


def input_deadline() -> str | None:
    section_header("Deadline")
    print(f"  {DIM}Định dạng: DD/MM/YYYY  |  Bỏ trống = không có deadline{RESET}")
    while True:
        raw = input(f"\n  {CYAN}→ Deadline: {RESET}").strip()
        if not raw:
            return None
        try:
            dt = datetime.strptime(raw, "%d/%m/%Y")
            if dt.date() < datetime.now().date():
                yn = input(f"  {YELLOW}⚠  Deadline đã qua! Vẫn tiếp tục? (y/n): {RESET}").strip().lower()
                if yn != "y":
                    continue
            return dt.strftime("%Y-%m-%d")
        except ValueError:
            print(f"  {RED}✗ Sai định dạng! Dùng DD/MM/YYYY (vd: 25/12/2026).{RESET}")


def input_tags() -> list:
    section_header("Tags")
    print(f"  {DIM}Nhập tags cách nhau bằng dấu phẩy (vd: python, backend, urgent){RESET}")
    raw = input(f"\n  {CYAN}→ Tags: {RESET}").strip()
    return [t.strip().lower() for t in raw.split(",") if t.strip()] if raw else []


def show_preview(task: dict):
    """Hiện preview task trước khi xác nhận lưu."""
    p = task["priority"]
    c = task["category"]
    deadline_str  = task["deadline"] or f"{DIM}Không có{RESET}"
    tags_str      = ", ".join(f"#{t}" for t in task["tags"]) or f"{DIM}Không có{RESET}"

    print(f"""
{MAGENTA}╔══════════════════════════════════════════════════════╗
║  {BOLD}  📋 XEM TRƯỚC TASK  {RESET}{MAGENTA}                               ║
╠══════════════════════════════════════════════════════╣{RESET}
  {BOLD}ID       :{RESET}  #{task['id']}
  {BOLD}Tiêu đề  :{RESET}  {YELLOW}{BOLD}{task['title']}{RESET}
  {BOLD}Mô tả    :{RESET}  {task['description'] or DIM + 'Không có' + RESET}
  {BOLD}Ưu tiên  :{RESET}  {p['color']}{p['icon']} {p['label']}{RESET}
  {BOLD}Danh mục :{RESET}  {c['icon']}  {c['label']}
  {BOLD}Deadline :{RESET}  {deadline_str}
  {BOLD}Tags     :{RESET}  {CYAN}{tags_str}{RESET}
  {BOLD}Tạo lúc  :{RESET}  {DIM}{task['created_at']}{RESET}
{MAGENTA}╚══════════════════════════════════════════════════════╝{RESET}""")


# ─── Core ───────────────────────────────────────────────────────────────────

def create_task() -> dict | None:
    """
    Tạo task mới thông qua giao diện CLI tương tác.
    Returns:
        dict: Task vừa tạo nếu thành công.
        None: Nếu người dùng hủy.
    """
    clear_screen()
    print_banner()
    typing_effect(f"  {DIM}Hãy điền thông tin để tạo task mới...{RESET}", 0.02)

    # Thu thập thông tin
    section_header("Thông tin cơ bản")
    title       = ask("Tiêu đề task", required=True,  hint="vd: Hoàn thành báo cáo tháng 11")
    description = ask("Mô tả chi tiết", required=False, hint="Mô tả ngắn gọn về task")
    priority    = choose_priority()
    category    = choose_category()
    deadline    = input_deadline()
    tags        = input_tags()

    # Tạo object task
    task_id  = get_next_id()
    now_str  = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    new_task = {
        "id":           task_id,
        "uuid":         str(uuid.uuid4()),
        "title":        title,
        "description":  description,
        "priority":     priority,
        "category":     category,
        "deadline":     deadline,
        "tags":         tags,
        "status":       "todo",
        "created_at":   now_str,
        "updated_at":   now_str,
        "completed_at": None,
    }

    # Preview & xác nhận
    show_preview(new_task)
    print(f"\n  {YELLOW}Bạn có muốn lưu task này không?{RESET}")
    print(f"  [{GREEN}Y{RESET}] Lưu   [{RED}N{RESET}] Hủy   [{CYAN}E{RESET}] Chỉnh sửa lại\n")
    confirm = input(f"  {CYAN}→ Lựa chọn: {RESET}").strip().lower()

    if confirm == "e":
        print(f"\n  {YELLOW}↺ Quay lại từ đầu...{RESET}\n")
        time.sleep(0.6)
        return create_task()  # Đệ quy để sửa lại

    if confirm != "y":
        print(f"\n  {RED}✗ Đã hủy tạo task.{RESET}\n")
        return None

    # Lưu vào JSON
    tasks = load_tasks()
    tasks.append(new_task)
    save_tasks(tasks)
    loading_bar("Đang lưu")

    print(f"\n  {GREEN}{BOLD}🎉 Task #{task_id} đã được tạo thành công!{RESET}")
    print(f"  {DIM}  \"{title}\"{RESET}\n")
    return new_task


# ─── Entry point ────────────────────────────────────────────────────────────
if __name__ == "__main__":
    create_task()
