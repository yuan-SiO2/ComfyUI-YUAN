from .bernini_patches import apply_bernini_patches

apply_bernini_patches()

from .nodes_bernini import (
    BerniniConditioning,
    BerniniPromptEnhancer,
    BerniniPromptResultParser,
)

NODE_CLASS_MAPPINGS = {
    "YUAN_BerniniConditioning": BerniniConditioning,
    "YUAN_BerniniPromptEnhancer": BerniniPromptEnhancer,
    "YUAN_BerniniPromptResultParser": BerniniPromptResultParser,
}

NODE_DISPLAY_NAME_MAPPINGS = {
    "YUAN_BerniniConditioning": "YUAN Bernini Conditioning (Multi-Ref)",
    "YUAN_BerniniPromptEnhancer": "YUAN Bernini Prompt Enhancer",
    "YUAN_BerniniPromptResultParser": "YUAN Bernini Prompt Result Parser",
}

__all__ = ["NODE_CLASS_MAPPINGS", "NODE_DISPLAY_NAME_MAPPINGS"]
