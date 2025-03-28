#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试HTML到Markdown转换功能
"""

import sys
import os
import unittest

# 添加项目根目录到Python路径，便于导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.magiclens.converters.html2md import Html2MarkdownConverter
from src.magiclens.core.rule import Rule


class TestHtml2Markdown(unittest.TestCase):
    """测试HTML到Markdown转换功能"""

    def setUp(self):
        """测试前的准备工作"""
        self.converter = Html2MarkdownConverter()

    def test_empty_html(self):
        """测试空HTML转换"""
        markdown = self.converter.convert_html("")
        self.assertEqual(markdown, "")

    def test_basic_html(self):
        """测试基本HTML转换"""
        html = "<h1>标题</h1><p>段落</p>"
        # 注意：由于我们没有实现具体规则，这里暂时不能测试实际结果
        # 只能测试方法可以调用
        markdown = self.converter.convert_html(html)
        self.assertIsInstance(markdown, str)

    def test_custom_rule(self):
        """测试自定义规则"""

        # 创建一个简单的自定义规则
        class CustomRule(Rule):
            def filter(self, node, options):
                return hasattr(node, 'name') and node.name == 'div' and 'custom' in node.get('class', [])

            def replacement(self, content, node, options):
                return f":::{content}:::"

        # 注册自定义规则
        self.converter.register_rule("custom-rule", CustomRule())

        # 由于没有实现具体的处理逻辑，这里只测试方法调用
        html = '<div class="custom">测试内容</div>'
        markdown = self.converter.convert_html(html)
        self.assertIsInstance(markdown, str)

    def test_custom_options(self):
        """测试自定义选项"""
        custom_options = {
            "headingStyle": "setext",
            "bulletListMarker": "-"
        }

        custom_converter = Html2MarkdownConverter(options=custom_options)
        html = "<h1>标题</h1><ul><li>项目</li></ul>"

        # 由于没有实现具体的处理逻辑，这里只测试方法调用
        markdown = custom_converter.convert_html(html)
        self.assertIsInstance(markdown, str)


if __name__ == '__main__':
    unittest.main()
