#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
核心模块，提供基础功能和接口。
"""

from .rule import Rule, CustomRule, RuleBuilder
from .registry import RuleRegistry
from .service import MagicLensService

__all__ = ["Rule", "CustomRule", "RuleBuilder", "RuleRegistry", "MagicLensService"]
