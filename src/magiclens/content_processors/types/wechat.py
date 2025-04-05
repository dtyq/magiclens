from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re

from ..base import ContentProcessorBase


class WeChatPublicAccountProcessor(ContentProcessorBase):
    """
    微信公众号文章内容处理器，处理微信公众号文章的HTML和Markdown内容。

    主要功能：
    1. 预处理：清理广告、处理图片、优化HTML结构
    2. 后处理：优化格式、移除多余内容
    """

    @property
    def content_type(self) -> str:
        """获取处理器支持的内容类型"""
        return "wechat_public_account"

    def preprocess(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> BeautifulSoup:
        """
        对微信公众号文章HTML进行预处理。

        Args:
            soup: 待处理的HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的BeautifulSoup对象
        """
        # 1. 处理微信图片
        self._fix_wechat_images(soup)

        # 2. 移除广告和无关内容
        self._remove_wechat_ads(soup)

        # 3. 识别并保留文章主体内容
        self._extract_main_content(soup)

        # 4. 清理多余的样式和属性
        self._clean_wechat_attributes(soup)

        return soup

    def postprocess(self, markdown: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        对转换后的微信公众号文章Markdown进行后处理。

        Args:
            markdown: 转换后的Markdown内容
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的Markdown内容
        """
        # 1. 移除微信特有的推广文本
        markdown = self._remove_promotion_text(markdown)

        # 2. 修复格式问题
        markdown = self._fix_format_issues(markdown)

        # 3. 整理空行
        markdown = self._clean_empty_lines(markdown)

        return markdown

    def _fix_wechat_images(self, soup: BeautifulSoup) -> None:
        """处理微信公众号文章中的图片"""
        # 处理data-src属性的图片
        for img in soup.find_all('img'):
            # 优先使用data-src属性
            data_src = img.get('data-src')
            if data_src and not data_src.startswith('data:'):
                img['src'] = data_src

                # 清除可能影响显示的属性
                for attr in ['data-srcset', 'srcset', 'data-ratio', 'data-w', 'style']:
                    if attr in img.attrs:
                        del img[attr]

            # 处理style中的背景图片
            style = img.get('style', '')
            bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', style)
            if bg_match and not img.get('src'):
                img['src'] = bg_match.group(1)

            # 处理base64图片
            src = img.get('src', '')
            if src and src.startswith('data:image/'):
                # 由于base64图片通常体积大、加载慢，这里用alt标记替代
                img['alt'] = '[图片]'
                if 'src' in img.attrs:
                    del img['src']

    def _remove_wechat_ads(self, soup: BeautifulSoup) -> None:
        """移除微信公众号文章中的广告和无关内容"""
        # 移除广告相关元素
        ad_selectors = [
            '.rich_media_area_extra',   # 底部推广区域
            '.qr_code_pc',              # 二维码
            '.rich_media_tool',         # 底部工具栏
            '#js_pc_qr_code',           # PC二维码
            '#js_profile_qrcode',       # 个人资料二维码
            '.rich_media_extra',        # 额外内容区
            '.rich_tips',               # 顶部提示
            '.discuss_container',       # 评论区
            '.function_mod',            # 功能模块
            '.rich_media_meta_list'     # 元数据列表（通常包含作者、公众号等信息）
        ]

        for selector in ad_selectors:
            for element in soup.select(selector):
                element.decompose()

        # 移除含特定文本的元素（如赞赏按钮、广告文本等）
        ad_texts = [
            "点击上方蓝字关注我们",
            "长按识别二维码关注",
            "点击在看",
            "点赞",
            "赞赏支持",
            "微信扫一扫赞赏作者"
        ]

        for text in ad_texts:
            for element in soup.find_all(string=lambda s: s and text in s):
                # 尝试找到包含此文本的父元素并移除
                parent = element.parent
                if parent:
                    parent.decompose()

    def _extract_main_content(self, soup: BeautifulSoup) -> None:
        """识别并保留文章主体内容"""
        # 查找微信文章主体内容区域
        content_selectors = [
            '#js_content',              # 标准微信文章内容区
            '.rich_media_content',      # 富媒体内容区
            'div.rich_media_area_primary_inner'  # 主要内容区内部
        ]

        content_element = None
        for selector in content_selectors:
            content_element = soup.select_one(selector)
            if content_element:
                break

        # 如果找到主体内容，则保留该部分，移除其他部分
        if content_element:
            # 保存标题
            title_element = soup.select_one('#activity-name') or soup.select_one('h1.rich_media_title')
            title_text = title_element.get_text().strip() if title_element else None

            # 创建新的文档结构
            new_body = soup.new_tag('body')

            # 添加标题（如果存在）
            if title_text:
                title_tag = soup.new_tag('h1')
                title_tag.string = title_text
                new_body.append(title_tag)

            # 添加主体内容
            new_body.append(content_element)

            # 替换body
            soup.body.replace_with(new_body)

    def _clean_wechat_attributes(self, soup: BeautifulSoup) -> None:
        """清理微信文章中的多余样式和属性"""
        # 移除内联样式
        for element in soup.find_all(style=True):
            del element['style']

        # 移除空类名
        for element in soup.find_all(class_=True):
            if not element['class'] or element['class'] == []:
                del element['class']

        # 移除微信特有属性
        wechat_attrs = [
            'data-copyright', 'data-fileid', 'data-tools', 'data-index',
            'data-id', 'data-wxconfig', 'data-componentname'
        ]

        for attr in wechat_attrs:
            for element in soup.find_all(attrs={attr: True}):
                del element[attr]

    def _remove_promotion_text(self, markdown: str) -> str:
        """移除Markdown中的推广文本"""
        promotion_patterns = [
            r'点击上方蓝字关注我们.*?\n',
            r'长按识别二维码关注.*?\n',
            r'微信扫一扫关注公众号.*?\n',
            r'长按识别二维码.*?\n',
            r'点击"在看"，每天第一时间为你推送.*?\n',
            r'欢迎关注我们的公众号.*?\n'
        ]

        result = markdown
        for pattern in promotion_patterns:
            result = re.sub(pattern, '', result, flags=re.DOTALL)

        return result

    def _fix_format_issues(self, markdown: str) -> str:
        """修复Markdown格式问题"""
        # 修复连续多个换行符
        result = re.sub(r'\n{3,}', '\n\n', markdown)

        # 修复标题前缺少空行的问题
        result = re.sub(r'([^\n])(\n#{1,6}\s)', r'\1\n\2', result)

        # 修复列表格式
        result = re.sub(r'\n\*([^\s])', r'\n* \1', result)  # 确保*后有空格
        result = re.sub(r'\n\d+\.([^\s])', r'\n\1. \2', result)  # 确保数字列表后有空格

        return result

    def _clean_empty_lines(self, markdown: str) -> str:
        """整理Markdown中的空行"""
        # 分割成行
        lines = markdown.split('\n')

        # 整理空行
        result = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()

            # 跳过连续的空行
            if is_empty and prev_empty:
                continue

            result.append(line)
            prev_empty = is_empty

        # 确保文档末尾有一个换行符
        if result and result[-1].strip():
            result.append('')

        return '\n'.join(result)
