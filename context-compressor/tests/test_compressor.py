#!/usr/bin/env python3
"""
Context Compressor 测试套件
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import unittest
from compressor import compress_conversation, should_compress, summarize_messages


class TestCompressConversation(unittest.TestCase):
    """测试对话压缩功能"""
    
    def test_no_compression_needed(self):
        """测试消息数未超过阈值时不压缩"""
        messages = [
            {'role': 'user', 'content': '你好'},
            {'role': 'assistant', 'content': '你好！'},
        ]
        result = compress_conversation(messages, max_messages=10)
        self.assertEqual(len(result), 2)
        self.assertEqual(result, messages)
    
    def test_compression_triggered(self):
        """测试消息数超过阈值时触发压缩"""
        messages = [{'role': 'user', 'content': f'消息{i}'} for i in range(25)]
        result = compress_conversation(messages, max_messages=10)
        
        # 应该返回摘要 + 10条最近消息
        self.assertEqual(len(result), 11)
        self.assertEqual(result[0]['role'], 'system')
        self.assertIn('[对话摘要]', result[0]['content'])
    
    def test_compression_preserves_recent(self):
        """测试压缩保留最近消息"""
        messages = [{'role': 'user', 'content': f'消息{i}'} for i in range(20)]
        result = compress_conversation(messages, max_messages=5)
        
        # 检查最近5条消息被保留
        self.assertEqual(result[-1]['content'], '消息19')
        self.assertEqual(result[-2]['content'], '消息18')
        self.assertEqual(result[-3]['content'], '消息17')
        self.assertEqual(result[-4]['content'], '消息16')
        self.assertEqual(result[-5]['content'], '消息15')


class TestShouldCompress(unittest.TestCase):
    """测试压缩判断功能"""
    
    def test_should_compress_when_over_threshold(self):
        """测试超过阈值时返回True"""
        self.assertTrue(should_compress(70000, max_tokens=131072))
        self.assertTrue(should_compress(131073, max_tokens=131072))
    
    def test_should_not_compress_when_under_threshold(self):
        """测试未超过阈值时返回False"""
        self.assertFalse(should_compress(50000, max_tokens=131072))
        self.assertFalse(should_compress(65535, max_tokens=131072))
    
    def test_default_max_tokens(self):
        """测试默认token限制"""
        self.assertFalse(should_compress(60000))  # 默认131072 * 0.5 = 65536
        self.assertTrue(should_compress(70000))


class TestSummarizeMessages(unittest.TestCase):
    """测试消息摘要功能"""
    
    def test_summarize_empty_messages(self):
        """测试空消息列表"""
        result = summarize_messages([])
        self.assertEqual(result, "共0轮对话")
    
    def test_summarize_with_decisions(self):
        """测试包含决策的消息"""
        messages = [
            {'role': 'user', 'content': '我们决定采用方案A'},
            {'role': 'assistant', 'content': '好的'},
        ]
        result = summarize_messages(messages)
        self.assertIn('关键决策', result)
    
    def test_summarize_with_actions(self):
        """测试包含行动项的消息"""
        messages = [
            {'role': 'user', 'content': '完成了代码审查'},
            {'role': 'assistant', 'content': '收到'},
        ]
        result = summarize_messages(messages)
        self.assertIn('执行任务', result)
    
    def test_summarize_mixed_content(self):
        """测试混合内容"""
        messages = [
            {'role': 'user', 'content': '确定最终方案'},
            {'role': 'assistant', 'content': '已部署到生产环境'},
        ]
        result = summarize_messages(messages)
        self.assertIn('关键决策', result)
        self.assertIn('执行任务', result)


class TestEdgeCases(unittest.TestCase):
    """测试边界情况"""
    
    def test_exact_threshold(self):
        """测试恰好达到阈值"""
        messages = [{'role': 'user', 'content': f'消息{i}'} for i in range(10)]
        result = compress_conversation(messages, max_messages=10)
        self.assertEqual(len(result), 10)  # 不压缩
    
    def test_single_message(self):
        """测试单条消息"""
        messages = [{'role': 'user', 'content': '测试'}]
        result = compress_conversation(messages, max_messages=10)
        self.assertEqual(len(result), 1)
    
    def test_large_message_count(self):
        """测试大量消息"""
        messages = [{'role': 'user', 'content': f'消息{i}'} for i in range(1000)]
        result = compress_conversation(messages, max_messages=20)
        self.assertEqual(len(result), 21)  # 摘要 + 20条


if __name__ == '__main__':
    unittest.main()
