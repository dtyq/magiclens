from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
from urllib.parse import urlparse

from ..base import ContentDetectorBase


class ZhihuContentDetector(ContentDetectorBase):
    """
    知乎内容检测器，识别知乎文章和问答页面。
    """

    @property
    def content_type(self) -> str:
        """获取内容类型标识符"""
        return "zhihu_content"

    @property
    def priority(self) -> int:
        """知乎内容检测器的优先级"""
        return 80

    def detect(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        检测HTML内容是否为知乎文章或问答页面。

        检测依据：
        1. URL特征：包含知乎域名和特定路径
        2. HTML特征：包含知乎页面特有的元素和类名

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            是否为知乎内容页面
        """
        # 检查URL特征
        if context and 'url' in context:
            url = context['url']
            parsed_url = urlparse(url)

            # 检查是否为知乎域名
            if 'zhihu.com' in parsed_url.netloc:
                # 检查是否为文章、问答页面路径
                if (
                    parsed_url.path.startswith('/p/') or
                    parsed_url.path.startswith('/question/') or
                    '/answer/' in parsed_url.path or
                    '/zhuanlan/' in parsed_url.path
                ):
                    return True

        # 检查HTML特征
        # 1. 检查知乎特有的CSS类名
        zhihu_classes = [
            'Post-RichTextContainer',  # 文章内容容器
            'QuestionHeader',          # 问题头部
            'QuestionAnswer',          # 问题回答
            'AnswerCard',              # 回答卡片
            'AuthorInfo',              # 作者信息
            'ContentItem-actions',     # 内容项操作栏
            'Post-Header',             # 文章头部
            'Post-Author',             # 文章作者
            'QuestionHeader-title'     # 问题标题
        ]

        for class_name in zhihu_classes:
            if soup.select_one(f'.{class_name}'):
                return True

        # 2. 检查meta标签
        for meta in soup.find_all('meta'):
            if meta.get('property') == 'og:site_name' and meta.get('content') == '知乎':
                return True
            if meta.get('name') == 'keywords' and '知乎' in meta.get('content', ''):
                return True
            if meta.get('name') == 'apple-itunes-app' and 'zhihu' in meta.get('content', ''):
                return True

        # 3. 检查页面标题
        title = soup.title.string if soup.title else ""
        if title and ("- 知乎" in title or "知乎专栏" in title):
            return True

        # 4. 检查知乎特有的UI元素
        if (
            soup.select_one('[itemprop="name"][content="知乎"]') or
            soup.select_one('.SignContainer') or
            soup.select_one('.AppHeader')
        ):
            return True

        return False
