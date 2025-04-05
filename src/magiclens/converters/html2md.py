from typing import Any, Dict, Optional, List, Type
import requests
import re
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
from ..content_detectors.manager import SmartContentDetectionManager
from ..content_detectors.discovery import discover_and_register_plugins


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

        # 初始化智能内容检测管理器
        self.smart_content_manager = None
        if self.options.get("smart_content_detection", False):
            self._init_smart_content_detection()

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

    def _init_smart_content_detection(self) -> None:
        """初始化智能内容检测系统"""
        self.smart_content_manager = SmartContentDetectionManager()
        # 自动发现并注册所有检测器和处理器
        discover_and_register_plugins(self.smart_content_manager)

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

        # 处理所有 data: URI 内联数据
        # 处理 img 标签的 src 属性
        for img in soup.find_all('img'):
            src = img.get('src', '')
            if src and src.startswith('data:'):
                # 删除 src 属性，保留 alt 属性
                if 'alt' not in img.attrs or not img['alt']:
                    img['alt'] = '[图片]'
                del img['src']

        # 处理 a 标签的 href 属性
        for a in soup.find_all('a'):
            href = a.get('href', '')
            if href and href.startswith('data:'):
                del a['href']

        # 处理 source 标签的 src 属性
        for source in soup.find_all('source'):
            src = source.get('src', '')
            if src and src.startswith('data:'):
                del source['src']

        # 处理背景图片和其他可能包含 data: URI 的样式属性
        for tag in soup.find_all(style=True):
            style = tag['style']
            if 'data:' in style:
                # 移除包含 data: URI 的样式
                style_parts = []
                for part in style.split(';'):
                    if 'data:' not in part:
                        style_parts.append(part)
                if style_parts:
                    tag['style'] = ';'.join(style_parts)
                else:
                    del tag['style']

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

        # 使用智能内容检测处理HTML
        if self.smart_content_manager and self.options.get("smart_content_detection", False):
            detection_context = self.options.get("detection_context", {})
            soup, _ = self.smart_content_manager.preprocess(soup, context=detection_context)

    def _postprocess(self, markdown: str) -> str:
        """
        后处理Markdown，优化输出格式。

        Args:
            markdown: 转换后的Markdown

        Returns:
            优化后的Markdown
        """
        # 使用智能内容检测进行后处理
        if self.smart_content_manager and self.options.get("smart_content_detection", False):
            detection_context = self.options.get("detection_context", {})
            content_type = self.options.get("detected_content_type")
            if content_type:
                markdown = self.smart_content_manager.postprocess(
                    markdown,
                    content_type=content_type,
                    context=detection_context
                )

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

    def _detect_website_type(self, html: str) -> Dict[str, bool]:
        """
        检测网站类型（已废弃，由智能内容检测系统替代）。

        Args:
            html: HTML内容

        Returns:
            检测结果字典
        """
        # 该方法已不再使用，保留以保持向后兼容
        return {"is_wechat": False}

    def turndown(self, html: str) -> str:
        """
        将HTML转换为Markdown。

        Args:
            html: HTML内容

        Returns:
            转换后的Markdown
        """
        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 检测内容类型
        detected_content_type = None
        if self.smart_content_manager and self.options.get("smart_content_detection", False):
            detection_context = self.options.get("detection_context", {})
            detected_content_type = self.smart_content_manager.detect_content_type(
                soup,
                context=detection_context
            )
            # 保存检测到的内容类型，供后处理使用
            self.options["detected_content_type"] = detected_content_type

        # 预处理HTML
        self._preprocess(soup)

        # 转换HTML到Markdown
        markdown = ""
        if soup.body:
            markdown = self._process_node(soup.body, self.options)
        else:
            # 如果没有body标签，则处理整个文档
            markdown = self._process_node(soup, self.options)

        # 后处理Markdown
        markdown = self._postprocess(markdown)

        return markdown


class Html2MarkdownConverter(BaseConverter):
    """
    HTML到Markdown的转换器，实现BaseConverter接口。
    """

    def __init__(self, options: Optional[Dict[str, Any]] = None) -> None:
        """
        初始化HTML到Markdown转换器。

        Args:
            options: 转换选项
        """
        super().__init__()
        self.options = options or {}

        # 如果指定了方言，加载方言配置
        if "dialect" in self.options:
            dialect_options = self._get_dialect_options(self.options["dialect"])
            # 合并方言配置与用户配置，用户配置优先
            for key, value in dialect_options.items():
                if key not in self.options:
                    self.options[key] = value

        # 初始化转换服务
        self.service = Html2MarkdownService(self.options)

    def _get_dialect_options(self, dialect: str) -> Dict[str, Any]:
        """
        获取方言选项。

        Args:
            dialect: 方言名称

        Returns:
            方言选项字典
        """
        # 方言选项字典
        dialect_options: Dict[str, Dict[str, Any]] = {
            "github": {
                # GitHub风格Markdown
                "headingStyle": "atx",       # atx风格的标题 (###)
                "hr": "---",                 # 水平分割线
                "bulletListMarker": "*",     # 无序列表标记
                "codeBlockStyle": "fenced",  # 代码块使用围栏风格 (```)
                "fence": "```",              # 围栏符号
                "emDelimiter": "*",          # 强调符号
                "strongDelimiter": "**",     # 加粗符号
                "linkStyle": "inlined",      # 内联链接风格
                "linkReferenceStyle": "full" # 链接引用风格
            },
            "commonmark": {
                # CommonMark风格
                "headingStyle": "atx",
                "hr": "---",
                "bulletListMarker": "*",
                "codeBlockStyle": "fenced",
                "fence": "```",
                "emDelimiter": "*",
                "strongDelimiter": "**",
                "linkStyle": "inlined",
                "linkReferenceStyle": "full"
            },
            "traditional": {
                # 传统风格Markdown
                "headingStyle": "setext",   # 底线风格标题
                "hr": "---",
                "bulletListMarker": "*",
                "codeBlockStyle": "indented", # 缩进式代码块
                "emDelimiter": "_",         # 下划线强调
                "strongDelimiter": "**",
                "linkStyle": "referenced",  # 引用式链接
                "linkReferenceStyle": "shortcut" # 快捷链接引用
            },
            "custom": {}  # 自定义风格，允许完全自定义选项
        }

        # 获取指定方言的选项
        if dialect in dialect_options:
            return dialect_options[dialect].copy()
        else:
            # 默认返回GitHub风格
            print(f"警告: 未知方言 '{dialect}'，使用默认GitHub风格。")
            return dialect_options["github"].copy()

    def convert_html(self, html: str, **kwargs: Any) -> str:
        """
        将HTML字符串转换为Markdown。

        Args:
            html: HTML字符串
            **kwargs: 额外的转换选项

        Returns:
            转换后的Markdown字符串
        """
        # 合并选项
        options = self.options.copy()
        for key, value in kwargs.items():
            options[key] = value

        # 更新服务配置
        self.service.options = options

        # 检测是否有URL上下文
        if 'url' in kwargs and self.service.options.get("smart_content_detection", False):
            # 确保detection_context存在
            if 'detection_context' not in self.service.options:
                self.service.options['detection_context'] = {}
            # 将URL添加到检测上下文
            self.service.options['detection_context']['url'] = kwargs['url']

        # 执行转换
        return self.service.turndown(html)

    def convert_html_fragment(self, html_fragment: str, **kwargs: Any) -> str:
        """
        将HTML片段转换为Markdown。适用于不完整的HTML，如单个元素或元素集合。

        Args:
            html_fragment: HTML片段
            **kwargs: 额外的转换选项
                fragment_root: 包装片段的根元素（默认'div'）

        Returns:
            转换后的Markdown字符串
        """
        # 获取根元素类型
        fragment_root = kwargs.pop("fragment_root", "div")

        # 包装HTML片段
        html = f"<{fragment_root}>{html_fragment}</{fragment_root}>"

        # 转换为Markdown
        return self.convert_html(html, **kwargs)

    def convert_url(self, url: str, **kwargs: Any) -> str:
        """
        从URL获取HTML内容并转换为Markdown。

        Args:
            url: 网页URL
            **kwargs: 额外的转换选项

        Returns:
            转换后的Markdown字符串
        """
        # 发送HTTP请求获取HTML内容
        try:
            headers = {
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
            }
            response = requests.get(url, headers=headers, timeout=30)
            response.raise_for_status()  # 检查请求是否成功
            html = response.text

            # 将URL作为额外选项传递给转换方法
            kwargs['url'] = url

            # 启用智能内容检测（如果未指定）
            if 'smart_content_detection' not in kwargs:
                kwargs['smart_content_detection'] = True

            # 转换HTML为Markdown
            return self.convert_html(html, **kwargs)
        except Exception as e:
            raise Exception(f"转换URL时出错: {str(e)}")

    def register_rule(self, name: str, rule: Rule, priority: Optional[int] = None) -> None:
        """
        注册转换规则。

        Args:
            name: 规则名称
            rule: 规则实例
            priority: 规则优先级（可选）
        """
        # 使用服务的register_rule方法
        self.service.register_rule(name, rule)
