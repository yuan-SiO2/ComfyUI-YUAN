from .nodes import (
    QwenVL模型加载器,
    QwenVL图像推理,
    QwenVL卸载模型,
)

from .yuan_nodes.yuan_txt_splitter import NODE_CLASS_MAPPINGS as YUAN_TXT_MAPPINGS
from .yuan_nodes.yuan_txt_splitter import NODE_DISPLAY_NAME_MAPPINGS as YUAN_TXT_DISPLAY_MAPPINGS

from .bernini import NODE_CLASS_MAPPINGS as BERNINI_MAPPINGS
from .bernini import NODE_DISPLAY_NAME_MAPPINGS as BERNINI_DISPLAY_MAPPINGS

NODE_CLASS_MAPPINGS = {
    "QwenVL_ModelLoader": QwenVL模型加载器,
    "QwenVL_ImageInfer": QwenVL图像推理,
    "QwenVL_Unload": QwenVL卸载模型,
    **YUAN_TXT_MAPPINGS,
    **BERNINI_MAPPINGS,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "QwenVL_ModelLoader": "Qwen VL 模型加载器",
    "QwenVL_ImageInfer": "Qwen VL 图像推理",
    "QwenVL_Unload": "Qwen VL 卸载模型",
    **YUAN_TXT_DISPLAY_MAPPINGS,
    **BERNINI_DISPLAY_MAPPINGS,
}

WEB_DIRECTORY = "./web"

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS", "WEB_DIRECTORY"]