#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
规则模块，定义规则系统的基类和工具函数。
"""

from typing import Dict, Any, Callable, Optional, List, Union, Type
from bs4 import Tag


class Rule:
    """
    规则基类，定义了规则的基本接口。

    所有HTML到Markdown的转换规则都应该继承这个类，
    并实现filter和replacement方法。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """
        判断规则是否适用于当前节点。

        Args:
            node: 当前处理的DOM节点
            options: 转换选项

        Returns:
            如果规则适用于当前节点，返回True；否则返回False
        """
        raise NotImplementedError("子类必须实现filter方法")

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """
        实现节点的转换逻辑。

        Args:
            content: 子节点处理后的内容
            node: 当前处理的DOM节点
            options: 转换选项

        Returns:
            转换后的Markdown文本
        """
        raise NotImplementedError("子类必须实现replacement方法")


class CustomRule(Rule):
    """
    自定义规则类，允许用户通过函数参数创建规则，而不需要创建子类。

    这个类接受filter_func和replacement_func两个函数参数，
    分别用于实现filter和replacement方法的逻辑。
    """

    def __init__(
        self,
        filter_func: Callable[[Tag, Dict[str, Any]], bool],
        replacement_func: Callable[[str, Tag, Dict[str, Any]], str]
    ) -> None:
        """
        初始化自定义规则。

        Args:
            filter_func: 判断规则是否适用的函数
            replacement_func: 实现转换逻辑的函数
        """
        self.filter_func = filter_func
        self.replacement_func = replacement_func

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """
        判断规则是否适用于当前节点。

        Args:
            node: 当前处理的DOM节点
            options: 转换选项

        Returns:
            如果规则适用于当前节点，返回True；否则返回False
        """
        return self.filter_func(node, options)

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """
        实现节点的转换逻辑。

        Args:
            content: 子节点处理后的内容
            node: 当前处理的DOM节点
            options: 转换选项

        Returns:
            转换后的Markdown文本
        """
        return self.replacement_func(content, node, options)


class RuleBuilder:
    """
    规则构建助手，提供流式API来创建自定义规则。

    使用示例：
    ```python
    rule = (RuleBuilder()
            .filter_by_tag("custom-tag")
            .with_replacement(lambda content, node, options: f"**{content}**")
            .build())
    ```
    """

    def __init__(self) -> None:
        """初始化规则构建助手。"""
        self._filter_func = lambda node, options: False
        self._replacement_func = lambda content, node, options: content

    def filter_by_tag(self, tag_name: Union[str, List[str]]) -> 'RuleBuilder':
        """
        根据标签名称设置过滤条件。

        Args:
            tag_name: 标签名称或名称列表

        Returns:
            规则构建助手实例（用于链式调用）
        """
        if isinstance(tag_name, str):
            self._filter_func = lambda node, options: node.name == tag_name
        else:
            self._filter_func = lambda node, options: node.name in tag_name
        return self

    def filter_by_class(self, class_name: Union[str, List[str]]) -> 'RuleBuilder':
        """
        根据类名设置过滤条件。

        Args:
            class_name: 类名或类名列表

        Returns:
            规则构建助手实例（用于链式调用）
        """
        def has_class(node, options):
            if not node.has_attr('class'):
                return False
            node_classes = set(node.get('class', []))
            if isinstance(class_name, str):
                return class_name in node_classes
            else:
                return bool(set(class_name) & node_classes)

        self._filter_func = has_class
        return self

    def filter_by_attr(self, attr_name: str, attr_value: Optional[str] = None) -> 'RuleBuilder':
        """
        根据属性设置过滤条件。

        Args:
            attr_name: 属性名
            attr_value: 属性值（如果为None，则只检查属性是否存在）

        Returns:
            规则构建助手实例（用于链式调用）
        """
        def has_attr(node, options):
            if not node.has_attr(attr_name):
                return False
            if attr_value is None:
                return True
            return node[attr_name] == attr_value

        self._filter_func = has_attr
        return self

    def filter_by_func(self, func: Callable[[Tag, Dict[str, Any]], bool]) -> 'RuleBuilder':
        """
        使用自定义函数设置过滤条件。

        Args:
            func: 自定义过滤函数

        Returns:
            规则构建助手实例（用于链式调用）
        """
        self._filter_func = func
        return self

    def with_replacement(self, func: Callable[[str, Tag, Dict[str, Any]], str]) -> 'RuleBuilder':
        """
        设置替换函数。

        Args:
            func: 自定义替换函数

        Returns:
            规则构建助手实例（用于链式调用）
        """
        self._replacement_func = func
        return self

    def wrap_with(self, prefix: str, suffix: str) -> 'RuleBuilder':
        """
        使用前缀和后缀包装内容。

        Args:
            prefix: 前缀字符串
            suffix: 后缀字符串

        Returns:
            规则构建助手实例（用于链式调用）
        """
        self._replacement_func = lambda content, node, options: f"{prefix}{content}{suffix}"
        return self

    def prepend(self, text: str) -> 'RuleBuilder':
        """
        在内容前添加文本。

        Args:
            text: 要添加的文本

        Returns:
            规则构建助手实例（用于链式调用）
        """
        self._replacement_func = lambda content, node, options: f"{text}{content}"
        return self

    def append(self, text: str) -> 'RuleBuilder':
        """
        在内容后添加文本。

        Args:
            text: 要添加的文本

        Returns:
            规则构建助手实例（用于链式调用）
        """
        self._replacement_func = lambda content, node, options: f"{content}{text}"
        return self

    def build(self) -> Rule:
        """
        构建并返回自定义规则。

        Returns:
            创建的自定义规则
        """
        return CustomRule(self._filter_func, self._replacement_func)
