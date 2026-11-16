"""
DeleteTask - Xóa task với các tính năng sáng tạo:
- Soft Delete (Chuyển vào thùng rác / Recycle Bin)
- Hard Delete (Xóa vĩnh viễn với mã bảo vệ / confirm word ngẫu nhiên)
- Khôi phục task đã xóa (Restore from Trash)
- Xem thùng rác & Dọn sạch thùng rác (Empty Trash)
- Xóa hàng loạt (Bulk Delete theo khoảng ID, trạng thái hoặc từ khóa)
"""

import sys
import os
import time
import random
import string
from datetime import datetime

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from JsonDataStorage.storage import (
    load_tasks,
    save_tasks,
    load_deleted_tasks,
    save_deleted_tasks,
)

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
{RED}╔══════════════════════════════════════════════════════╗
║  {BOLD}{WHITE}        🗑️   QUẢN LÝ XÓA TASK  🗑️        {RESET}{RED}           ║
║  {DIM}{WHITE}   TeamTodo · Delete & Recycle Bin Module      {RESET}{RED}     ║
╚══════════════════════════════════════════════════════╝{RESET}
""")

def section_header(title: str):
    line = "─" * (44 - len(title))
    print(f"\n  {RED}┌─ {BOLD}{title} {RESET}{RED}{line}┐{RESET}")

def loading_bar(label: str = "Đang xử lý", duration: float = 0.6):
    total = 20
    for i in range(total + 1):
        filled = "█" * i
        empty  = "░" * (total - i)
        pct    = int(i / total * 100)
        print(f"\r  {YELLOW}{label}...{RESET} [{RED}{filled}{DIM}{empty}{RESET}] {BOLD}{pct}%{RESET}", end="", flush=True)
        time.sleep(duration / total)
    print(f"\r  {GREEN}✔ Xong!{RESET}{' ' * 35}")

def display_task_compact(task: dict, in_trash: bool = False):
    prio_color = task.get("priority", {}).get("color", "") if isinstance(task.get("priority"), dict) else ""
    prio_label = task.get("priority", {}).get("label", "NORMAL") if isinstance(task.get("priority"), dict) else str(task.get("priority", ""))
    cat_label  = task.get("category", {}).get("label", "Chung") if isinstance(task.get("category"), dict) else str(task.get("category", ""))
    cat_icon   = task.get("category", {}).get("icon", "📌") if isinstance(task.get("category"), dict) else "📌"
    
    trash_info = f" {DIM}(Xóa lúc: {task.get('deleted_at', 'N/A')}){RESET}" if in_trash else ""
    print(f"  {BOLD}#{task.get('id', '?')}{RESET} | {cat_icon} [{cat_label}] | {prio_color}{prio_label}{RESET} | {BOLD}{task.get('title', 'Untitled')}{RESET}{trash_info}")

def find_task_by_id(tasks: list, task_id: int):
    for idx, t in enumerate(tasks):
        if t.get("id") == task_id:
            return idx, t
    return -1, None

# ─── 1. Soft Delete (Đưa vào thùng rác) ────────────────────────────────────
def soft_delete_task():
    tasks = load_tasks()
    if not tasks:
        print(f"\n  {YELLOW}⚠ Hiện tại không có task nào trong danh sách!{RESET}\n")
        return

    section_header("Danh sách Task hiện tại")
    for t in tasks:
        display_task_compact(t)

    print(f"\n  {CYAN}Nhập ID task muốn chuyển vào thùng rác (hoặc nhấn Enter để quay lại):{RESET}")
    val = input(f"  {YELLOW}→ ID: {RESET}").strip()
    if not val:
        return

    try:
        task_id = int(val)
    except ValueError:
        print(f"  {RED}✗ ID phải là số nguyên!{RESET}")
        return

    idx, task = find_task_by_id(tasks, task_id)
    if not task:
        print(f"  {RED}✗ Không tìm thấy task mang ID #{task_id}!{RESET}")
        return

    print(f"\n  {YELLOW}Bạn có chắc muốn chuyển task #{task_id} \"{task.get('title')}\" vào thùng rác? [y/N]: {RESET}", end="")
    confirm = input().strip().lower()
    if confirm != "y":
        print(f"  {DIM}Đã hủy thao tác.{RESET}")
        return

    # Gắn metadata ngày xóa & lý do xóa
    task["deleted_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    reason = input(f"  {CYAN}Lý do xóa (tùy chọn, Enter để bỏ qua): {RESET}").strip()
    task["delete_reason"] = reason or "Người dùng xóa thông thường"

    # Lưu vào deleted và gỡ khỏi tasks
    deleted_tasks = load_deleted_tasks()
    deleted_tasks.append(task)
    tasks.pop(idx)

    save_tasks(tasks)
    save_deleted_tasks(deleted_tasks)

    loading_bar("Đang chuyển vào thùng rác")
    print(f"\n  {GREEN}✔ Đã chuyển task #{task_id} vào thùng rác an toàn!{RESET}")
    print(f"  {DIM}Gợi ý: Bạn có thể khôi phục lại bất kỳ lúc nào từ menu Thùng rác.{RESET}\n")

# ─── 2. Hard Delete (Xóa vĩnh viễn với mã bảo vệ ngẫu nhiên) ─────────────
def hard_delete_task():
    tasks = load_tasks()
    if not tasks:
        print(f"\n  {YELLOW}⚠ Hiện không có task nào để xóa!{RESET}\n")
        return

    section_header("Xóa vĩnh viễn (Cảnh báo: Không thể hoàn tác!)")
    for t in tasks:
        display_task_compact(t)

    val = input(f"\n  {RED}→ Nhập ID task cần xóa vĩnh viễn (Enter để hủy): {RESET}").strip()
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

    # Tạo mã an toàn 4 ký tự ngẫu nhiên
    confirm_code = "".join(random.choices(string.ascii_uppercase + string.digits, k=4))
    print(f"""
  {RED}{BOLD}🚨 CẢNH BÁO AN TOÀN:{RESET}
  Task #{task_id}: {BOLD}\"{task.get('title')}\"{RESET} sẽ bị {RED}{BOLD}XÓA VĨNH VIỄN{RESET}!
  Dữ liệu không thể khôi phục sau khi xóa.
  
  Để xác nhận, vui lòng gõ chính xác mã: {YELLOW}{BOLD}{confirm_code}{RESET}
""")
    user_code = input(f"  {CYAN}→ Nhập mã: {RESET}").strip()
    if user_code != confirm_code:
        print(f"\n  {RED}✗ Mã xác nhận không khớp! Hủy lệnh xóa.{RESET}\n")
        return

    tasks.pop(idx)
    save_tasks(tasks)
    loading_bar("Đang xóa vĩnh viễn")
    print(f"\n  {RED}✔ Đã xóa vĩnh viễn task #{task_id} khỏi hệ thống!{RESET}\n")

# ─── 3. Thùng rác & Khôi phục (Recycle Bin & Restore) ──────────────────────
def view_recycle_bin():
    deleted_tasks = load_deleted_tasks()
    if not deleted_tasks:
        print(f"\n  {GREEN}🍃 Thùng rác hiện đang trống!{RESET}\n")
        return

    section_header("Thùng rác (Recycle Bin)")
    for t in deleted_tasks:
        display_task_compact(t, in_trash=True)
        if t.get("delete_reason"):
            print(f"    {DIM}↳ Lý do: {t['delete_reason']}{RESET}")

    print(f"""
  {BOLD}Tùy chọn thùng rác:{RESET}
    {CYAN}[R]{RESET} Khôi phục 1 task (Restore)
    {CYAN}[A]{RESET} Khôi phục TẤT CẢ (Restore All)
    {RED}[E]{RESET} Dọn sạch thùng rác (Empty Trash - Xóa vĩnh viễn)
    {YELLOW}[B]{RESET} Quay lại menu trước
""")
    choice = input(f"  {CYAN}→ Chọn thao tác: {RESET}").strip().lower()

    if choice == "r":
        restore_single_task()
    elif choice == "a":
        restore_all_tasks()
    elif choice == "e":
        empty_recycle_bin()

def restore_single_task():
    deleted_tasks = load_deleted_tasks()
    if not deleted_tasks:
        return

    val = input(f"\n  {CYAN}→ Nhập ID task muốn khôi phục: {RESET}").strip()
    try:
        task_id = int(val)
    except ValueError:
        print(f"  {RED}✗ ID không hợp lệ!{RESET}")
        return

    idx, task = find_task_by_id(deleted_tasks, task_id)
    if not task:
        print(f"  {RED}✗ Không tìm thấy task #{task_id} trong thùng rác!{RESET}")
        return

    # Xóa metadata thùng rác
    task.pop("deleted_at", None)
    task.pop("delete_reason", None)
    task["restored_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    tasks = load_tasks()
    tasks.append(task)
    deleted_tasks.pop(idx)

    save_tasks(tasks)
    save_deleted_tasks(deleted_tasks)

    loading_bar("Đang khôi phục task")
    print(f"\n  {GREEN}✔ Đã khôi phục thành công task #{task_id} về danh sách chính!{RESET}\n")

def restore_all_tasks():
    deleted_tasks = load_deleted_tasks()
    if not deleted_tasks:
        return

    confirm = input(f"  {YELLOW}Bạn có chắc muốn khôi phục toàn bộ {len(deleted_tasks)} task? [y/N]: {RESET}").strip().lower()
    if confirm != "y":
        return

    tasks = load_tasks()
    for t in deleted_tasks:
        t.pop("deleted_at", None)
        t.pop("delete_reason", None)
        t["restored_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        tasks.append(t)

    save_tasks(tasks)
    save_deleted_tasks([])

    loading_bar("Đang khôi phục toàn bộ")
    print(f"\n  {GREEN}✔ Toàn bộ task đã được đưa trở lại danh sách chính!{RESET}\n")

def empty_recycle_bin():
    deleted_tasks = load_deleted_tasks()
    if not deleted_tasks:
        return

    print(f"\n  {RED}{BOLD}🚨 CẢNH BÁO: Hành động này sẽ xóa vĩnh viễn tất cả {len(deleted_tasks)} task trong thùng rác!{RESET}")
    confirm = input(f"  {RED}Gõ 'CLEAR' để dọn sạch: {RESET}").strip()
    if confirm != "CLEAR":
        print(f"  {DIM}Đã hủy thao tác.{RESET}")
        return

    save_deleted_tasks([])
    loading_bar("Đang dọn sạch thùng rác")
    print(f"\n  {GREEN}✔ Thùng rác đã được dọn sạch hoàn toàn!{RESET}\n")

# ─── 4. Xóa hàng loạt (Bulk Delete thông minh) ───────────────────────────
def bulk_delete_tasks():
    tasks = load_tasks()
    if not tasks:
        print(f"\n  {YELLOW}⚠ Không có task nào để xóa.{RESET}\n")
        return

    section_header("Xóa hàng loạt (Bulk Delete)")
    print(f"""
  {BOLD}Chọn phương thức xóa hàng loạt:{RESET}
    {CYAN}1.{RESET} Xóa theo danh sách ID (vd: 1, 3, 5)
    {CYAN}2.{RESET} Xóa tất cả các task đã hoàn thành (status = completed)
    {CYAN}3.{RESET} Xóa các task chứa từ khóa trong tiêu đề
    {CYAN}4.{RESET} Hủy bỏ
""")
    sub_c = input(f"  {CYAN}→ Chọn (1-4): {RESET}").strip()
    targets = []

    if sub_c == "1":
        raw = input(f"  {CYAN}Nhập các ID cách nhau bởi dấu phẩy: {RESET}").strip()
        ids_to_del = set()
        for x in raw.split(","):
            x = x.strip()
            if x.isdigit():
                ids_to_del.add(int(x))
        targets = [t for t in tasks if t.get("id") in ids_to_del]

    elif sub_c == "2":
        targets = [t for t in tasks if t.get("status") == "completed"]

    elif sub_c == "3":
        kw = input(f"  {CYAN}Nhập từ khóa cần tìm để xóa: {RESET}").strip().lower()
        if kw:
            targets = [t for t in tasks if kw in t.get("title", "").lower()]

    else:
        return

    if not targets:
        print(f"\n  {YELLOW}Không tìm thấy task nào phù hợp tiêu chí!{RESET}\n")
        return

    print(f"\n  {YELLOW}Tìm thấy {len(targets)} task cần xóa:{RESET}")
    for t in targets:
        display_task_compact(t)

    print(f"\n  {CYAN}Đưa vào thùng rác [1] hay Xóa vĩnh viễn [2]? (Enter để hủy): {RESET}", end="")
    del_mode = input().strip()

    target_ids = {t["id"] for t in targets}
    remaining_tasks = [t for t in tasks if t["id"] not in target_ids]

    if del_mode == "1":
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        for t in targets:
            t["deleted_at"] = now_str
            t["delete_reason"] = "Bulk delete"
        deleted = load_deleted_tasks()
        deleted.extend(targets)
        save_deleted_tasks(deleted)
        save_tasks(remaining_tasks)
        loading_bar("Đang di chuyển vào thùng rác")
        print(f"\n  {GREEN}✔ Đã chuyển {len(targets)} task vào thùng rác.{RESET}\n")

    elif del_mode == "2":
        confirm = input(f"  {RED}Nhập 'YES' để xác nhận xóa vĩnh viễn {len(targets)} task: {RESET}").strip()
        if confirm == "YES":
            save_tasks(remaining_tasks)
            loading_bar("Đang xóa vĩnh viễn")
            print(f"\n  {RED}✔ Đã xóa vĩnh viễn {len(targets)} task.{RESET}\n")
        else:
            print(f"  {DIM}Đã hủy thao tác.{RESET}")

# ─── Main Menu của Delete Task Module ──────────────────────────────────────
def delete_task_menu():
    while True:
        clear_screen()
        print_banner()
        tasks = load_tasks()
        deleted = load_deleted_tasks()

        print(f"  {DIM}Thống kê: Hiện có {BOLD}{len(tasks)}{RESET}{DIM} task đang hoạt động | {BOLD}{len(deleted)}{RESET}{DIM} task trong thùng rác{RESET}\n")

        print(f"""  {BOLD}DANH MỤC THAO TÁC:{RESET}
    {CYAN}1.{RESET} 🗑️  Chuyển task vào thùng rác (Soft Delete - Khuyên dùng)
    {CYAN}2.{RESET} ⚡  Xóa vĩnh viễn task (Hard Delete - Có mã bảo vệ)
    {CYAN}3.{RESET} 📦  Mở Thùng rác & Khôi phục task (Recycle Bin)
    {CYAN}4.{RESET} 🧹  Xóa hàng loạt (Bulk Delete thông minh)
    {CYAN}0.{RESET} 🚪  Thoát về Menu chính
""")
        choice = input(f"  {CYAN}→ Lựa chọn của bạn (0-4): {RESET}").strip()

        if choice == "1":
            soft_delete_task()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "2":
            hard_delete_task()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "3":
            view_recycle_bin()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "4":
            bulk_delete_tasks()
            input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")
        elif choice == "0":
            print(f"\n  {GREEN}Tạm biệt!{RESET}\n")
            break
        else:
            print(f"\n  {RED}Lựa chọn không hợp lệ! Vui lòng chọn từ 0-4.{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    delete_task_menu()
