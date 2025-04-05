#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MagicLens命令行接口。
提供命令行工具用于HTML到Markdown的转换。
"""

import argparse
import sys
import os
import json
import yaml
from pathlib import Path
from typing import Dict, Any, Optional

from .converters.html2md import Html2MarkdownConverter


def parse_args() -> argparse.Namespace:
    """解析命令行参数。"""
    parser = argparse.ArgumentParser(
        description="MagicLens - 将HTML转换为Markdown。",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter
    )

    # 输入源选项组
    input_group = parser.add_argument_group("输入选项")
    source = input_group.add_mutually_exclusive_group(required=True)
    source.add_argument("-f", "--file", help="HTML文件路径")
    source.add_argument("-u", "--url", help="HTML网页URL")
    source.add_argument("-s", "--string", help="HTML字符串")

    # 输出选项组
    output_group = parser.add_argument_group("输出选项")
    output_group.add_argument("-o", "--output", help="输出文件路径，不指定则输出到标准输出")

    # 转换选项组
    convert_group = parser.add_argument_group("转换选项")
    convert_group.add_argument("--dialect", choices=["github", "commonmark", "traditional", "custom"],
                               default="github", help="Markdown方言")
    convert_group.add_argument("--heading-style", choices=["atx", "setext"],
                               help="标题样式：atx使用#号，setext使用====和----")
    convert_group.add_argument("--bullet-list-marker", choices=["*", "-", "+"],
                               help="无序列表标记")
    convert_group.add_argument("--code-block-style", choices=["fenced", "indented"],
                               help="代码块样式：fenced使用```，indented使用缩进")
    convert_group.add_argument("--fence", choices=["```", "~~~"],
                               help="代码块围栏标记")
    convert_group.add_argument("--em-delimiter", choices=["*", "_"],
                               help="斜体分隔符")
    convert_group.add_argument("--strong-delimiter", choices=["**", "__"],
                               help="粗体分隔符")
    convert_group.add_argument("--link-style", choices=["inlined", "referenced"],
                               help="链接样式：inlined为内联，referenced为引用")
    convert_group.add_argument("--no-images", action="store_true",
                               help="不转换图片，只保留替代文本")
    convert_group.add_argument("--fragment", action="store_true",
                               help="将输入视为HTML片段而非完整HTML")
    convert_group.add_argument("--fragment-root", default="div",
                               help="HTML片段的根元素，仅在fragment=True时有效")
    convert_group.add_argument("--config", help="配置文件路径，支持JSON或YAML格式")
    convert_group.add_argument("--create-config", help="创建默认配置文件")
    convert_group.add_argument("--smart-detection", action="store_true",
                               help="启用智能内容检测，自动识别和优化特定网站内容")
    convert_group.add_argument("--site-type", help="指定网站类型，如'baidu'、'zhihu'、'wechat'等")

    # 杂项选项
    parser.add_argument("-v", "--version", action="store_true", help="显示版本信息")

    return parser.parse_args()


def create_default_config(output_path: str) -> None:
    """
    创建默认配置文件。

    Args:
        output_path: 输出文件路径
    """
    default_config = {
        "dialect": "github",
        "headingStyle": "atx",
        "bulletListMarker": "-",
        "codeBlockStyle": "fenced",
        "fence": "```",
        "emDelimiter": "*",
        "strongDelimiter": "**",
        "linkStyle": "inlined",
        "convertImages": True,
        "clean": {
            "removeTags": ["script", "style", "noscript"],
            "removeAttrs": [],
            "removeClasses": [],
            "removeEmptyTags": False,
            "removeComments": True
        }
    }

    # 确定文件格式
    is_yaml = output_path.lower().endswith(('.yaml', '.yml'))

    try:
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 保存配置到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            if is_yaml:
                yaml.safe_dump(default_config, f, indent=2, sort_keys=False)
            else:
                json.dump(default_config, f, indent=2, ensure_ascii=False)

        print(f"已创建默认配置文件: {output_path}")
    except Exception as e:
        print(f"创建配置文件失败: {e}", file=sys.stderr)
        sys.exit(1)


def load_config(config_path: str) -> Dict[str, Any]:
    """
    从配置文件加载转换选项。支持JSON或YAML格式。

    Args:
        config_path: 配置文件路径

    Returns:
        配置选项字典
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            # 根据文件扩展名判断格式
            if config_path.lower().endswith(('.yaml', '.yml')):
                try:
                    return yaml.safe_load(f) or {}
                except yaml.YAMLError as e:
                    print(f"YAML配置文件解析错误: {e}", file=sys.stderr)
                    sys.exit(1)
            else:
                # 默认尝试解析为JSON
                try:
                    return json.load(f)
                except json.JSONDecodeError as e:
                    print(f"JSON配置文件解析错误: {e}", file=sys.stderr)
                    sys.exit(1)
    except FileNotFoundError:
        print(f"配置文件不存在: {config_path}", file=sys.stderr)
        sys.exit(1)


def get_options_from_args(args: argparse.Namespace) -> Dict[str, Any]:
    """
    从命令行参数生成转换选项。

    Args:
        args: 命令行参数

    Returns:
        转换选项字典
    """
    options = {}

    # 如果指定了配置文件，先从配置文件加载
    if args.config:
        options.update(load_config(args.config))

    # 命令行参数覆盖配置文件
    if args.dialect:
        options["dialect"] = args.dialect

    if args.heading_style:
        options["headingStyle"] = args.heading_style

    if args.bullet_list_marker:
        options["bulletListMarker"] = args.bullet_list_marker

    if args.code_block_style:
        options["codeBlockStyle"] = args.code_block_style

    if args.fence:
        options["fence"] = args.fence

    if args.em_delimiter:
        options["emDelimiter"] = args.em_delimiter

    if args.strong_delimiter:
        options["strongDelimiter"] = args.strong_delimiter

    if args.link_style:
        options["linkStyle"] = args.link_style

    if args.no_images:
        options["convertImages"] = False

    # 添加智能内容检测选项
    if args.smart_detection:
        options["smart_content_detection"] = True

    if args.site_type:
        # 如果指定了网站类型，添加到检测上下文
        if "detection_context" not in options:
            options["detection_context"] = {}
        options["detection_context"]["site_type"] = args.site_type

    return options


def convert_html(args: argparse.Namespace, options: Dict[str, Any]) -> str:
    """
    根据命令行参数转换HTML为Markdown。

    Args:
        args: 命令行参数
        options: 转换选项

    Returns:
        转换后的Markdown文本
    """
    converter = Html2MarkdownConverter(options=options)

    # 准备HTML片段选项
    fragment = args.fragment
    fragment_root = args.fragment_root

    if args.file:
        # 从文件读取HTML
        try:
            with open(args.file, 'r', encoding='utf-8') as f:
                html = f.read()
            if fragment:
                return converter.convert_html_fragment(html, fragment_root=fragment_root)
            else:
                return converter.convert_html(html)
        except FileNotFoundError:
            print(f"文件不存在: {args.file}", file=sys.stderr)
            sys.exit(1)

    elif args.url:
        # 从URL获取HTML
        try:
            if fragment:
                # 先获取URL内容，再当作片段处理
                html = converter.service._get_html_from_url(args.url)
                return converter.convert_html_fragment(html, fragment_root=fragment_root)
            else:
                return converter.convert_url(args.url)
        except Exception as e:
            print(f"URL获取失败: {e}", file=sys.stderr)
            sys.exit(1)

    elif args.string:
        # 直接转换HTML字符串
        if fragment:
            return converter.convert_html_fragment(args.string, fragment_root=fragment_root)
        else:
            return converter.convert_html(args.string)

    return ""


def save_output(text: str, output_path: Optional[str] = None) -> None:
    """
    保存转换结果。

    Args:
        text: 要保存的文本
        output_path: 输出文件路径，None则输出到标准输出
    """
    if output_path:
        # 创建输出目录（如果不存在）
        output_dir = os.path.dirname(output_path)
        if output_dir:
            os.makedirs(output_dir, exist_ok=True)

        # 保存到文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(text)
        print(f"转换完成，已保存到: {output_path}")
    else:
        # 输出到标准输出
        print(text)


def show_version() -> None:
    """显示版本信息。"""
    from . import __version__
    print(f"MagicLens 版本: {__version__}")


def main() -> None:
    """命令行主函数。"""
    args = parse_args()

    if args.version:
        show_version()
        return

    if args.create_config:
        create_default_config(args.create_config)
        return

    # 获取转换选项
    options = get_options_from_args(args)

    # 执行转换
    markdown = convert_html(args, options)

    # 保存输出
    save_output(markdown, args.output)


if __name__ == "__main__":
    main()
