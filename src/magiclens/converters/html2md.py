from typing import Any, Dict, Optional, List, Type
import requests
from bs4 import BeautifulSoup, Comment

from ..core.service import MagicLensService
from ..core.rule import Rule
from ..core.registry import RuleRegistry
from .base import BaseConverter
from .rules import (
    ParagraphRule, HeadingRule, EmphasisRule, StrongRule,
    ListItemRule, UnorderedListRule, OrderedListRule,
    LinkRule, ImageRule, CodeRule, PreRule,
    BlockquoteRule, HorizontalRuleRule, TextRule,
    TableRule, DefinitionListRule, StrikethroughRule,
    SubscriptRule, SuperscriptRule, TaskListRule
)


class Html2MarkdownService(MagicLensService):
    """
    HTML到Markdown的转换服务，扩展MagicLensService。

    实现特定于Markdown转换的功能，包括默认规则注册和Markdown特定的处理。
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化转换器。

        Args:
            options: 转换选项
        """
        self.options = options or {}
        self.rules = RuleRegistry()
        self._register_default_rules()

    def _register_default_rules(self) -> None:
        """注册默认规则。

        注册所有默认的HTML到Markdown转换规则。
        注册顺序很重要，会影响转换结果。
        """
        # 块级元素规则
        self.register_rule("paragraph", ParagraphRule())
        self.register_rule("heading", HeadingRule())
        self.register_rule("blockquote", BlockquoteRule())
        self.register_rule("code-block", PreRule())
        self.register_rule("unordered-list", UnorderedListRule())
        self.register_rule("ordered-list", OrderedListRule())

        # 任务列表规则必须在列表项之前注册，使其优先匹配
        self.register_rule("task-list", TaskListRule())
        self.register_rule("list-item", ListItemRule())

        self.register_rule("horizontal-rule", HorizontalRuleRule())
        self.register_rule("table", TableRule())
        self.register_rule("definition-list", DefinitionListRule())

        # 内联元素规则
        self.register_rule("strong", StrongRule())
        self.register_rule("emphasis", EmphasisRule())
        self.register_rule("code", CodeRule())
        self.register_rule("link", LinkRule())
        self.register_rule("image", ImageRule())
        self.register_rule("strikethrough", StrikethroughRule())
        self.register_rule("subscript", SubscriptRule())
        self.register_rule("superscript", SuperscriptRule())

        # 必须放在最后，处理纯文本节点
        self.register_rule("text", TextRule())

    def _preprocess(self, soup: BeautifulSoup) -> None:
        """
        预处理HTML，为Markdown转换做准备。

        Args:
            soup: BeautifulSoup对象
        """
        # 获取HTML清理选项
        clean_options = self.options.get("clean", {})

        # 默认移除的标签
        default_remove_tags = ['script', 'style', 'noscript']
        remove_tags = clean_options.get("removeTags", default_remove_tags)

        # 移除指定的标签
        for tag_name in remove_tags:
            for tag in soup.find_all(tag_name):
                tag.decompose()

        # 移除指定的属性
        remove_attrs = clean_options.get("removeAttrs", [])
        if remove_attrs:
            for tag in soup.find_all(True):  # 查找所有标签
                for attr in remove_attrs:
                    if attr in tag.attrs:
                        del tag.attrs[attr]

        # 移除指定的类
        remove_classes = clean_options.get("removeClasses", [])
        if remove_classes:
            for tag in soup.find_all(class_=True):
                classes = set(tag.get("class", []))
                classes_to_remove = classes.intersection(remove_classes)
                if classes_to_remove:
                    classes = classes - classes_to_remove
                    if classes:
                        tag["class"] = list(classes)
                    else:
                        del tag["class"]

        # 移除空标签
        if clean_options.get("removeEmptyTags", False):
            for tag in soup.find_all():
                # 如果标签没有内容且不是自闭合标签
                if not tag.contents and tag.name not in ['img', 'br', 'hr', 'input', 'meta', 'link']:
                    tag.decompose()

        # 移除注释
        if clean_options.get("removeComments", True):
            for comment in soup.find_all(string=lambda text: isinstance(text, Comment)):
                comment.extract()

    def _postprocess(self, markdown: str) -> str:
        """
        后处理Markdown，优化输出格式。

        Args:
            markdown: 转换后的Markdown

        Returns:
            优化后的Markdown
        """
        # 修复多余的空行
        lines = markdown.split('\n')
        result = []
        prev_empty = False

        for line in lines:
            is_empty = not line.strip()
            if is_empty and prev_empty:
                continue
            result.append(line)
            prev_empty = is_empty

        # 合并和返回
        return '\n'.join(result)

    def register_rule(self, name: str, rule: Rule) -> None:
        """注册转换规则。

        Args:
            name: 规则名称
            rule: 规则实例
        """
        self.rules.add(name, rule)


class Html2MarkdownConverter(BaseConverter):
    """
    HTML到Markdown转换器，使用Html2MarkdownService实现转换。

    提供简单的接口用于HTML到Markdown的转换。
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化转换器。

        Args:
            options: 转换选项
                dialect: Markdown方言（'commonmark', 'github', 'traditional', 'custom'），默认为'github'
        """
        # 处理方言选项
        options = options or {}
        dialect = options.pop("dialect", "github")

        # 根据方言设置默认选项
        dialect_options = self._get_dialect_options(dialect)

        # 合并用户提供的选项
        if options:
            dialect_options.update(options)

        self.service = Html2MarkdownService(dialect_options)

    def _get_dialect_options(self, dialect: str) -> Dict[str, Any]:
        """
        获取特定Markdown方言的默认选项。

        Args:
            dialect: Markdown方言

        Returns:
            方言对应的默认选项
        """
        # 方言选项
        dialect_options = {
            # CommonMark (https://commonmark.org/)
            "commonmark": {
                "headingStyle": "atx",          # 使用'#'风格的标题
                "bulletListMarker": "*",         # 使用'*'作为无序列表标记
                "codeBlockStyle": "fenced",      # 使用```风格的代码块
                "emDelimiter": "*",              # 使用*作为斜体标记
                "strongDelimiter": "**",         # 使用**作为粗体标记
                "linkStyle": "inlined",          # 使用内联链接
                "useHtmlTags": True,             # 对不支持的元素保留HTML标签
                "gfm": False                     # 不使用GitHub特性
            },

            # GitHub Flavored Markdown (https://github.github.com/gfm/)
            "github": {
                "headingStyle": "atx",
                "bulletListMarker": "-",         # 更常用于GitHub的风格
                "codeBlockStyle": "fenced",
                "emDelimiter": "*",
                "strongDelimiter": "**",
                "linkStyle": "inlined",
                "useHtmlTags": True,
                "gfm": True,                     # 启用GitHub特性：表格、任务列表、删除线等
                "strikethrough": True,           # 使用~~删除线~~
                "tables": True,                  # 启用表格
                "taskLists": True                # 启用任务列表[x]
            },

            # 传统Markdown (https://daringfireball.net/projects/markdown/)
            "traditional": {
                "headingStyle": "setext",        # 使用===和---风格的标题
                "bulletListMarker": "*",
                "codeBlockStyle": "indented",    # 使用缩进的代码块
                "emDelimiter": "_",              # 使用_作为斜体标记
                "strongDelimiter": "__",         # 使用__作为粗体标记
                "linkStyle": "referenced",       # 使用引用式链接[text][1]
                "useHtmlTags": True,
                "gfm": False,
                "smartPunctuation": True         # 智能标点（引号、破折号等）
            },

            # 自定义（不设置默认值，由用户完全控制）
            "custom": {}
        }

        # 返回选择的方言选项，如果不存在则返回空字典
        return dialect_options.get(dialect, {})

    def convert_html(self, html: str, **kwargs: Any) -> str:
        """
        将HTML字符串转换为Markdown。

        Args:
            html: HTML字符串
            **kwargs: 额外参数，会覆盖初始化时的选项
                fragment: 是否为HTML片段（默认False）
                fragment_root: 当处理片段时使用的根元素（默认'div'）

        Returns:
            Markdown字符串
        """
        # 提取片段相关选项
        fragment = kwargs.pop("fragment", False)
        fragment_root = kwargs.pop("fragment_root", "div")

        # 处理HTML片段
        if fragment:
            # 如果是HTML片段，包装在指定的根元素中
            html = f"<{fragment_root}>{html}</{fragment_root}>"

        # 如果有额外选项，创建一个临时服务
        if kwargs:
            options = self.service.options.copy()
            options.update(kwargs)
            temp_service = Html2MarkdownService(options)
            return temp_service.turndown(html)

        return self.service.turndown(html)

    def convert_html_fragment(self, html_fragment: str, **kwargs: Any) -> str:
        """
        将HTML片段转换为Markdown。适用于不完整的HTML，如单个元素或元素集合。

        Args:
            html_fragment: HTML片段
            **kwargs: 额外参数，会覆盖初始化时的选项
                fragment_root: 包装片段的根元素（默认'div'）

        Returns:
            Markdown字符串
        """
        # 设置fragment=True，并传递其他参数
        kwargs["fragment"] = True
        return self.convert_html(html_fragment, **kwargs)

    def convert_url(self, url: str, **kwargs: Any) -> str:
        """
        从URL获取HTML并转换为Markdown。

        Args:
            url: 网页URL
            **kwargs: 额外参数，会覆盖初始化时的选项

        Returns:
            Markdown字符串
        """
        # 获取网页内容
        response = requests.get(url)
        response.raise_for_status()

        # 设置内容类型
        if 'content_type' not in kwargs:
            kwargs['content_type'] = response.headers.get('Content-Type', '')

        # 将URL添加到选项中
        kwargs['url'] = url

        # 转换HTML
        return self.convert_html(response.text, **kwargs)

    def register_rule(self, name: str, rule: Rule, priority: Optional[int] = None) -> None:
        """
        注册一个自定义规则。

        Args:
            name: 规则名称
            rule: 规则对象
            priority: 规则优先级，如果提供，将在指定位置插入规则；
                     否则会在text规则之前插入（如果存在）
        """
        # 如果没有提供优先级，尝试在text规则之前插入
        if priority is None:
            # 获取当前规则列表
            rules = list(self.service.rules.get_rules())
            # 查找text规则的位置
            text_rule_index = next((i for i, (rule_name, _) in enumerate(rules) if rule_name == "text"), -1)

            if text_rule_index >= 0:
                # 如果找到text规则，在它之前插入
                self.service.rules.insert(name, rule, text_rule_index)
                return

        # 使用服务的register_rule方法
        self.service.register_rule(name, rule)
