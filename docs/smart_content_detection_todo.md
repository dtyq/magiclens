# 智能内容检测实施 TODO

## 1. 基础架构实现

- [x] 创建目录结构
  - [x] `src/magiclens/content_detectors/` 目录
    - [x] `__init__.py`
    - [x] `base.py`
    - [x] `registry.py`
    - [x] `types/` 子目录
  - [x] `src/magiclens/content_processors/` 目录
    - [x] `__init__.py`
    - [x] `base.py`
    - [x] `registry.py`
    - [x] `types/` 子目录
- [x] 实现核心接口
  - [x] `ContentDetectorBase` 类
  - [x] `ContentProcessorBase` 类
- [x] 实现注册表
  - [x] `ContentDetectorRegistry` 类
- [x] 实现智能内容检测管理器
  - [x] `SmartContentDetectionManager` 类
- [x] 实现自动发现和注册机制
  - [x] 使用入口点(entry points)或动态导入

## 2. 内容检测器实现

- [x] 微信公众号内容检测器
  - [x] 基于HTML特征的检测逻辑
  - [x] 支持URL和元数据的上下文检测
- [x] 百度搜索结果检测器
  - [x] 基于HTML特征的检测逻辑
  - [x] 支持URL的上下文检测
- [x] 知乎文章检测器
  - [x] 基于HTML特征的检测逻辑
  - [x] 支持URL的上下文检测
- [x] 其他常用网站检测器
  - [x] 简书、CSDN等技术博客
  - [x] 新闻网站

## 3. 内容处理器实现

- [x] 微信公众号内容处理器
  - [x] 预处理逻辑 (处理图片、清理广告等)
  - [x] 后处理逻辑 (格式优化等)
- [x] 百度搜索结果处理器
  - [x] 预处理逻辑 (清理导航栏、侧边栏等)
  - [x] 后处理逻辑 (格式优化等)
- [x] 知乎文章处理器
  - [x] 预处理逻辑
  - [x] 后处理逻辑
- [x] 其他常用网站处理器
  - [x] 简书、CSDN等技术博客
  - [x] 新闻网站处理器

## 4. 与核心转换器集成

- [x] 在 `html2md.py` 中集成智能内容检测系统
  - [x] 添加 `smart_content_detection` 参数支持
  - [x] 添加 `detection_context` 参数支持
  - [x] 修改转换流程以使用内容检测
- [x] 确保改造完全完成
  - [x] 无需考虑兼容性，确保一次性改造到位

## 5. 测试和验证

- [x] 单元测试（只需要写两个）
  - [x] 写一个百度首页+百度搜索页的测试
  - [x] 写一个知乎首页+知乎内容页的测试

## 6. 文档和示例

- [x] 无需编写文档，直接完成
