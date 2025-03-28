#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
规则注册表模块，提供规则的注册和管理功能。
"""

from typing import Dict, List, Tuple, Iterator, Any, Optional
from collections import OrderedDict

from .rule import Rule


class RuleRegistry:
    """
    规则注册表，用于管理和应用转换规则。

    规则按照注册顺序存储，并按相同顺序应用。
    """

    def __init__(self) -> None:
        """初始化规则注册表。"""
        self._rules = OrderedDict()

    def add(self, name: str, rule: Rule) -> None:
        """
        添加规则到注册表。

        Args:
            name: 规则名称
            rule: 规则对象
        """
        self._rules[name] = rule

    def get(self, name: str) -> Rule:
        """
        根据名称获取规则。

        Args:
            name: 规则名称

        Returns:
            对应的规则对象

        Raises:
            KeyError: 如果规则不存在
        """
        return self._rules[name]

    def remove(self, name: str) -> None:
        """
        从注册表中移除规则。

        Args:
            name: 规则名称

        Raises:
            KeyError: 如果规则不存在
        """
        del self._rules[name]

    def insert(self, name: str, rule: Rule, index: int) -> None:
        """
        在指定位置插入规则。

        Args:
            name: 规则名称
            rule: 规则对象
            index: 插入位置的索引

        Raises:
            IndexError: 如果索引超出范围
        """
        if index < 0 or index > len(self._rules):
            raise IndexError(f"索引 {index} 超出范围 [0, {len(self._rules)}]")

        # 创建一个新的有序字典
        new_rules = OrderedDict()

        # 添加索引之前的规则
        for i, (rule_name, rule_obj) in enumerate(self._rules.items()):
            if i == index:
                new_rules[name] = rule
            new_rules[rule_name] = rule_obj

        # 如果索引等于长度，添加到末尾
        if index == len(self._rules):
            new_rules[name] = rule

        # 更新规则字典
        self._rules = new_rules

    def get_rules(self) -> Iterator[Tuple[str, Rule]]:
        """
        获取所有规则的迭代器。

        Returns:
            规则名称和规则对象的元组迭代器
        """
        return iter(self._rules.items())

    def find_rule(self, node: Any, options: Dict[str, Any]) -> Optional[Tuple[str, Rule]]:
        """
        查找适用于节点的第一个规则。

        Args:
            node: DOM节点
            options: 转换选项

        Returns:
            规则名称和规则对象的元组，如果没有找到则返回None
        """
        for name, rule in self._rules.items():
            if rule.filter(node, options):
                return name, rule

        return None
