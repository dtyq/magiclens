"""
CommonMark规则模块。

这个模块提供了一组基于CommonMark规范的HTML到Markdown转换规则。
"""

import re
from html import escape as html_escape
from .utilities import clean_attribute


def paragraph(content, node, options):
    """转换段落。"""
    return content


def line_break(content, node, options):
    """转换换行符。"""
    return options.get('br', '  ') + '\n'


def heading(content, node, options):
    """转换标题。"""
    heading_level = int(node.tag_name[1])

    if options.get('heading_style') == 'setext' and heading_level < 3:
        marker = '=' if heading_level == 1 else '-'
        return '\n\n' + content + '\n' + marker * len(content) + '\n\n'

    return '\n\n' + '#' * heading_level + ' ' + content + '\n\n'


def blockquote(content, node, options):
    """转换引用块。"""
    # 在每行前面添加>符号
    content = re.sub(r'\n$', '\n\n', content)
    content = re.sub(r'\n', '\n> ', content)
    return '\n\n' + '> ' + content + '\n\n'


def void_elements(content, node, options):
    """转换自闭合元素。"""
    return ''


def hr(content, node, options):
    """转换水平线。"""
    return '\n\n' + options.get('hr', '* * *') + '\n\n'


def image(content, node, options):
    """转换图片。"""
    alt = clean_attribute(node.get_attribute('alt'))
    src = node.get_attribute('src') or ''
    title = clean_attribute(node.get_attribute('title'))
    title_part = ' "' + re.sub(r'"', r'\"', title) + '"' if title else ''

    return '![' + alt + '](' + src + title_part + ')'


def code_block(content, node, options):
    """转换代码块。"""
    code_content = re.sub(r'\n$', '', node.inner_text)

    if options.get('code_block_style') == 'indented':
        return '\n\n    ' + re.sub(r'\n', '\n    ', code_content) + '\n\n'

    # fenced
    fence = options.get('fence', '```')
    info_string = node.get_attribute('class') or ''
    language = ''

    # 尝试从class属性中提取语言信息
    if 'language-' in info_string:
        match = re.search(r'language-(\S+)', info_string)
        if match:
            language = match.group(1)

    return '\n\n' + fence + language + '\n' + code_content + '\n' + fence + '\n\n'


def code_inline(content, node, options):
    """转换内联代码。"""
    return '`' + node.inner_text + '`'


def list_item(content, node, options):
    """转换列表项。"""
    content = re.sub(r'^\n+', '', content)  # 删除开头的换行符
    content = re.sub(r'\n+$', '\n', content)  # 确保只有一个尾部换行符

    if '\n' in content:
        content = re.sub(r'\n', '\n    ', content)

    return content


def unordered_list(content, node, options):
    """转换无序列表。"""
    marker = options.get('bullet_list_marker', '*')
    return '\n\n' + re.sub(r'^(.)', marker + r' \1', content, flags=re.MULTILINE) + '\n\n'


def ordered_list(content, node, options):
    """转换有序列表。"""
    # 计算起始索引
    start = node.get_attribute('start')
    start = int(start) if start and start.isdigit() else 1

    # 拆分内容并在每行前面添加编号
    items = content.split('\n')
    for i, item in enumerate(items):
        if item:
            index = start + i
            items[i] = f"{index}. {item}"

    return '\n\n' + '\n'.join(items) + '\n\n'


def strong(content, node, options):
    """转换粗体文本。"""
    marker = options.get('strong_delimiter', '**')
    return marker + content + marker


def emphasis(content, node, options):
    """转换斜体文本。"""
    marker = options.get('em_delimiter', '_')
    return marker + content + marker


def link(content, node, options):
    """转换链接。"""
    href = node.get_attribute('href') or ''
    title = clean_attribute(node.get_attribute('title'))
    title_part = ' "' + re.sub(r'"', r'\"', title) + '"' if title else ''

    if options.get('link_style') == 'inlined':
        return '[' + content + '](' + href + title_part + ')'

    # 对于其他链接样式，实际处理在主转换器中
    return '[' + content + '](' + href + title_part + ')'


def link_filter(node, options):
    """链接过滤器函数。"""
    return (
        node.tag_name.lower() == 'a' and
        node.get_attribute('href')
    )


# 规则字典
COMMONMARK_RULES = {
    'paragraph': {
        'filter': 'p',
        'replacement': paragraph
    },
    'br': {
        'filter': 'br',
        'replacement': line_break
    },
    'heading': {
        'filter': ['h1', 'h2', 'h3', 'h4', 'h5', 'h6'],
        'replacement': heading
    },
    'blockquote': {
        'filter': 'blockquote',
        'replacement': blockquote
    },
    'void_elements': {
        'filter': ['area', 'base', 'col', 'embed', 'hr', 'img', 'input',
                  'keygen', 'link', 'menuitem', 'meta', 'param', 'source',
                  'track', 'wbr'],
        'replacement': void_elements
    },
    'hr': {
        'filter': 'hr',
        'replacement': hr
    },
    'image': {
        'filter': 'img',
        'replacement': image
    },
    'code_block': {
        'filter': ['pre'],
        'replacement': code_block
    },
    'code_inline': {
        'filter': ['code'],
        'replacement': code_inline
    },
    'list_item': {
        'filter': 'li',
        'replacement': list_item
    },
    'unordered_list': {
        'filter': ['ul'],
        'replacement': unordered_list
    },
    'ordered_list': {
        'filter': ['ol'],
        'replacement': ordered_list
    },
    'strong': {
        'filter': ['strong', 'b'],
        'replacement': strong
    },
    'emphasis': {
        'filter': ['em', 'i'],
        'replacement': emphasis
    },
    'link': {
        'filter': link_filter,
        'replacement': link
    }
}
