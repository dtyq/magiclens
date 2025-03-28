#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
基本用法示例：展示如何使用MagicLens将HTML转换为Markdown
"""

import sys
import os

# 添加项目根目录到Python路径，便于导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from src.magiclens.converters import Html2MarkdownConverter


def main():
    # 创建转换器实例
    converter = Html2MarkdownConverter()

    # 示例HTML
    html = """
    <html>
    <head>
        <title>MagicLens示例</title>
    </head>
    <body>
        <h1>HTML到Markdown转换示例</h1>
        <p>这是一个<strong>段落</strong>，包含了<em>斜体</em>和<strong>粗体</strong>文本。</p>
        <h2>列表示例</h2>
        <ul>
            <li>项目1</li>
            <li>项目2</li>
            <li>项目3</li>
        </ul>
        <h2>链接示例</h2>
        <p>这是一个<a href="https://github.com/">链接</a>。</p>
        <h2>图片示例</h2>
        <p><img src="https://github.com/logo.png" alt="GitHub Logo"></p>
        <h2>代码示例</h2>
        <pre><code>
def hello_world():
    print("Hello, World!")
        </code></pre>
    </body>
    </html>
    """

    # 转换HTML到Markdown
    markdown = converter.convert_html(html)

    # 打印结果
    print("转换后的Markdown：")
    print("-" * 50)
    print(markdown)
    print("-" * 50)

    # 使用自定义选项
    custom_options = {
        "headingStyle": "setext",
        "bulletListMarker": "-",
        "codeBlockStyle": "fenced"
    }

    # 创建带自定义选项的转换器
    custom_converter = Html2MarkdownConverter(options=custom_options)

    # 转换HTML
    custom_markdown = custom_converter.convert_html(html)

    # 打印结果
    print("\n使用自定义选项的Markdown：")
    print("-" * 50)
    print(custom_markdown)
    print("-" * 50)

    # 从URL转换
    print("\n从URL转换：")
    print("-" * 50)
    try:
        url_markdown = converter.convert_url("https://example.com")
        print(url_markdown)
    except Exception as e:
        print(f"转换URL时出错：{e}")
    print("-" * 50)


if __name__ == "__main__":
    main()
