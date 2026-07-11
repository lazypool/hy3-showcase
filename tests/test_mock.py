import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hy3_showcase import Hy3Client
from hy3_showcase._mock_data import select_content


class TestHy3MockClient(unittest.TestCase):
    def setUp(self):
        os.environ["HY3_MOCK"] = "true"
        self.client = Hy3Client()

    def test_mock_mode_enabled(self):
        self.assertTrue(self.client.mock)

    def test_basic_chat(self):
        resp = self.client.chat([{"role": "user", "content": "你好"}], stream=False)
        text = resp.to_text()
        self.assertIsNotNone(text)
        self.assertIn("Hy3", text)

    def test_streaming_chat(self):
        stream = self.client.chat(
            [{"role": "user", "content": "介绍一下你自己"}], stream=True
        )
        chunks = [c.content for c in stream]
        text = "".join(chunks)
        self.assertGreater(len(text), 0)

    def test_quicksort_mock(self):
        resp = self.client.chat(
            [{"role": "user", "content": "用 Python 写一个快速排序"}], stream=False
        )
        self.assertIn("quicksort", resp.to_text().lower())

    def test_moe_explanation(self):
        resp = self.client.chat(
            [{"role": "user", "content": "解释 MoE 架构"}], stream=False
        )
        self.assertIn("MoE", resp.to_text())

    def test_high_reasoning(self):
        resp = self.client.chat(
            [{"role": "user", "content": "24点问题：3, 3, 8, 8"}],
            stream=False,
            reasoning_effort="high",
        )
        text = resp.to_text()
        self.assertTrue("24" in text or "推理" in text)

    def test_tool_calling_calculator(self):
        resp = self.client.chat_with_tools(
            [{"role": "user", "content": "计算 (238491 * 78345) / 100"}],
            reasoning_effort="high",
        )
        self.assertIn("calculator", resp.to_text().lower())

    def test_distributed_system_design(self):
        resp = self.client.chat(
            [{"role": "user", "content": "设计一个分布式缓存系统"}], stream=False
        )
        self.assertIn("分布式", resp.to_text())

    def test_mock_chat_fallback(self):
        text = select_content([{"role": "user", "content": "一些随机内容"}])
        self.assertIsNotNone(text)

    def test_flask_app_generation(self):
        resp = self.client.chat(
            [{"role": "user", "content": "创建一个 Flask Web 应用"}], stream=False
        )
        self.assertIn("Flask", resp.to_text())


if __name__ == "__main__":
    unittest.main()
