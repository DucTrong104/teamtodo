"""TaskStatistics Module - Thống kê và hiển thị báo cáo công việc.

Tính toán tổng số task, tỷ lệ hoàn thành, phân loại theo độ ưu tiên,
số lượng task quá hạn dựa trên due_date/deadline, và hiển thị bảng báo cáo console trực quan.
"""

from datetime import date, datetime
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


def _parse_due_date(task: Dict[str, Any]) -> Optional[date]:
    """Phân tích ngày hết hạn từ các trường 'due_date' hoặc 'deadline'."""
    raw_date = task.get("due_date") or task.get("deadline")
    if not raw_date:
        return None

    raw_str = str(raw_date).strip()
    # Thử các định dạng ngày phổ biến
    for fmt in ("%Y-%m-%d", "%Y-%m-%d %H:%M:%S", "%d/%m/%Y"):
        try:
            return datetime.strptime(raw_str, fmt).date()
        except ValueError:
            continue
    return None


def get_task_statistics(
    tasks: List[Dict[str, Any]],
    reference_date: Optional[date] = None,
) -> Dict[str, Any]:
    """Tính toán các chỉ số thống kê tổng hợp về danh sách công việc.

    Args:
        tasks: Danh sách các dictionary chứa thông tin công việc.
        reference_date: Ngày tham chiếu để so sánh quá hạn (mặc định: ngày hiện tại).

    Returns:
        Dictionary chứa các chỉ số:
            - total_tasks (int): Tổng số lượng công việc.
            - completed_tasks (int): Số lượng công việc đã hoàn thành.
            - pending_tasks (int): Số lượng công việc chưa hoàn thành.
            - completion_rate (float): Tỷ lệ % hoàn thành (làm tròn 2 chữ số).
            - priority_breakdown (dict): Phân loại số lượng theo độ ưu tiên (High, Medium, Low).
            - overdue_tasks (int): Số lượng công việc chưa hoàn thành đã quá hạn.
    """
    if reference_date is None:
        reference_date = datetime.now().date()

    total_tasks = len(tasks)

    # Xử lý an toàn danh sách rỗng để tránh lỗi chia cho 0 (ZeroDivisionError)
    if total_tasks == 0:
        return {
            "total_tasks": 0,
            "completed_tasks": 0,
            "pending_tasks": 0,
            "completion_rate": 0.0,
            "priority_breakdown": {"High": 0, "Medium": 0, "Low": 0},
            "overdue_tasks": 0,
        }

    completed_count = 0
    pending_count = 0
    priority_counts: Dict[str, int] = {"High": 0, "Medium": 0, "Low": 0}
    overdue_count = 0

    for task in tasks:
        # Kiểm tra trạng thái: completed vs pending
        status_raw = str(task.get("status", "pending")).strip().lower()
        is_completed = status_raw in ("completed", "done")

        if is_completed:
            completed_count += 1
        else:
            pending_count += 1

        # Phân loại mức độ ưu tiên (hỗ trợ cả dạng dict và chuỗi)
        prio_raw = task.get("priority")
        if isinstance(prio_raw, dict):
            prio_label = str(prio_raw.get("label", prio_raw.get("value", ""))).strip().capitalize()
        else:
            prio_label = str(prio_raw or "Low").strip().capitalize()

        if prio_label in priority_counts:
            priority_counts[prio_label] += 1
        elif prio_label == "Urgent":
            # Nếu có mức Urgent, quy về nhóm High hoặc tính thêm
            priority_counts["High"] += 1
        else:
            priority_counts[prio_label] = priority_counts.get(prio_label, 0) + 1

        # Tính toán công việc quá hạn: task chưa hoàn thành và ngày hết hạn < ngày tham chiếu
        if not is_completed:
            due_dt = _parse_due_date(task)
            if due_dt and due_dt < reference_date:
                overdue_count += 1

    completion_rate = round((completed_count / total_tasks) * 100, 2)

    return {
        "total_tasks": total_tasks,
        "completed_tasks": completed_count,
        "pending_tasks": pending_count,
        "completion_rate": completion_rate,
        "priority_breakdown": priority_counts,
        "overdue_tasks": overdue_count,
    }


def display_statistics(stats: Dict[str, Any]) -> None:
    """Hiển thị bảng báo cáo thống kê trực quan ra màn hình console.

    Args:
        stats: Dictionary chứa các chỉ số lấy từ hàm get_task_statistics.
    """
    total = stats.get("total_tasks", 0)
    completed = stats.get("completed_tasks", 0)
    pending = stats.get("pending_tasks", 0)
    rate = stats.get("completion_rate", 0.0)
    overdue = stats.get("overdue_tasks", 0)
    priorities = stats.get("priority_breakdown", {})

    # Thanh tiến trình phần trăm dạng thanh ngang
    bar_length = 20
    filled_len = int(bar_length * (rate / 100)) if total > 0 else 0
    progress_bar = f"{GREEN}{'█' * filled_len}{DIM}{'░' * (bar_length - filled_len)}{RESET}"

    print(f"""
{CYAN}╔══════════════════════════════════════════════════════════════╗
║  {BOLD}{WHITE}             📊  BÁO CÁO THỐNG KÊ CÔNG VIỆC  📊            {RESET}{CYAN}║
║  {DIM}{WHITE}            TeamTodo · Task Statistics Module                 {RESET}{CYAN}║
╠══════════════════════════════════════════════════════════════╣{RESET}
  {BOLD}📌 TỔNG QUAN CHỈ SỐ TIẾN ĐỘ:{RESET}
    • Tổng số công việc    : {BOLD}{WHITE}{total}{RESET}
    • Đã hoàn thành        : {GREEN}{BOLD}{completed}{RESET} ({rate:.2f}%)
    • Chưa hoàn thành      : {YELLOW}{BOLD}{pending}{RESET} ({100 - rate if total > 0 else 0.0:.2f}%)
    • Công việc quá hạn    : {RED}{BOLD}{overdue}{RESET}
    • Tiến độ thực hiện    : [{progress_bar}] {BOLD}{rate:.1f}%{RESET}
{CYAN}╟──────────────────────────────────────────────────────────────╢{RESET}
  {BOLD}🎯 PHÂN LOẠI THEO MỨC ĐỘ ƯU TIÊN:{RESET}""")

    for p_name, p_count in priorities.items():
        if p_name.upper() == "HIGH":
            p_color = RED
            icon = "🔴"
        elif p_name.upper() == "MEDIUM":
            p_color = YELLOW
            icon = "🟡"
        else:
            p_color = GREEN
            icon = "🟢"
        print(f"    • {icon} {p_color}{p_name:<16}{RESET}: {BOLD}{p_count}{RESET} task")

    print(f"{CYAN}╚══════════════════════════════════════════════════════════════╝{RESET}\n")


def clear_screen() -> None:
    """Xóa màn hình console."""
    os.system("cls" if os.name == "nt" else "clear")


def statistics_menu() -> None:
    """Giao diện CLI hiển thị thống kê công việc."""
    clear_screen()
    tasks = load_tasks()
    stats = get_task_statistics(tasks)
    display_statistics(stats)
    input(f"  {DIM}Nhấn Enter để quay lại menu chính...{RESET}")


if __name__ == "__main__":
    statistics_menu()
