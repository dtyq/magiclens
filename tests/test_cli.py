#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
测试命令行接口功能。
"""

import os
import sys
import unittest
from unittest.mock import patch
import tempfile
from pathlib import Path

# 将项目根目录添加到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.magiclens.cli import main, parse_args, convert_html, get_options_from_args


class TestCLI(unittest.TestCase):
    """测试命令行接口功能。"""

    def setUp(self):
        self.test_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>测试页面</title>
        </head>
        <body>
            <h1>标题1</h1>
            <p>这是一个<strong>测试</strong>段落，包含<em>斜体</em>文本。</p>
            <ul>
                <li>项目1</li>
                <li>项目2</li>
            </ul>
        </body>
        </html>
        """

        # 创建临时HTML文件
        self.temp_dir = tempfile.TemporaryDirectory()
        self.temp_html_path = os.path.join(self.temp_dir.name, "test.html")
        with open(self.temp_html_path, "w", encoding="utf-8") as f:
            f.write(self.test_html)

        # 创建临时配置文件
        self.temp_config_path = os.path.join(self.temp_dir.name, "test_config.yaml")
        with open(self.temp_config_path, "w", encoding="utf-8") as f:
            f.write('{"headingStyle": "setext", "bulletListMarker": "-"}')

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_parse_args(self):
        """测试参数解析功能。"""
        with patch('sys.argv', ['magiclens', '-f', 'test.html']):
            args = parse_args()
            self.assertEqual(args.file, 'test.html')
            self.assertIsNone(args.url)
            self.assertIsNone(args.string)

        with patch('sys.argv', ['magiclens', '-u', 'https://example.com']):
            args = parse_args()
            self.assertEqual(args.url, 'https://example.com')

        with patch('sys.argv', ['magiclens', '-s', '<p>测试</p>']):
            args = parse_args()
            self.assertEqual(args.string, '<p>测试</p>')

    def test_get_options_from_args(self):
        """测试从参数获取选项功能。"""
        with patch('sys.argv', [
            'magiclens',
            '-s', '<p>测试</p>',
            '--heading-style', 'setext',
            '--bullet-list-marker', '-'
        ]):
            args = parse_args()
            options = get_options_from_args(args)
            self.assertEqual(options['headingStyle'], 'setext')
            self.assertEqual(options['bulletListMarker'], '-')

    def test_convert_html_from_file(self):
        """测试从文件转换HTML功能。"""
        # 创建临时HTML文件
        html_content = """
        <html>
        <head><title>测试页面</title></head>
        <body>
            <h1>标题1</h1>
            <p>这是一个<strong>测试</strong>段落，包含<em>斜体</em>文本。</p>
            <ul>
                <li>项目1</li>
                <li>项目2</li>
            </ul>
        </body>
        </html>
        """
        html_file = os.path.join(self.temp_dir.name, "test.html")
        with open(html_file, 'w', encoding='utf-8') as f:
            f.write(html_content)

        with patch('sys.argv', ['magiclens', '-f', html_file]):
            args = parse_args()
            options = get_options_from_args(args)
            markdown = convert_html(args, options)

            # 验证转换结果
            self.assertIn('# 标题1', markdown)
            self.assertIn('**测试**', markdown)
            self.assertIn('*斜体*', markdown)
            self.assertIn('- 项目1', markdown)  # 使用GitHub风格的'-'作为列表标记

    def test_convert_html_from_string(self):
        """测试从字符串转换HTML功能。"""
        test_html = "<h1>测试标题</h1><p>测试段落</p>"
        with patch('sys.argv', ['magiclens', '-s', test_html]):
            args = parse_args()
            options = get_options_from_args(args)
            markdown = convert_html(args, options)

            # 验证转换结果
            self.assertIn('# 测试标题', markdown)
            self.assertIn('测试段落', markdown)

    def test_config_file(self):
        """测试配置文件功能。"""
        # 创建传统风格Markdown的配置
        config_content = """dialect: traditional
headingStyle: setext
bulletListMarker: "-"
"""
        with open(self.temp_config_path, 'w') as f:
            f.write(config_content)

        with patch('sys.argv', [
            'magiclens',
            '-s', '<h1>测试</h1><ul><li>项目</li></ul>',
            '--config', self.temp_config_path
        ]):
            args = parse_args()
            options = get_options_from_args(args)
            markdown = convert_html(args, options)

            # 验证使用了配置文件中的设置
            # 检查是否使用了Setext风格标题（标题下有=号）
            lines = markdown.strip().split('\n')
            for i in range(1, len(lines)):
                if lines[i-1].strip() == '测试' and all(c == '=' for c in lines[i].strip()):
                    setext_style_found = True
                    break
            else:
                setext_style_found = False

            self.assertTrue(setext_style_found, "未找到Setext风格标题")
            self.assertIn('- 项目', markdown)     # - 作为列表标记

    def test_output_to_file(self):
        """测试输出到文件功能。"""
        output_path = os.path.join(self.temp_dir.name, "output.md")

        with patch('sys.argv', [
            'magiclens',
            '-s', '<h1>输出测试</h1>',
            '-o', output_path
        ]), patch('sys.stdout'):  # 禁止打印
            main()

            # 验证输出文件是否存在并包含正确内容
            self.assertTrue(os.path.exists(output_path))
            with open(output_path, 'r', encoding='utf-8') as f:
                content = f.read()
                self.assertIn('# 输出测试', content)


if __name__ == '__main__':
    unittest.main()
