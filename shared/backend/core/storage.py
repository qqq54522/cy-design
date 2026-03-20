"""存储工具函数与基类 — 路径校验、JSON 异步读写、项目/任务存储基类。

各模块可直接使用工具函数，或继承 BaseProjectStorage 获得项目 CRUD 能力。
"""

from __future__ import annotations

import asyncio
import json
import re
import shutil
import uuid
from collections.abc import Callable
from pathlib import Path

import aiofiles
import structlog

logger = structlog.get_logger()

_SAFE_ID_RE = re.compile(r"^[a-zA-Z0-9_-]+$")


# ── 工具函数 ──────────────────────────────────────────────


def validate_id(value: str, label: str = "ID") -> None:
    """校验 ID 格式，拒绝非法字符。"""
    if not value or not _SAFE_ID_RE.match(value):
        raise ValueError(f"非法的{label}: {value}")


def validate_path_component(value: str, label: str = "路径") -> None:
    """拒绝路径遍历攻击。"""
    if not value or ".." in value or "/" in value or "\\" in value:
        raise ValueError(f"非法的{label}: {value}")


def new_id(length: int = 12) -> str:
    """生成短 UUID（默认 12 字符 hex）"""
    return uuid.uuid4().hex[:length]


async def read_json(path: Path) -> dict:
    """异步读取 JSON 文件并返回 dict。"""
    async with aiofiles.open(path, encoding="utf-8") as f:
        content = await f.read()
    return json.loads(content)


async def write_json(path: Path, data: dict, *, ensure_dir: bool = True) -> None:
    """异步写入 JSON 文件，默认自动创建父目录。"""
    if ensure_dir:
        path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    logger.info("json_written", path=str(path))


async def write_json_atomic(path: Path, data: dict, *, ensure_dir: bool = True) -> None:
    """原子写入 JSON（先写 .tmp 再 replace），防止并发写入产生空文件。"""
    if ensure_dir:
        path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(".json.tmp")
    async with aiofiles.open(tmp, "w", encoding="utf-8") as f:
        await f.write(json.dumps(data, ensure_ascii=False, indent=2, default=str))
    tmp.replace(path)
    logger.info("json_written_atomic", path=str(path))


async def save_binary(path: Path, data: bytes, *, ensure_dir: bool = True) -> None:
    """异步保存二进制文件。"""
    if ensure_dir:
        path.parent.mkdir(parents=True, exist_ok=True)
    async with aiofiles.open(path, "wb") as f:
        await f.write(data)
    logger.info("binary_saved", path=str(path), size=len(data))


# ── 项目存储基类 ──────────────────────────────────────────


class BaseProjectStorage:
    """项目/任务存储基类，提供带锁的 CRUD 操作。

    子类只需设置 base_dir 和 meta_filename，即可获得：
    - save_meta / load_meta / update_meta（带项目级锁）
    - list_all / delete
    - save_file（二进制文件保存）
    - safe_subpath（路径遍历防护）
    """

    meta_filename: str = "project.json"

    def __init__(self, base_dir: Path):
        self.base_dir = base_dir
        self._locks: dict[str, asyncio.Lock] = {}

    def _get_lock(self, entity_id: str) -> asyncio.Lock:
        if entity_id not in self._locks:
            self._locks[entity_id] = asyncio.Lock()
        return self._locks[entity_id]

    def entity_dir(self, entity_id: str) -> Path:
        validate_id(entity_id, "entity_id")
        return self.base_dir / entity_id

    def meta_path(self, entity_id: str) -> Path:
        return self.entity_dir(entity_id) / self.meta_filename

    def safe_subpath(self, entity_id: str, *parts: str) -> Path:
        """构造安全的子路径，防止路径遍历。"""
        for p in parts:
            validate_path_component(p)
        target = self.entity_dir(entity_id).joinpath(*parts).resolve()
        if not str(target).startswith(str(self.entity_dir(entity_id).resolve())):
            raise ValueError(f"路径遍历攻击: {parts}")
        return target

    async def save_meta(self, entity_id: str, data: dict) -> None:
        async with self._get_lock(entity_id):
            path = self.meta_path(entity_id)
            await write_json(path, data)

    async def load_meta(self, entity_id: str) -> dict | None:
        path = self.meta_path(entity_id)
        if not path.exists():
            return None
        async with self._get_lock(entity_id):
            return await read_json(path)

    async def update_meta(
        self, entity_id: str, updater: Callable[[dict], dict]
    ) -> dict:
        """读-改-写（带锁），updater 接收当前 dict 返回新 dict。"""
        async with self._get_lock(entity_id):
            path = self.meta_path(entity_id)
            if not path.exists():
                raise FileNotFoundError(f"元数据不存在: {entity_id}")
            current = await read_json(path)
            updated = updater(current)
            await write_json(path, updated)
            return updated

    async def list_all(self, limit: int = 50) -> list[dict]:
        """列出所有实体的元数据，按修改时间倒序。"""
        if not self.base_dir.exists():
            return []
        items = []
        for d in sorted(
            self.base_dir.iterdir(), key=lambda p: p.stat().st_mtime, reverse=True
        ):
            if not d.is_dir():
                continue
            meta_file = d / self.meta_filename
            if meta_file.exists():
                try:
                    data = await read_json(meta_file)
                    items.append(data)
                except Exception:
                    continue
            if len(items) >= limit:
                break
        return items

    async def delete(self, entity_id: str) -> None:
        validate_id(entity_id, "entity_id")
        target = self.entity_dir(entity_id)
        if target.exists():
            await asyncio.to_thread(shutil.rmtree, target)
            self._locks.pop(entity_id, None)
            logger.info("entity_deleted", id=entity_id)

    async def save_file(
        self, entity_id: str, subdir: str, filename: str, data: bytes
    ) -> str:
        """保存二进制文件到实体子目录，返回相对路径。"""
        validate_path_component(subdir)
        validate_path_component(filename)
        path = self.entity_dir(entity_id) / subdir / filename
        await save_binary(path, data)
        return f"{subdir}/{filename}"
