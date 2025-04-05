from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re

from ..base import ContentProcessorBase


class ZhihuContentProcessor(ContentProcessorBase):
    """
    知乎内容处理器，处理知乎文章和问答页面的HTML和Markdown内容。

    主要功能：
    1. 预处理：清理侧边栏、广告、登录提示等，保留文章和回答核心内容
    2. 后处理：优化格式、调整结构、添加元信息
    """

    @property
    def content_type(self) -> str:
        """获取处理器支持的内容类型"""
        return "zhihu_content"

    def preprocess(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> BeautifulSoup:
        """
        对知乎文章和问答页面HTML进行预处理。

        Args:
            soup: 待处理的HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的BeautifulSoup对象
        """
        # 1. 移除导航栏、侧边栏和广告
        self._remove_navigation_and_ads(soup)

        # 2. 提取文章或问答内容
        self._extract_main_content(soup)

        # 3. 处理知乎特有的元素
        self._process_zhihu_elements(soup)

        # 4. 清理多余的样式和属性
        self._clean_attributes(soup)

        return soup

    def postprocess(self, markdown: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        对转换后的知乎内容Markdown进行后处理。

        Args:
            markdown: 转换后的Markdown内容
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的Markdown内容
        """
        # 1. 移除知乎特有的提示文本
        markdown = self._remove_zhihu_tips(markdown)

        # 2. 修复格式问题
        markdown = self._fix_format_issues(markdown)

        # 3. 整理结构
        markdown = self._organize_structure(markdown)

        # 4. 添加来源信息（如果有URL）
        if context and 'url' in context:
            markdown = self._add_source_info(markdown, context['url'])

        return markdown

    def _remove_navigation_and_ads(self, soup: BeautifulSoup) -> None:
        """移除导航栏、侧边栏和广告"""
        # 移除导航栏、侧边栏等元素
        nav_selectors = [
            '.AppHeader',           # 应用头部
            '.Sticky',              # 粘性元素
            '.ColumnPageHeader',    # 专栏页头部
            '.Topstory-container',  # 顶部故事容器
            '.TopstoryTabs',        # 顶部故事标签
            '.CornerButtons',       # 角落按钮
            '.BottomInfo',          # 底部信息
            '.Footer',              # 页脚
            '.Sticky--holder',      # 粘性元素占位符
            '.Question-sideColumn', # 问题侧边栏
            '.GlobalSideBar',       # 全局侧边栏
            '.QuestionHeader-footer', # 问题头部页脚
            '.Card-headerOptions',  # 卡片头部选项
            '.ContentItem-actions', # 内容项操作
            '.Reward',              # 打赏区
            '.ModalWrap',           # 模态包装
            '.ModalLoading',        # 模态加载
            '.signFlowModal',       # 登录流模态框
            '#SignFlowModal',       # 登录流模态框ID
            '.AdblockBanner',       # 广告拦截横幅
            '.Banner-link',         # 横幅链接
            '.RichContent-actions', # 富内容操作
            '.Comments-container',  # 评论容器
            '.RelatedReadings',     # 相关阅读
            '.AnswerAdd',           # 添加回答
            '.MoreAnswers',         # 更多回答
        ]

        for selector in nav_selectors:
            for element in soup.select(selector):
                element.decompose()

    def _extract_main_content(self, soup: BeautifulSoup) -> None:
        """提取文章或问答内容"""
        # 检测页面类型并提取主要内容
        content_element = None
        title_element = None

        # 1. 尝试提取文章内容
        article_content = soup.select_one('.Post-RichTextContainer') or soup.select_one('.Post-RichText') or soup.select_one('.RichContent-inner')
        if article_content:
            content_element = article_content
            # 获取文章标题
            title_element = soup.select_one('.Post-Title') or soup.select_one('h1.QuestionHeader-title')

        # 2. 尝试提取问答内容
        if not content_element:
            # 问题内容
            question_content = soup.select_one('.QuestionRichText')
            # 回答内容
            answer_content = soup.select_one('.AnswerCard .RichContent-inner') or soup.select_one('.QuestionAnswer-content .RichContent-inner')

            if question_content or answer_content:
                # 创建新的内容容器
                content_element = soup.new_tag('div')

                # 添加问题内容（如果有）
                if question_content:
                    content_element.append(question_content)

                # 添加回答内容（如果有）
                if answer_content:
                    content_element.append(answer_content)

                # 获取问题标题
                title_element = soup.select_one('h1.QuestionHeader-title')

        # 如果找到内容，则创建新的文档结构
        if content_element:
            # 创建新的body元素
            new_body = soup.new_tag('body')

            # 添加标题（如果存在）
            if title_element:
                title_text = title_element.get_text().strip()
                title_tag = soup.new_tag('h1')
                title_tag.string = title_text
                new_body.append(title_tag)

            # 添加主体内容
            new_body.append(content_element)

            # 替换body
            if soup.body:
                soup.body.replace_with(new_body)
            else:
                soup.append(new_body)

    def _process_zhihu_elements(self, soup: BeautifulSoup) -> None:
        """处理知乎特有的元素"""
        # 处理知乎链接卡片
        for link_card in soup.select('.LinkCard'):
            # 提取链接信息
            link = link_card.select_one('a')
            if link and 'href' in link.attrs:
                href = link['href']
                title = link.get_text().strip() or href

                # 创建简单的链接替代卡片
                new_p = soup.new_tag('p')
                new_a = soup.new_tag('a', href=href)
                new_a.string = title
                new_p.append(new_a)

                link_card.replace_with(new_p)

        # 处理知乎视频
        for video in soup.select('.VideoCard'):
            # 提取视频标题
            title_element = video.select_one('.VideoCard-title')
            title = title_element.get_text().strip() if title_element else "知乎视频"

            # 创建视频占位符
            placeholder = soup.new_tag('p')
            placeholder.string = f"[视频: {title}]"
            video.replace_with(placeholder)

        # 处理知乎图片
        for img in soup.select('img'):
            # 确保图片有src属性
            if 'src' not in img.attrs or not img['src']:
                # 尝试从data-original或其他属性获取
                for attr in ['data-original', 'data-actualsrc', 'data-src']:
                    if attr in img.attrs and img[attr]:
                        img['src'] = img[attr]
                        break

            # 确保图片有alt属性
            if 'alt' not in img.attrs or not img['alt']:
                img['alt'] = "知乎图片"

    def _clean_attributes(self, soup: BeautifulSoup) -> None:
        """清理多余的样式和属性"""
        # 移除内联样式
        for element in soup.find_all(style=True):
            del element['style']

        # 移除知乎特有属性
        zhihu_attrs = [
            'data-za-detail-view-id', 'data-za-element-name', 'data-za-module',
            'data-reactid', 'data-zop', 'data-za-extra-module',
            'data-draft-type', 'data-draft-id', 'data-votecount'
        ]

        for attr in zhihu_attrs:
            for element in soup.find_all(attrs={attr: True}):
                del element[attr]

        # 清理无用的类名
        for element in soup.find_all(class_=True):
            del element['class']

    def _remove_zhihu_tips(self, markdown: str) -> str:
        """移除知乎特有的提示文本"""
        # 知乎特有的提示文本模式
        tips_patterns = [
            r'发布于 .*?\n',
            r'编辑于 .*?\n',
            r'\d+人赞同了该回答',
            r'赞同 \d+',
            r'​图片来源.*?\n',
            r'原文链接.*?\n',
            r'知乎用户.*?回答.*?\n',
            r'展开全文',
            r'查看全部.*?条评论',
            r'写回答',
        ]

        result = markdown
        for pattern in tips_patterns:
            result = re.sub(pattern, '', result, flags=re.MULTILINE)

        return result

    def _fix_format_issues(self, markdown: str) -> str:
        """修复Markdown格式问题"""
        # 修复连续的空行
        result = re.sub(r'\n{3,}', '\n\n', markdown)

        # 修复缺少空格的列表项
        result = re.sub(r'\n(\d+\.|\*)([^\s])', r'\n\1 \2', result)

        # 确保标题前有空行
        result = re.sub(r'([^\n])(\n#{1,6}\s)', r'\1\n\2', result)

        # 修复连续的分隔线
        result = re.sub(r'\n---\s*\n---\s*\n', '\n---\n', result)

        return result

    def _organize_structure(self, markdown: str) -> str:
        """整理Markdown结构"""
        # 分割成行
        lines = markdown.split('\n')

        # 整理结构
        result = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()

            # 跳过连续的空行
            if is_empty and prev_empty:
                continue

            result.append(line)
            prev_empty = is_empty

        return '\n'.join(result)

    def _add_source_info(self, markdown: str, url: str) -> str:
        """添加来源信息"""
        # 在Markdown末尾添加来源链接
        source_info = f"\n\n---\n\n*来源: [{url}]({url})*\n"
        return markdown + source_info
