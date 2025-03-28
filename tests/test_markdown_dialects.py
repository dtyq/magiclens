#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试Markdown方言支持功能。
"""

import unittest
from magiclens.converters.html2md import Html2MarkdownConverter


class TestMarkdownDialects(unittest.TestCase):
    """测试Markdown方言支持功能。"""

    def test_github_dialect(self):
        """测试GitHub风格Markdown。"""
        # GitHub方言（默认）
        converter = Html2MarkdownConverter(options={"dialect": "github"})

        # 测试标题风格
        html = "<h1>Title</h1>"
        markdown = converter.convert_html(html)
        self.assertEqual(markdown.strip(), "# Title")

        # 测试无序列表标记
        html = "<ul><li>Item</li></ul>"
        markdown = converter.convert_html(html)
        self.assertIn("- Item", markdown)

        # 测试任务列表
        html = '<ul><li><input type="checkbox" checked/>Task</li></ul>'
        markdown = converter.convert_html(html)
        self.assertIn("[x] Task", markdown)

        # 测试删除线
        html = "<p><del>Deleted text</del></p>"
        markdown = converter.convert_html(html)
        self.assertIn("~~Deleted text~~", markdown)

    def test_commonmark_dialect(self):
        """测试CommonMark风格。"""
        converter = Html2MarkdownConverter(options={"dialect": "commonmark"})

        # 测试标题风格
        html = "<h1>Title</h1>"
        markdown = converter.convert_html(html)
        self.assertEqual(markdown.strip(), "# Title")

        # 测试无序列表标记
        html = "<ul><li>Item</li></ul>"
        markdown = converter.convert_html(html)
        self.assertIn("* Item", markdown)

    def test_traditional_dialect(self):
        """测试传统Markdown风格。"""
        converter = Html2MarkdownConverter(options={"dialect": "traditional"})

        # 测试标题风格应该是setext风格
        html = "<h1>Title</h1>"
        markdown = converter.convert_html(html)
        self.assertRegex(markdown.strip(), r"Title\n=+")

        # 测试无序列表标记
        html = "<ul><li>Item</li></ul>"
        markdown = converter.convert_html(html)
        self.assertIn("* Item", markdown)

        # 测试强调标记
        html = "<p><em>Emphasized text</em></p>"
        markdown = converter.convert_html(html)
        self.assertIn("_Emphasized text_", markdown)

        # 测试强调标记
        html = "<p><strong>Strong text</strong></p>"
        markdown = converter.convert_html(html)
        self.assertIn("__Strong text__", markdown)

    def test_custom_dialect(self):
        """测试自定义Markdown风格。"""
        # 创建自定义方言
        custom_options = {
            "dialect": "custom",
            "headingStyle": "atx",
            "bulletListMarker": "+",
            "emDelimiter": "_",
            "strongDelimiter": "__",
            "useHtmlTags": False
        }

        converter = Html2MarkdownConverter(options=custom_options)

        # 测试标题风格
        html = "<h1>Title</h1>"
        markdown = converter.convert_html(html)
        self.assertEqual(markdown.strip(), "# Title")

        # 测试无序列表标记
        html = "<ul><li>Item</li></ul>"
        markdown = converter.convert_html(html)
        self.assertIn("+ Item", markdown)

        # 测试强调标记
        html = "<p><em>Emphasized text</em></p>"
        markdown = converter.convert_html(html)
        self.assertIn("_Emphasized text_", markdown)

    def test_override_dialect_options(self):
        """测试覆盖方言选项。"""
        # 使用GitHub方言但覆盖某些选项
        options = {
            "dialect": "github",
            "bulletListMarker": "+",  # 覆盖GitHub默认的'-'
            "headingStyle": "setext"  # 覆盖GitHub默认的'atx'
        }

        converter = Html2MarkdownConverter(options=options)

        # 测试标题风格应该是setext（被覆盖）
        html = "<h1>Title</h1>"
        markdown = converter.convert_html(html)
        self.assertRegex(markdown.strip(), r"Title\n=+")

        # 测试无序列表标记应该是'+'（被覆盖）
        html = "<ul><li>Item</li></ul>"
        markdown = converter.convert_html(html)
        self.assertIn("+ Item", markdown)

        # 但仍然应该支持GitHub特性，如任务列表
        html = '<ul><li><input type="checkbox" checked/>Task</li></ul>'
        markdown = converter.convert_html(html)
        self.assertIn("[x] Task", markdown)

    def test_invalid_dialect(self):
        """测试无效的方言设置。"""
        # 指定一个不存在的方言，应该使用空选项（等效于custom）
        converter = Html2MarkdownConverter(options={"dialect": "nonexistent"})

        # 应该仍然能够正常工作，使用默认行为
        html = "<h1>Title</h1><p>Paragraph</p>"
        markdown = converter.convert_html(html)
        self.assertIn("Title", markdown)
        self.assertIn("Paragraph", markdown)


if __name__ == "__main__":
    unittest.main()
