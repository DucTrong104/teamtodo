"""Unit tests cho module TaskStatistics.

Kiểm thử tính năng tính toán thống kê công việc:
- Xử lý an toàn danh sách rỗng (tránh ZeroDivisionError).
- Tính toán tổng số, số lượng và phần trăm hoàn thành.
- Thống kê phân loại theo mức độ ưu tiên.
- Tính toán số lượng công việc quá hạn theo due_date/deadline.
"""

from datetime import date
import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from TaskStatistics.task_statistics import get_task_statistics


class TestTaskStatistics(unittest.TestCase):
    """Test suite kiểm thử hàm get_task_statistics."""

    def setUp(self) -> None:
        """Thiết lập dữ liệu mẫu và ngày mốc kiểm thử."""
        self.sample_tasks = [
            {
                "id": 1,
                "title": "Báo cáo doanh thu tháng",
                "status": "completed",
                "priority": "High",
                "due_date": "2026-11-01",
            },
            {
                "id": 2,
                "title": "Triển khai database cluster",
                "status": "pending",
                "priority": "High",
                "due_date": "2026-11-05",  # Quá hạn so với 2026-11-16
            },
            {
                "id": 3,
                "title": "Kiểm thử bảo mật API",
                "status": "pending",
                "priority": "Medium",
                "due_date": "2026-11-25",  # Chưa quá hạn
            },
            {
                "id": 4,
                "title": "Cập nhật tài liệu nội bộ",
                "status": "pending",
                "priority": "Low",
                "due_date": "2026-10-15",  # Quá hạn so với 2026-11-16
            },
        ]
        # Ngày tham chiếu cố định để test độc lập thời gian
        self.reference_date = date(2026, 11, 16)

    def test_statistics_empty_task_list(self):
        """Kiểm thử xử lý danh sách rỗng an toàn, tránh lỗi chia cho 0."""
        stats = get_task_statistics([])
        self.assertEqual(stats["total_tasks"], 0)
        self.assertEqual(stats["completed_tasks"], 0)
        self.assertEqual(stats["pending_tasks"], 0)
        self.assertEqual(stats["completion_rate"], 0.0)
        self.assertEqual(stats["overdue_tasks"], 0)
        self.assertEqual(
            stats["priority_breakdown"],
            {"High": 0, "Medium": 0, "Low": 0},
        )

    def test_statistics_completion_metrics(self):
        """Kiểm thử độ chính xác các chỉ số tổng số, completed, pending và tỷ lệ %."""
        stats = get_task_statistics(self.sample_tasks, reference_date=self.reference_date)
        self.assertEqual(stats["total_tasks"], 4)
        self.assertEqual(stats["completed_tasks"], 1)
        self.assertEqual(stats["pending_tasks"], 3)
        self.assertEqual(stats["completion_rate"], 25.0)

    def test_statistics_priority_breakdown(self):
        """Kiểm thử phân loại số lượng công việc theo mức độ ưu tiên."""
        stats = get_task_statistics(self.sample_tasks, reference_date=self.reference_date)
        breakdown = stats["priority_breakdown"]
        self.assertEqual(breakdown["High"], 2)
        self.assertEqual(breakdown["Medium"], 1)
        self.assertEqual(breakdown["Low"], 1)

    def test_statistics_overdue_calculation(self):
        """Kiểm thử tính toán số lượng task quá hạn.
        
        Quy tắc: Chỉ tính task chưa hoàn thành (status != 'completed')
        có due_date < reference_date.
        - Task 1: due 2026-11-01 nhưng đã completed -> Không tính.
        - Task 2: due 2026-11-05, pending -> Quá hạn (+1).
        - Task 3: due 2026-11-25, pending -> Chưa quá hạn.
        - Task 4: due 2026-10-15, pending -> Quá hạn (+1).
        => Tổng: 2.
        """
        stats = get_task_statistics(self.sample_tasks, reference_date=self.reference_date)
        self.assertEqual(stats["overdue_tasks"], 2)


if __name__ == "__main__":
    unittest.main()
