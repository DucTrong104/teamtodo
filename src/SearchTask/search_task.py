"""SearchTask Module - Tìm kiếm và lọc danh sách công việc.

Hỗ trợ tìm kiếm theo từ khóa (case-insensitive) trong cả title và description,
lọc nâng cao theo trạng thái (status) hoặc mức độ ưu tiên (priority),
cùng giao diện CLI tương tác thân thiện có màu sắc.
"""

from datetime import datetime
import os
import sys
from typing import Any, Dict, List, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))
from JsonDataStorage.storage import load_tasks

# ─── ANSI Colors ───────────────────────────────────────────────────────────
RESET = "\033[0m"
BOLD = "\033[1m"
DIM = "\033[2m"
RED = "\033[91m"
GREEN = "\033[92m"
YELLOW = "\033[93m"
BLUE = "\033[94m"
MAGENTA = "\033[95m"
CYAN = "\033[96m"
WHITE = "\033[97m"


def _extract_priority_str(task: Dict[str, Any]) -> str:
    """Trích xuất chuỗi mức độ ưu tiên từ task."""
    prio = task.get("priority")
    if isinstance(prio, dict):
        return str(prio.get("label", prio.get("value", ""))).strip().capitalize()
    return str(prio or "").strip().capitalize()


def _extract_status_str(task: Dict[str, Any]) -> str:
    """Trích xuất chuỗi trạng thái từ task."""
    return str(task.get("status", "pending")).strip().lower()


def search_tasks(
    tasks: List[Dict[str, Any]],
    keyword: str,
    filter_by: Optional[Dict[str, str]] = None,
) -> List[Dict[str, Any]]:
    """Tìm kiếm và lọc danh sách công việc theo từ khóa và bộ lọc nâng cao.

    Tìm kiếm không phân biệt chữ hoa/chữ thường trong cả trường 'title'
    và 'description'. Hỗ trợ lọc tùy chọn theo 'status' hoặc 'priority'.

    Args:
        tasks: Danh sách các dictionary chứa thông tin công việc.
        keyword: Từ khóa cần tìm kiếm.
        filter_by: Dictionary chứa tiêu chí lọc, ví dụ:
            {"status": "completed"} hoặc {"priority": "High"}.

    Returns:
        Danh sách các dictionary công việc khớp với tất cả điều kiện.
        Trả về [] nếu danh sách rỗng hoặc không có kết quả phù hợp.
    """
    if not tasks:
        print(f"\n  {YELLOW}⚠ [Thông báo] Danh sách công việc hiện đang trống.{RESET}\n")
        return []

    keyword_clean = keyword.strip().lower()
    matching_tasks: List[Dict[str, Any]] = []

    for task in tasks:
        title = str(task.get("title", "")).lower()
        description = str(task.get("description", "")).lower()

        # 1. Tìm kiếm theo keyword trong title hoặc description
        keyword_matched = (keyword_clean in title) or (keyword_clean in description)
        if not keyword_matched:
            continue

        # 2. Lọc nâng cao (nếu có filter_by)
        filter_matched = True
        if filter_by:
            for field, expected_val in filter_by.items():
                expected_str = str(expected_val).strip().lower()

                if field == "priority":
                    actual_prio = _extract_priority_str(task).lower()
                    if actual_prio != expected_str:
                        filter_matched = False
                        break
                elif field == "status":
                    actual_status = _extract_status_str(task)
                    # Hỗ trợ completed / pending linh hoạt
                    if expected_str == "completed":
                        if actual_status not in ("completed", "done"):
                            filter_matched = False
                            break
                    elif expected_str in ("pending", "todo", "in_progress"):
                        if actual_status in ("completed", "done"):
                            filter_matched = False
                            break
                    else:
                        if actual_status != expected_str:
                            filter_matched = False
                            break
                else:
                    actual_val = str(task.get(field, "")).strip().lower()
                    if actual_val != expected_str:
                        filter_matched = False
                        break

        if filter_matched:
            matching_tasks.append(task)

    if not matching_tasks:
        print(
            f"\n  {YELLOW}⚠ [Thông báo] Không tìm thấy task nào khớp với từ khóa '{keyword}'.{RESET}\n"
        )
        return []

    return matching_tasks


# ─── UI & CLI Menu Helpers ──────────────────────────────────────────────────

def clear_screen() -> None:
    """Xóa màn hình console."""
    os.system("cls" if os.name == "nt" else "clear")


def print_search_banner() -> None:
    """In banner giao diện tìm kiếm task."""
    print(f"""
{CYAN}╔══════════════════════════════════════════════════════╗
║  {BOLD}{WHITE}        🔍  TÌM KIẾM CÔNG VIỆC  🔍          {RESET}{CYAN}     ║
║  {DIM}{WHITE}       TeamTodo · Search Task Module            {RESET}{CYAN}     ║
╚══════════════════════════════════════════════════════╝{RESET}
""")


def display_task_row(task: Dict[str, Any]) -> None:
    """Hiển thị một task dạng dòng thông tin chi tiết."""
    task_id = task.get("id", "?")
    title = task.get("title", "Untitled")
    desc = task.get("description", "")
    desc_str = f" - {DIM}{desc}{RESET}" if desc else ""

    # Priority
    prio_raw = task.get("priority")
    if isinstance(prio_raw, dict):
        prio_color = prio_raw.get("color", "")
        prio_label = prio_raw.get("label", "NORMAL")
    else:
        prio_label = str(prio_raw or "Normal").upper()
        prio_color = RED if prio_label == "HIGH" else (YELLOW if prio_label == "MEDIUM" else GREEN)

    # Status
    status = _extract_status_str(task)
    status_badge = f"{GREEN}[Hoàn thành]{RESET}" if status in ("completed", "done") else f"{YELLOW}[Chưa xong]{RESET}"

    # Due date
    due = task.get("due_date") or task.get("deadline")
    due_str = f" | ⏰ {due}" if due else ""

    print(f"  {BOLD}#{task_id:<3}{RESET} {status_badge} {prio_color}[{prio_label:<6}]{RESET} {BOLD}{title}{RESET}{desc_str}{due_str}")


def search_task_menu() -> None:
    """Giao diện tương tác CLI cho chức năng tìm kiếm công việc."""
    clear_screen()
    print_search_banner()

    tasks = load_tasks()
    if not tasks:
        print(f"  {YELLOW}⚠ Hiện chưa có công việc nào trong hệ thống!{RESET}")
        input(f"\n  {DIM}Nhấn Enter để quay lại...{RESET}")
        return

    print(f"  {CYAN}▶ Nhập từ khóa tìm kiếm (tìm trong tiêu đề và mô tả):{RESET}")
    keyword = input(f"    {YELLOW}→ Từ khóa: {RESET}").strip()
    if not keyword:
        print(f"  {RED}✗ Từ khóa không được để trống!{RESET}")
        time_sleep_input()
        return

    print(f"\n  {CYAN}▶ Tùy chọn lọc nâng cao (Nhấn Enter để bỏ qua):{RESET}")
    print(f"    [1] Lọc theo trạng thái ({GREEN}completed{RESET} / {YELLOW}pending{RESET})")
    print(f"    [2] Lọc theo mức độ ưu tiên ({RED}High{RESET} / {YELLOW}Medium{RESET} / {GREEN}Low{RESET})")
    print(f"    [3] Không lọc thêm")
    filter_choice = input(f"    {YELLOW}→ Lựa chọn (1-3, mặc định 3): {RESET}").strip()

    filter_by: Optional[Dict[str, str]] = None
    if filter_choice == "1":
        print(f"    Chọn trạng thái: [1] Completed   [2] Pending")
        st_choice = input(f"    {YELLOW}→ Trạng thái: {RESET}").strip()
        st_val = "completed" if st_choice == "1" else "pending"
        filter_by = {"status": st_val}
    elif filter_choice == "2":
        print(f"    Chọn mức độ ưu tiên: [1] High   [2] Medium   [3] Low")
        pr_choice = input(f"    {YELLOW}→ Mức ưu tiên: {RESET}").strip()
        pr_map = {"1": "High", "2": "Medium", "3": "Low"}
        if pr_choice in pr_map:
            filter_by = {"priority": pr_map[pr_choice]}

    # Thực hiện tìm kiếm
    results = search_tasks(tasks, keyword, filter_by=filter_by)

    if results:
        print(f"\n  {GREEN}{BOLD}✔ TÌM THẤY {len(results)} CÔNG VIỆC PHÙ HỢP:{RESET}\n")
        print("  " + "─" * 65)
        for t in results:
            display_task_row(t)
        print("  " + "─" * 65)

    input(f"\n  {DIM}Nhấn Enter để quay lại menu chính...{RESET}")


def time_sleep_input() -> None:
    """Dừng màn hình chờ người dùng xác nhận."""
    input(f"\n  {DIM}Nhấn Enter để tiếp tục...{RESET}")


if __name__ == "__main__":
    search_task_menu()
