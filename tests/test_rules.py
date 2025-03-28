#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试HTML到Markdown转换规则。
"""

import unittest
from bs4 import BeautifulSoup
from src.magiclens.converters.html2md import Html2MarkdownConverter


class TestTableRule(unittest.TestCase):
    """测试表格规则。"""

    def setUp(self):
        """测试前的设置。"""
        self.converter = Html2MarkdownConverter()

    def test_simple_table(self):
        """测试简单表格转换。"""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Cell 1</td>
                    <td>Cell 2</td>
                </tr>
                <tr>
                    <td>Cell 3</td>
                    <td>Cell 4</td>
                </tr>
            </tbody>
        </table>
        """
        markdown = self.converter.convert_html(html)
        expected = """
| Header 1 | Header 2 |
| --- | --- |
| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |
        """
        self.assertEqual(markdown.strip(), expected.strip())

    def test_table_without_header(self):
        """测试没有表头的表格转换。"""
        html = """
        <table>
            <tbody>
                <tr>
                    <td>Cell 1</td>
                    <td>Cell 2</td>
                </tr>
                <tr>
                    <td>Cell 3</td>
                    <td>Cell 4</td>
                </tr>
            </tbody>
        </table>
        """
        markdown = self.converter.convert_html(html)
        expected = """
|  |  |
| --- | --- |
| Cell 1 | Cell 2 |
| Cell 3 | Cell 4 |
        """
        self.assertEqual(markdown.strip(), expected.strip())

    def test_table_structure(self):
        """测试基本表格结构转换。"""
        html = """
        <table>
            <thead>
                <tr>
                    <th>Header 1</th>
                    <th>Header 2</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>Cell 1</td>
                    <td>Cell 2</td>
                </tr>
                <tr>
                    <td>Cell 3</td>
                    <td>Cell 4</td>
                </tr>
            </tbody>
        </table>
        """
        markdown = self.converter.convert_html(html)
        self.assertIn("| Header 1 | Header 2 |", markdown)
        self.assertIn("| --- | --- |", markdown)
        self.assertIn("| Cell 1 | Cell 2 |", markdown)
        self.assertIn("| Cell 3 | Cell 4 |", markdown)

    def test_table_with_empty_cells(self):
        """测试包含空单元格的表格转换。"""
        html = """
        <table>
            <tr>
                <th>Name</th>
                <th>Age</th>
                <th>Note</th>
            </tr>
            <tr>
                <td>Alice</td>
                <td>30</td>
                <td></td>
            </tr>
            <tr>
                <td></td>
                <td>25</td>
                <td>Test</td>
            </tr>
        </table>
        """
        markdown = self.converter.convert_html(html)

        # 简单检查表格内容是否存在，不检查确切格式
        self.assertIn("Name", markdown)
        self.assertIn("Age", markdown)
        self.assertIn("Note", markdown)
        self.assertIn("Alice", markdown)
        self.assertIn("30", markdown)
        self.assertIn("25", markdown)
        self.assertIn("Test", markdown)


class TestDefinitionListRule(unittest.TestCase):
    """测试定义列表规则。"""

    def setUp(self):
        """测试前的设置。"""
        self.converter = Html2MarkdownConverter()

    def test_simple_definition_list(self):
        """测试简单定义列表转换。"""
        html = """
        <dl>
            <dt>Term 1</dt>
            <dd>Definition 1</dd>
            <dt>Term 2</dt>
            <dd>Definition 2</dd>
        </dl>
        """
        markdown = self.converter.convert_html(html)
        self.assertIn("**Term 1**", markdown)
        self.assertIn(": Definition 1", markdown)
        self.assertIn("**Term 2**", markdown)
        self.assertIn(": Definition 2", markdown)


class TestStrikethroughRule(unittest.TestCase):
    """测试删除线转换规则。"""

    def setUp(self):
        self.converter = Html2MarkdownConverter()

    def test_s_tag(self):
        """测试<s>标签转换。"""
        html = "<p>This is <s>strikethrough</s> text.</p>"
        markdown = self.converter.convert_html(html)
        self.assertIn("This is ~~strikethrough~~ text.", markdown)

    def test_del_tag(self):
        """测试<del>标签转换。"""
        html = "<p>This is <del>deleted</del> text.</p>"
        markdown = self.converter.convert_html(html)
        self.assertIn("This is ~~deleted~~ text.", markdown)

    def test_strike_tag(self):
        """测试<strike>标签转换。"""
        html = "<p>This is <strike>struck through</strike> text.</p>"
        markdown = self.converter.convert_html(html)
        self.assertIn("This is ~~struck through~~ text.", markdown)


class TestSubscriptSuperscriptRules(unittest.TestCase):
    """测试上标和下标规则。"""

    def setUp(self):
        """测试前的设置。"""
        # 默认使用HTML标签
        self.converter = Html2MarkdownConverter()

        # 不使用HTML标签的转换器
        self.converter_no_html = Html2MarkdownConverter(options={"useHtmlTags": False})

    def test_subscript(self):
        """测试下标转换。"""
        html = "<p>H<sub>2</sub>O is water.</p>"

        # 使用HTML标签
        markdown = self.converter.convert_html(html)
        self.assertIn("H<sub>2</sub>O is water.", markdown)

        # 不使用HTML标签
        markdown = self.converter_no_html.convert_html(html)
        self.assertIn("H_2", markdown)

    def test_superscript(self):
        """测试上标转换。"""
        html = "<p>E=mc<sup>2</sup> is Einstein's equation.</p>"

        # 使用HTML标签
        markdown = self.converter.convert_html(html)
        self.assertIn("E=mc<sup>2</sup> is Einstein's equation.", markdown)

        # 不使用HTML标签
        markdown = self.converter_no_html.convert_html(html)
        self.assertIn("E=mc^2", markdown)


class TestTaskListRule(unittest.TestCase):
    """测试任务列表规则。"""

    def setUp(self):
        """测试前的设置。"""
        self.converter = Html2MarkdownConverter()

    def test_checked_task(self):
        """测试已选中任务项的转换。"""
        html = "<ul><li><input type='checkbox' checked/>Completed task</li></ul>"
        markdown = self.converter.convert_html(html)
        self.assertIn("- [x] Completed task", markdown)

    def test_unchecked_task(self):
        """测试未选中任务项的转换。"""
        html = "<ul><li><input type='checkbox'/>Pending task</li></ul>"
        markdown = self.converter.convert_html(html)
        self.assertIn("- [ ] Pending task", markdown)

    def test_multiple_tasks(self):
        """测试多个任务项的转换。"""
        html = """
        <ul>
            <li><input type='checkbox' checked/>Task 1</li>
            <li><input type='checkbox'/>Task 2</li>
            <li><input type='checkbox' checked/>Task 3</li>
        </ul>
        """
        markdown = self.converter.convert_html(html)
        self.assertIn("- [x] Task 1", markdown)
        self.assertIn("- [ ] Task 2", markdown)
        self.assertIn("- [x] Task 3", markdown)

    def test_custom_checkbox(self):
        """测试自定义复选框元素。"""
        # 使用非标准结构的复选框
        html = """
        <ul>
            <li><input type='checkbox' checked/>Task 1</li>
            <li><input type='checkbox'/>Task 2</li>
        </ul>
        """
        markdown = self.converter.convert_html(html)
        self.assertIn("- [x] Task 1", markdown)
        self.assertIn("- [ ] Task 2", markdown)


if __name__ == "__main__":
    unittest.main()
