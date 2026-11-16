"""
TeamTodo - Ứng dụng quản lý công việc cá nhân
Menu điều hướng chính tích hợp các module.
"""

import sys
import os
import time

# Đường dẫn src
sys.path.insert(0, os.path.dirname(__file__))

from CreateTask.create_task import create_task
from UpdateTask.update_task import update_task_menu
from CompleteTask.complete_task import complete_task_menu
from DeleteTask.delete_task import delete_task_menu
from JsonDataStorage.storage import load_tasks, load_deleted_tasks

# ANSI Colors
RESET   = "\033[0m"
BOLD    = "\033[1m"
DIM     = "\033[2m"
CYAN    = "\033[96m"
GREEN   = "\033[92m"
YELLOW  = "\033[93m"
RED     = "\033[91m"
MAGENTA = "\033[95m"
BLUE    = "\033[94m"

def clear_screen():
    os.system("cls" if os.name == "nt" else "clear")

def print_home_banner():
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════╗
║  {BOLD}{MAGENTA}        🌟 TEAMTODO APPLICATION 🌟        {RESET}{CYAN}         ║
║  {DIM}   Ứng dụng quản lý công việc cá nhân thông minh    {RESET}{CYAN}║
╚══════════════════════════════════════════════════════╝{RESET}
""")

def main():
    while True:
        clear_screen()
        print_home_banner()
        tasks = load_tasks()
        deleted = load_deleted_tasks()
        completed_count = sum(1 for t in tasks if t.get("status") == "completed")

        print(f"  📊 {BOLD}Tổng quan:{RESET} Đang có {GREEN}{BOLD}{len(tasks)}{RESET} task hoạt động ({GREEN}{completed_count} hoàn thành{RESET}) | {YELLOW}{BOLD}{len(deleted)}{RESET} task trong thùng rác\n")
        print(f"""  {BOLD}DANH SÁCH CHỨC NĂNG:{RESET}
    {GREEN}{BOLD}[1]{RESET} ➕  {BOLD}Tạo công việc mới (Create Task){RESET}
    {YELLOW}{BOLD}[2]{RESET} ✏️   {BOLD}Cập nhật công việc (Update Task){RESET}
    {GREEN}{BOLD}[3]{RESET} ✅  {BOLD}Đánh dấu hoàn thành (Complete Task){RESET}
    {RED}{BOLD}[4]{RESET} 🗑️   {BOLD}Xóa & Quản lý Thùng rác (Delete Task & Recycle Bin){RESET}
    {CYAN}[5]{RESET} 📋  Xem danh sách công việc (View Task)
    {YELLOW}[0]{RESET} 🚪  Thoát ứng dụng
""")
        choice = input(f"  {CYAN}→ Nhập lựa chọn (0-5): {RESET}").strip()

        if choice == "1":
            create_task()
            input(f"\n  {DIM}Nhấn Enter để quay lại menu chính...{RESET}")
        elif choice == "2":
            update_task_menu()
        elif choice == "3":
            complete_task_menu()
        elif choice == "4":
            delete_task_menu()
        elif choice == "5":
            clear_screen()
            print_home_banner()
            print(f"  {BOLD}📋 DANH SÁCH TASK HIỆN CÓ:{RESET}\n")
            if not tasks:
                print(f"  {YELLOW}Chưa có task nào. Hãy chọn [1] để tạo task mới!{RESET}")
            else:
                for t in tasks:
                    p = t.get("priority", {})
                    p_label = p.get("label", "NORMAL") if isinstance(p, dict) else str(p)
                    c = t.get("category", {})
                    c_label = c.get("label", "Khác") if isinstance(c, dict) else str(c)
                    c_icon = c.get("icon", "📌") if isinstance(c, dict) else "📌"
                    dl = f" | ⏰ {t.get('deadline')}" if t.get("deadline") else ""
                    st = t.get("status", "todo")
                    st_str = f"{GREEN}[✔️ Xong]{RESET}" if st == "completed" else f"{YELLOW}[⏳ Chờ]{RESET}"
                    print(f"  #{t.get('id')} {st_str} {c_icon} [{c_label}] {p_label} - {BOLD}{t.get('title')}{RESET}{dl}")
            input(f"\n  {DIM}Nhấn Enter để quay lại menu chính...{RESET}")
        elif choice == "0":
            print(f"\n  {GREEN}Cảm ơn bạn đã sử dụng TeamTodo! Hẹn gặp lại! 👋{RESET}\n")
            break
        else:
            print(f"  {RED}Lựa chọn không hợp lệ!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
