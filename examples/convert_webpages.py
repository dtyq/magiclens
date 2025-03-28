#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
批量转换Web页面示例

此示例展示如何使用MagicLens将目录中的HTML文件批量转换为Markdown文件。
本示例将处理 web-pages 目录中的所有HTML文件，并在同一目录中生成对应的Markdown文件。
支持对微信公众号文章的特殊处理，正确提取图片链接。
"""

import os
import time
import re
import json
from pathlib import Path
from bs4 import BeautifulSoup

from magiclens.converters import Html2MarkdownConverter


def fix_wechat_article_html(html_content):
    """
    修复微信公众号文章的HTML，主要处理图片链接

    Args:
        html_content: 原始HTML内容

    Returns:
        修复后的HTML内容
    """
    soup = BeautifulSoup(html_content, 'html.parser')

    # 处理微信图片：微信公众号文章中图片通常有多种存储方式
    for img in soup.find_all('img'):
        # 1. 优先检查data-src属性（微信最常用的图片加载方式）
        data_src = img.get('data-src')
        if data_src and not data_src.startswith('data:'):
            img['src'] = data_src
            # 清除可能引起问题的属性
            for attr in ['data-lazy-src', 'data-srcset', 'srcset', 'data-ratio', 'data-w']:
                if attr in img.attrs:
                    del img[attr]
            continue

        # 2. 检查可能存在的其他图片源
        possible_src_attrs = ['data-original', 'data-actualsrc', 'data-lazy-src']
        for attr in possible_src_attrs:
            if attr in img.attrs and img[attr] and not img[attr].startswith('data:'):
                img['src'] = img[attr]
                break

        # 3. 检查图片是否已有正常src
        src = img.get('src', '')
        if src.startswith('data:image/svg') or src.startswith('data:') or not src:
            # 尝试从style属性中提取background-image
            style = img.get('style', '')

            # 查找background-image样式
            bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', style)
            if bg_match:
                img['src'] = bg_match.group(1)
                continue

            # 无法找到有效的图片链接，尝试检查周边元素
            parent = img.parent
            if parent and 'style' in parent.attrs:
                parent_style = parent.get('style', '')
                bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', parent_style)
                if bg_match:
                    img['src'] = bg_match.group(1)
                    continue

            # 尝试检查最近的<section>是否有背景图
            section = img.find_parent('section')
            if section and 'style' in section.attrs:
                section_style = section.get('style', '')
                bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', section_style)
                if bg_match:
                    img['src'] = bg_match.group(1)
                    continue

            # 微信常用域名的图片修复
            if 'class' in img.attrs:
                classes = img.get('class', [])
                for cls in classes:
                    if cls.startswith('__bg_') and parent and 'data-src' in parent.attrs:
                        img['src'] = parent['data-src']
                        break

        # 4. 处理相对URL、不完整URL和缺少协议的URL
        if 'src' in img.attrs and img['src']:
            src = img['src']
            # 添加协议前缀
            if src.startswith('//'):
                img['src'] = 'https:' + src
            # 微信文章图片常用域名扩展
            elif src.startswith('/mmbiz_'):
                img['src'] = 'https://mmbiz.qpic.cn' + src

    # 移除微信公众号中的一些不需要的元素
    for selector in [
        '.rich_media_meta_list', '.reward_area', '.qr_code_pc', '.tool_area',
        '.weui-dialog', '.weapp_text_link', '.weapp_display_element',
        '.js_wx_tap_highlight', '.js_img_loading', '.audio_card'
    ]:
        for element in soup.select(selector):
            element.decompose()

    # 移除js脚本内容
    for script in soup.find_all('script'):
        script.decompose()

    # 移除样式内容
    for style in soup.find_all('style'):
        style.decompose()

    # 处理微信的一些特殊封装元素
    for mpvoice in soup.find_all('mpvoice'):
        new_p = soup.new_tag('p')
        new_p.string = f"[音频消息] {mpvoice.get('name', '语音')}"
        mpvoice.replace_with(new_p)

    for qqmusic in soup.find_all('qqmusic'):
        new_p = soup.new_tag('p')
        new_p.string = f"[音乐] {qqmusic.get('musicname', '音乐')}"
        qqmusic.replace_with(new_p)

    # 尝试提取文章标题
    title_tags = soup.select('.rich_media_title')
    if title_tags:
        title = title_tags[0].get_text(strip=True)
        # 创建标题标签
        h1 = soup.new_tag('h1')
        h1.string = title
        # 在正文开头插入标题
        content = soup.select('.rich_media_content')
        if content:
            content[0].insert(0, h1)

    return str(soup)


def post_process_markdown(markdown_content):
    """
    对转换后的Markdown内容进行后处理

    Args:
        markdown_content: 原始Markdown内容

    Returns:
        处理后的Markdown内容
    """
    # 移除特殊字符和转义序列
    markdown_content = re.sub(r'&#x[0-9a-fA-F]+;', '', markdown_content)

    # 修复图片链接中的问题
    markdown_content = re.sub(r'!\[图片\]\(data:image/svg.*?\)', '', markdown_content)
    markdown_content = re.sub(r'!\[\]\(data:image/svg.*?\)', '', markdown_content)

    # 移除空图片
    markdown_content = re.sub(r'!\[\]\(\s*\)', '', markdown_content)
    markdown_content = re.sub(r'!\[图片\]\(\s*\)', '', markdown_content)

    # 修复微信中的一些特殊格式
    markdown_content = re.sub(r'javascript:void\(0\);', '#', markdown_content)
    markdown_content = re.sub(r'javascript:;', '#', markdown_content)

    # 删除微信文章中的评论、赞赏等无关内容
    patterns_to_remove = [
        r'微信扫一扫赞赏作者.*?返回',
        r'喜欢作者.*?赞赏支持',
        r'长按二维码向我转账',
        r'受苹果公司新规定影响.*?无法使用',
        r'名称已清空.*?其它金额',
        r'修改于202\d年\d{1,2}月\d{1,2}日',
    ]

    for pattern in patterns_to_remove:
        markdown_content = re.sub(pattern, '', markdown_content, flags=re.DOTALL)

    # 移除多余的空行
    markdown_content = re.sub(r'\n{3,}', '\n\n', markdown_content)

    # 移除图片后的无用交互文本
    markdown_content = re.sub(r'轻点两下取消赞|，轻点两下取消在看', '', markdown_content)

    # 移除预览时标签不可点等微信特殊文本
    markdown_content = re.sub(r'预览时标签不可点.*?关闭更多', '', markdown_content, flags=re.DOTALL)

    # 移除底部导航条
    markdown_content = re.sub(r'分析.{0,50}：.{0,50}，.{0,50}，.{0,50}，.*?收藏.{0,50}听过', '', markdown_content, flags=re.DOTALL)

    # 移除公众号文章结尾常见的提示内容
    markdown_content = re.sub(r'继续滑动看下一个.*?轻触阅读原文', '', markdown_content, flags=re.DOTALL)
    markdown_content = re.sub(r'向上滑动看下一个.*?当前内容可能存在.*?广告规范指引', '', markdown_content, flags=re.DOTALL)

    return markdown_content


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

            # 检测是否为微信公众号文章
            is_wechat = "微信公众号" in html_content or "data-src" in html_content or "rich_media" in html_content

            # 预处理HTML，修复微信公众号文章
            if is_wechat:
                print("    检测到微信公众号文章，应用特殊处理...")
                html_content = fix_wechat_article_html(html_content)

            # 转换为Markdown
            markdown_content = converter.convert_html(html_content)

            # 后处理Markdown内容
            markdown_content = post_process_markdown(markdown_content)

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

    # 转换选项 - 这里使用默认的GitHub风格Markdown
    options = {
        "dialect": "github",
        # 优化选项可以根据需要调整
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
