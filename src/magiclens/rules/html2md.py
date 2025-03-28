#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
HTML到Markdown转换规则。

包含了将各种HTML元素转换为Markdown格式的规则实现。
"""

import re
from typing import Dict, Any, List, Optional, Union, Tuple
from bs4 import Tag, NavigableString

from .base import BaseRule

class TableRule(BaseRule):
    """表格转换规则。

    将HTML表格(<table>)转换为Markdown表格格式。
    支持表头(<th>)、表格行(<tr>)、单元格(<td>)等元素。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """检查节点是否为表格。

        Args:
            node: 要检查的节点
            options: 转换选项

        Returns:
            是否为表格节点
        """
        return node.name == "table"

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """将表格转换为Markdown格式。

        Args:
            content: 子节点处理后的内容
            node: 当前节点
            options: 转换选项

        Returns:
            转换后的Markdown表格
        """
        # 解析表格结构
        rows = self._get_table_rows(node)
        if not rows or not rows[0]:
            return ""  # 空表格

        column_count = max(len(row) for row in rows)

        # 构建表格头部
        if self._has_thead(node):
            header = rows[0]
            body_rows = rows[1:]
        else:
            # 如果没有明确的表头，使用第一行作为表头
            header = rows[0]
            body_rows = rows[1:]

        # 创建Markdown表格
        result = []

        # 表头行
        header_md = "| " + " | ".join(header) + " |"
        result.append(header_md)

        # 分隔行
        separator = "| " + " | ".join(["---"] * column_count) + " |"
        result.append(separator)

        # 数据行
        for row in body_rows:
            # 确保行具有相同的列数
            if len(row) < column_count:
                row.extend([""] * (column_count - len(row)))
            row_md = "| " + " | ".join(row) + " |"
            result.append(row_md)

        return "\n".join(result) + "\n\n"

    def _get_table_rows(self, table: Tag) -> List[List[str]]:
        """从表格节点中提取所有行的内容。

        Args:
            table: 表格节点

        Returns:
            表格行内容列表，每行是一个单元格内容的列表
        """
        rows = []

        # 首先处理表头
        thead = table.find("thead")
        if thead:
            for tr in thead.find_all("tr", recursive=False):
                row = []
                for th in tr.find_all(["th", "td"], recursive=False):
                    cell_content = self._process_cell(th)
                    row.append(cell_content)
                if row:
                    rows.append(row)

        # 然后处理表体
        tbody = table.find("tbody") or table
        for tr in tbody.find_all("tr", recursive=False):
            row = []
            for td in tr.find_all(["td", "th"], recursive=False):
                cell_content = self._process_cell(td)
                row.append(cell_content)
            if row:
                rows.append(row)

        return rows

    def _process_cell(self, cell: Tag) -> str:
        """处理单元格内容，去除多余空白并处理特殊字符。

        Args:
            cell: 单元格节点

        Returns:
            处理后的单元格内容
        """
        # 获取单元格内容并处理
        content = "".join(str(c) for c in cell.contents)

        # 处理内联HTML元素（比如加粗、斜体等）
        # 这里依赖于子节点已经被正确处理，实际实现中可能需要递归调用

        # 替换管道符号，避免破坏表格格式
        content = content.replace("|", "\\|")

        # 清理空白字符
        content = content.strip()

        return content

    def _has_thead(self, table: Tag) -> bool:
        """检查表格是否有明确的表头部分。

        Args:
            table: 表格节点

        Returns:
            是否有表头
        """
        return bool(table.find("thead")) or bool(table.find("th"))


class DefinitionListRule(BaseRule):
    """定义列表转换规则。

    将HTML定义列表(<dl>、<dt>、<dd>)转换为Markdown格式。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """检查节点是否为定义列表。

        Args:
            node: 要检查的节点
            options: 转换选项

        Returns:
            是否为定义列表节点
        """
        return node.name == "dl"

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """将定义列表转换为Markdown格式。

        Args:
            content: 子节点处理后的内容
            node: 当前节点
            options: 转换选项

        Returns:
            转换后的Markdown定义列表
        """
        result = []

        # 遍历所有dt和dd对
        dt_list = node.find_all("dt", recursive=False)
        dd_list = node.find_all("dd", recursive=False)

        for i, dt in enumerate(dt_list):
            # 添加定义术语
            term = dt.get_text().strip()
            result.append(f"**{term}**")

            # 添加定义描述（如果存在）
            if i < len(dd_list):
                dd = dd_list[i]
                description = dd.get_text().strip()
                # 缩进描述内容
                description_lines = description.split("\n")
                formatted_description = "\n".join([f"  {line}" for line in description_lines])
                result.append(formatted_description)

            # 添加空行分隔
            result.append("")

        return "\n".join(result)


class StrikethroughRule(BaseRule):
    """删除线转换规则。

    将HTML删除线(<s>、<del>、<strike>)转换为Markdown格式的删除线(~~text~~)。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """检查节点是否为删除线。

        Args:
            node: 要检查的节点
            options: 转换选项

        Returns:
            是否为删除线节点
        """
        return node.name in ["s", "del", "strike"]

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """将删除线转换为Markdown格式。

        Args:
            content: 子节点处理后的内容
            node: 当前节点
            options: 转换选项

        Returns:
            转换后的Markdown删除线
        """
        if not content.strip():
            return ""
        return f"~~{content}~~"


class SubscriptRule(BaseRule):
    """下标转换规则。

    将HTML下标(<sub>)转换为Markdown格式的下标(~text~)或HTML标签。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """检查节点是否为下标。

        Args:
            node: 要检查的节点
            options: 转换选项

        Returns:
            是否为下标节点
        """
        return node.name == "sub"

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """将下标转换为Markdown格式。

        Args:
            content: 子节点处理后的内容
            node: 当前节点
            options: 转换选项

        Returns:
            转换后的Markdown下标
        """
        if not content.strip():
            return ""

        # 默认使用~符号，但某些Markdown方言不支持，可以选择保留HTML标签
        use_html_tags = options.get("useHtmlTags", False)

        if use_html_tags:
            return f"<sub>{content}</sub>"
        else:
            return f"~{content}~"


class SuperscriptRule(BaseRule):
    """上标转换规则。

    将HTML上标(<sup>)转换为Markdown格式的上标(^text^)或HTML标签。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """检查节点是否为上标。

        Args:
            node: 要检查的节点
            options: 转换选项

        Returns:
            是否为上标节点
        """
        return node.name == "sup"

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """将上标转换为Markdown格式。

        Args:
            content: 子节点处理后的内容
            node: 当前节点
            options: 转换选项

        Returns:
            转换后的Markdown上标
        """
        if not content.strip():
            return ""

        # 默认使用^符号，但某些Markdown方言不支持，可以选择保留HTML标签
        use_html_tags = options.get("useHtmlTags", False)

        if use_html_tags:
            return f"<sup>{content}</sup>"
        else:
            return f"^{content}^"


class TaskListRule(BaseRule):
    """任务列表转换规则。

    将具有checkbox的列表项转换为Markdown格式的任务列表项([x] 或 [ ])。
    支持常见的任务列表格式，包括HTML5 <input type="checkbox"> 以及一些自定义格式。
    """

    def filter(self, node: Tag, options: Dict[str, Any]) -> bool:
        """检查节点是否为任务列表项。

        Args:
            node: 要检查的节点
            options: 转换选项

        Returns:
            是否为任务列表项节点
        """
        # 仅处理列表项
        if node.name != "li":
            return False

        # 检查是否包含复选框
        has_checkbox = False

        # 查找input type=checkbox
        checkbox = node.find("input", attrs={"type": "checkbox"})
        if checkbox:
            has_checkbox = True

        # 一些站点可能使用span或其他元素来模拟复选框
        for element in node.find_all(["span", "div", "i"], class_=["checkbox", "task-checkbox", "check-box"]):
            has_checkbox = True
            break

        return has_checkbox

    def replacement(self, content: str, node: Tag, options: Dict[str, Any]) -> str:
        """将任务列表项转换为Markdown格式。

        Args:
            content: 子节点处理后的内容
            node: 当前节点
            options: 转换选项

        Returns:
            转换后的Markdown任务列表项
        """
        checkbox = node.find("input", attrs={"type": "checkbox"})
        is_checked = False

        if checkbox and checkbox.get("checked") is not None:
            is_checked = True

        # 处理其他类型的复选框指示器
        if not checkbox:
            for element in node.find_all(["span", "div", "i"], class_=["checked", "completed", "done"]):
                is_checked = True
                break

        # 移除内容中可能已包含的复选框元素文本
        content = re.sub(r'^\s*\[[\sxX]\]\s*', '', content.strip())

        # 添加任务列表标记
        if is_checked:
            return f"[x] {content}"
        else:
            return f"[ ] {content}"
