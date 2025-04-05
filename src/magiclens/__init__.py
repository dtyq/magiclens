#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MagicLens - 一个灵活的HTML到Markdown转换工具

本模块提供了将HTML文档转换为Markdown格式的功能，支持各种转换规则和选项。
可以通过编程方式使用或通过命令行工具使用。
"""

__version__ = "0.3.0"
__author__ = "MagicLens Team"
__email__ = "info@magiclens.io"
__all__ = ["converters"]

from . import converters

# 导出公共API
from .converters.html2md import Html2MarkdownConverter
from .core.rule import Rule

__all__ = ["Html2MarkdownConverter", "Rule", "__version__"]
