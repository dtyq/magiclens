import unittest
from bs4 import BeautifulSoup
import os
import sys

# 添加src目录到Python路径
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

from magiclens.content_detectors.manager import SmartContentDetectionManager
from magiclens.content_detectors.discovery import discover_and_register_plugins
from magiclens.content_detectors.types.baidu import BaiduSearchResultDetector
from magiclens.content_detectors.types.zhihu import ZhihuContentDetector
from magiclens.converters.html2md import Html2MarkdownConverter


class TestSmartContentDetection(unittest.TestCase):
    """智能内容检测系统的测试用例"""

    def setUp(self):
        """初始化测试环境"""
        self.manager = SmartContentDetectionManager()
        # 注册检测器和处理器
        discover_and_register_plugins(self.manager)

        # 创建带有智能内容检测的HTML2MD转换器
        self.converter = Html2MarkdownConverter({
            "smart_content_detection": True,
            "dialect": "github"
        })

    def test_detector_registration(self):
        """测试检测器注册"""
        # 检查是否有检测器被注册
        detectors = self.manager.detector_registry.list_detectors()
        self.assertTrue(len(detectors) > 0, "没有检测器被注册")

        # 检查特定检测器是否存在
        detector_types = [type(d) for d in detectors]
        self.assertIn(BaiduSearchResultDetector, detector_types, "百度搜索结果检测器未注册")
        self.assertIn(ZhihuContentDetector, detector_types, "知乎内容检测器未注册")

    def test_baidu_detection(self):
        """测试百度搜索结果检测"""
        # 创建模拟的百度搜索结果HTML
        baidu_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>智能内容检测 - 百度搜索</title>
            <meta charset="utf-8">
        </head>
        <body>
            <div id="head">
                <div id="s_top_wrap">顶部导航</div>
                <div id="u">用户信息</div>
                <div id="head_wrapper">
                    <div id="s_form">
                        <input type="text" id="kw" name="wd" value="智能内容检测">
                        <input type="submit" id="su" value="百度一下">
                    </div>
                </div>
            </div>
            <div id="s_tab">标签栏</div>
            <div id="content_left">
                <div class="c-container">
                    <h3 class="t"><a href="http://example.com/1">第一个结果</a></h3>
                    <div class="c-abstract">结果摘要内容</div>
                </div>
                <div class="c-container">
                    <h3 class="t"><a href="http://example.com/2">第二个结果</a></h3>
                    <div class="c-abstract">结果摘要内容</div>
                </div>
            </div>
            <div id="content_right">右侧栏内容</div>
            <div id="foot">页脚内容</div>
            <div id="page">分页内容</div>
        </body>
        </html>
        """

        # 测试检测器
        soup = BeautifulSoup(baidu_html, 'html.parser')
        detector = BaiduSearchResultDetector()
        self.assertTrue(detector.detect(soup), "未检测到百度搜索结果")

        # 测试预处理
        context = {"url": "https://www.baidu.com/s?wd=智能内容检测"}
        soup, content_type = self.manager.preprocess(soup, context=context)

        # 检查是否移除了导航栏和侧边栏
        self.assertIsNone(soup.select_one('#head'), "导航栏未被移除")
        self.assertIsNone(soup.select_one('#content_right'), "侧边栏未被移除")

        # 检查Markdown转换
        markdown = self.converter.convert_html(str(soup), detection_context=context)
        self.assertIn("智能内容检测", markdown, "关键词未保留在Markdown中")
        self.assertIn("第一个结果", markdown, "搜索结果未保留在Markdown中")
        self.assertIn("第二个结果", markdown, "搜索结果未保留在Markdown中")

    def test_zhihu_detection(self):
        """测试知乎内容检测"""
        # 创建模拟的知乎文章HTML
        zhihu_html = """
        <!DOCTYPE html>
        <html>
        <head>
            <title>智能内容检测是什么？如何实现？ - 知乎</title>
            <meta charset="utf-8">
            <meta name="keywords" content="知乎,智能内容检测">
        </head>
        <body>
            <div class="AppHeader">顶部导航</div>
            <div class="QuestionHeader">
                <h1 class="QuestionHeader-title">智能内容检测是什么？如何实现？</h1>
            </div>
            <div class="Question-main">
                <div class="QuestionAnswer-content">
                    <div class="RichContent-inner">
                        <p>智能内容检测是指通过技术手段自动识别和处理不同来源的网页内容，并针对其特点进行优化处理。</p>
                        <p>实现方法包括：</p>
                        <ol>
                            <li>特征检测算法</li>
                            <li>HTML结构分析</li>
                            <li>机器学习模型</li>
                        </ol>
                    </div>
                </div>
            </div>
            <div class="Comments-container">评论区域</div>
            <div class="Reward">打赏区域</div>
            <div class="CornerButtons">角落按钮</div>
            <div class="Footer">页脚内容</div>
        </body>
        </html>
        """

        # 测试检测器
        soup = BeautifulSoup(zhihu_html, 'html.parser')
        detector = ZhihuContentDetector()
        self.assertTrue(detector.detect(soup), "未检测到知乎内容")

        # 测试预处理
        context = {"url": "https://www.zhihu.com/question/123456/answer/789012"}
        soup, content_type = self.manager.preprocess(soup, context=context)

        # 检查是否移除了导航栏和页脚
        self.assertIsNone(soup.select_one('.AppHeader'), "导航栏未被移除")
        self.assertIsNone(soup.select_one('.Footer'), "页脚未被移除")

        # 检查Markdown转换
        markdown = self.converter.convert_html(str(soup), detection_context=context)
        self.assertIn("智能内容检测是什么？如何实现？", markdown, "标题未保留在Markdown中")
        self.assertIn("智能内容检测是指", markdown, "正文内容未保留在Markdown中")
        self.assertIn("特征检测算法", markdown, "列表内容未保留在Markdown中")


if __name__ == '__main__':
    unittest.main()
