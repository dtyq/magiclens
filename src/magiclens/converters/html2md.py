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
        # 处理微信公众号文章
        wechat_mode = self.options.get("wechat", False)

        # 检查HTML是否为微信公众号文章
        if wechat_mode or self.options.get("auto_detect_website_type", True):
            # 简单检查当前soup是否为微信公众号文章
            is_wechat = (
                soup.select('.rich_media_content') or
                soup.select('[data-src]') or
                'data-src' in str(soup)[:5000]  # 仅检查前5000个字符提高性能
            )

            if is_wechat:
                # 应用微信专用的处理
                self._fix_wechat_article_html(soup)

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
        # 处理微信公众号文章
        wechat_mode = self.options.get("wechat", False)
        auto_detect_website_type = self.options.get("auto_detect_website_type", True)

        # 检查是否启用了微信模式或自动检测
        if wechat_mode or auto_detect_website_type:
            # 简单检测是否为微信文章结果
            wechat_indicators = [
                "微信扫一扫赞赏作者",
                "轻点两下取消赞",
                "预览时标签不可点",
                "长按二维码向我转账",
                "继续滑动看下一个"
            ]

            is_wechat = any(indicator in markdown for indicator in wechat_indicators)

            if is_wechat or wechat_mode:
                # 应用微信专用的后处理
                markdown = self._post_process_wechat_markdown(markdown)

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

    def _fix_wechat_article_html(self, soup: BeautifulSoup) -> None:
        """
        修复微信公众号文章的HTML，主要处理图片链接

        Args:
            soup: BeautifulSoup对象
        """
        # 处理微信图片：微信公众号文章中图片通常有多种存储方式
        for img in soup.find_all('img'):
            # 检查是否为base64编码的图片，如果是则直接移除
            src = img.get('src', '')
            if src and (src.startswith('data:image/jpeg;base64,') or src.startswith('data:image/png;base64,')):
                # 将base64编码的图片替换为占位符或直接移除
                img['src'] = ''
                img['alt'] = '[图片]'
                continue

            # 1. 优先检查data-src属性（微信最常用的图片加载方式）
            data_src = img.get('data-src')
            if data_src and not data_src.startswith('data:'):
                img['src'] = data_src
                # 清除可能引起问题的属性
                for attr in ['data-lazy-src', 'data-srcset', 'srcset', 'data-ratio', 'data-w']:
                    if attr in img.attrs:
                        del img[attr]
                continue

            # 2. 检查可能存在的其他图片源
            possible_src_attrs = ['data-original', 'data-actualsrc', 'data-lazy-src']
            for attr in possible_src_attrs:
                if attr in img.attrs and img[attr] and not img[attr].startswith('data:'):
                    img['src'] = img[attr]
                    break

            # 3. 检查图片是否已有正常src
            src = img.get('src', '')
            if src.startswith('data:image/svg') or src.startswith('data:') or not src:
                # 尝试从style属性中提取background-image
                style = img.get('style', '')

                # 查找background-image样式
                bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', style)
                if bg_match:
                    img['src'] = bg_match.group(1)
                    continue

                # 无法找到有效的图片链接，尝试检查周边元素
                parent = img.parent
                if parent and 'style' in parent.attrs:
                    parent_style = parent.get('style', '')
                    bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', parent_style)
                    if bg_match:
                        img['src'] = bg_match.group(1)
                        continue

                # 尝试检查最近的<section>是否有背景图
                section = img.find_parent('section')
                if section and 'style' in section.attrs:
                    section_style = section.get('style', '')
                    bg_match = re.search(r'background-image:\s*url\([\'"]?(.*?)[\'"]?\)', section_style)
                    if bg_match:
                        img['src'] = bg_match.group(1)
                        continue

                # 微信常用域名的图片修复
                if 'class' in img.attrs:
                    classes = img.get('class', [])
                    for cls in classes:
                        if cls.startswith('__bg_') and parent and 'data-src' in parent.attrs:
                            img['src'] = parent['data-src']
                            break

            # 4. 处理相对URL、不完整URL和缺少协议的URL
            if 'src' in img.attrs and img['src']:
                src = img['src']
                # 检查是否为base64编码的图片
                if src.startswith('data:image/jpeg;base64,') or src.startswith('data:image/png;base64,'):
                    img['src'] = ''
                    img['alt'] = '[图片]'
                    continue
                # 添加协议前缀
                if src.startswith('//'):
                    img['src'] = 'https:' + src
                # 微信文章图片常用域名扩展
                elif src.startswith('/mmbiz_'):
                    img['src'] = 'https://mmbiz.qpic.cn' + src

        # 移除微信公众号中的一些不需要的元素
        for selector in [
            '.rich_media_meta_list', '.reward_area', '.qr_code_pc', '.tool_area',
            '.weui-dialog', '.weapp_text_link', '.weapp_display_element',
            '.js_wx_tap_highlight', '.js_img_loading', '.audio_card'
        ]:
            for element in soup.select(selector):
                element.decompose()

        # 处理微信的一些特殊封装元素
        for mpvoice in soup.find_all('mpvoice'):
            new_p = soup.new_tag('p')
            new_p.string = f"[音频消息] {mpvoice.get('name', '语音')}"
            mpvoice.replace_with(new_p)

        for qqmusic in soup.find_all('qqmusic'):
            new_p = soup.new_tag('p')
            new_p.string = f"[音乐] {qqmusic.get('musicname', '音乐')}"
            qqmusic.replace_with(new_p)

        # 尝试提取文章标题
        title_tags = soup.select('.rich_media_title')
        if title_tags:
            title = title_tags[0].get_text(strip=True)
            # 创建标题标签
            h1 = soup.new_tag('h1')
            h1.string = title
            # 在正文开头插入标题
            content = soup.select('.rich_media_content')
            if content:
                content[0].insert(0, h1)

    def _post_process_wechat_markdown(self, markdown: str) -> str:
        """
        对转换后的微信公众号Markdown内容进行后处理

        Args:
            markdown: 原始Markdown内容

        Returns:
            处理后的Markdown内容
        """
        # 移除特殊字符和转义序列
        markdown = re.sub(r'&#x[0-9a-fA-F]+;', '', markdown)

        # 移除base64编码的图片链接（一般体积很大）
        markdown = re.sub(r'!\[.*?\]\(data:image/(?:jpeg|png);base64,.*?\)', '![图片]', markdown)

        # 修复图片链接中的问题
        markdown = re.sub(r'!\[图片\]\(data:image/svg.*?\)', '', markdown)
        markdown = re.sub(r'!\[\]\(data:image/svg.*?\)', '', markdown)

        # 移除空图片
        markdown = re.sub(r'!\[\]\(\s*\)', '', markdown)
        markdown = re.sub(r'!\[图片\]\(\s*\)', '', markdown)

        # 修复微信中的一些特殊格式
        markdown = re.sub(r'javascript:void\(0\);', '#', markdown)
        markdown = re.sub(r'javascript:;', '#', markdown)

        # 删除微信文章中的评论、赞赏等无关内容
        patterns_to_remove = [
            r'微信扫一扫赞赏作者.*?返回',
            r'喜欢作者.*?赞赏支持',
            r'长按二维码向我转账',
            r'受苹果公司新规定影响.*?无法使用',
            r'名称已清空.*?其它金额',
            r'修改于202\d年\d{1,2}月\d{1,2}日',
        ]

        for pattern in patterns_to_remove:
            markdown = re.sub(pattern, '', markdown, flags=re.DOTALL)

        # 移除多余的空行
        markdown = re.sub(r'\n{3,}', '\n\n', markdown)

        # 移除图片后的无用交互文本
        markdown = re.sub(r'轻点两下取消赞|，轻点两下取消在看', '', markdown)

        # 移除预览时标签不可点等微信特殊文本
        markdown = re.sub(r'预览时标签不可点.*?关闭更多', '', markdown, flags=re.DOTALL)

        # 移除底部导航条
        markdown = re.sub(r'分析.{0,50}：.{0,50}，.{0,50}，.{0,50}，.*?收藏.{0,50}听过', '', markdown, flags=re.DOTALL)

        # 移除公众号文章结尾常见的提示内容
        markdown = re.sub(r'继续滑动看下一个.*?轻触阅读原文', '', markdown, flags=re.DOTALL)
        markdown = re.sub(r'向上滑动看下一个.*?当前内容可能存在.*?广告规范指引', '', markdown, flags=re.DOTALL)

        return markdown

    def _detect_website_type(self, html: str) -> Dict[str, bool]:
        """
        检测HTML内容的网站类型

        Args:
            html: HTML内容

        Returns:
            网站类型检测结果字典，包含各种类型的检测结果
        """
        result = {
            "wechat": False,  # 微信公众号
            # 其他网站类型可以在这里添加
        }

        # 检测微信公众号
        wechat_indicators = [
            "微信公众号",
            "data-src",
            "rich_media",
            "js_wx_tap_highlight",
            "weui-",
            "mpvoice",
            "wxw-img"
        ]

        for indicator in wechat_indicators:
            if indicator in html:
                result["wechat"] = True
                break

        # 这里可以添加其他网站类型的检测逻辑

        return result

    def turndown(self, html: str) -> str:
        """
        将HTML字符串转换为Markdown。

        Args:
            html: HTML字符串

        Returns:
            Markdown字符串
        """
        # 自动检测网站类型
        if (self.options.get("auto_detect_website_type", True)
                and not self.options.get("wechat", False)):
            website_types = self._detect_website_type(html)
            if website_types["wechat"]:
                self.options["wechat"] = True

            # 这里可以根据检测结果设置其他网站类型的处理选项

        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 预处理HTML
        self._preprocess(soup)

        # 转换处理过的HTML
        markdown = self._process_node(soup, self.options)

        # 后处理Markdown
        markdown = self._postprocess(markdown)

        return markdown


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

            # 微信公众号文章 (特殊处理模式)
            "wechat": {
                # 基于GitHub风格Markdown
                "headingStyle": "atx",
                "bulletListMarker": "-",
                "codeBlockStyle": "fenced",
                "emDelimiter": "*",
                "strongDelimiter": "**",
                "linkStyle": "inlined",
                "useHtmlTags": True,
                "gfm": True,
                "strikethrough": True,
                "tables": True,
                "taskLists": True,
                # 微信专用选项
                "wechat": True,                   # 启用微信处理模式
                "auto_detect_website_type": True, # 启用自动检测网站类型功能
                "clean": {
                    "removeComments": True,
                    "removeEmptyTags": True,
                    "removeTags": ["script", "style", "noscript", "iframe", "form", "svg"],
                    "removeAttrs": ["id", "class", "data-w", "data-ratio"]
                }
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
                auto_detect_website_type: 是否自动检测网站类型（默认True）
            ---
            `fragment` 参数是用来指示输入的 HTML 是否是一个 HTML 片段（而不是完整的 HTML 文档）。

            在 HTML 转 Markdown 的过程中，这个参数很重要，具体用途如下：

            1. 当 `fragment=True` 时，表示输入的 HTML 只是一个片段，比如：
            ```html
            <p>这是一个段落</p><ul><li>列表项</li></ul>
            ```

            2. 当 `fragment=False`（默认值）时，表示输入的是完整 HTML 文档，包含 `<html>`、`<head>`、`<body>` 等标签：
            ```html
            <!DOCTYPE html>
            <html>
            <head><title>标题</title></head>
            <body>
                <p>这是一个段落</p>
            </body>
            </html>
            ```

            当设置 `fragment=True` 时，转换器会自动将 HTML 片段包装在一个指定的根元素（通过 `fragment_root` 参数指定，默认是 `"div"`）中，以便正确解析。这样处理是因为大多数 HTML 解析器需要一个完整的、有效的 HTML 结构才能正确工作。

            所以当你只有一小段 HTML 内容而不是完整的 HTML 文档时，你应该使用 `fragment=True`，确保转换器能正确处理这些不完整的 HTML 片段。
            ---
            1. `fragment` 参数：
            - 默认值为 False
            - 当设置为 True 时，表示输入的 HTML 不是完整文档，只是一段 HTML 片段（如单个元素或多个元素）
            - 转换器会将这个片段包装在一个根元素中进行处理

            2. `fragment_root` 参数：
            - 默认值为 'div'
            - 当 fragment=True 时，用于指定包装 HTML 片段的容器元素
            - 例如，设置为 'div' 时，会将片段包装为 `<div>片段内容</div>` 再进行处理
            - 在 convert_html_fragment 方法中，可以通过此参数指定不同的包装元素，如 'article'，将片段包装为 `<article>片段内容</article>`
            ---

        Returns:
            Markdown字符串
        """
        # 提取片段相关选项
        fragment = kwargs.pop("fragment", False)
        fragment_root = kwargs.pop("fragment_root", "div")
        auto_detect_website_type = kwargs.pop("auto_detect_website_type", True)

        # 处理HTML片段
        if fragment:
            # 如果是HTML片段，包装在指定的根元素中
            html = f"<{fragment_root}>{html}</{fragment_root}>"

        # 自动检测网站类型
        if auto_detect_website_type and "wechat" not in kwargs:
            is_wechat = False
            # 仅当用户未显式禁用自动检测时检查
            if self.service.options.get("auto_detect_website_type", True):
                website_types = self.service._detect_website_type(html)
                is_wechat = website_types["wechat"]

            # 如果检测到是微信公众号文章，应用微信专用处理
            if is_wechat:
                # 将dialect设置为wechat
                kwargs["wechat"] = True
                print("检测到微信公众号文章，应用专用处理...")

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
