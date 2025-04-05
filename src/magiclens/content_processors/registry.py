from typing import Dict, List, Optional
from .base import ContentProcessorBase


class ContentProcessorRegistry:
    """
    内容处理器注册表，管理所有注册的内容处理器。

    提供添加、获取和列出处理器的功能，并支持按内容类型查询处理器。
    """

    def __init__(self):
        """初始化内容处理器注册表"""
        self._processors: Dict[str, ContentProcessorBase] = {}

    def register(self, processor: ContentProcessorBase) -> None:
        """
        注册一个内容处理器。

        Args:
            processor: 要注册的内容处理器实例
        """
        content_type = processor.content_type
        self._processors[content_type] = processor

    def get(self, content_type: str) -> Optional[ContentProcessorBase]:
        """
        获取指定内容类型的处理器。

        Args:
            content_type: 内容类型标识符

        Returns:
            对应的内容处理器，如果不存在则返回None
        """
        return self._processors.get(content_type)

    def list_processors(self) -> List[ContentProcessorBase]:
        """
        获取所有注册的内容处理器列表。

        Returns:
            内容处理器列表
        """
        return list(self._processors.values())
