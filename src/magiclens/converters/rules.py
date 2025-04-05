"""
HTML到Markdown转换规则。
实现各种HTML元素到Markdown的转换规则。
"""

from typing import Any, Dict, Optional, List, Set
import re
from bs4 import Tag

from ..core.rule import Rule


class ParagraphRule(Rule):
    """段落转换规则，将<p>标签转换为Markdown段落。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'p'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 去除内容前后的空白，并确保段落前后有空行
        content = content.strip()
        return f"\n\n{content}\n\n"


class HeadingRule(Rule):
    """标题转换规则，将<h1>-<h6>标签转换为Markdown标题。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name and re.match(r'h[1-6]', node.name)

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        level = int(node.name[1])
        content = content.strip()

        # 支持两种标题样式: setext (=== 和 ---) 或 atx (#)
        if options.get('headingStyle', 'atx') == 'setext' and level < 3:
            # Setext风格只支持h1和h2
            marker = '=' if level == 1 else '-'
            return f"\n\n{content}\n{marker * len(content)}\n\n"
        else:
            # Atx风格 (# 或 ## 等)
            return f"\n\n{'#' * level} {content}\n\n"


class EmphasisRule(Rule):
    """强调转换规则，将<em>标签转换为Markdown斜体。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'em'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        delimiter = options.get('emDelimiter', '_')
        # 确保内容不是空的
        if not content.strip():
            return ''
        return f"{delimiter}{content}{delimiter}"


class StrongRule(Rule):
    """强调转换规则，将<strong>标签转换为Markdown粗体。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name in ('strong', 'b')

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        delimiter = options.get('strongDelimiter', '**')
        # 确保内容不是空的
        if not content.strip():
            return ''
        return f"{delimiter}{content}{delimiter}"


class ListItemRule(Rule):
    """列表项转换规则，将<li>标签转换为Markdown列表项。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'li'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 获取父元素确定是有序列表还是无序列表
        parent = node.parent
        is_ordered = parent and hasattr(parent, 'name') and parent.name == 'ol'

        # 计算缩进等级
        level = 0
        ancestor = parent
        while ancestor and hasattr(ancestor, 'name') and ancestor.name in ('ul', 'ol'):
            level += 1
            ancestor = ancestor.parent

        indent = '  ' * (level - 1)

        # 确定列表标记
        if is_ordered:
            # 获取列表项索引
            index = 0
            for i, child in enumerate(parent.children):
                if hasattr(child, 'name') and child.name == 'li':
                    index += 1
                    if child is node:
                        break

            # 使用数字作为标记
            marker = f"{index}."
        else:
            # 使用配置的无序列表标记
            marker = options.get('bulletListMarker', '*')

        # 处理列表项内容
        content = content.strip()

        # 如果有子列表，确保它们前面有空行
        lines = content.split('\n')
        for i in range(1, len(lines)):
            if lines[i].strip() and lines[i].strip()[0] in ('*', '-', '+', '1'):
                # 这是子列表的开始，确保前面有空行
                lines[i - 1] += '\n'
                break

        content = '\n'.join(lines)

        return f"{indent}{marker} {content}\n"


class UnorderedListRule(Rule):
    """无序列表转换规则，将<ul>标签转换为Markdown无序列表。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'ul'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 内容已经包含了所有处理过的列表项，直接返回，确保前后有空行
        return f"\n\n{content.strip()}\n\n"


class OrderedListRule(Rule):
    """有序列表转换规则，将<ol>标签转换为Markdown有序列表。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'ol'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 内容已经包含了所有处理过的列表项，直接返回，确保前后有空行
        return f"\n\n{content.strip()}\n\n"


class LinkRule(Rule):
    """链接转换规则，将<a>标签转换为Markdown链接。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'a' and node.get('href')

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        href = node.get('href', '')
        title = node.get('title', '')

        # 处理空链接
        if not href:
            return content

        # 过滤所有 data: URI 数据链接
        if href.startswith('data:'):
            # 不生成链接，只返回链接文本
            return content

        # 标准化链接地址
        href = href.replace('(', '%28').replace(')', '%29')

        # 内容处理
        content = content.strip()
        if not content:
            content = href  # 如果没有链接文本，使用链接地址作为文本

        # 根据链接样式返回不同格式
        link_style = options.get('linkStyle', 'inlined')

        if link_style == 'inlined':
            # 内联链接: [text](url "title")
            if title:
                return f'[{content}]({href} "{title}")'
            else:
                return f'[{content}]({href})'
        elif link_style == 'referenced':
            # 引用链接: [text][id]
            # 这里需要更复杂的处理，简化实现
            return f'[{content}]({href})'
        else:
            # 丢弃链接
            return content


class ImageRule(Rule):
    """图片转换规则，将<img>标签转换为Markdown图片。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        # 处理有 src 属性的图片或只有 alt 属性的图片(可能是预处理阶段删除了 src 属性)
        return (hasattr(node, 'name') and node.name == 'img' and
                (node.get('src') or node.get('alt')))

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        if not options.get('convertImages', True):
            return ''

        src = node.get('src', '')
        alt = node.get('alt', '')
        title = node.get('title', '')

        # 过滤所有 data: URI 数据
        if src.startswith('data:'):
            # 只返回图片的 alt 文本，不包含巨大的数据
            alt_text = alt or '[图片]'
            return f'*{alt_text}*'

        # 处理预处理阶段已移除 src 属性的情况
        if not src:
            alt_text = alt or '[图片]'
            return f'*{alt_text}*'

        # 标准化图片地址
        src = src.replace('(', '%28').replace(')', '%29')

        # 构建Markdown图片语法
        if title:
            return f'![{alt}]({src} "{title}")'
        else:
            return f'![{alt}]({src})'


class CodeRule(Rule):
    """代码转换规则，将<code>标签转换为Markdown代码。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'code'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 检查父元素是否为<pre>，确定是行内代码还是代码块
        if node.parent and hasattr(node.parent, 'name') and node.parent.name == 'pre':
            # 代码块
            code_block_style = options.get('codeBlockStyle', 'fenced')
            fence = options.get('fence', '```')

            # 提取代码内容，移除多余空行和缩进
            content = content.strip()

            if code_block_style == 'fenced':
                # 围栏式代码块
                return f"\n\n{fence}\n{content}\n{fence}\n\n"
            else:
                # 缩进式代码块
                lines = content.split('\n')
                indented = ['    ' + line for line in lines]
                return f"\n\n{'\n'.join(indented)}\n\n"
        else:
            # 行内代码
            delimiter = '`'
            # 处理内容中的特殊情况，如内容本身包含反引号
            if '`' in content:
                delimiter = '``'
                if content.startswith('`') or content.endswith('`'):
                    content = f" {content} "
            return f"{delimiter}{content}{delimiter}"


class PreRule(Rule):
    """预格式化文本转换规则，将<pre>标签转换为Markdown代码块。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        # 只处理不含<code>子元素的<pre>标签
        if not hasattr(node, 'name') or node.name != 'pre':
            return False
        # 如果有<code>子元素，已由CodeRule处理
        if node.findChild('code'):
            return False
        return True

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        code_block_style = options.get('codeBlockStyle', 'fenced')
        fence = options.get('fence', '```')

        # 提取内容，移除多余空行和缩进
        content = content.strip()

        if code_block_style == 'fenced':
            # 围栏式代码块
            return f"\n\n{fence}\n{content}\n{fence}\n\n"
        else:
            # 缩进式代码块
            lines = content.split('\n')
            indented = ['    ' + line for line in lines]
            return f"\n\n{'\n'.join(indented)}\n\n"


class BlockquoteRule(Rule):
    """引用转换规则，将<blockquote>标签转换为Markdown引用。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'blockquote'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 处理内容，每行前添加>
        lines = content.strip().split('\n')
        quoted_lines = []

        for line in lines:
            if line.strip():
                quoted_lines.append(f"> {line}")
            else:
                quoted_lines.append(">")

        return f"\n\n{'\n'.join(quoted_lines)}\n\n"


class HorizontalRuleRule(Rule):
    """水平线转换规则，将<hr>标签转换为Markdown水平线。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'hr'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        hr = options.get('hr', '---')
        return f"\n\n{hr}\n\n"


class TextRule(Rule):
    """文本节点转换规则，直接返回文本内容。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        # 处理纯文本节点
        return node.name is None

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 对于纯文本节点，直接返回其内容
        return content


class TableRule(Rule):
    """表格转换规则，将<table>标签转换为Markdown表格。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'table'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        if not hasattr(node, 'find_all'):
            return content

        # 查找表头和表体
        thead = node.find('thead')
        tbody = node.find('tbody')

        # 没有表头或表体，直接返回内容
        if not thead and not tbody:
            return f"\n\n{content}\n\n"

        rows = []

        # 处理表头
        if thead:
            header_row = thead.find('tr')
            if header_row:
                header_cells = []
                for cell in header_row.find_all(['th', 'td']):
                    # 递归处理单元格内的内容
                    cell_content = ""
                    for child in cell.children:
                        # 如果是字符串，直接添加
                        if isinstance(child, str):
                            cell_content += child
                        # 否则递归处理
                        elif hasattr(child, 'name'):
                            from ..core.service import MagicLensService
                            service = MagicLensService(options)
                            cell_content += service._process_node(child, options)

                    header_cells.append(cell_content.strip())

                if header_cells:
                    rows.append('| ' + ' | '.join(header_cells) + ' |')
                    # 添加分隔行
                    rows.append('| ' + ' | '.join(['---'] * len(header_cells)) + ' |')

        # 处理表体
        if tbody:
            for tr in tbody.find_all('tr'):
                cells = []
                for cell in tr.find_all(['td', 'th']):
                    # 递归处理单元格内的内容
                    cell_content = ""
                    for child in cell.children:
                        # 如果是字符串，直接添加
                        if isinstance(child, str):
                            cell_content += child
                        # 否则递归处理
                        elif hasattr(child, 'name'):
                            from ..core.service import MagicLensService
                            service = MagicLensService(options)
                            cell_content += service._process_node(child, options)

                    cells.append(cell_content.strip())

                if cells:
                    rows.append('| ' + ' | '.join(cells) + ' |')

        # 如果没有表头但有数据行，创建一个空白表头
        if not thead and rows:
            first_row = tbody.find('tr')
            if first_row:
                cell_count = len(first_row.find_all(['td', 'th']))
                if cell_count > 0:
                    rows.insert(0, '| ' + ' | '.join([''] * cell_count) + ' |')
                    rows.insert(1, '| ' + ' | '.join(['---'] * cell_count) + ' |')

        return f"\n\n{'\n'.join(rows)}\n\n" if rows else content


class DefinitionListRule(Rule):
    """定义列表转换规则，将<dl>, <dt>, <dd>标签转换为Markdown格式。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'dl'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        if not hasattr(node, 'find_all'):
            return content

        result = []

        # 找到所有的dt和dd元素
        dt_elements = node.find_all('dt')
        dd_elements = node.find_all('dd')

        # 如果没有定义项或定义描述，返回原内容
        if not dt_elements and not dd_elements:
            return content

        for i, dt in enumerate(dt_elements):
            # 添加定义项
            dt_text = dt.get_text().strip()
            result.append(f"**{dt_text}**")

            # 查找对应的定义描述
            if i < len(dd_elements):
                dd = dd_elements[i]
                dd_text = dd.get_text().strip()
                result.append(f": {dd_text}\n")
            else:
                result.append("\n")

        return f"\n\n{'\n'.join(result)}\n\n"


class StrikethroughRule(Rule):
    """删除线转换规则，将<del>, <s>, <strike>标签转换为Markdown删除线。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name in ('del', 's', 'strike')

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 确保内容不是空的
        if not content.strip():
            return ''
        return f"~~{content}~~"


class SubscriptRule(Rule):
    """下标转换规则，将<sub>标签转换为Markdown或HTML下标。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'sub'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 如果配置允许使用HTML标签，则保留HTML标签，否则尝试使用Markdown语法
        use_html_tags = options.get('useHtmlTags', True)
        if use_html_tags:
            return f"<sub>{content}</sub>"
        else:
            # Markdown没有原生的下标语法，使用unicode下标或其他可读的表示
            return f"_{content}"


class SuperscriptRule(Rule):
    """上标转换规则，将<sup>标签转换为Markdown或HTML上标。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return hasattr(node, 'name') and node.name == 'sup'

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 如果配置允许使用HTML标签，则保留HTML标签，否则尝试使用Markdown语法
        use_html_tags = options.get('useHtmlTags', True)
        if use_html_tags:
            return f"<sup>{content}</sup>"
        else:
            # Markdown没有原生的上标语法，使用unicode上标或其他可读的表示
            return f"^{content}"


class TaskListRule(Rule):
    """任务列表转换规则，将带有checkbox的列表项转换为Markdown任务列表。"""

    def filter(self, node: Any, options: Dict[str, Any]) -> bool:
        return (hasattr(node, 'name') and node.name == 'li' and
                node.find('input', attrs={'type': 'checkbox'}) is not None)

    def replacement(self, content: str, node: Any, options: Dict[str, Any]) -> str:
        # 查找checkbox元素并确定其状态
        checkbox = node.find('input', attrs={'type': 'checkbox'})
        is_checked = checkbox and checkbox.has_attr('checked')

        # 获取无序列表标记
        marker = options.get('bulletListMarker', '-')

        # 根据列表级别决定缩进
        level = 0
        ancestor = node.parent
        while ancestor and hasattr(ancestor, 'name') and ancestor.name in ('ul', 'ol'):
            level += 1
            ancestor = ancestor.parent

        indent = '  ' * (level - 1)

        # 为了修复内容中可能存在的checkbox文本，直接从原始HTML中获取内容
        content_parts = []
        for child in node.children:
            if not (hasattr(child, 'name') and child.name == 'input' and child.get('type') == 'checkbox'):
                if hasattr(child, 'string') and child.string:
                    content_parts.append(str(child.string))
                elif hasattr(child, 'get_text'):
                    content_parts.append(child.get_text())

        content = ''.join(content_parts).strip()

        # 决定任务列表的标记
        checkbox_mark = "[x]" if is_checked else "[ ]"

        return f"{indent}{marker} {checkbox_mark} {content}\n"


# 导出所有规则类
__all__ = [
    'ParagraphRule', 'HeadingRule', 'EmphasisRule', 'StrongRule',
    'ListItemRule', 'UnorderedListRule', 'OrderedListRule',
    'LinkRule', 'ImageRule', 'CodeRule', 'PreRule',
    'BlockquoteRule', 'HorizontalRuleRule', 'TextRule',
    'TableRule', 'DefinitionListRule', 'StrikethroughRule',
    'SubscriptRule', 'SuperscriptRule', 'TaskListRule'
]
