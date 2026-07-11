import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from hy3_showcase.client import Hy3Client, _mock_chat


class TestHy3MockClient(unittest.TestCase):
    def setUp(self):
        os.environ["HY3_MOCK"] = "true"
        self.client = Hy3Client()

    def test_mock_mode_enabled(self):
        self.assertTrue(self.client.mock)

    def test_basic_chat(self):
        messages = [{"role": "user", "content": "你好"}]
        resp = self.client.chat(messages, stream=False)
        text = resp.choices[0].message.content
        self.assertIsNotNone(text)
        self.assertIn("Hy3", text)

    def test_streaming_chat(self):
        messages = [{"role": "user", "content": "介绍一下你自己"}]
        stream = self.client.chat(messages, stream=True)
        chunks = []
        for chunk in stream:
            delta = chunk.choices[0].delta
            if delta.content:
                chunks.append(delta.content)
        text = "".join(chunks)
        self.assertGreater(len(text), 0)

    def test_quicksort_mock(self):
        messages = [{"role": "user", "content": "用 Python 写一个快速排序"}]
        resp = self.client.chat(messages, stream=False)
        self.assertIn("quicksort", resp.choices[0].message.content.lower())

    def test_moe_explanation(self):
        messages = [{"role": "user", "content": "解释 MoE 架构"}]
        resp = self.client.chat(messages, stream=False)
        self.assertIn("MoE", resp.choices[0].message.content)

    def test_high_reasoning(self):
        messages = [{"role": "user", "content": "24点问题：3, 3, 8, 8"}]
        resp = self.client.chat(messages, stream=False, reasoning_effort="high")
        text = resp.choices[0].message.content
        self.assertTrue("24" in text or "推理" in text)

    def test_tool_calling_calculator(self):
        result = self.client.chat_with_tools(
            [{"role": "user", "content": "计算 (238491 * 78345) / 100"}],
            reasoning_effort="high",
        )
        self.assertIn("calculator", result.lower())

    def test_distributed_system_design(self):
        messages = [{"role": "user", "content": "设计一个分布式缓存系统"}]
        resp = self.client.chat(messages, stream=False)
        text = resp.choices[0].message.content
        self.assertIn("分布式", text)

    def test_mock_chat_fallback(self):
        text = _mock_chat([{"role": "user", "content": "一些随机内容"}])
        self.assertIsNotNone(text)

    def test_flask_app_generation(self):
        messages = [{"role": "user", "content": "创建一个 Flask Web 应用"}]
        resp = self.client.chat(messages, stream=False)
        self.assertIn("Flask", resp.choices[0].message.content)


if __name__ == "__main__":
    unittest.main()
