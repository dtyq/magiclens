import importlib
import pkgutil
import inspect
from typing import Dict, Any, List, Type, Tuple

from .base import ContentDetectorBase
from .manager import SmartContentDetectionManager
from ..content_processors.base import ContentProcessorBase


def discover_and_register_plugins(manager: SmartContentDetectionManager) -> None:
    """
    发现并注册所有内容检测器和处理器。

    该函数会搜索内容检测器和处理器包中的所有模块，并自动注册找到的检测器和处理器。

    Args:
        manager: 智能内容检测管理器实例
    """
    # 导入检测器类型包
    from . import types as detector_types
    discovered_detectors = _discover_classes(detector_types, ContentDetectorBase)

    # 导入处理器类型包
    from ..content_processors import types as processor_types
    discovered_processors = _discover_classes(processor_types, ContentProcessorBase)

    # 注册所有发现的检测器
    for detector_class in discovered_detectors:
        detector = detector_class()
        manager.register_detector(detector)

    # 注册所有发现的处理器
    for processor_class in discovered_processors:
        processor = processor_class()
        manager.register_processor(processor)


def _discover_classes(package, base_class: Type) -> List[Type]:
    """
    在指定包中发现指定基类的所有子类。

    Args:
        package: 要搜索的包
        base_class: 基类类型

    Returns:
        发现的类列表
    """
    discovered_classes = []

    # 遍历包中的所有模块
    prefix = package.__name__ + "."
    for _, modname, _ in pkgutil.iter_modules(package.__path__, prefix):
        try:
            module = importlib.import_module(modname)

            # 获取模块中的所有类
            for name, obj in inspect.getmembers(module, inspect.isclass):
                # 检查类是否是基类的子类，且不是基类本身
                if issubclass(obj, base_class) and obj is not base_class:
                    discovered_classes.append(obj)
        except (ImportError, AttributeError) as e:
            # 记录错误但继续处理其他模块
            print(f"Error loading module {modname}: {e}")

    return discovered_classes
