#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MagicLens服务基类，提供转换服务的核心功能。
"""

from typing import Any, Dict, Optional, List
from bs4 import BeautifulSoup, Tag

from .registry import RuleRegistry
from .rule import Rule

# 默认转换选项
DEFAULT_OPTIONS = {
    # 标题样式: setext 使用 === 和 ---，atx 使用 #
    "headingStyle": "atx",
    # 水平线样式
    "hr": "---",
    # 列表标记
    "bulletListMarker": "*",
    # 代码块样式: indented 使用缩进，fenced 使用 ```
    "codeBlockStyle": "fenced",
    # 突出显示语言
    "fence": "```",
    # 斜体分隔符
    "emDelimiter": "*",
    # 粗体分隔符
    "strongDelimiter": "**",
    # 链接样式: inlined, referenced, or discarded
    "linkStyle": "inlined",
    # 链接引用样式: full, collapsed, or shortcut
    "linkReferenceStyle": "full",
    # 是否转换图片
    "convertImages": True
}


class MagicLensService:
    """
    MagicLens基础服务类，提供转换HTML的核心功能。

    子类应该实现自己的转换逻辑。
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化服务。

        Args:
            options: 转换选项
        """
        self.options = options or {}
        self.rules = RuleRegistry()

    def _process_node(self, node: Tag, options: Dict[str, Any]) -> str:
        """
        处理单个节点，返回转换后的内容。

        Args:
            node: 当前处理的节点
            options: 转换选项

        Returns:
            转换后的内容
        """
        # 处理子节点并获取内容
        content = self._process_children(node, options)

        # 查找适用的规则
        rule_info = self.rules.find_rule(node, options)

        if rule_info:
            # 如果有适用的规则，应用它
            rule_name, rule = rule_info
            return rule.replacement(content, node, options)

        # 如果没有规则，直接返回内容
        return content

    def _process_children(self, node: Tag, options: Dict[str, Any]) -> str:
        """
        处理节点的所有子节点。

        Args:
            node: 父节点
            options: 转换选项

        Returns:
            处理后的子节点内容拼接结果
        """
        result = []
        for child in node.children:
            if isinstance(child, Tag):
                # 递归处理子标签
                content = self._process_node(child, options)
                result.append(content)
            else:
                # 处理文本节点
                result.append(str(child))

        return ''.join(result)

    def _preprocess(self, soup: BeautifulSoup) -> None:
        """
        预处理HTML。

        Args:
            soup: BeautifulSoup对象
        """
        pass

    def _postprocess(self, content: str) -> str:
        """
        后处理转换后的内容。

        Args:
            content: 转换后的内容

        Returns:
            后处理后的内容
        """
        return content

    def turndown(self, html: str) -> str:
        """
        将HTML转换为目标格式。

        Args:
            html: HTML字符串

        Returns:
            转换后的内容
        """
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 预处理
        self._preprocess(soup)

        # 处理根节点
        content = self._process_node(soup, self.options)

        # 后处理
        return self._postprocess(content)

    def _register_default_rules(self) -> None:
        """注册默认的转换规则"""
        # 默认规则将在子类中实现
        pass

    def register_rule(self, name: str, rule: Rule, priority: Optional[int] = None) -> None:
        """
        注册一个自定义规则。

        Args:
            name: 规则名称
            rule: 规则对象
            priority: 规则优先级
        """
        self.rules.add(name, rule, priority)

    def remove_rule(self, name: str) -> None:
        """
        移除一个规则。

        Args:
            name: 规则名称
        """
        self.rules.remove(name)
