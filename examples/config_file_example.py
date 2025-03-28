#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
演示如何使用配置文件来定制HTML到Markdown转换。
"""

import os
import json
import yaml
from magiclens.converters import Html2MarkdownConverter


def load_config(config_path):
    """
    从配置文件加载选项。

    Args:
        config_path: 配置文件路径

    Returns:
        配置选项字典
    """
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.lower().endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def example_with_github_config():
    """
    使用GitHub风格的配置文件。
    """
    print("\n=== 使用GitHub风格配置文件 ===")

    # 获取配置文件路径
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config_examples",
        "github.json"
    )

    # 加载配置
    options = load_config(config_path)

    # 创建转换器
    converter = Html2MarkdownConverter(options=options)

    # 转换HTML
    html = """
    <div>
        <h1>GitHub风格Markdown</h1>
        <ul>
            <li><input type="checkbox" checked> 已完成任务</li>
            <li><input type="checkbox"> 未完成任务</li>
            <li><del>删除线文本</del></li>
        </ul>
        <pre><code>print("GitHub风格代码块")</code></pre>
    </div>
    """

    # 转换并打印结果
    markdown = converter.convert_html(html)
    print(markdown)


def example_with_traditional_config():
    """
    使用传统Markdown风格的配置文件。
    """
    print("\n=== 使用传统Markdown风格配置文件 ===")

    # 获取配置文件路径
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config_examples",
        "traditional.yaml"
    )

    # 加载配置
    options = load_config(config_path)

    # 创建转换器
    converter = Html2MarkdownConverter(options=options)

    # 转换HTML
    html = """
    <div>
        <h1>传统风格Markdown</h1>
        <p><em>强调文本</em> 和 <strong>加粗文本</strong></p>
        <p>代码示例: <code>print("Hello")</code></p>
        <p>链接示例: <a href="https://example.com">链接文本</a></p>
    </div>
    """

    # 转换并打印结果
    markdown = converter.convert_html(html)
    print(markdown)


def example_with_custom_config():
    """
    使用自定义配置文件。
    """
    print("\n=== 使用自定义配置文件 ===")

    # 获取配置文件路径
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config_examples",
        "custom.json"
    )

    # 加载配置
    options = load_config(config_path)

    # 创建转换器
    converter = Html2MarkdownConverter(options=options)

    # 转换HTML
    html = """
    <div>
        <h1>自定义风格Markdown</h1>
        <p><em>斜体</em> 和 <strong>粗体</strong></p>
        <ul>
            <li>项目1</li>
            <li>项目2</li>
        </ul>
        <pre><code>print("自定义代码块")</code></pre>
    </div>
    """

    # 转换并打印结果
    markdown = converter.convert_html(html)
    print(markdown)


def example_modify_config():
    """
    加载配置文件并修改选项。
    """
    print("\n=== 加载并修改配置 ===")

    # 获取配置文件路径
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config_examples",
        "github.json"
    )

    # 加载配置
    options = load_config(config_path)

    # 修改部分选项
    options["bulletListMarker"] = "+"  # 更改列表标记
    options["headingStyle"] = "setext"  # 更改标题样式

    # 创建转换器
    converter = Html2MarkdownConverter(options=options)

    # 转换HTML
    html = """
    <div>
        <h1>修改后的配置</h1>
        <ul>
            <li>使用+作为列表标记</li>
            <li>使用下划线作为标题样式</li>
        </ul>
    </div>
    """

    # 转换并打印结果
    markdown = converter.convert_html(html)
    print(markdown)


if __name__ == "__main__":
    example_with_github_config()
    example_with_traditional_config()
    example_with_custom_config()
    example_modify_config()
