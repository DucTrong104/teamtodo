"""
CompleteTask - Đánh dấu hoàn thành task, hoàn tác và xem lịch sử hoàn thành
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

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_banner():
    print(f"""
{GREEN}╔══════════════════════════════════════════════════════╗
║  {BOLD}{WHITE}        ✅   HOÀN THÀNH CÔNG VIỆC  ✅        {RESET}{GREEN}      ║
║  {DIM}{WHITE}   TeamTodo · Complete Task Module             {RESET}{GREEN}║
╚══════════════════════════════════════════════════════╝{RESET}
""")

def section_header(title: str):
    line = "─" * (44 - len(title))
    print(f"\n  {GREEN}┌─ {BOLD}{title} {RESET}{GREEN}{line}┐{RESET}")

def loading_bar(label: str = "Đang xử lý", duration: float = 0.5):
    total = 20
    for i in range(total + 1):
        filled = "█" * i
        empty  = "░" * (total - i)
        pct    = int(i / total * 100)
        print(f"\r  {CYAN}{label}...{RESET} [{GREEN}{filled}{DIM}{empty}{RESET}] {BOLD}{pct}%{RESET}", end="", flush=True)
        time.sleep(duration / total)
    print(f"\r  {GREEN}✔ Thành công!{RESET}{' ' * 35}")

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
        st_badge = f"{GREEN}[✔️ Đã xong]{RESET}"
    elif st == "in_progress":
        st_badge = f"{BLUE}[⏳ Đang làm]{RESET}"
    else:
        st_badge = f"{YELLOW}[📋 Cần làm]{RESET}"

    done_time = f" {DIM}(Xong lúc: {task.get('completed_at')}){RESET}" if task.get("completed_at") else ""
    print(f"  {BOLD}#{task.get('id', '?')}{RESET} {st_badge} | {cat_icon} [{cat_label}] | {prio_color}{prio_icon} {prio_label}{RESET} | {BOLD}{task.get('title', 'Untitled')}{RESET}{done_time}")

def find_task_by_id(tasks: list, task_id: int):
    for idx, t in enumerate(tasks):
        if t.get("id") == task_id:
            return idx, t
    return -1, None

# ─── 1. Hoàn thành 1 task ──────────────────────────────────────────────────
def complete_single_task():
    tasks = load_tasks()
    if not tasks:
        print(f"\n  {YELLOW}⚠ Hiện tại không có task nào trong danh sách!{RESET}\n")
        return

    # Lọc danh sách task chưa hoàn thành
    pending_tasks = [t for t in tasks if t.get("status") != "completed"]
    if not pending_tasks:
        print(f"\n  {GREEN}🎉 Tuyệt vời! Bạn đã hoàn thành tất cả các task trong danh sách!{RESET}\n")
        return

    section_header("Danh sách công việc đang chờ xử lý")
    for t in pending_tasks:
        display_task_compact(t)

    val = input(f"\n  {CYAN}→ Nhập ID task muốn đánh dấu hoàn thành (Enter để quay lại): {RESET}").strip()
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

    if task.get("status") == "completed":
        print(f"\n  {YELLOW}ℹ️ Task #{task_id} \"{task.get('title')}\" đã hoàn thành từ trước!{RESET}\n")
        return

    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    task["status"] = "completed"
    task["completed_at"] = now_str
    task["updated_at"] = now_str

    save_tasks(tasks)
    loading_bar("Đang cập nhật trạng thái")
    print(f"""
  {GREEN}{BOLD}🎉 CHÚC MỪNG BẠN ĐÃ HOÀN THÀNH TỐT CÔNG VIỆC!{RESET}
  {BOLD}Task #{task_id}:{RESET} {YELLOW}\"{task.get('title')}\"{RESET}
  {DIM}Thời gian hoàn thành: {now_str}{RESET}
""")

# ─── 2. Hoàn thành hàng loạt ───────────────────────────────────────────────
def complete_multiple_tasks():
    tasks = load_tasks()
    pending = [t for t in tasks if t.get("status") != "completed"]
    if not pending:
        print(f"\n  {GREEN}🎉 Tất cả task đều đã hoàn thành!{RESET}\n")
        return

    section_header("Hoàn thành nhiều task cùng lúc")
    for t in pending:
        display_task_compact(t)

    raw = input(f"\n  {CYAN}→ Nhập các ID cần hoàn thành (cách nhau bởi dấu phẩy, vd: 1, 2, 4): {RESET}").strip()
    if not raw:
        return

    target_ids = set()
    for item in raw.split(","):
        item = item.strip()
        if item.isdigit():
            target_ids.add(int(item))

    if not target_ids:
        print(f"  {RED}✗ Không có ID hợp lệ nào được nhập!{RESET}")
        return

    count = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    for t in tasks:
        if t.get("id") in target_ids and t.get("status") != "completed":
            t["status"] = "completed"
            t["completed_at"] = now_str
            t["updated_at"] = now_str
            count += 1

    if count > 0:
        save_tasks(tasks)
        loading_bar("Đang cập nhật hàng loạt")
        print(f"\n  {GREEN}✔ Đã đánh dấu hoàn thành {count} task thành công!{RESET}\n")
    else:
        print(f"\n  {YELLOW}⚠ Không có task nào được cập nhật (ID không tồn tại hoặc đã hoàn thành).{RESET}\n")

# ─── 3. Hoàn tác / Mở lại task đã hoàn thành ──────────────────────────────
def reopen_task():
    tasks = load_tasks()
    completed_tasks = [t for t in tasks if t.get("status") == "completed"]
    if not completed_tasks:
        print(f"\n  {YELLOW}Chưa có task nào ở trạng thái hoàn thành.{RESET}\n")
        return

    section_header("Danh sách Task đã hoàn thành")
    for t in completed_tasks:
        display_task_compact(t)

    val = input(f"\n  {CYAN}→ Nhập ID task muốn mở lại (Chuyển về Cần làm): {RESET}").strip()
    if not val:
        return

    try:
        task_id = int(val)
    except ValueError:
        print(f"  {RED}✗ ID không hợp lệ!{RESET}")
        return

    idx, task = find_task_by_id(tasks, task_id)
    if not task:
        print(f"  {RED}✗ Không tìm thấy task #{task_id}!{RESET}")
        return

    if task.get("status") != "completed":
        print(f"  {YELLOW}Task này chưa hoàn thành nên không cần mở lại.{RESET}")
        return

    task["status"] = "todo"
    task["completed_at"] = None
    task["updated_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    save_tasks(tasks)
    loading_bar("Đang mở lại task")
    print(f"\n  {GREEN}✔ Đã chuyển task #{task_id} \"{task.get('title')}\" về trạng thái [Cần làm].{RESET}\n")

# ─── 4. Xem danh sách đã hoàn thành ─────────────────────────────────────────
def view_completed_tasks():
    tasks = load_tasks()
    completed = [t for t in tasks if t.get("status") == "completed"]
    
    clear_screen()
    print_banner()
    section_header(f"Danh sách Task đã hoàn thành ({len(completed)} task)")
    if not completed:
        print(f"  {YELLOW}Chưa có task nào được hoàn thành.{RESET}\n")
    else:
        for t in completed:
            display_task_compact(t)
        print()

# ─── Menu chính của Complete Task Module ────────────────────────────────────
def complete_task_menu():
    while True:
        clear_screen()
        print_banner()
        tasks = load_tasks()
        done_count = sum(1 for t in tasks if t.get("status") == "completed")
        total_count = len(tasks)
        pct = int(done_count / total_count * 100) if total_count > 0 else 0

        print(f"  📊 {BOLD}Tiến độ hoàn thành:{RESET} {GREEN}{BOLD}{done_count}/{total_count}{RESET} task ({pct}%)\n")

        print(f"""  {BOLD}TÙY CHỌN HOÀN THÀNH:{RESET}
    {GREEN}{BOLD}[1]{RESET} ✅  {BOLD}Đánh dấu 1 task đã hoàn thành (Complete Task){RESET}
    {CYAN}[2]{RESET} ⏩  Hoàn thành nhiều task cùng lúc (Bulk Complete)
    {YELLOW}[3]{RESET} ↺   Mở lại task đã hoàn thành (Re-open Task)
    {BLUE}[4]{RESET} 📜  Xem danh sách các task đã hoàn thành
    {WHITE}[0]{RESET} 🚪  Quay lại Menu chính
""")
        choice = input(f"  {CYAN}→ Lựa chọn của bạn (0-4): {RESET}").strip()

        if choice == "1":
            complete_single_task()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "2":
            complete_multiple_tasks()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "3":
            reopen_task()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "4":
            view_completed_tasks()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "0":
            break
        else:
            print(f"  {RED}Lựa chọn không hợp lệ!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    complete_task_menu()
