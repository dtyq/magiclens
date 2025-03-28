#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试HTML片段转换功能。
"""

import unittest
from src.magiclens.converters.html2md import Html2MarkdownConverter


class TestHtmlFragments(unittest.TestCase):
    """测试HTML片段转换功能。"""

    def setUp(self):
        self.converter = Html2MarkdownConverter()

    def test_convert_single_element(self):
        """测试转换单个HTML元素。"""
        html = "<p>This is a paragraph.</p>"
        markdown = self.converter.convert_html_fragment(html)
        self.assertEqual(markdown.strip(), "This is a paragraph.")

    def test_convert_multiple_elements(self):
        """测试转换多个HTML元素。"""
        html = """
        <h1>Title</h1>
        <p>Paragraph 1</p>
        <p>Paragraph 2</p>
        """
        markdown = self.converter.convert_html_fragment(html)
        lines = markdown.strip().split('\n')
        self.assertIn("# Title", lines)
        self.assertIn("Paragraph 1", lines)
        self.assertIn("Paragraph 2", lines)

    def test_convert_partial_table(self):
        """测试转换不完整的表格。"""
        html = """
        <tr>
            <td>Cell 1</td>
            <td>Cell 2</td>
        </tr>
        """
        # 一般情况下，不完整的表格会得到不正确的结果
        # 但使用fragment=True，应该能得到正确的结果
        markdown = self.converter.convert_html_fragment(html, fragment_root="table")
        self.assertIn("Cell 1", markdown)
        self.assertIn("Cell 2", markdown)

    def test_convert_list_items(self):
        """测试转换列表项。"""
        # 无序列表项
        fragment_ul = "<li>Item 1</li><li>Item 2</li><li>Item 3</li>"
        markdown = self.converter.convert_html_fragment(fragment_ul)
        lines = markdown.strip().split('\n')
        self.assertIn("- Item 1", lines)  # 更新为GitHub风格的'-'标记
        self.assertIn("- Item 2", lines)

        # 有序列表项
        fragment_ol = "<li value='1'>First</li><li value='2'>Second</li>"
        markdown = self.converter.convert_html_fragment(fragment_ol, fragment_root='ol')
        self.assertIn("1. First", markdown)
        self.assertIn("2. Second", markdown)

    def test_convert_nested_fragments(self):
        """测试转换嵌套的HTML片段。"""
        # 嵌套HTML片段
        fragment = """
        <div class="container">
            <h2>Subtitle</h2>
            <ul>
                <li>Point 1</li>
                <li>Point 2</li>
            </ul>
        </div>
        """
        markdown = self.converter.convert_html_fragment(fragment)
        lines = markdown.strip().split('\n')
        self.assertIn("## Subtitle", lines)
        self.assertIn("- Point 1", lines)  # 更新为GitHub风格的'-'标记
        self.assertIn("- Point 2", lines)

    def test_convert_with_normal_method(self):
        """测试使用常规convert_html方法但设置fragment参数。"""
        html = "<p>This is a paragraph.</p>"
        markdown = self.converter.convert_html(html, fragment=True)
        self.assertEqual(markdown.strip(), "This is a paragraph.")


if __name__ == "__main__":
    unittest.main()
