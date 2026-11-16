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
from DeleteTask.delete_task import delete_task_menu
from SearchTask.search_task import search_task_menu
from TaskStatistics.task_statistics import statistics_menu
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

        print(f"  📊 {BOLD}Tổng quan:{RESET} Đang có {GREEN}{BOLD}{len(tasks)}{RESET} task hoạt động | {YELLOW}{BOLD}{len(deleted)}{RESET} task trong thùng rác\n")
        print(f"""  {BOLD}DANH SÁCH CHỨC NĂNG:{RESET}
    {GREEN}{BOLD}[1]{RESET} ➕  {BOLD}Tạo công việc mới (Create Task){RESET}
    {RED}{BOLD}[2]{RESET} 🗑️   {BOLD}Xóa & Quản lý Thùng rác (Delete Task & Recycle Bin){RESET}
    {CYAN}[3]{RESET} 📋  Xem danh sách công việc (View Task - Tích hợp nhanh)
    {BLUE}{BOLD}[4]{RESET} 🔍  {BOLD}Tìm kiếm công việc (Search Task){RESET}
    {MAGENTA}{BOLD}[5]{RESET} 📊  {BOLD}Thống kê & Báo cáo (Task Statistics){RESET}
    {YELLOW}[0]{RESET} 🚪  Thoát ứng dụng
""")
        choice = input(f"  {CYAN}→ Nhập lựa chọn (0-5): {RESET}").strip()

        if choice == "1":
            create_task()
            input(f"\n  {DIM}Nhấn Enter để quay lại menu chính...{RESET}")
        elif choice == "2":
            delete_task_menu()
        elif choice == "3":
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
                    print(f"  #{t.get('id')} {c_icon} [{c_label}] {p_label} - {BOLD}{t.get('title')}{RESET}{dl}")
            input(f"\n  {DIM}Nhấn Enter để quay lại menu chính...{RESET}")
        elif choice == "4":
            search_task_menu()
        elif choice == "5":
            statistics_menu()
        elif choice == "0":
            print(f"\n  {GREEN}Cảm ơn bạn đã sử dụng TeamTodo! Hẹn gặp lại! 👋{RESET}\n")
            break
        else:
            print(f"  {RED}Lựa chọn không hợp lệ!{RESET}")
            time.sleep(1)

if __name__ == "__main__":
    main()
