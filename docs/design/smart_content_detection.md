# 内容类型检测重构方案

## 1. 背景和问题

当前 `html2md.py` 文件中包含了内容类型检测和相应处理逻辑，随着支持的内容类型增加，这个文件将会变得极度膨胀和难以维护。主要问题包括：

1. **代码耦合度高**：内容检测和处理逻辑与转换器核心功能耦合
2. **可扩展性差**：添加新内容类型需要修改核心代码文件
3. **测试困难**：各内容类型的处理逻辑混杂在一起，难以单独测试
4. **维护成本高**：不同内容的特殊处理逻辑混合在同一文件中
5. **灵活性不足**：用户难以自定义和控制检测行为

## 2. 设计目标

1. **解耦内容检测与处理逻辑**：将内容类型检测和处理逻辑从核心转换器中分离
2. **插件式架构**：允许通过插件方式添加新的内容类型支持，无需修改核心代码
3. **标准化接口**：建立统一的接口规范，使所有内容处理器遵循相同的约定
4. **易于测试**：支持对每个内容处理器单独进行测试
5. **配置灵活**：允许用户自定义启用或禁用特定内容类型的处理逻辑

## 3. 架构设计

### 3.1 整体架构

采用策略模式和工厂模式的组合：

```
src/magiclens/
├── ...
├── content_detectors/              # 内容检测器目录
│   ├── __init__.py                 # 注册和管理所有检测器
│   ├── base.py                     # 基础检测器类和接口定义
│   ├── registry.py                 # 检测器注册表
│   └── types/                      # 具体内容类型检测器实现
│       ├── __init__.py
│       ├── wechat.py               # 微信公众号检测器
│       ├── baidu.py                # 百度网页检测器
│       └── ...                     # 其他内容类型检测器
├── content_processors/             # 内容处理器目录
│   ├── __init__.py                 # 注册和管理所有处理器
│   ├── base.py                     # 基础处理器类和接口定义
│   ├── registry.py                 # 处理器注册表
│   └── types/                      # 具体内容类型处理器实现
│       ├── __init__.py
│       ├── wechat.py               # 微信公众号处理器
│       ├── baidu.py                # 百度网页处理器
│       └── ...                     # 其他内容类型处理器
├── converters/                     # 现有转换器目录
│   ├── __init__.py
│   ├── base.py
│   ├── html2md.py                  # 需要修改以集成内容检测
│   └── ...
└── ...
```

### 3.2 核心接口设计

#### 3.2.1 内容检测器接口

```python
class ContentDetectorBase(ABC):
    """内容检测器基类"""

    @property
    @abstractmethod
    def content_type(self) -> str:
        """返回内容类型标识符"""
        pass

    @abstractmethod
    def detect(self, html: str, context: Optional[Dict[str, Any]] = None) -> bool:
        """
        检测HTML是否为特定内容类型

        Args:
            html: HTML内容
            context: 可选的上下文信息，如URL、来源等

        Returns:
            是否匹配当前内容类型
        """
        pass

    @property
    def priority(self) -> int:
        """
        检测器优先级，数值越小优先级越高
        默认为100
        """
        return 100
```

#### 3.2.2 内容处理器接口

```python
class ContentProcessorBase(ABC):
    """内容处理器基类"""

    @property
    @abstractmethod
    def content_type(self) -> str:
        """返回内容类型标识符，必须与对应检测器匹配"""
        pass

    @abstractmethod
    def preprocess_html(self, soup: BeautifulSoup) -> None:
        """
        预处理HTML

        Args:
            soup: BeautifulSoup对象
        """
        pass

    @abstractmethod
    def postprocess_markdown(self, markdown: str) -> str:
        """
        后处理Markdown

        Args:
            markdown: 转换后的Markdown内容

        Returns:
            处理后的Markdown内容
        """
        pass

    def get_dialect_options(self) -> Dict[str, Any]:
        """
        获取此内容类型的方言选项

        Returns:
            方言选项字典
        """
        return {}
```

#### 3.2.3 检测器注册表

```python
class ContentDetectorRegistry:
    """内容检测器注册表"""

    def __init__(self):
        self._detectors = []

    def register(self, detector: ContentDetectorBase) -> None:
        """注册检测器"""
        self._detectors.append(detector)
        # 按优先级排序
        self._detectors.sort(key=lambda d: d.priority)

    def detect_content_type(self, html: str, context: Optional[Dict[str, Any]] = None) -> List[str]:
        """
        检测HTML的内容类型

        Args:
            html: HTML内容
            context: 可选的上下文信息，如URL、来源等

        Returns:
            匹配的内容类型列表，按优先级排序
        """
        matched_types = []
        for detector in self._detectors:
            if detector.detect(html, context):
                matched_types.append(detector.content_type)
        return matched_types
```

#### 3.2.4 智能内容检测管理器

```python
class SmartContentDetectionManager:
    """智能内容检测管理器"""

    def __init__(self, registry: ContentDetectorRegistry):
        self.registry = registry
        self._processor_map = {}  # 内容类型到处理器的映射

    def register_processor(self, content_type: str, processor: ContentProcessorBase) -> None:
        """注册处理器"""
        self._processor_map[content_type] = processor

    def detect_and_get_processor(self, html: str, detection_mode: str = 'auto', context: Optional[Dict[str, Any]] = None) -> Tuple[str, Optional[ContentProcessorBase]]:
        """
        检测内容类型并获取相应处理器

        Args:
            html: HTML内容
            detection_mode: 检测模式
                - 'auto': 自动检测内容类型
                - 'default': 不进行特殊处理
                - 其他值: 指定的内容类型名称
            context: 可选的上下文信息，如URL、来源等

        Returns:
            检测到的内容类型和对应的处理器（如果有）
        """
        if detection_mode == 'auto':
            # 自动检测模式
            content_types = self.registry.detect_content_type(html, context)
            if content_types:
                # 返回第一个匹配的类型及其处理器
                content_type = content_types[0]
                return content_type, self._processor_map.get(content_type)
        elif detection_mode != 'default' and detection_mode in self._processor_map:
            # 使用指定的内容类型
            return detection_mode, self._processor_map.get(detection_mode)

        # 默认情况：使用默认处理或无处理
        return 'default', None
```

### 3.3 集成方案

1. 在 `html2md.py` 中使用新的检测器和处理器架构
2. 保持向后兼容，通过配置选项允许切换新旧实现
3. 通过自动发现和注册机制，支持插件式扩展

### 3.4 `smart_content_detection` 参数设计

在转换器中引入 `smart_content_detection` 参数，支持以下值：

1. `"auto"` (默认值): 自动检测内容类型，应用最匹配的处理器
2. `"default"`: 不应用任何特殊内容处理
3. 特定内容类型名称 (如 `"wechat"`, `"baidu"` 等): 直接应用指定类型的处理器

另外，可以通过 `detection_context` 参数传入上下文信息，用于辅助内容类型的检测：

```python
detection_context = {
    "url": "https://www.baidu.com/s?wd=Python",  # 页面URL
    "source": "browser",                          # 内容来源
    "metadata": {                                 # 其他元数据
        "title": "Python - 百度搜索",
        "timestamp": "2023-05-15T12:30:45Z"
    }
}
```

#### 3.4.1 使用示例

```python
# 自动检测模式（默认）
converter = Html2MarkdownConverter({
    "smart_content_detection": "auto"
})

# 禁用特殊处理
converter = Html2MarkdownConverter({
    "smart_content_detection": "default"
})

# 指定使用百度处理器
converter = Html2MarkdownConverter({
    "smart_content_detection": "baidu"
})

# 使用上下文信息辅助检测
converter = Html2MarkdownConverter({
    "smart_content_detection": "auto",
    "detection_context": {
        "url": "https://www.baidu.com/s?wd=Python",
        "source": "browser"
    }
})
```

## 4. 实现步骤

1. 创建基础架构和接口
2. 实现智能内容检测管理器
3. 将现有的微信公众号检测和处理逻辑迁移到新架构
4. 实现百度网页的检测和处理逻辑
5. 修改 `html2md.py` 以使用新架构
6. 编写单元测试
7. 更新文档和示例

## 5. 百度内容支持方案

百度搜索结果页面特点：
1. 包含特定的DOM结构和CSS类名
2. 搜索结果通常包含在特定的容器中
3. 有特定的页面元素需要清理或处理

检测逻辑：
- 检查页面是否包含百度特有的元素和结构
- 检查URL是否为百度域名

处理逻辑：
- 清理导航栏、侧边栏等无关元素
- 优化搜索结果的格式
- 确保链接可用性
- 调整图片处理方式

## 6. 内容类型示例

### 6.1 微信公众号文章

特点：
1. 使用特定的图片加载方式（如data-src属性）
2. 包含特定的页面结构和类名
3. 包含微信特有的互动元素

检测逻辑：
- 检查是否包含微信公众号特有的元素
- 检查页面元数据中的微信标识

处理逻辑：
- 提取文章标题和正文
- 处理图片资源路径
- 移除广告和无关互动元素

## 7. 示例实现

### 7.1 百度内容检测器

```python
class BaiduDetector(ContentDetectorBase):
    """百度网页检测器"""

    @property
    def content_type(self) -> str:
        return "baidu"

    @property
    def priority(self) -> int:
        return 50  # 优先级高于一般检测器

    def detect(self, html: str, context: Optional[Dict[str, Any]] = None) -> bool:
        # 检测是否为百度页面
        baidu_indicators = [
            "百度一下，你就知道",
            "www.baidu.com",
            "content=\"百度",
            "class=\"result c-container",
            "class=\"s_form\"",
        ]

        # 通过URL检测
        if context and 'url' in context:
            url = context['url']
            if 'baidu.com' in url or 'baidu.cn' in url:
                return True

        # 通过HTML内容检测
        for indicator in baidu_indicators:
            if indicator in html:
                return True
        return False
```

### 7.2 百度内容处理器

```python
class BaiduProcessor(ContentProcessorBase):
    """百度网页处理器"""

    @property
    def content_type(self) -> str:
        return "baidu"

    def preprocess_html(self, soup: BeautifulSoup) -> None:
        # 删除无关元素
        selectors_to_remove = [
            "#s_tab",             # 顶部导航
            "#bottom_layer",      # 底部信息
            "#content_right",     # 右侧栏
            ".sam_content_right", # 其他右侧内容
            "#searchTag",         # 搜索标签
            ".s-top-right",       # 顶部右侧
            "#foot"               # 页脚
        ]

        for selector in selectors_to_remove:
            for element in soup.select(selector):
                element.decompose()

        # 处理搜索结果
        for result in soup.select(".result.c-container"):
            # 确保每个结果都有标题标签
            title = result.select_one(".t")
            if title:
                h3 = soup.new_tag("h3")
                h3.append(title.text)
                title.replace_with(h3)

            # 处理摘要
            abstract = result.select_one(".c-abstract")
            if abstract:
                p = soup.new_tag("p")
                p.string = abstract.text
                abstract.replace_with(p)

    def postprocess_markdown(self, markdown: str) -> str:
        # 清理百度特有的杂项内容
        patterns_to_remove = [
            r"百度快照.*?$",
            r"收藏举报.*?$",
            r"广告[0-9\s]*$"
        ]

        for pattern in patterns_to_remove:
            markdown = re.sub(pattern, "", markdown, flags=re.MULTILINE)

        # 优化格式
        markdown = re.sub(r"\n{3,}", "\n\n", markdown)
        return markdown

    def get_dialect_options(self) -> Dict[str, Any]:
        return {
            "headingStyle": "atx",
            "bulletListMarker": "-",
            "codeBlockStyle": "fenced",
            "emDelimiter": "*",
            "strongDelimiter": "**",
            "linkStyle": "inlined",
            "useHtmlTags": False,  # 移除不支持的HTML标签
            "clean": {
                "removeComments": True,
                "removeEmptyTags": True,
                "removeTags": ["script", "style", "noscript", "iframe", "form"],
                "removeAttrs": ["id", "class", "onclick", "onload"]
            }
        }
```

## 8. 迁移策略

1. **分阶段迁移**：先实现新架构，但保持旧代码可用
2. **双重注册**：同一内容类型可以注册多个检测器，优先使用高优先级检测器
3. **默认启用**：智能内容检测默认为启用状态，可通过配置禁用
4. **版本管理**：在新的版本中标记旧实现为过时，在未来版本中移除

## 9. 单元测试策略

1. 为每个检测器编写专门的测试用例
2. 使用真实HTML样本进行测试
3. 测试不同内容类型的组合检测情况
4. 测试配置选项对检测和处理的影响

## 10. 时间线

1. **第一阶段（1周）**：创建基础架构和接口，实现智能内容检测管理器
2. **第二阶段（1周）**：迁移微信公众号检测和处理逻辑，实现百度内容支持
3. **第三阶段（1周）**：集成到主转换器，提供 `smart_content_detection` 参数支持
4. **第四阶段（1周）**：完善测试和文档

## 11. 结论

这种重构将使内容类型检测和处理更加模块化和可扩展，大大降低维护成本。同时，它为添加新内容类型提供了标准化的框架，使扩展变得简单高效。通过 `smart_content_detection` 参数，用户可以灵活选择使用自动检测、默认处理或指定特定内容类型处理，满足不同使用场景的需求。

## 12. Html2MarkdownConverter 的集成接口

```python
class Html2MarkdownConverter:
    def __init__(self, options: Dict[str, Any] = None):
        """
        初始化 HTML 到 Markdown 转换器

        Args:
            options: 配置选项
                - smart_content_detection: 内容检测模式
                    - "auto": 自动检测内容类型 (默认)
                    - "default": 不应用特殊内容处理
                    - 特定内容类型名称: 直接应用指定类型处理器
                - detection_context: 内容检测的上下文信息
                    - url: 页面URL
                    - source: 内容来源
                    - metadata: 其他元数据
        """
        self.options = options or {}
        self._init_content_detection()

    def _init_content_detection(self):
        # 初始化内容检测系统
        self.content_registry = ContentDetectorRegistry()
        self.content_manager = SmartContentDetectionManager(self.content_registry)

        # 注册所有内容检测器和处理器
        self._register_content_detectors_and_processors()

    def _register_content_detectors_and_processors(self):
        # 注册所有内容检测器和处理器
        # 此处会通过自动发现插件的方式加载所有可用的检测器和处理器
        pass

    def convert(self, html: str) -> str:
        """
        将HTML转换为Markdown

        Args:
            html: HTML内容

        Returns:
            转换后的Markdown内容
        """
        # 获取内容检测模式
        detection_mode = self.options.get('smart_content_detection', 'auto')

        # 获取内容检测上下文
        context = self.options.get('detection_context')

        # 检测内容类型并获取处理器
        content_type, processor = self.content_manager.detect_and_get_processor(
            html, detection_mode, context
        )

        # 解析HTML
        soup = BeautifulSoup(html, 'html.parser')

        # 应用内容预处理
        if processor:
            processor.preprocess_html(soup)

        # 转换为Markdown（核心转换逻辑）
        markdown = self._convert_to_markdown(soup, processor)

        # 应用内容后处理
        if processor:
            markdown = processor.postprocess_markdown(markdown)

        return markdown

    def _convert_to_markdown(self, soup: BeautifulSoup, processor: Optional[ContentProcessorBase]) -> str:
        # 核心HTML到Markdown转换逻辑
        # 如果有处理器，考虑其dialect_options
        dialect_options = {}
        if processor:
            dialect_options = processor.get_dialect_options()

        # 应用转换
        # ...

        return "Markdown content"  # 实际会返回转换后的内容
```
