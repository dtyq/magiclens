#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
MagicLens包安装配置文件。
"""

from setuptools import setup, find_packages
import os


def read(fname):
    with open(os.path.join(os.path.dirname(__file__), fname), encoding='utf-8') as f:
        return f.read()


# 定义版本信息
about = {
    '__version__': '0.3.0',
    '__author__': 'MagicLens Team',
    '__email__': 'cc@dtyq.com',
}


setup(
    name="magiclens",
    version=about['__version__'],
    author=about['__author__'],
    author_email=about['__email__'],
    description="一个灵活的HTML到Markdown转换工具",
    long_description=read('README.md'),
    long_description_content_type="text/markdown",
    url="https://github.com/magiclens/magiclens",
    package_dir={"": "src"},
    packages=find_packages(where="src"),
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Text Processing :: Markup :: HTML",
        "Topic :: Text Processing :: Markup :: Markdown",
    ],
    python_requires=">=3.8",
    install_requires=[
        "beautifulsoup4>=4.9.0",
        "requests>=2.25.0",
        "lxml>=4.6.0",
        "pyyaml>=6.0.0",
    ],
    entry_points={
        'console_scripts': [
            'magiclens=magiclens.cli:main',
        ],
    },
    include_package_data=True,
    zip_safe=False,
)
