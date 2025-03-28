#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
比较不同Markdown方言对同一HTML内容的转换效果。
"""

import os
import json
import yaml
from magiclens.converters import Html2MarkdownConverter


def load_config(config_path):
    """加载配置文件"""
    with open(config_path, 'r', encoding='utf-8') as f:
        if config_path.lower().endswith(('.yaml', '.yml')):
            return yaml.safe_load(f)
        else:
            return json.load(f)


def convert_with_dialect(html, dialect_name, config_file):
    """使用指定方言配置转换HTML"""
    config_path = os.path.join(
        os.path.dirname(__file__),
        "config_examples",
        config_file
    )

    options = load_config(config_path)
    converter = Html2MarkdownConverter(options=options)
    markdown = converter.convert_html(html)

    # 为了显示效果，我们在控制台中打印结果
    print(f"\n=== {dialect_name} 转换结果 ===")
    print(markdown)
    print("="*40)

    return markdown


def main():
    """主函数：比较不同方言的转换效果"""
    # 样本HTML，包含各种Markdown常见元素
    html = """
    <article>
        <h1>Markdown格式转换比较</h1>

        <h2>文本格式</h2>
        <p>这是<em>强调</em>和<strong>加粗</strong>文本。</p>
        <p>这是<del>删除线</del>文本和<code>内联代码</code>示例。</p>

        <h2>列表</h2>
        <h3>无序列表</h3>
        <ul>
            <li>项目一</li>
            <li>项目二
                <ul>
                    <li>嵌套项目A</li>
                    <li>嵌套项目B</li>
                </ul>
            </li>
            <li>项目三</li>
        </ul>

        <h3>有序列表</h3>
        <ol>
            <li>第一步</li>
            <li>第二步</li>
            <li>第三步</li>
        </ol>

        <h3>任务列表</h3>
        <ul>
            <li><input type="checkbox" checked> 已完成任务</li>
            <li><input type="checkbox"> 未完成任务</li>
        </ul>

        <h2>代码块</h2>
        <pre><code>function example() {
    console.log("这是一个代码块");
    return true;
}</code></pre>

        <h2>表格</h2>
        <table>
            <thead>
                <tr>
                    <th>方言</th>
                    <th>特点</th>
                    <th>用途</th>
                </tr>
            </thead>
            <tbody>
                <tr>
                    <td>GitHub</td>
                    <td>支持任务列表、表格</td>
                    <td>GitHub文档</td>
                </tr>
                <tr>
                    <td>CommonMark</td>
                    <td>标准化</td>
                    <td>通用文档</td>
                </tr>
                <tr>
                    <td>传统Markdown</td>
                    <td>简洁</td>
                    <td>基础文档</td>
                </tr>
            </tbody>
        </table>

        <h2>引用</h2>
        <blockquote>
            <p>这是一个块引用的例子。</p>
            <blockquote>
                <p>这是嵌套的引用。</p>
            </blockquote>
        </blockquote>

        <h2>链接和图片</h2>
        <p>这是一个<a href="https://example.com">链接</a>示例。</p>
        <p>这是一个图片示例：<img src="https://example.com/image.jpg" alt="示例图片"></p>
    </article>
    """

    # 使用不同方言转换相同HTML
    convert_with_dialect(html, "GitHub风格", "github.json")
    convert_with_dialect(html, "CommonMark风格", "commonmark.yaml")
    convert_with_dialect(html, "传统Markdown风格", "traditional.yaml")
    convert_with_dialect(html, "自定义风格", "custom.json")

    print("\n各方言特点比较:")
    print("1. GitHub风格: 支持任务列表、表格，使用ATX风格的标题(#)")
    print("2. CommonMark风格: 更加标准化，使用反引号作为代码块标识")
    print("3. 传统Markdown风格: 使用缩进代码块，Setext风格的标题(===)")
    print("4. 自定义风格: 根据用户需求定制的特殊格式")


if __name__ == "__main__":
    main()
