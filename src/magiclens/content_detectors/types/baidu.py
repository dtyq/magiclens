from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ..base import ContentDetectorBase


class BaiduSearchResultDetector(ContentDetectorBase):
    """
    百度搜索结果检测器，识别百度搜索结果页面。
    """

    @property
    def content_type(self) -> str:
        """获取内容类型标识符"""
        return "baidu_search_result"

    @property
    def priority(self) -> int:
        """百度搜索结果检测器的优先级"""
        return 90

    def detect(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        检测HTML内容是否为百度搜索结果页面。

        检测依据：
        1. URL特征：包含百度域名和搜索查询参数
        2. HTML特征：包含百度搜索结果页特有的元素和类名

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            是否为百度搜索结果页面
        """
        # 检查URL特征
        if context and 'url' in context:
            url = context['url']
            parsed_url = urlparse(url)

            # 检查是否为百度域名
            if 'baidu.com' in parsed_url.netloc:
                # 检查是否为搜索URL
                if '/s?' in parsed_url.path or parsed_url.path == '/s' or 'wd=' in parsed_url.query:
                    return True

        # 检查HTML特征
        # 1. 检查搜索框
        search_input = soup.select_one('#kw') or soup.select_one('input[name="wd"]')
        if search_input:
            # 进一步检查是否为搜索结果页
            result_elements = soup.select('.result') or soup.select('.c-container')
            if result_elements:
                return True

        # 2. 检查结果列表元素
        if soup.select_one('#content_left') and (soup.select('.result') or soup.select('.c-container')):
            return True

        # 3. 检查百度搜索结果页特有的元素
        if soup.select_one('#page') and soup.select_one('#foot'):
            return True

        # 4. 检查页面标题
        title = soup.title.string if soup.title else ""
        if title and "百度搜索" in title:
            return True

        # 5. 检查meta标签
        for meta in soup.find_all('meta'):
            if meta.get('name') == 'keywords' and 'baidu' in meta.get('content', '').lower():
                return True

        return False
