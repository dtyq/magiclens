from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from bs4 import BeautifulSoup


class ContentDetectorBase(ABC):
    """
    内容检测器基类，定义内容检测器的基本接口。

    内容检测器负责识别特定类型的网页内容，如微信公众号、知乎文章等。
    检测器通过检查HTML内容和上下文信息（如URL）来判断内容类型。
    """

    @abstractmethod
    def detect(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        检测给定的HTML内容是否为该检测器处理的特定类型。

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            如果内容匹配该检测器类型，返回True；否则返回False
        """
        pass

    @property
    @abstractmethod
    def content_type(self) -> str:
        """
        获取该检测器的内容类型标识符。

        Returns:
            内容类型的唯一字符串标识符
        """
        pass

    @property
    def priority(self) -> int:
        """
        获取检测器的优先级，优先级较高的检测器会先被尝试。

        Returns:
            检测器优先级，默认为0
        """
        return 0
