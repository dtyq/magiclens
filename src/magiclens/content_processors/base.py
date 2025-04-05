from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup


class ContentProcessorBase(ABC):
    """
    内容处理器基类，定义内容处理器的基本接口。

    内容处理器负责针对特定类型的网页内容进行预处理和后处理，
    如清理微信公众号文章中的广告、优化知乎文章格式等。
    """

    @property
    @abstractmethod
    def content_type(self) -> str:
        """
        获取该处理器支持的内容类型标识符。

        Returns:
            内容类型的唯一字符串标识符
        """
        pass

    def preprocess(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> BeautifulSoup:
        """
        对HTML内容进行预处理，在转换为Markdown前优化HTML结构。

        Args:
            soup: 待处理的HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的BeautifulSoup对象
        """
        return soup

    def postprocess(self, markdown: str, context: Optional[Dict[str, Any]] = None) -> str:
        """
        对转换后的Markdown内容进行后处理，优化输出格式。

        Args:
            markdown: 转换后的Markdown内容
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的Markdown内容
        """
        return markdown
