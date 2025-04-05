from typing import Dict, List, Type, Optional, Any
from .base import ContentDetectorBase


class ContentDetectorRegistry:
    """
    内容检测器注册表，管理所有注册的内容检测器。

    提供添加、获取和列出检测器的功能，并支持按优先级排序的检测器查询。
    """

    def __init__(self):
        """初始化内容检测器注册表"""
        self._detectors: Dict[str, ContentDetectorBase] = {}

    def register(self, detector: ContentDetectorBase) -> None:
        """
        注册一个内容检测器。

        Args:
            detector: 要注册的内容检测器实例
        """
        content_type = detector.content_type
        self._detectors[content_type] = detector

    def get(self, content_type: str) -> Optional[ContentDetectorBase]:
        """
        获取指定类型的内容检测器。

        Args:
            content_type: 内容类型标识符

        Returns:
            对应的内容检测器，如果不存在则返回None
        """
        return self._detectors.get(content_type)

    def list_detectors(self) -> List[ContentDetectorBase]:
        """
        获取所有注册的内容检测器列表，按优先级排序。

        Returns:
            按优先级排序的内容检测器列表
        """
        return sorted(self._detectors.values(), key=lambda d: -d.priority)

    def detect_content_type(self, soup, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        检测给定内容的类型。

        顺序尝试所有注册的检测器，返回第一个匹配的检测器的内容类型。

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            检测到的内容类型，如果没有匹配的检测器则返回None
        """
        for detector in self.list_detectors():
            if detector.detect(soup, context):
                return detector.content_type
        return None
