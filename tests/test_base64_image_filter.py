import pytest
from bs4 import BeautifulSoup
from src.magiclens.converters import Html2MarkdownConverter


def test_base64_image_filtering():
    """测试过滤 base64 图片链接的功能"""

    # 测试 HTML 包含 base64 图片
    html = """
    <html>
    <body>
        <h1>测试图片</h1>
        <p>普通图片: <img src="https://example.com/image.jpg" alt="普通图片"></p>
        <p>Base64图片: <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" alt="Base64图片"></p>
        <p>无 Alt 的 Base64 图片: <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg=="></p>
        <p><a href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==">Base64链接</a></p>
    </body>
    </html>
    """

    # 创建转换器
    converter = Html2MarkdownConverter()

    # 转换 HTML 到 Markdown
    markdown = converter.convert_html(html)

    # 验证结果
    assert "https://example.com/image.jpg" in markdown  # 普通图片保留
    assert "data:image/png;base64," not in markdown  # base64 数据被过滤
    assert "*Base64图片*" in markdown  # base64 图片被替换为 alt 文本
    assert "*[图片]*" in markdown  # 无 alt 的 base64 图片被替换为 [图片]
    assert "Base64链接" in markdown  # 包含 base64 的链接只保留文本
    assert "iVBORw0KGgoAAAA" not in markdown  # 确保没有 base64 数据残留

def test_base64_preprocessing():
    """测试 HTML 预处理阶段对 base64 图片的处理"""

    html = """
    <html>
    <body>
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" alt="预处理测试">
    </body>
    </html>
    """

    # 创建转换器
    converter = Html2MarkdownConverter()

    # 通过 soup 检查预处理
    soup = BeautifulSoup(html, 'html.parser')
    converter.service._preprocess(soup)

    # 验证 src 属性已被删除
    img = soup.find('img')
    assert 'src' not in img.attrs
    assert img['alt'] == "预处理测试"

def test_data_uri_filtering():
    """测试过滤各种 data: URI 的功能"""

    # 测试 HTML 包含各种 data: URI
    html = """
    <html>
    <body>
        <h1>测试内联数据过滤</h1>
        <!-- 普通图片 -->
        <p>普通图片: <img src="https://example.com/image.jpg" alt="普通图片"></p>

        <!-- 各种格式的内联数据 -->
        <p>PNG Base64: <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" alt="PNG图片"></p>
        <p>JPEG Base64: <img src="data:image/jpeg;base64,/9j/4AAQSkZJRgABAQEAYABgAAD//gA+Q1JFQVRPUjogZ2QtanBlZyB2MS4wICh1c2luZyBJSkcgSlBFRyB2ODApLCBkZWZhdWx0IHF1YWx0eQD/2wBDAAIBAQIBAQICAgICAgICAwUDAwMDAwYEBAMFBwYHBwcGBwcICQsJCAgKCAcHCg0KCgsMDAwMBwkODw0MDgsMDAz/2wBDAQICAgMDAwYDAwYMCAcIDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAwMDAz/wAARCAABAAEDASIAAhEBAxEB/8QAHwAAAQUBAQEBAQEAAAAAAAAAAAECAwQFBgcICQoL/8QAtRAAAgEDAwIEAwUFBAQAAAF9AQIDAAQRBRIhMUEGE1FhByJxFDKBkaEII0KxwRVS0fAkM2JyggkKFhcYGRolJicoKSo0NTY3ODk6Q0RFRkdISUpTVFVWV1hZWmNkZWZnaGlqc3R1dnd4eXqDhIWGh4iJipKTlJWWl5iZmqKjpKWmp6ipqrKztLW2t7i5usLDxMXGx8jJytLT1NXW19jZ2uHi4+Tl5ufo6erx8vP09fb3+Pn6/8QAHwEAAwEBAQEBAQEBAQAAAAAAAAECAwQFBgcICQoL/8QAtREAAgECBAQDBAcFBAQAAQJ3AAECAxEEBSExBhJBUQdhcRMiMoEIFEKRobHBCSMzUvAVYnLRChYkNOEl8RcYGRomJygpKjU2Nzg5OkNERUZHSElKU1RVVldYWVpjZGVmZ2hpanN0dXZ3eHl6goOEhYaHiImKkpOUlZaXmJmaoqOkpaanqKmqsrO0tba3uLm6wsPExcbHyMnK0tPU1dbX2Nna4uPk5ebn6Onq8vP09fb3+Pn6/9oADAMBAAIRAxEAPwD9/KKKKAP/2Q==" alt="JPEG图片"></p>
        <p>SVG Base64: <img src="data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHdpZHRoPSIxMDAiIGhlaWdodD0iMTAwIj48Y2lyY2xlIGN4PSI1MCIgY3k9IjUwIiByPSI0MCIgc3Ryb2tlPSJibGFjayIgc3Ryb2tlLXdpZHRoPSIzIiBmaWxsPSJyZWQiIC8+PC9zdmc+" alt="SVG图片"></p>
        <p>无 Alt 的图片: <img src="data:image/gif;base64,R0lGODlhAQABAIAAAAAAAP///yH5BAEAAAAALAAAAAABAAEAAAIBRAA7"></p>

        <!-- 链接中的内联数据 -->
        <p><a href="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==">图片链接</a></p>
        <p><a href="data:text/html;base64,PGgxPkhUTUwgRG9jdW1lbnQ8L2gxPg==">HTML文档链接</a></p>
        <p><a href="data:application/pdf;base64,JVBERi0xLjQKJcOkw7zDtsOfCjIgMCBvYmoKPDwvTGVuZ3RoIDMgMCBSL0ZpbHRlci9GbGF0ZURlY29kZT4+CnN0cmVhbQp4nO2BgZ8cFxAA7Zt3MX9MYwA5G1wDFwE2kRRNfJAAEAACAG4wN+JJAAAAAAAA" target="_blank">PDF链接</a></p>

        <!-- 其他标签中的内联数据 -->
        <video controls>
            <source src="data:video/mp4;base64,AAAAGGZ0eXBtcDQyAAAAAG1wNDJtcDQxaXNvbQAAAfBtZGF0AAAAAAAAUlIODk5JVL4yEeRbPy+BAUAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAM3NXQtH3HMnE3N8jzXZZvvX+sXZXqkHGEgMw9HRcqaVnSfWV36YzIlD6pZv9JBY86Dv++OEYZVu2x9b58///" type="video/mp4">
            您的浏览器不支持视频标签。
        </video>

        <!-- 内联样式中的内联数据 -->
        <div style="background-image: url('data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==');">样式中的内联图片</div>
    </body>
    </html>
    """

    # 创建转换器
    converter = Html2MarkdownConverter()

    # 转换 HTML 到 Markdown
    markdown = converter.convert_html(html)

    # 验证结果
    assert "https://example.com/image.jpg" in markdown  # 普通图片保留
    assert "data:" not in markdown  # 所有 data: URI 都被过滤
    assert "*PNG图片*" in markdown  # data:image/png 被替换为 alt 文本
    assert "*JPEG图片*" in markdown  # data:image/jpeg 被替换为 alt 文本
    assert "*SVG图片*" in markdown  # data:image/svg+xml 被替换为 alt 文本
    assert "*[图片]*" in markdown  # 无 alt 的 data: URI 被替换为 [图片]
    assert "图片链接" in markdown  # 包含 data: URI 的链接只保留文本
    assert "HTML文档链接" in markdown  # data:text/html 链接只保留文本
    assert "PDF链接" in markdown  # data:application/pdf 链接只保留文本
    # 确保没有 base64 数据片段残留
    assert "base64" not in markdown
    assert "iVBORw0KGgo" not in markdown
    assert "/9j/4AAQSkZJRg" not in markdown
    assert "PHN2ZyB4bWxu" not in markdown

def test_data_uri_preprocessing():
    """测试 HTML 预处理阶段对各种内联数据的处理"""

    html = """
    <html>
    <body>
        <!-- 图片标签 -->
        <img src="data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mP8z8BQDwAEhQGAhKmMIQAAAABJRU5ErkJggg==" alt="测试图片">

        <!-- 链接标签 -->
        <a href="data:text/plain;base64,SGVsbG8gV29ybGQ=">文本链接</a>

        <!-- 视频源标签 -->
        <source src="data:video/mp4;base64,AAAAGGZ0eXBtcDQyAAAAAG1wNDJtcDQxaXNvbQAAAfBtZGF0" type="video/mp4">

        <!-- 样式属性 -->
        <div style="background-image: url('data:image/gif;base64,R0lGODlhAQABAIAAAP///wAAACH5BAEAAAAALAAAAAABAAEAAAICRAEAOw=='); color: red;">带有内联图片样式的元素</div>
    </body>
    </html>
    """

    # 创建转换器
    converter = Html2MarkdownConverter()

    # 通过 soup 检查预处理
    soup = BeautifulSoup(html, 'html.parser')
    converter.service._preprocess(soup)

    # 验证 img 标签的 src 属性被删除
    img = soup.find('img')
    assert 'src' not in img.attrs
    assert img['alt'] == "测试图片"

    # 验证 a 标签的 href 属性被删除
    a = soup.find('a')
    assert 'href' not in a.attrs
    assert a.string == "文本链接"

    # 验证 source 标签的 src 属性被删除
    source = soup.find('source')
    assert 'src' not in source.attrs

    # 验证样式属性中的 data: URI 被删除
    div = soup.find('div')
    assert 'style' in div.attrs
    assert 'data:' not in div['style']
    assert 'color: red' in div['style']
