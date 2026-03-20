"""
统一 AI 模型调度器

所有 AI 模型调用（LLM 文本、图片生成）应通过此模块进行。
提供：模型轮换、自动降级、重试、流式输出、Mock 模式。

使用方式：
    from shared.backend.core.ai_router import AIRouter
    router = AIRouter(settings)  # settings 需提供 get_llm_config / get_image_config 等方法
"""

from __future__ import annotations

import asyncio
import base64
import hashlib
import io
import json
import re
from typing import AsyncIterator, Protocol, runtime_checkable

import structlog

logger = structlog.get_logger()


# ── 配置协议 ──────────────────────────────────────────────


@runtime_checkable
class AISettingsProtocol(Protocol):
    """各模块 Settings 需满足的接口（鸭子类型）"""

    MAX_RETRIES: int
    RETRY_BASE_DELAY: float

    def get_llm_config(self, key: str) -> dict: ...
    def get_image_config(self, key: str) -> dict: ...
    def list_available_llms(self) -> list: ...
    def list_available_image_models(self) -> list: ...

    @property
    def is_mock_mode(self) -> bool: ...


# ── JSON 提取工具 ─────────────────────────────────────────


def extract_json(text: str) -> str:
    """从 LLM 返回中提取 JSON，处理 markdown 代码块包裹"""
    text = text.strip()
    match = re.search(r"```(?:json)?\s*\n?(.*?)\n?```", text, re.DOTALL)
    if match:
        return match.group(1).strip()
    if text.startswith("{") or text.startswith("["):
        return text
    return text


# ── 图片响应提取 ──────────────────────────────────────────


def extract_image_from_openai_response(data: dict) -> bytes | None:
    """从 OpenAI 兼容的 chat/completions 响应中提取图片 bytes"""
    try:
        message = data["choices"][0]["message"]
        content = message.get("content")

        if isinstance(content, list):
            for block in content:
                if not isinstance(block, dict):
                    continue
                if "inline_data" in block:
                    return base64.b64decode(block["inline_data"]["data"])
                if block.get("type") == "image_url" or "image_url" in block:
                    url = (block.get("image_url") or {}).get("url", "")
                    if url.startswith("data:image"):
                        b64 = url.split(",", 1)[1]
                        return base64.b64decode(b64)
                if block.get("type") == "image" and block.get("data"):
                    return base64.b64decode(block["data"])

        if isinstance(content, str):
            md_match = re.search(
                r"data:image/[^;]+;base64,([A-Za-z0-9+/=]+)", content
            )
            if md_match:
                return base64.b64decode(md_match.group(1))

        return None
    except Exception as e:
        logger.error("image_extract_failed", error=str(e))
        return None


# ── Mock 工具 ─────────────────────────────────────────────


def mock_image_bytes(prompt: str, size: str = "1024x1024") -> bytes:
    """Mock 模式：用 Pillow 生成占位图"""
    from PIL import Image, ImageDraw, ImageFont

    w, h = (int(x) for x in size.split("x"))
    seed = int(hashlib.md5(prompt.encode()).hexdigest()[:8], 16)
    r = min(230, max(80, (seed >> 16) & 0xFF))
    g = min(230, max(80, (seed >> 8) & 0xFF))
    b = min(230, max(80, seed & 0xFF))

    img = Image.new("RGB", (w, h), (r, g, b))
    draw = ImageDraw.Draw(img)
    draw.rectangle([(20, 20), (w - 20, h - 20)], outline=(255, 255, 255), width=2)

    try:
        font = ImageFont.truetype("arial.ttf", 24)
    except (OSError, IOError):
        font = ImageFont.load_default()

    label = "MOCK IMAGE"
    bbox = draw.textbbox((0, 0), label, font=font)
    tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
    draw.text(((w - tw) / 2, (h - th) / 2 - 20), label, fill="white", font=font)

    short_prompt = prompt[:60] + "..." if len(prompt) > 60 else prompt
    try:
        small_font = ImageFont.truetype("arial.ttf", 14)
    except (OSError, IOError):
        small_font = ImageFont.load_default()
    draw.text((40, h / 2 + 10), short_prompt, fill=(255, 255, 255), font=small_font)

    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def mock_llm_response(messages: list[dict]) -> str:
    """Mock 模式下返回的示例文本"""
    last_msg = messages[-1].get("content", "") if messages else ""
    if isinstance(last_msg, list):
        last_msg = " ".join(
            p.get("text", "") for p in last_msg if isinstance(p, dict)
        )
    if "分析" in last_msg or "analysis" in last_msg.lower():
        return json.dumps(
            {
                "summary": "这是一个 Mock 分析结果",
                "background": "当前处于 Mock 模式，请配置 API Key 以使用真实 AI 分析。",
                "keywords": ["热点", "营销", "AI"],
            },
            ensure_ascii=False,
        )
    return "这是 Mock 模式的回复。请在 .env 文件中配置 API Key 以使用真实的 AI 模型。"


# ── 即梦 Seedream 尺寸映射 ────────────────────────────────

SEEDREAM_SIZE_MAP = {
    "1024x1024": "2048x2048",
    "1792x1024": "2560x1440",
    "1024x1792": "1440x2560",
    "1080x1440": "1728x2304",
    "1080x1080": "2048x2048",
    "900x383": "2560x1440",
    "1920x1080": "2560x1440",
    "1080x1920": "1440x2560",
}


# ── 核心调度器类 ──────────────────────────────────────────


class AIRouter:
    """统一 AI 调度器，各模块实例化时传入自己的 settings。"""

    def __init__(self, settings: AISettingsProtocol):
        self._s = settings

    # ── 模型轮换 ──────────────────────────────────────

    def next_llm(self, current: str | None = None) -> str:
        available = [
            k if isinstance(k, str) else k.get("key", k)
            for k in self._s.list_available_llms()
        ]
        if not available:
            return "mock"
        if current is None or current not in available:
            return available[0]
        idx = available.index(current)
        return available[(idx + 1) % len(available)]

    def next_image_model(self, current: str | None = None) -> str:
        available = [
            k if isinstance(k, str) else k.get("key", k)
            for k in self._s.list_available_image_models()
        ]
        if not available:
            return "mock"
        if current is None or current not in available:
            return available[0]
        idx = available.index(current)
        return available[(idx + 1) % len(available)]

    # ── LLM 调用 ──────────────────────────────────────

    async def call_llm(
        self,
        http_client,
        model_key: str,
        messages: list[dict],
        temperature: float = 0.7,
        response_format: dict | None = None,
        timeout: int = 60,
    ) -> str:
        """单模型 LLM 调用，失败即抛异常"""
        if model_key == "mock" or self._s.is_mock_mode:
            return mock_llm_response(messages)

        cfg = self._s.get_llm_config(model_key)
        if not cfg or not cfg.get("api_key"):
            logger.warning("llm_key_missing", model=model_key)
            return mock_llm_response(messages)

        headers = {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        }
        payload: dict = {
            "model": cfg["model"],
            "messages": messages,
            "temperature": temperature,
        }
        if response_format:
            payload["response_format"] = response_format

        max_retries = self._s.MAX_RETRIES
        for attempt in range(max_retries):
            try:
                resp = await http_client.post(
                    f"{cfg['base_url']}/chat/completions",
                    json=payload,
                    headers=headers,
                    timeout=timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                content = data["choices"][0]["message"]["content"]
                logger.info("llm_call_success", model=model_key, length=len(content))
                return content
            except Exception as e:
                logger.warning(
                    "llm_call_attempt_failed",
                    model=model_key,
                    attempt=attempt + 1,
                    error=str(e),
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(self._s.RETRY_BASE_DELAY * (attempt + 1))
                    continue
                raise

        return mock_llm_response(messages)  # unreachable but safe

    async def call_llm_with_fallback(
        self,
        http_client,
        messages: list[dict],
        temperature: float = 0.7,
        preferred_model: str | None = None,
        response_format: dict | None = None,
        timeout: int = 60,
    ) -> tuple[str, str]:
        """带自动降级的 LLM 调用，返回 (content, model_used)"""
        available = [
            k if isinstance(k, str) else k.get("key", k)
            for k in self._s.list_available_llms()
        ]

        if preferred_model and preferred_model in available:
            order = [preferred_model] + [m for m in available if m != preferred_model]
        else:
            order = available

        for model_key in order:
            try:
                content = await self.call_llm(
                    http_client, model_key, messages, temperature,
                    response_format=response_format, timeout=timeout,
                )
                return content, model_key
            except Exception as e:
                logger.warning("llm_fallback", failed_model=model_key, error=str(e))
                continue

        logger.warning("all_llm_failed_using_mock")
        return mock_llm_response(messages), "mock"

    async def call_llm_stream(
        self,
        http_client,
        model_key: str,
        messages: list[dict],
        temperature: float = 0.7,
    ) -> AsyncIterator[str]:
        """LLM 流式调用（生成器，用于 SSE）"""
        if model_key == "mock" or self._s.is_mock_mode:
            mock_text = mock_llm_response(messages)
            for char in mock_text:
                yield char
            return

        cfg = self._s.get_llm_config(model_key)
        if not cfg or not cfg.get("api_key"):
            mock_text = mock_llm_response(messages)
            for char in mock_text:
                yield char
            return

        headers = {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": cfg["model"],
            "messages": messages,
            "temperature": temperature,
            "stream": True,
        }

        try:
            async with http_client.stream(
                "POST",
                f"{cfg['base_url']}/chat/completions",
                json=payload,
                headers=headers,
            ) as resp:
                resp.raise_for_status()
                async for line in resp.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]
                        if data_str.strip() == "[DONE]":
                            break
                        try:
                            data = json.loads(data_str)
                            delta = data.get("choices", [{}])[0].get("delta", {})
                            content = delta.get("content", "")
                            if content:
                                yield content
                        except json.JSONDecodeError:
                            continue
        except Exception as e:
            logger.error("llm_stream_failed", model=model_key, error=str(e))
            raise

    # ── 图片生成 ──────────────────────────────────────

    async def call_image_model(
        self,
        http_client,
        model_key: str,
        prompt: str,
        size: str = "1024x1024",
        reference_url: str | None = None,
        reference_images: list[dict] | None = None,
        reference_guidance: str | None = None,
        timeout: int = 120,
    ) -> bytes:
        """统一生图入口，返回图片 bytes"""
        if model_key == "mock" or self._s.is_mock_mode:
            return mock_image_bytes(prompt, size)

        cfg = self._s.get_image_config(model_key)
        if not cfg or not cfg.get("api_key"):
            logger.warning("image_key_missing", model=model_key)
            return mock_image_bytes(prompt, size)

        model_type = cfg.get("type", "")
        if model_type in ("doubao_image", "doubao"):
            return await self._call_jimeng(http_client, cfg, prompt, size, timeout)
        elif model_type in ("openai_compatible_image", "openai"):
            return await self._call_openai_image(
                http_client, cfg, prompt, size,
                reference_url=reference_url,
                reference_images=reference_images,
                reference_guidance=reference_guidance,
                timeout=timeout,
            )
        else:
            logger.error("unknown_image_model_type", model=model_key, type=model_type)
            return mock_image_bytes(prompt, size)

    async def call_image_model_with_fallback(
        self,
        http_client,
        prompt: str,
        size: str = "1024x1024",
        preferred_model: str | None = None,
        reference_url: str | None = None,
        reference_images: list[dict] | None = None,
        reference_guidance: str | None = None,
        timeout: int = 120,
    ) -> tuple[bytes, str]:
        """带自动降级的生图调用，返回 (image_bytes, model_used)"""
        available = [
            k if isinstance(k, str) else k.get("key", k)
            for k in self._s.list_available_image_models()
        ]

        if preferred_model and preferred_model in available:
            order = [preferred_model] + [m for m in available if m != preferred_model]
        else:
            order = available

        for model_key in order:
            try:
                img_bytes = await self.call_image_model(
                    http_client, model_key, prompt, size,
                    reference_url, reference_images, reference_guidance, timeout,
                )
                return img_bytes, model_key
            except Exception as e:
                logger.error(
                    "image_fallback",
                    failed_model=model_key,
                    error_type=type(e).__name__,
                    error=str(e),
                )
                continue

        logger.error("all_image_models_failed_using_mock", tried=order)
        return mock_image_bytes(prompt, size), "mock"

    # ── 图生图 ────────────────────────────────────────

    async def call_image_to_image(
        self,
        http_client,
        model_key: str,
        source_image_b64: str,
        prompt: str,
        mime: str = "image/png",
        timeout: int = 180,
    ) -> bytes | None:
        """基于参考图 + prompt 生成新图（图生图）"""
        if model_key == "mock" or self._s.is_mock_mode:
            return mock_image_bytes(prompt)

        cfg = self._s.get_image_config(model_key)
        if not cfg or not cfg.get("api_key"):
            return None

        data_url = f"data:{mime};base64,{source_image_b64}"
        messages = [
            {
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": data_url}},
                    {"type": "text", "text": prompt},
                ],
            }
        ]

        max_retries = self._s.MAX_RETRIES
        for attempt in range(max_retries):
            try:
                resp = await http_client.post(
                    f"{cfg['base_url']}/chat/completions",
                    headers={
                        "Authorization": f"Bearer {cfg['api_key']}",
                        "Content-Type": "application/json",
                    },
                    json={"model": cfg["model"], "messages": messages},
                    timeout=timeout,
                )
                resp.raise_for_status()
                data = resp.json()
                result = extract_image_from_openai_response(data)
                if result:
                    logger.info("img2img_success", model=model_key, attempt=attempt + 1)
                    return result
                logger.warning("img2img_no_image", model=model_key, attempt=attempt + 1)
            except Exception as e:
                logger.warning(
                    "img2img_retry",
                    model=model_key,
                    attempt=attempt + 1,
                    max=max_retries,
                    error=str(e),
                )
                if attempt < max_retries - 1:
                    await asyncio.sleep(self._s.RETRY_BASE_DELAY * (attempt + 1))

        logger.error("img2img_all_retries_failed", model=model_key)
        return None

    # ── 内部：即梦 Seedream ───────────────────────────

    async def _call_jimeng(
        self, http_client, cfg: dict, prompt: str, size: str, timeout: int
    ) -> bytes:
        seedream_size = SEEDREAM_SIZE_MAP.get(size, "2048x2048")
        headers = {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": cfg["model"],
            "prompt": prompt,
            "response_format": "url",
            "size": seedream_size,
            "sequential_image_generation": "disabled",
            "stream": False,
            "watermark": False,
        }

        logger.info("jimeng_request", model=cfg["model"], size=seedream_size)
        resp = await http_client.post(
            f"{cfg['base_url']}/images/generations",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()
        item = data["data"][0]

        if "url" in item:
            img_resp = await http_client.get(item["url"], timeout=60)
            img_resp.raise_for_status()
            logger.info("jimeng_success", size=seedream_size, bytes=len(img_resp.content))
            return img_resp.content
        elif "b64_json" in item:
            return base64.b64decode(item["b64_json"])
        raise ValueError("Jimeng 响应中无图片数据")

    # ── 内部：OpenAI 兼容生图（Gemini / NanoBanana）──

    async def _call_openai_image(
        self,
        http_client,
        cfg: dict,
        prompt: str,
        size: str,
        reference_url: str | None = None,
        reference_images: list[dict] | None = None,
        reference_guidance: str | None = None,
        timeout: int = 120,
    ) -> bytes:
        content_parts: list[dict] = []
        effective_refs = reference_images or []

        if not effective_refs and reference_url:
            effective_refs = [{"url": reference_url, "kind": "style", "strength": "medium"}]

        for ref in effective_refs[:3]:
            url = ref.get("url")
            if not url:
                continue
            content_parts.append({"type": "image_url", "image_url": {"url": url}})

        if effective_refs:
            guidance = reference_guidance or (
                "Use the provided images only as visual references for style, composition, "
                "materials, lighting, and mood. Create a brand-new original commercial image. "
                "Do not copy exact objects, text, layout, logos, or trademarks."
            )
            content_parts.append(
                {"type": "text", "text": f"{guidance}\n\nTarget size: {size}\n\nPrompt:\n{prompt}"}
            )
        else:
            content_parts.append({"type": "text", "text": prompt})

        headers = {
            "Authorization": f"Bearer {cfg['api_key']}",
            "Content-Type": "application/json",
        }
        payload = {
            "model": cfg["model"],
            "messages": [{"role": "user", "content": content_parts}],
            "max_tokens": 4096,
            "modalities": ["text", "image"],
        }

        logger.info(
            "openai_image_request",
            model=cfg["model"],
            base_url=cfg["base_url"],
            ref_count=len(effective_refs),
        )

        resp = await http_client.post(
            f"{cfg['base_url']}/chat/completions",
            json=payload,
            headers=headers,
            timeout=timeout,
        )
        resp.raise_for_status()
        data = resp.json()

        img_bytes = extract_image_from_openai_response(data)
        if img_bytes:
            return img_bytes

        logger.error("openai_image_no_image_in_response")
        raise ValueError("OpenAI 兼容接口响应中无图片数据")
