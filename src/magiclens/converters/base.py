from typing import Any, Dict, Optional
from abc import ABC, abstractmethod


class BaseConverter(ABC):
    """
    转换器基类，定义了从HTML转换到其他格式的接口。

    所有具体的转换器都应该继承这个类，并实现相应的方法。
    """

    @abstractmethod
    def convert_html(self, html: str, **kwargs: Any) -> str:
        """
        将HTML字符串转换为目标格式。

        Args:
            html: 要转换的HTML字符串
            **kwargs: 额外的转换参数

        Returns:
            转换后的字符串
        """
        pass

    @abstractmethod
    def convert_url(self, url: str, **kwargs: Any) -> str:
        """
        从URL获取HTML并转换为目标格式。

        Args:
            url: 网页URL
            **kwargs: 额外的转换参数

        Returns:
            转换后的字符串
        """
        pass
