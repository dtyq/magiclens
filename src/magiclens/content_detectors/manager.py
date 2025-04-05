from typing import Dict, Any, Optional, List, Tuple
from bs4 import BeautifulSoup

from .registry import ContentDetectorRegistry
from ..content_processors.registry import ContentProcessorRegistry


class SmartContentDetectionManager:
    """
    智能内容检测管理器，负责协调内容检测和处理流程。

    管理器维护内容检测器和处理器的注册表，提供内容检测、预处理和后处理功能。
    """

    def __init__(self):
        """初始化智能内容检测管理器"""
        self._detector_registry = ContentDetectorRegistry()
        self._processor_registry = ContentProcessorRegistry()

    @property
    def detector_registry(self) -> ContentDetectorRegistry:
        """获取内容检测器注册表"""
        return self._detector_registry

    @property
    def processor_registry(self) -> ContentProcessorRegistry:
        """获取内容处理器注册表"""
        return self._processor_registry

    def detect_content_type(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> Optional[str]:
        """
        检测内容类型。

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            检测到的内容类型，如果无法检测则返回None
        """
        return self._detector_registry.detect_content_type(soup, context)

    def preprocess(self, soup: BeautifulSoup, content_type: Optional[str] = None,
                  context: Optional[Dict[str, Any]] = None) -> Tuple[BeautifulSoup, Optional[str]]:
        """
        对HTML内容进行预处理。

        如果未指定内容类型，则自动检测内容类型。

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            content_type: 内容类型，如果不提供则自动检测
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的BeautifulSoup对象和检测到的内容类型的元组
        """
        # 如果未指定内容类型，自动检测
        detected_type = content_type
        if detected_type is None:
            detected_type = self.detect_content_type(soup, context)

        # 如果有对应的处理器，进行预处理
        if detected_type is not None:
            processor = self._processor_registry.get(detected_type)
            if processor is not None:
                soup = processor.preprocess(soup, context)

        return soup, detected_type

    def postprocess(self, markdown: str, content_type: Optional[str],
                   context: Optional[Dict[str, Any]] = None) -> str:
        """
        对Markdown内容进行后处理。

        Args:
            markdown: 转换后的Markdown内容
            content_type: 内容类型
            context: 上下文信息，如URL、元数据等

        Returns:
            处理后的Markdown内容
        """
        if content_type is not None:
            processor = self._processor_registry.get(content_type)
            if processor is not None:
                markdown = processor.postprocess(markdown, context)

        return markdown

    def register_detector(self, detector) -> None:
        """
        注册内容检测器。

        Args:
            detector: 要注册的内容检测器实例
        """
        self._detector_registry.register(detector)

    def register_processor(self, processor) -> None:
        """
        注册内容处理器。

        Args:
            processor: 要注册的内容处理器实例
        """
        self._processor_registry.register(processor)
