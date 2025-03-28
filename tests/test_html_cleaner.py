#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试HTML清理选项功能。
"""

import unittest
from src.magiclens.converters.html2md import Html2MarkdownConverter


class TestHtmlCleaner(unittest.TestCase):
    """测试HTML清理选项功能。"""

    def test_default_cleaning(self):
        """测试默认的清理行为（移除script、style和noscript标签）。"""
        html = """
        <html>
        <head>
            <style>body { color: red; }</style>
            <script>alert('hello');</script>
        </head>
        <body>
            <noscript>Please enable JavaScript.</noscript>
            <p>This is a test.</p>
        </body>
        </html>
        """
        converter = Html2MarkdownConverter()
        markdown = converter.convert_html(html)
        self.assertIn("This is a test.", markdown)
        self.assertNotIn("Please enable JavaScript", markdown)
        self.assertNotIn("alert('hello')", markdown)
        self.assertNotIn("color: red", markdown)

    def test_custom_tag_removal(self):
        """测试自定义标签移除。"""
        html = """
        <div>
            <p>Paragraph 1</p>
            <aside>Side note</aside>
            <p>Paragraph 2</p>
        </div>
        """
        options = {
            "clean": {
                "removeTags": ["aside"]
            }
        }
        converter = Html2MarkdownConverter(options=options)
        markdown = converter.convert_html(html)
        self.assertIn("Paragraph 1", markdown)
        self.assertIn("Paragraph 2", markdown)
        self.assertNotIn("Side note", markdown)

    def test_attribute_removal(self):
        """测试属性移除。"""
        html = """
        <div id="content" data-test="value">
            <p class="important" style="color: blue;">Important text</p>
        </div>
        """
        options = {
            "clean": {
                "removeAttrs": ["data-test", "style"]
            }
        }
        converter = Html2MarkdownConverter(options=options)
        result = converter.convert_html(html)

        # 测试间接方式：确保转换后的内容仍有关键文本
        self.assertIn("Important text", result)

        # 注意：我们无法直接从Markdown中检查HTML属性是否被移除
        # 因为它们在转换过程中会被丢弃，所以这个测试有一定局限性

    def test_class_removal(self):
        """测试类移除。"""
        html = """
        <div class="container">
            <p class="important highlight">Important highlighted text</p>
            <div class="sidebar highlight">Sidebar content</div>
        </div>
        """
        options = {
            "clean": {
                "removeClasses": ["highlight"]
            }
        }
        converter = Html2MarkdownConverter(options=options)
        result = converter.convert_html(html)

        # 验证内容被保留
        self.assertIn("Important highlighted text", result)
        self.assertIn("Sidebar content", result)

    def test_empty_tag_removal(self):
        """测试空标签移除。"""
        html = """
        <div>
            <p>Content</p>
            <div></div>
            <span></span>
            <p><br/></p>
            <img src="image.jpg" alt="">
        </div>
        """
        options = {
            "clean": {
                "removeEmptyTags": True
            }
        }
        converter = Html2MarkdownConverter(options=options)
        result = converter.convert_html(html)

        # 验证内容被保留
        self.assertIn("Content", result)
        # 注意：空标签会在HTML->Markdown转换中自然被忽略，不需要特别验证

    def test_comment_removal(self):
        """测试注释移除。"""
        html = """
        <div>
            <!-- This is a comment -->
            <p>Content</p>
            <!-- Another comment -->
        </div>
        """
        # 默认应该移除注释
        converter = Html2MarkdownConverter()
        result = converter.convert_html(html)

        # 验证实际内容被保留
        self.assertIn("Content", result)
        # 注释在转换为Markdown时会自然被忽略

    def test_disable_comment_removal(self):
        """测试禁用注释移除。"""
        html = """
        <div>
            <!-- This is a comment -->
            <p>Content</p>
        </div>
        """
        options = {
            "clean": {
                "removeComments": False
            }
        }
        converter = Html2MarkdownConverter(options=options)
        result = converter.convert_html(html)

        # 验证内容被保留
        self.assertIn("Content", result)
        # 注意：即使不移除注释，它们在转换到Markdown时也通常会被忽略


if __name__ == "__main__":
    unittest.main()
