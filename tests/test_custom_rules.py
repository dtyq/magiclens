#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试自定义规则功能。
"""

import unittest
from magiclens.converters.html2md import Html2MarkdownConverter
from magiclens.core.rule import Rule


class TestCustomRules(unittest.TestCase):
    """测试自定义规则功能。"""

    def test_custom_rule_class(self):
        """测试创建和注册自定义规则。"""
        # 创建高亮规则
        class HighlightRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'span' and
                        node.get('class') and
                        'highlight' in node.get('class'))

            def replacement(self, content, node, options):
                return f"**{content}**"

        # 创建转换器并注册规则
        converter = Html2MarkdownConverter()
        converter.service.register_rule("highlight", HighlightRule())

        # 测试规则
        html = "<p>This is <span class='highlight'>highlighted text</span> in a paragraph.</p>"
        markdown = converter.convert_html(html)

        # 验证结果
        self.assertIn("This is **highlighted text** in a paragraph", markdown)

    def test_rule_builder(self):
        """测试使用规则构建器创建规则。"""
        # 创建注意事项规则
        class NoteRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'div' and
                        node.get('class') and
                        'note' in node.get('class'))

            def replacement(self, content, node, options):
                return f"> **Note:** {content}\n"

        # 创建重要事项规则
        class ImportantRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'div' and
                        node.get('class') and
                        'important' in node.get('class'))

            def replacement(self, content, node, options):
                return f"**IMPORTANT:** {content}"

        # 创建转换器并注册规则
        converter = Html2MarkdownConverter()
        converter.service.register_rule("note", NoteRule())
        converter.service.register_rule("important", ImportantRule())

        # 测试规则
        html = """
        <div class='note'>This is a note.</div>
        <div class='important'>This is important.</div>
        """
        markdown = converter.convert_html(html)

        # 验证结果
        self.assertIn("> **Note:** This is a note.", markdown)
        self.assertIn("**IMPORTANT:** This is important.", markdown)

    def test_custom_tag_rule(self):
        """测试自定义标签规则。"""
        # 创建自定义元素规则
        class CustomElementRule(Rule):
            def filter(self, node, options):
                return hasattr(node, 'name') and node.name == 'custom-element'

            def replacement(self, content, node, options):
                title = node.get('title', 'Custom Element')
                return f"### {title} ###\n{content}\n"

        # 创建转换器并注册规则
        converter = Html2MarkdownConverter()
        converter.service.register_rule("custom-element", CustomElementRule())

        # 测试规则
        html = """
        <custom-element title="Special Content">
            This is custom content.
        </custom-element>
        """
        markdown = converter.convert_html(html)

        # 验证结果
        self.assertIn("### Special Content ###", markdown)
        self.assertIn("This is custom content.", markdown)

    def test_rule_priority(self):
        """测试规则优先级。"""
        # 创建两个可能匹配同一元素的规则
        class GenericNoteRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'div' and
                        node.get('class') and
                        'note' in node.get('class'))

            def replacement(self, content, node, options):
                return f"> Note: {content}\n"

        class SpecificNoteRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'div' and
                        node.get('class') and
                        'note' in node.get('class') and
                        'warning' in node.get('class'))

            def replacement(self, content, node, options):
                return f"> WARNING: {content}\n"

        # 创建转换器并注册规则 - 特定规则应该先注册以获得更高优先级
        converter = Html2MarkdownConverter()
        converter.service.register_rule("warning-note", SpecificNoteRule())
        converter.service.register_rule("generic-note", GenericNoteRule())

        # 测试规则
        html = "<div class='note warning'>This is a warning note.</div>"
        markdown = converter.convert_html(html)

        # 特定规则应该先匹配
        self.assertIn("> WARNING: This is a warning note.", markdown)

    def test_multiple_rules(self):
        """测试注册多个自定义规则。"""
        # 创建注意事项规则
        class NoteRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'div' and
                        node.get('class') and
                        'note' in node.get('class'))

            def replacement(self, content, node, options):
                return f"> **Note:** {content}\n"

        # 创建重要事项规则
        class ImportantRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'div' and
                        node.get('class') and
                        'important' in node.get('class'))

            def replacement(self, content, node, options):
                return f"**IMPORTANT:** {content}"

        # 创建高亮规则
        class HighlightRule(Rule):
            def filter(self, node, options):
                return (hasattr(node, 'name') and
                        node.name == 'span' and
                        node.get('class') and
                        'highlight' in node.get('class'))

            def replacement(self, content, node, options):
                return f"**{content}**"

        # 创建转换器并注册所有规则
        converter = Html2MarkdownConverter()
        converter.service.register_rule("note", NoteRule())
        converter.service.register_rule("important", ImportantRule())
        converter.service.register_rule("highlight", HighlightRule())

        # 测试多个规则
        html = """
        <div class='note'>This is a note.</div>
        <div class='important'>This is <span class='highlight'>very</span> important.</div>
        """
        markdown = converter.convert_html(html)

        # 验证结果
        self.assertIn("> **Note:** This is a note.", markdown)
        self.assertIn("**IMPORTANT:** This is **very** important.", markdown)


if __name__ == "__main__":
    unittest.main()
