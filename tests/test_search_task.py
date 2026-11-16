"""Unit tests cho module SearchTask.

Kiểm thử tính năng tìm kiếm và lọc danh sách công việc:
- Tìm kiếm từ khóa theo title và description không phân biệt hoa thường.
- Lọc nâng cao theo trạng thái và mức độ ưu tiên.
- Xử lý ngoại lệ khi danh sách rỗng hoặc không có kết quả phù hợp.
"""

import os
import sys
import unittest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from SearchTask.search_task import search_tasks


class TestSearchTasks(unittest.TestCase):
    """Test suite kiểm thử hàm search_tasks."""

    def setUp(self) -> None:
        """Thiết lập dữ liệu mẫu cho mỗi test case."""
        self.sample_tasks = [
            {
                "id": 1,
                "title": "Hoàn thiện báo cáo quý 4",
                "description": "Tổng hợp doanh thu và chi phí toàn công ty",
                "status": "completed",
                "priority": "High",
                "due_date": "2026-11-10",
            },
            {
                "id": 2,
                "title": "Thiết kế kiến trúc hệ thống",
                "description": "Tạo sơ đồ cơ sở dữ liệu và workflow backend",
                "status": "pending",
                "priority": "High",
                "due_date": "2026-11-25",
            },
            {
                "id": 3,
                "title": "Fix bug xác thực người dùng",
                "description": "Sửa lỗi crash JWT token khi hết hạn phiên",
                "status": "pending",
                "priority": "Medium",
                "due_date": "2026-11-18",
            },
            {
                "id": 4,
                "title": "Viết tài liệu hướng dẫn API",
                "description": "Cập nhật tài liệu Swagger cho phòng Mobile",
                "status": "pending",
                "priority": "Low",
                "due_date": "2026-10-30",
            },
        ]

    def test_search_by_keyword_in_title_case_insensitive(self):
        """Kiểm thử tìm kiếm theo từ khóa trong title không phân biệt chữ hoa/thường."""
        results = search_tasks(self.sample_tasks, keyword="BÁO CÁO")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 1)

    def test_search_by_keyword_in_description_case_insensitive(self):
        """Kiểm thử tìm kiếm theo từ khóa trong description không phân biệt chữ hoa/thường."""
        results = search_tasks(self.sample_tasks, keyword="jwt token")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 3)

    def test_search_with_filter_by_status(self):
        """Kiểm thử tìm kiếm kết hợp lọc theo trạng thái status."""
        # Tìm từ khóa 'hệ thống' với status 'pending'
        results = search_tasks(
            self.sample_tasks,
            keyword="hệ thống",
            filter_by={"status": "pending"},
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 2)

    def test_search_with_filter_by_priority(self):
        """Kiểm thử tìm kiếm kết hợp lọc theo mức độ ưu tiên priority."""
        # Tìm các task có mức độ ưu tiên High
        results = search_tasks(
            self.sample_tasks,
            keyword="tạo",
            filter_by={"priority": "High"},
        )
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]["id"], 2)

    def test_search_not_found_returns_empty_list(self):
        """Kiểm thử khi từ khóa không khớp trả về danh sách rỗng []."""
        results = search_tasks(self.sample_tasks, keyword="từ khóa hoàn toàn không tồn tại")
        self.assertEqual(results, [])

    def test_search_empty_tasks_list_returns_empty_list(self):
        """Kiểm thử khi danh sách tasks truyền vào rỗng."""
        results = search_tasks([], keyword="báo cáo")
        self.assertEqual(results, [])


if __name__ == "__main__":
    unittest.main()
