import re
import torch
import comfy.model_management
import comfy.utils
import node_helpers
import folder_paths

from .prompt_enhancer import (
    build_llm_prompt,
    build_prompt_request,
    get_system_prompt_for_task,
    parse_prompt_response,
)

MAX_INDIVIDUAL_REFS = 10


def _resize_long_edge(image, max_size, stride=16):
    h, w = image.shape[1], image.shape[2]
    scale = min(max_size / max(h, w), 1.0)
    nh = max(stride, round(h * scale / stride) * stride)
    nw = max(stride, round(w * scale / stride) * stride)
    return comfy.utils.common_upscale(image[:, :, :, :3].movedim(-1, 1), nw, nh, "area", "disabled").movedim(1, -1)


def _collect_reference_images(reference_images=None, **kwargs):
    refs = []
    if reference_images is not None:
        for i in range(reference_images.shape[0]):
            refs.append(reference_images[i : i + 1])
    for i in range(1, MAX_INDIVIDUAL_REFS + 1):
        key = f"reference_image_{i}"
        img = kwargs.get(key, None)
        if img is not None:
            refs.append(img[0:1] if img.ndim == 4 else img.unsqueeze(0))
    return refs


def _build_bernini_context(vae, length, width, height, source_video=None, reference_video=None, ref_max_size=848, **kwargs):
    device = comfy.model_management.get_torch_device()
    offload_device = comfy.model_management.unet_offload_device()

    context = {}
    if source_video is not None:
        vid = comfy.utils.common_upscale(
            source_video[:length, :, :, :3].movedim(-1, 1), width, height, "area", "center"
        ).movedim(1, -1)
        context["video"] = vae.encode(vid[:, :, :, :3].to(device))

    refs = []
    if reference_video is not None:
        ref_vid = _resize_long_edge(reference_video[:length], ref_max_size)
        refs.append(vae.encode(ref_vid[:, :, :, :3].to(device)))

    collected = _collect_reference_images(**kwargs)
    for img in collected:
        resized = _resize_long_edge(img, ref_max_size)
        refs.append(vae.encode(resized[:, :, :, :3].to(device)))

    context["refs"] = refs
    return context


def _build_chat_prompts(system_prompt, api_prompt, original_prompt):
    system_prompt = (system_prompt or "").strip()
    api_prompt = (api_prompt or "").strip()
    original_prompt = (original_prompt or "").strip()
    if not api_prompt or api_prompt == original_prompt:
        return system_prompt, original_prompt

    text = api_prompt
    match = re.search(
        r"\n\s*(?P<label>Original (?:instruction|description)):\s*\n(?P<user>.*?)\s*$",
        text,
        flags=re.DOTALL,
    )
    if match:
        return text[: match.start()].strip(), match.group("user").strip()

    match = re.search(
        r"(?m)^\s*-?\s*User's (?:raw instruction|editing instruction|instruction|prompt):\s*\"(?P<user>.*?)\"\s*$",
        text,
    )
    if match:
        cleaned = (text[: match.start()] + text[match.end() :]).strip()
        return cleaned, match.group("user").strip()

    return api_prompt, original_prompt


class BerniniConditioning:
    @classmethod
    def INPUT_TYPES(cls):
        inputs = {
            "required": {
                "positive": ("CONDITIONING",),
                "negative": ("CONDITIONING",),
                "vae": ("VAE",),
                "width": ("INT", {"default": 832, "min": 16, "max": 8192, "step": 16}),
                "height": ("INT", {"default": 480, "min": 16, "max": 8192, "step": 16}),
                "length": ("INT", {"default": 81, "min": 1, "max": 8192, "step": 4}),
                "batch_size": ("INT", {"default": 1, "min": 1, "max": 4096}),
                "ref_max_size": ("INT", {"default": 848, "min": 16, "max": 8192, "step": 16}),
            },
            "optional": {
                "source_video": ("IMAGE",),
                "reference_video": ("IMAGE",),
                "reference_images": ("IMAGE",),
            },
        }
        for i in range(1, MAX_INDIVIDUAL_REFS + 1):
            inputs["optional"][f"reference_image_{i}"] = ("IMAGE",)
        return inputs

    RETURN_TYPES = ("CONDITIONING", "CONDITIONING", "LATENT")
    RETURN_NAMES = ("positive", "negative", "latent")
    FUNCTION = "execute"
    CATEGORY = "YUAN_ALL"

    def execute(
        self,
        positive,
        negative,
        vae,
        width,
        height,
        length,
        batch_size,
        ref_max_size=848,
        source_video=None,
        reference_video=None,
        reference_images=None,
        **kwargs,
    ):
        latent = torch.zeros(
            [batch_size, 16, ((length - 1) // 4) + 1, height // 8, width // 8],
            device=comfy.model_management.intermediate_device(),
        )

        context_parts = _build_bernini_context(
            vae,
            length,
            width,
            height,
            source_video=source_video,
            reference_video=reference_video,
            reference_images=reference_images,
            ref_max_size=ref_max_size,
            **kwargs,
        )
        context = []
        if "video" in context_parts:
            context.append(context_parts["video"])
        context.extend(context_parts["refs"])

        if context:
            positive = node_helpers.conditioning_set_values(positive, {"context_latents": context})
            negative = node_helpers.conditioning_set_values(negative, {"context_latents": context})

        return (positive, negative, {"samples": latent})


class BerniniPromptEnhancer:
    TASK_TYPES = [
        "t2v", "t2i", "v2v", "mv2v", "i2i", "i2v",
        "r2v", "r2i", "rv2v", "vrc2v", "vi2v", "ads2v",
    ]

    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "prompt": ("STRING", {"default": "", "multiline": True}),
                "task_type": (cls.TASK_TYPES, {"default": "v2v"}),
            },
            "optional": {
                "video_frames": ("INT", {"default": 3, "min": 1, "max": 8}),
                "source_video": ("IMAGE",),
                "source_image": ("IMAGE",),
                "reference_images": ("IMAGE",),
            },
        }

    RETURN_TYPES = ("STRING", "STRING", "STRING", "STRING", "STRING")
    RETURN_NAMES = ("system_prompt", "user_prompt", "llm_prompt", "api_prompt", "json_mode")
    FUNCTION = "execute"
    CATEGORY = "YUAN_ALL"

    def execute(
        self,
        prompt,
        task_type,
        video_frames=3,
        source_video=None,
        source_image=None,
        reference_images=None,
    ):
        prompt = (prompt or "").strip()
        if not prompt:
            system_prompt = get_system_prompt_for_task(task_type)
            return (system_prompt, "", "", "", "false")

        system_prompt, api_prompt, json_mode = build_prompt_request(
            task_type,
            prompt,
            video=source_video,
            image=source_image,
            images=reference_images,
            video_frames=video_frames,
        )
        chat_system_prompt, chat_user_prompt = _build_chat_prompts(system_prompt, api_prompt, prompt)
        llm_prompt = build_llm_prompt(chat_system_prompt, chat_user_prompt, json_mode=json_mode)
        return (
            chat_system_prompt,
            chat_user_prompt,
            llm_prompt,
            api_prompt,
            "true" if json_mode else "false",
        )


class BerniniPromptResultParser:
    @classmethod
    def INPUT_TYPES(cls):
        return {
            "required": {
                "api_response": ("STRING", {"default": "", "multiline": True, "forceInput": True}),
            },
            "optional": {
                "original_prompt": ("STRING", {"default": "", "multiline": True}),
                "json_mode": ("STRING", {"default": "false"}),
            },
        }

    RETURN_TYPES = ("STRING",)
    RETURN_NAMES = ("enhanced_prompt",)
    FUNCTION = "execute"
    CATEGORY = "YUAN_ALL"

    def execute(self, api_response, original_prompt="", json_mode="false"):
        json_mode_bool = str(json_mode or "").strip().lower() in {"1", "true", "yes", "json"}
        return (parse_prompt_response(api_response, original_prompt, json_mode=json_mode_bool),)
