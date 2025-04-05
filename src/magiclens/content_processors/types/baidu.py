from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re

from ..base import ContentProcessorBase


class BaiduSearchResultProcessor(ContentProcessorBase):
    """
    百度搜索结果内容处理器，处理百度搜索结果页面的HTML和Markdown内容。

    主要功能：
    1. 预处理：清理导航栏、侧边栏、广告等无关内容
    2. 后处理：优化格式、调整搜索结果结构
    """

    @property
    def content_type(self) -> str:
        """获取处理器支持的内容类型"""
        return "baidu_search_result"

    def preprocess(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> BeautifulSoup:
        """
        对百度搜索结果页面HTML进行预处理。

        Args:
            soup: 待处理的HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的BeautifulSoup对象
        """
        # 1. 移除导航栏、侧边栏和广告
        self._remove_navigation_and_ads(soup)

        # 2. 清理百度特有的HTML注释
        self._clean_special_comments(soup)

        # 3. 提取搜索信息和主要结果
        self._extract_search_content(soup)

        # 4. 增强搜索结果的可读性
        self._enhance_search_results(soup)

        # 5. 清理多余的样式和属性
        self._clean_attributes(soup)

        return soup

    def postprocess(self, markdown: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        对转换后的百度搜索结果Markdown进行后处理。

        Args:
            markdown: 转换后的Markdown内容
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的Markdown内容
        """
        # 1. 改进搜索结果的结构
        markdown = self._improve_structure(markdown)

        # 2. 修复格式问题
        markdown = self._fix_format_issues(markdown)

        # 3. 移除重复的分隔线
        markdown = self._clean_separators(markdown)

        # 4. 清理可能残留的特殊注释
        markdown = self._clean_encoded_comments(markdown)

        # 5. 清理额外的空白行和空格
        markdown = self._clean_whitespace(markdown)

        return markdown

    def _remove_navigation_and_ads(self, soup: BeautifulSoup) -> None:
        """移除导航栏、侧边栏和广告"""
        # 移除导航栏、页眉和相关元素
        nav_selectors = [
            '#head',                # 顶部导航
            '#s_top_wrap',          # 顶部包装
            '#u',                   # 用户信息
            '#s_tab',               # 标签栏
            '#s_upfunc_menus',      # 上部功能菜单
            '#bottom_layer',        # 底部层
            '#s_side_wrapper',      # 侧边栏包装
            '#content_right',       # 右侧内容（通常是广告和相关搜索）
            '#foot',                # 页脚
            '#page'                 # 分页
        ]

        for selector in nav_selectors:
            for element in soup.select(selector):
                element.decompose()

        # 移除广告
        ad_selectors = [
            '.ec_wise_ad',          # 移动广告
            '.ec_pp_f',             # 推广模块
            '.ec_wise_pp',          # 智能推广
            '.b_promoteTitle',      # 推广标题
            '.c-container.ec-container',  # 广告容器
            '[tpl="recommend_list"]',     # 推荐列表
            '[tpl="recommend_text_default"]',  # 推荐文本
            '.se_com_irregular_gallery',       # 图片推广
            '.single-card',                   # 单卡片
            '#results-op',                    # 操作结果
        ]

        for selector in ad_selectors:
            for element in soup.select(selector):
                element.decompose()

    def _clean_special_comments(self, soup: BeautifulSoup) -> None:
        """清理百度特有的HTML注释"""
        # 查找所有注释节点
        comments = soup.find_all(text=lambda text: isinstance(text, str) and text.strip().startswith('<!--') and text.strip().endswith('-->'))

        # 移除所有注释节点
        for comment in comments:
            comment.extract()

        # 清理所有带有s-slot的标签内容
        slots = soup.select('[s-slot]') + soup.select('[s-text]')
        for slot in slots:
            # 只保留文本内容，移除内部的所有标签
            if slot.string:
                text = slot.string
            else:
                text = ' '.join(slot.stripped_strings)

            # 创建一个新的文本节点
            new_text = soup.new_string(text)
            slot.replace_with(new_text)

    def _extract_search_content(self, soup: BeautifulSoup) -> None:
        """提取搜索信息和主要结果"""
        # 找到搜索结果容器
        content_left = soup.select_one('#content_left')

        if not content_left:
            return  # 如果找不到主要内容容器，则退出

        # 保存搜索查询
        search_input = soup.select_one('#kw') or soup.select_one('input[name="wd"]')
        search_query = search_input.get('value', '') if search_input else ''

        # 创建新的主体结构
        new_body = soup.new_tag('body')

        # 如果有搜索查询，添加标题
        if search_query:
            title = soup.new_tag('h1')
            title.string = f"百度搜索: {search_query}"
            new_body.append(title)

        # 添加搜索结果
        new_body.append(content_left)

        # 替换原来的body
        if soup.body:
            soup.body.replace_with(new_body)
        else:
            soup.append(new_body)

    def _enhance_search_results(self, soup: BeautifulSoup) -> None:
        """增强搜索结果的可读性"""
        # 处理搜索结果项
        for result in soup.select('.c-container'):
            # 找到标题
            title = result.select_one('h3') or result.select_one('.t')
            if title:
                # 确保标题是h3
                if title.name != 'h3':
                    new_h3 = soup.new_tag('h3')
                    new_h3.append(title)
                    title.replace_with(new_h3)
                    title = new_h3

                # 获取链接
                link = title.select_one('a')
                if link and 'href' in link.attrs:
                    # 保持链接中的内容
                    pass

            # 添加分隔线
            hr = soup.new_tag('hr')
            result.append(hr)

    def _clean_attributes(self, soup: BeautifulSoup) -> None:
        """清理多余的样式和属性"""
        # 移除内联样式
        for element in soup.find_all(style=True):
            del element['style']

        # 移除样式类
        for element in soup.find_all(class_=True):
            del element['class']

        # 移除百度特有属性
        baidu_attrs = [
            'data-tools', 'data-click', 'data-log', 'data-rank',
            'data-index', 'data-urlsign', 'data-card-info'
        ]

        for attr in baidu_attrs:
            for element in soup.find_all(attrs={attr: True}):
                del element[attr]

    def _improve_structure(self, markdown: str) -> str:
        """改进搜索结果的结构"""
        # 将每个搜索结果标题转换为二级标题
        result = re.sub(r'### (.*?)$', r'## \1', markdown, flags=re.MULTILINE)

        # 确保URL显示在独立行
        result = re.sub(r'\[(.*?)\]\((http[^)]+)\)', r'[\1](\2)\n', result)

        # A到B的替换：将内联URL转换为参考样式链接
        result = re.sub(r'\[(.*?)\]\((http[^)]+)\)', r'[\1][\1]', result)

        # 在Markdown末尾添加参考链接
        links = re.findall(r'\[(.*?)\]\((http[^)]+)\)', markdown)
        if links:
            result += "\n\n## 参考链接\n\n"
            for i, (text, url) in enumerate(links):
                result += f"[{text}]: {url}\n"

        return result

    def _fix_format_issues(self, markdown: str) -> str:
        """修复Markdown格式问题"""
        # 修复连续的分隔线
        result = re.sub(r'\n---\s*\n---\s*\n', '\n---\n', markdown)

        # 确保分隔线前后有空行
        result = re.sub(r'([^\n])(\n---)', r'\1\n\n---', result)
        result = re.sub(r'(---)(\n[^\n])', r'---\n\n\2', result)

        # 修复标题前缺少空行的问题
        result = re.sub(r'([^\n])(\n#{1,6}\s)', r'\1\n\2', result)

        return result

    def _clean_separators(self, markdown: str) -> str:
        """移除重复的分隔线"""
        # 分割成行
        lines = markdown.split('\n')

        # 移除连续的分隔线
        result = []
        prev_line_is_separator = False

        for line in lines:
            is_separator = line.strip() in ['---', '***', '___']

            # 跳过连续的分隔线
            if is_separator and prev_line_is_separator:
                continue

            result.append(line)
            prev_line_is_separator = is_separator

        return '\n'.join(result)

    def _clean_encoded_comments(self, markdown: str) -> str:
        """清理编码后的HTML注释"""
        # 移除 \x3C!--数字--> 格式的注释
        result = re.sub(r'\\x3C!--\d+-->', '', markdown)

        # 移除 \x3C!--s-slot--> 和 \x3C!--/s-slot--> 格式的注释
        result = re.sub(r'\\x3C!--s-\w+-->', '', result)
        result = re.sub(r'\\x3C!--/s-\w+-->', '', result)

        # 移除所有未编码的正常HTML注释
        result = re.sub(r'<!--[\s\S]*?-->', '', result)

        return result

    def _clean_whitespace(self, markdown: str) -> str:
        """清理多余的空白行和空格"""
        # 移除连续的空行（3个或更多）
        result = re.sub(r'\n{3,}', '\n\n', markdown)

        # 移除行首和行尾的空白
        lines = result.split('\n')
        lines = [line.strip() for line in lines]

        # 移除全是空白符号的行
        lines = [line for line in lines if not (line and all(c in '\t\n\r ' for c in line))]

        return '\n'.join(lines)
