#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
展示如何使用MagicLens中的Markdown方言功能。
"""

from magiclens.converters import Html2MarkdownConverter


def example_github_dialect():
    """
    展示GitHub风格Markdown的使用。
    """
    print("\n=== GitHub Flavored Markdown ===")

    converter = Html2MarkdownConverter(options={"dialect": "github"})

    html = """
    <h1>GitHub风格Markdown</h1>
    <p>GitHub风格Markdown支持以下特性：</p>
    <ul>
        <li><input type="checkbox" checked> 任务列表</li>
        <li><input type="checkbox"> 未完成的任务</li>
        <li><del>删除线文本</del></li>
        <li>代码块使用```标记</li>
        <li>表格支持</li>
    </ul>

    <table>
        <thead>
            <tr><th>名称</th><th>说明</th></tr>
        </thead>
        <tbody>
            <tr><td>GitHub</td><td>支持表格、任务列表等</td></tr>
            <tr><td>CommonMark</td><td>标准Markdown规范</td></tr>
        </tbody>
    </table>

    <p>代码块示例：</p>
    <pre><code class="python">
    def hello():
        print("Hello, World!")
    </code></pre>
    """

    markdown = converter.convert_html(html)
    print(markdown)


def example_commonmark_dialect():
    """
    展示CommonMark风格的使用。
    """
    print("\n=== CommonMark 规范 ===")

    converter = Html2MarkdownConverter(options={"dialect": "commonmark"})

    html = """
    <h1>CommonMark规范</h1>
    <p>CommonMark是一个标准化的Markdown规范：</p>
    <ul>
        <li>使用*作为无序列表标记</li>
        <li>使用ATX风格的标题（# 标题）</li>
        <li>强调使用*号</li>
        <li>代码块使用缩进或```标记</li>
    </ul>

    <p><em>强调文本</em> 和 <strong>加粗文本</strong></p>
    <blockquote>
        <p>这是引用文本</p>
    </blockquote>
    """

    markdown = converter.convert_html(html)
    print(markdown)


def example_traditional_dialect():
    """
    展示传统Markdown风格的使用。
    """
    print("\n=== 传统Markdown ===")

    converter = Html2MarkdownConverter(options={"dialect": "traditional"})

    html = """
    <h1>传统Markdown</h1>
    <h2>子标题</h2>
    <p>传统Markdown风格特点：</p>
    <ul>
        <li>使用Setext风格的标题（标题下划线）</li>
        <li>使用_号进行强调</li>
        <li>使用*号作为无序列表标记</li>
    </ul>

    <p><em>斜体文本</em> 和 <strong>粗体文本</strong></p>
    <p>代码片段：<code>print("Hello")</code></p>
    """

    markdown = converter.convert_html(html)
    print(markdown)


def example_custom_dialect():
    """
    展示自定义Markdown风格的使用。
    """
    print("\n=== 自定义Markdown风格 ===")

    # 创建自定义方言设置
    custom_options = {
        "dialect": "custom",
        "headingStyle": "atx",          # 使用ATX风格标题 (# 标题)
        "bulletListMarker": "+",        # 使用+作为无序列表标记
        "codeBlockStyle": "fenced",     # 使用围栏式代码块
        "fence": "~~~",                 # 使用~~~作为代码块围栏
        "emDelimiter": "_",             # 使用_作为斜体标记
        "strongDelimiter": "__",        # 使用__作为粗体标记
        "linkStyle": "inlined",         # 使用内联链接风格
        "linkReferenceStyle": "full",   # 使用完整的引用链接
        "useHtmlTags": False            # 不使用HTML标签，尽量都转为Markdown
    }

    converter = Html2MarkdownConverter(options=custom_options)

    html = """
    <h1>自定义Markdown风格</h1>
    <p>这是一个<em>使用自定义选项</em>的Markdown示例。</p>
    <ul>
        <li>第一项</li>
        <li>第二项</li>
        <li>第三项</li>
    </ul>
    <p>代码示例：</p>
    <pre><code>
    function hello() {
        console.log("Hello, World!");
    }
    </code></pre>
    <p><a href="https://example.com">示例链接</a></p>
    """

    markdown = converter.convert_html(html)
    print(markdown)


def example_override_dialect():
    """
    展示覆盖方言默认选项的使用。
    """
    print("\n=== 覆盖默认方言选项 ===")

    # 使用GitHub方言，但覆盖某些选项
    options = {
        "dialect": "github",
        "bulletListMarker": "+",    # 覆盖GitHub默认的-
        "headingStyle": "setext",   # 覆盖GitHub默认的atx
        "codeBlockStyle": "indented" # 覆盖GitHub默认的fenced
    }

    converter = Html2MarkdownConverter(options=options)

    html = """
    <h1>覆盖默认选项</h1>
    <p>这个示例展示了如何覆盖默认方言选项：</p>
    <ul>
        <li>无序列表使用+而不是-</li>
        <li>标题使用Setext风格</li>
        <li>代码块使用缩进而不是围栏</li>
    </ul>
    <pre><code>
    // 代码块示例
    const greeting = "Hello!";
    </code></pre>
    <p>但仍然支持GitHub特性，如：</p>
    <ul>
        <li><input type="checkbox" checked> 已完成任务</li>
        <li><del>删除线文本</del></li>
    </ul>
    """

    markdown = converter.convert_html(html)
    print(markdown)


if __name__ == "__main__":
    example_github_dialect()
    example_commonmark_dialect()
    example_traditional_dialect()
    example_custom_dialect()
    example_override_dialect()
