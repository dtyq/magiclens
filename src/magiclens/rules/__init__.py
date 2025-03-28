#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
转换规则模块。

提供用于从HTML转换为Markdown的各种规则实现。
"""

from .base import BaseRule
from .html2md import (
    ParagraphRule,
    HeadingRule,
    EmphasisRule,
    StrongRule,
    ListItemRule,
    UnorderedListRule,
    OrderedListRule,
    LinkRule,
    ImageRule,
    CodeRule,
    PreRule,
    BlockquoteRule,
    HorizontalRuleRule,
    TextRule,
    TableRule,
    DefinitionListRule,
    StrikethroughRule,
    SubscriptRule,
    SuperscriptRule,
    TaskListRule,
)

__all__ = [
    "BaseRule",
    "ParagraphRule",
    "HeadingRule",
    "EmphasisRule",
    "StrongRule",
    "ListItemRule",
    "UnorderedListRule",
    "OrderedListRule",
    "LinkRule",
    "ImageRule",
    "CodeRule",
    "PreRule",
    "BlockquoteRule",
    "HorizontalRuleRule",
    "TextRule",
    "TableRule",
    "DefinitionListRule",
    "StrikethroughRule",
    "SubscriptRule",
    "SuperscriptRule",
    "TaskListRule",
]
