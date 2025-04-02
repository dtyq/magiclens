#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量转换Web页面示例

此示例展示如何使用MagicLens将目录中的HTML文件批量转换为Markdown文件。
本示例将处理 web-pages 目录中的所有HTML文件，并在同一目录中生成对应的Markdown文件。
MagicLens现在内置了对微信公众号文章的自动检测和处理功能，无需额外的代码。
"""

import time
from pathlib import Path

from magiclens.converters import Html2MarkdownConverter


def convert_html_files(source_dir, output_dir=None, options=None):
    """
    批量转换目录中的HTML文件为Markdown格式

    Args:
        source_dir: 源HTML文件目录
        output_dir: 输出Markdown文件目录，默认与源目录相同
        options: 转换选项
    """
    # 如果未指定输出目录，使用源目录
    if output_dir is None:
        output_dir = source_dir

    # 确保目录存在
    Path(output_dir).mkdir(parents=True, exist_ok=True)

    # 创建转换器
    converter = Html2MarkdownConverter(options=options)

    # 获取所有HTML文件
    html_files = list(Path(source_dir).glob("*.html"))
    total_files = len(html_files)

    if total_files == 0:
        print(f"在 {source_dir} 目录中未找到HTML文件")
        return

    print(f"开始转换 {total_files} 个HTML文件:")

    # 转换每个文件
    for i, html_file in enumerate(html_files, 1):
        # 输出文件路径（将.html替换为.md）
        md_file = Path(output_dir) / f"{html_file.stem}.md"

        print(f"[{i}/{total_files}] 转换 {html_file.name} -> {md_file.name}")
        start_time = time.time()

        try:
            # 读取HTML文件
            with open(html_file, 'r', encoding='utf-8') as f:
                html_content = f.read()

            # 转换为Markdown（自动检测和处理微信公众号文章）
            markdown_content = converter.convert_html(html_content)

            # 写入Markdown文件
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(markdown_content)

            elapsed = time.time() - start_time
            print(f"    完成 ({elapsed:.2f}秒)")

        except Exception as e:
            print(f"    转换失败: {str(e)}")

    print(f"\n所有转换完成。结果保存在: {output_dir}")


def main():
    # 示例路径 - 当前脚本所在目录下的web-pages目录
    script_dir = Path(__file__).parent
    source_dir = script_dir / "web-pages"

    # 可以自定义输出目录，这里我们使用源目录
    output_dir = source_dir

    # 转换选项
    # 您可以使用任何支持的方言: "github", "commonmark", "traditional", "wechat"
    options = {
        "dialect": "github",  # 也可以使用 "wechat" 专门针对微信公众号文章
        "auto_detect_website_type": True,  # 自动检测网站类型 (默认为True)
        "clean": {
            "removeComments": True,      # 删除HTML注释
            "removeEmptyTags": True,     # 删除空标签
            "removeTags": ["script", "style", "noscript", "iframe"]  # 删除特定标签
        }
    }

    print("=" * 50)
    print("批量HTML到Markdown转换示例")
    print("=" * 50)
    print(f"源目录: {source_dir}")
    print(f"输出目录: {output_dir}")
    print("-" * 50)

    # 执行转换
    convert_html_files(source_dir, output_dir, options)


if __name__ == "__main__":
    main()
