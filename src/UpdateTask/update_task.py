"""
UpdateTask - Cập nhật thông tin task với giao diện tương tác CLI có màu sắc & kiểm tra dữ liệu
"""

import sys
import os
import time
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from JsonDataStorage.storage import load_tasks, save_tasks

# ─── ANSI Colors ───────────────────────────────────────────────────────────
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
RED     = "\033[91m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
BLUE    = "\033[94m"
MAGENTA = "\033[95m"
CYAN    = "\033[96m"
WHITE   = "\033[97m"
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

STATUS_CHOICES = {
    "1": {"label": "Chờ xử lý (Todo)",        "value": "todo",        "color": YELLOW},
    "2": {"label": "Đang làm (In Progress)",  "value": "in_progress", "color": BLUE},
    "3": {"label": "Đã hoàn thành (Completed)", "value": "completed",   "color": GREEN},
}

# ─── UI Helpers ─────────────────────────────────────────────────────────────
def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(f"""
{YELLOW}╔══════════════════════════════════════════════════════╗
║  {BOLD}{WHITE}        ✏️   CẬP NHẬT CÔNG VIỆC  ✏️        {RESET}{YELLOW}        ║
║  {DIM}{WHITE}   TeamTodo · Update Task Module               {RESET}{YELLOW}║
╚══════════════════════════════════════════════════════╝{RESET}
""")

def section_header(title: str):
    line = "─" * (44 - len(title))
    print(f"\n  {YELLOW}┌─ {BOLD}{title} {RESET}{YELLOW}{line}┐{RESET}")

def loading_bar(label: str = "Đang cập nhật", duration: float = 0.6):
    total = 20
    for i in range(total + 1):
        filled = "█" * i
        empty  = "░" * (total - i)
        pct    = int(i / total * 100)
        print(f"\r  {CYAN}{label}...{RESET} [{YELLOW}{filled}{DIM}{empty}{RESET}] {BOLD}{pct}%{RESET}", end="", flush=True)
        time.sleep(duration / total)
    print(f"\r  {GREEN}✔ Hoàn tất!{RESET}{' ' * 35}")

def display_task_compact(task: dict):
    p = task.get("priority", {})
    prio_color = p.get("color", "") if isinstance(p, dict) else ""
    prio_label = p.get("label", "NORMAL") if isinstance(p, dict) else str(p)
    prio_icon  = p.get("icon", "📌") if isinstance(p, dict) else ""
    
    c = task.get("category", {})
    cat_label  = c.get("label", "Chung") if isinstance(c, dict) else str(c)
    cat_icon   = c.get("icon", "📁") if isinstance(c, dict) else "📁"
    
    st = task.get("status", "todo")
    if st == "completed":
        st_badge = f"{GREEN}[Hoàn thành]{RESET}"
    elif st == "in_progress":
        st_badge = f"{BLUE}[Đang làm]{RESET}"
    else:
        st_badge = f"{YELLOW}[Cần làm]{RESET}"

    dl = f" | ⏰ {task.get('deadline')}" if task.get("deadline") else ""
    print(f"  {BOLD}#{task.get('id', '?')}{RESET} {st_badge} | {cat_icon} [{cat_label}] | {prio_color}{prio_icon} {prio_label}{RESET} | {BOLD}{task.get('title', 'Untitled')}{RESET}{dl}")

def find_task_by_id(tasks: list, task_id: int):
    for idx, t in enumerate(tasks):
        if t.get("id") == task_id:
            return idx, t
    return -1, None

# ─── Core Update Functions ──────────────────────────────────────────────────
def update_task_interactively(task: dict) -> dict:
    """Cho phép người dùng chỉnh sửa từng trường, nhấn Enter để giữ nguyên."""
    print(f"\n  {DIM}Nhấn {BOLD}[Enter]{RESET}{DIM} nếu muốn giữ nguyên thông tin hiện tại.{RESET}")

    # 1. Tiêu đề
    section_header("1. Tiêu đề")
    print(f"  {DIM}Hiện tại: {RESET}{BOLD}{task.get('title')}{RESET}")
    new_title = input(f"  {CYAN}→ Tiêu đề mới: {RESET}").strip()
    if new_title:
        task["title"] = new_title

    # 2. Mô tả
    section_header("2. Mô tả chi tiết")
    print(f"  {DIM}Hiện tại: {RESET}{task.get('description') or '(Trống)'}")
    new_desc = input(f"  {CYAN}→ Mô tả mới: {RESET}").strip()
    if new_desc:
        task["description"] = new_desc

    # 3. Mức độ ưu tiên
    section_header("3. Mức độ ưu tiên")
    cur_p = task.get("priority", {})
    cur_p_name = cur_p.get("label", "NORMAL") if isinstance(cur_p, dict) else str(cur_p)
    print(f"  {DIM}Hiện tại: {RESET}{cur_p_name}")
    for k, v in PRIORITY_LEVELS.items():
        print(f"    {BOLD}{k}.{RESET} {v['color']}{v['icon']} {v['label']}{RESET}")
    p_choice = input(f"  {CYAN}→ Chọn (1-4) hoặc Enter để giữ nguyên: {RESET}").strip()
    if p_choice in PRIORITY_LEVELS:
        task["priority"] = PRIORITY_LEVELS[p_choice]

    # 4. Danh mục
    section_header("4. Danh mục")
    cur_c = task.get("category", {})
    cur_c_name = cur_c.get("label", "Khác") if isinstance(cur_c, dict) else str(cur_c)
    print(f"  {DIM}Hiện tại: {RESET}{cur_c_name}")
    for k, v in CATEGORIES.items():
        print(f"    {BOLD}{k}.{RESET} {v['icon']}  {v['label']}")
    c_choice = input(f"  {CYAN}→ Chọn (1-6) hoặc Enter để giữ nguyên: {RESET}").strip()
    if c_choice in CATEGORIES:
        task["category"] = CATEGORIES[c_choice]

    # 5. Deadline
    section_header("5. Hạn chót (Deadline)")
    print(f"  {DIM}Hiện tại: {RESET}{task.get('deadline') or '(Không có)'}")
    print(f"  {DIM}Gợi ý: Nhập DD/MM/YYYY, hoặc gõ 'none' để gỡ bỏ deadline, Enter để giữ nguyên{RESET}")
    while True:
        raw_dl = input(f"  {CYAN}→ Deadline mới: {RESET}").strip()
        if not raw_dl:
            break
        if raw_dl.lower() in ("none", "clear", "xoa", "x"):
            task["deadline"] = None
            break
        try:
            dt = datetime.strptime(raw_dl, "%d/%m/%Y")
            task["deadline"] = dt.strftime("%Y-%m-%d")
            break
        except ValueError:
            print(f"  {RED}✗ Sai định dạng! Vui lòng dùng DD/MM/YYYY (ví dụ: 30/11/2026).{RESET}")

    # 6. Tags
    section_header("6. Tags")
    cur_tags = task.get("tags", [])
    print(f"  {DIM}Hiện tại: {RESET}{', '.join(cur_tags) if cur_tags else '(Trống)'}")
    new_tags_raw = input(f"  {CYAN}→ Tags mới (cách nhau bởi dấu phẩy, Enter giữ nguyên): {RESET}").strip()
    if new_tags_raw:
        task["tags"] = [t.strip().lower() for t in new_tags_raw.split(",") if t.strip()]

    # 7. Trạng thái
    section_header("7. Trạng thái (Status)")
    cur_status = task.get("status", "todo")
    print(f"  {DIM}Hiện tại: {RESET}{cur_status}")
    for k, v in STATUS_CHOICES.items():
        print(f"    {BOLD}{k}.{RESET} {v['color']}{v['label']}{RESET}")
    s_choice = input(f"  {CYAN}→ Chọn (1-3) hoặc Enter để giữ nguyên: {RESET}").strip()
    if s_choice in STATUS_CHOICES:
        chosen_status = STATUS_CHOICES[s_choice]["value"]
        task["status"] = chosen_status
        if chosen_status == "completed":
            task["completed_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        else:
            task["completed_at"] = None

    # Cập nhật thời gian sửa
    task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return task

def update_single_task():
    """Hàm xử lý cập nhật 1 task."""
    tasks = load_tasks()
    if not tasks:
        print(f"\n  {YELLOW}⚠ Hiện tại không có task nào để cập nhật!{RESET}\n")
        return

    section_header("Danh sách task hiện tại")
    for t in tasks:
        display_task_compact(t)

    val = input(f"\n  {CYAN}→ Nhập ID task cần cập nhật (Enter để quay lại): {RESET}").strip()
    if not val:
        return

    try:
        task_id = int(val)
    except ValueError:
        print(f"  {RED}✗ ID phải là một số nguyên!{RESET}")
        return

    idx, task = find_task_by_id(tasks, task_id)
    if not task:
        print(f"  {RED}✗ Không tìm thấy task với ID #{task_id}!{RESET}")
        return

    print(f"\n  {GREEN}Bắt đầu cập nhật cho Task #{task_id}: \"{task.get('title')}\"{RESET}")
    
    # Tạo bản sao dự phòng
    updated_task = dict(task)
    update_task_interactively(updated_task)

    # Xác nhận lưu
    print(f"\n  {YELLOW}Bạn có muốn lưu các thay đổi cho Task #{task_id}? [Y/n]: {RESET}", end="")
    confirm = input().strip().lower()
    if confirm not in ("", "y", "yes"):
        print(f"\n  {DIM}Đã hủy thao tác cập nhật.{RESET}\n")
        return

    tasks[idx] = updated_task
    save_tasks(tasks)
    loading_bar("Đang lưu thay đổi")
    print(f"\n  {GREEN}{BOLD}🎉 Đã cập nhật thành công Task #{task_id}!{RESET}\n")

def update_task_menu():
    """Menu chính của Update Task."""
    while True:
        clear_screen()
        print_banner()
        tasks = load_tasks()
        print(f"  {DIM}Hệ thống đang có {BOLD}{len(tasks)}{RESET}{DIM} task hoạt động.{RESET}\n")

        print(f"""  {BOLD}TÙY CHỌN CẬP NHẬT:{RESET}
    {CYAN}1.{RESET} ✏️  Cập nhật thông tin chi tiết một task (Update Task)
    {CYAN}2.{RESET} 📋  Xem danh sách task hiện có
    {CYAN}0.{RESET} 🚪  Quay lại Menu chính
""")
        choice = input(f"  {CYAN}→ Nhập lựa chọn (0-2): {RESET}").strip()

        if choice == "1":
            update_single_task()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "2":
            clear_screen()
            print_banner()
            section_header("Danh sách Task hiện tại")
            tasks = load_tasks()
            if not tasks:
                print(f"  {YELLOW}Chưa có task nào.{RESET}")
            else:
                for t in tasks:
                    display_task_compact(t)
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "0":
            break
        else:
            print(f"  {RED}Lựa chọn không hợp lệ!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    update_task_menu()
