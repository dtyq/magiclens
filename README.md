# MagicLens

![版本](https://img.shields.io/badge/版本-0.3.0-blue.svg)
![Python](https://img.shields.io/badge/Python-3.8%2B-blue.svg)
![许可证](https://img.shields.io/badge/许可证-MIT-green.svg)

MagicLens 是一个强大而灵活的HTML到Markdown转换工具，它使用可扩展的规则系统，能够准确地将HTML文档转换为Markdown格式。

## 名称寓意

MagicLens（神奇透镜）的名称灵感来源于透镜能够聚焦、放大并清晰呈现物体本质的特性。就像一个魔法透镜可以将复杂的事物简化并呈现其本质一样，我们的工具可以将复杂的HTML结构"透视"并转换为简洁清晰的Markdown格式。这个过程就像是通过一个神奇的透镜，让文档内容保持原貌，只是以一种更加简洁、可读性更强的方式呈现。"神奇透镜"不仅能看透HTML的复杂结构，还能智能地解析和转换各种元素，确保转换后的Markdown保留原始内容的精髓和格式，使得内容创作者可以专注于内容本身，而不是被复杂的标记语言所困扰。

## 特性

- 高质量的HTML到Markdown转换
- 支持所有标准HTML元素
- 基于规则的转换系统，易于扩展和自定义
- 提供多种转换选项，适应不同格式需求
- 默认支持GitHub风格Markdown (GFM)
- 支持HTML片段和自定义转换规则
- 支持从文件、URL或字符串中转换HTML
- 简单易用的命令行工具
- Python API，方便集成到其他应用中

## 安装

### 使用pip安装（推荐）

```bash
pip install magiclens
```

### 从源码安装

```bash
git clone https://github.com/magiclens/magiclens.git
cd magiclens
pip install -e .
```

## 快速入门

### 命令行使用

MagicLens 提供了一个简单的命令行工具：

```bash
# 从HTML文件转换
magiclens -f input.html -o output.md

# 从URL转换
magiclens -u https://example.com -o example.md

# 从字符串转换
magiclens -s "<h1>标题</h1><p>段落</p>" -o output.md

# 显示帮助信息
magiclens --help
```

### Python API使用

```python
from magiclens.converters import Html2MarkdownConverter

# 创建转换器
converter = Html2MarkdownConverter()

# 从HTML字符串转换
html = "<h1>标题</h1><p>这是一个<strong>示例</strong>。</p>"
markdown = converter.convert_html(html)
print(markdown)

# 从URL转换
url_markdown = converter.convert_url("https://example.com")
print(url_markdown)

# 使用自定义选项
options = {
    "headingStyle": "atx",      # setext 或 atx
    "bulletListMarker": "-",    # *, -, 或 +
    "codeBlockStyle": "fenced", # fenced 或 indented
    "emDelimiter": "*",         # * 或 _
    "strongDelimiter": "**"     # ** 或 __
}
custom_converter = Html2MarkdownConverter(options=options)
custom_markdown = custom_converter.convert_html(html)
print(custom_markdown)

# 转换HTML片段
fragment = "<li>列表项1</li><li>列表项2</li>"
markdown = converter.convert_html_fragment(fragment)
print(markdown)
```

更多示例，请查看 [examples](examples/) 目录。

## 转换选项

MagicLens 支持多种转换选项，可以通过命令行参数或API选项进行设置：

| 选项名 | 可选值 | 默认值 | 描述 |
|--------|--------|--------|------|
| dialect | "github", "commonmark", "traditional", "custom" | "github" | Markdown方言类型 |
| headingStyle | "atx", "setext" | "atx" | 标题样式 (# 或 ====) |
| bulletListMarker | "*", "-", "+" | "-" | 无序列表标记 |
| codeBlockStyle | "fenced", "indented" | "fenced" | 代码块样式 (``` 或缩进) |
| fence | "```", "~~~" | "```" | 代码块围栏标记 |
| emDelimiter | "*", "_" | "*" | 斜体分隔符 |
| strongDelimiter | "**", "__" | "**" | 粗体分隔符 |
| linkStyle | "inlined", "referenced" | "inlined" | 链接样式（内联或引用） |
| linkReferenceStyle | "full", "collapsed", "shortcut" | "full" | 引用链接样式 |
| convertImages | Boolean | true | 是否转换图片 |

## Markdown方言支持

MagicLens默认使用GitHub风格Markdown（GFM），这是目前最广泛使用的Markdown方言。

### GitHub风格Markdown (GFM)

GitHub风格Markdown是本工具的默认方言，支持表格、任务列表、删除线等扩展特性：

- 任务列表 (`- [x]` 和 `- [ ]`)
- 表格支持
- 删除线 (`~~文本~~`)
- 自动链接
- ATX风格标题 (`# 标题`)
- 围栏式代码块 (```)

```python
# 默认已使用GitHub风格
converter = Html2MarkdownConverter()

# 或明确指定
converter = Html2MarkdownConverter(options={"dialect": "github"})
```

MagicLens还支持其他方言如CommonMark和传统Markdown，但我们推荐使用GFM以获得最佳体验和最广泛的兼容性。

## 项目结构

```
magiclens/
├── src/
│   └── magiclens/
│       ├── converters/    # 转换器实现
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── html2md.py
│       ├── rules/         # 转换规则
│       │   ├── __init__.py
│       │   ├── base.py
│       │   └── html2md.py
│       ├── __init__.py
│       ├── __main__.py
│       └── cli.py         # 命令行接口
├── tests/                 # 测试代码
├── examples/              # 使用示例
├── setup.py               # 安装配置
└── README.md              # 项目文档
```

## 贡献指南

我们欢迎各种形式的贡献，包括但不限于：

- 报告问题和错误
- 提出新功能建议
- 改进文档
- 提交代码修复或新功能

### 贡献步骤

1. Fork 本仓库
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m '添加一些令人惊叹的功能'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建Pull Request

## 许可证

本项目采用 MIT 许可证 - 详见 [LICENSE](LICENSE) 文件。

## 联系我们

- 项目维护者: MagicLens Team
- 电子邮件: info@magiclens.io
- GitHub Issues: [提交问题](https://github.com/magiclens/magiclens/issues)

---

*Made with ❤️ by MagicLens Team*
