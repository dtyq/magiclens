from typing import Dict, Any, Optional
from bs4 import BeautifulSoup
import re
from urllib.parse import urlparse

from ..base import ContentDetectorBase


class WeChatPublicAccountDetector(ContentDetectorBase):
    """
    微信公众号内容检测器，识别微信公众号文章页面。
    """

    @property
    def content_type(self) -> str:
        """获取内容类型标识符"""
        return "wechat_public_account"

    @property
    def priority(self) -> int:
        """微信检测器的优先级较高"""
        return 100

    def detect(self, soup: BeautifulSoup, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        检测HTML内容是否为微信公众号文章。

        检测依据：
        1. URL特征：包含微信域名或特定路径
        2. HTML特征：包含特定的类名、元素或属性

        Args:
            soup: HTML内容的BeautifulSoup解析结果
            context: 上下文信息，如URL、元数据等

        Returns:
            是否为微信公众号文章
        """
        # 检查URL特征
        if context and 'url' in context:
            url = context['url']
            parsed_url = urlparse(url)

            # 检查域名是否为微信域名
            if 'weixin.qq.com' in parsed_url.netloc or 'mp.weixin.qq.com' in parsed_url.netloc:
                return True

        # 检查HTML特征
        # 1. 特定的类名
        if soup.select_one('.rich_media_content') or soup.select_one('#js_content'):
            return True

        # 2. data-src属性（微信公众号文章中图片常用属性）
        if len(soup.select('img[data-src]')) > 0:
            return True

        # 3. 检查meta标签
        for meta in soup.find_all('meta'):
            if meta.get('property') == 'og:url' and 'weixin.qq.com' in meta.get('content', ''):
                return True
            if meta.get('name') == 'author' and '微信公众平台' in meta.get('content', ''):
                return True

        # 4. 检查页面文本特征
        page_text = soup.get_text()[:10000]  # 限制检查范围提高性能
        wechat_indicators = [
            "微信公众号",
            "长按识别二维码关注",
            "微信扫一扫关注公众号",
            "微信扫一扫赞赏作者",
            "已关注公众号",
            "点击上方蓝字关注我们"
        ]

        for indicator in wechat_indicators:
            if indicator in page_text:
                return True

        return False
