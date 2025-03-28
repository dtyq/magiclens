#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MagicLens 快速入门示例。

本示例展示了如何使用MagicLens将HTML转换为Markdown的基本用法。
"""

import os
import sys

# 将项目根目录添加到sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.magiclens.converters.html2md import Html2MarkdownConverter


def example_convert_html_string():
    """示例：从HTML字符串转换为Markdown。"""
    print("=== 示例1：从HTML字符串转换 ===")

    # 创建转换器
    converter = Html2MarkdownConverter()

    # HTML字符串
    html = """
    <h1>MagicLens 示例</h1>
    <p>这是一个<strong>示例</strong>，演示如何使用<em>MagicLens</em>将HTML转换为Markdown。</p>
    <ul>
        <li>支持<a href="https://example.com">链接</a></li>
        <li>支持<code>代码</code></li>
        <li>支持<img src="image.png" alt="图片"></li>
    </ul>
    <blockquote>
        <p>这是一段引用</p>
    </blockquote>
    """

    # 转换HTML
    markdown = converter.convert_html(html)

    # 打印结果
    print(markdown)
    print()


def example_convert_with_options():
    """示例：使用不同选项进行转换。"""
    print("=== 示例2：使用不同选项 ===")

    # HTML字符串
    html = """
    <h1>自定义选项示例</h1>
    <p>这个示例展示了如何使用<strong>自定义选项</strong>。</p>
    <ul>
        <li>列表项1</li>
        <li>列表项2</li>
    </ul>
    """

    # 使用不同的选项创建转换器
    options = {
        "headingStyle": "setext",  # 使用下划线风格的标题
        "bulletListMarker": "-",   # 使用减号作为无序列表标记
        "emDelimiter": "_",        # 使用下划线作为斜体标记
        "strongDelimiter": "__"    # 使用双下划线作为粗体标记
    }
    converter = Html2MarkdownConverter(options=options)

    # 转换HTML
    markdown = converter.convert_html(html)

    # 打印结果
    print(markdown)
    print()


def example_convert_url():
    """示例：从URL转换HTML。"""
    print("=== 示例3：从URL转换 ===")

    # 创建转换器
    converter = Html2MarkdownConverter()

    # 转换URL（使用示例网页）
    url = "https://example.com"
    try:
        markdown = converter.convert_url(url)
        print(f"已转换 {url}:")
        print(markdown[:500] + "..." if len(markdown) > 500 else markdown)
    except Exception as e:
        print(f"转换URL时出错: {e}")
    print()


def example_save_to_file():
    """示例：保存转换结果到文件。"""
    print("=== 示例4：保存到文件 ===")

    # 创建转换器
    converter = Html2MarkdownConverter()

    # HTML字符串
    html = "<h1>保存到文件</h1><p>这个示例展示了如何将转换结果保存到文件。</p>"

    # 转换HTML
    markdown = converter.convert_html(html)

    # 保存到文件
    output_file = "example_output.md"
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(markdown)

    print(f"转换结果已保存到: {output_file}")
    print()


if __name__ == "__main__":
    print("MagicLens 快速入门示例\n")

    # 运行所有示例
    example_convert_html_string()
    example_convert_with_options()
    example_convert_url()
    example_save_to_file()

    print("示例运行完毕！")
