"""Single-source module registry.

Reads ``config/modules.json`` once at import time and exposes typed helpers
so that every part of platform_api can reference modules without hard-coding.
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

# ---------------------------------------------------------------------------
# Data classes – intentionally plain (not Pydantic) so the registry stays
# import-lightweight and decoupled from the API response models.
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class NavItem:
    path: str
    label: str


@dataclass(frozen=True)
class FrontendInfo:
    port: int
    origin: str
    cwd: str
    start_command: str


@dataclass(frozen=True)
class BackendInfo:
    port: int
    origin: str
    cwd: str
    health_path: str
    start_command: str
    uvicorn_module: str


@dataclass(frozen=True)
class IndexingInfo:
    data_dirs: list[str] = field(default_factory=list)
    retention_days: int = 30


@dataclass(frozen=True)
class EmbedInfo:
    enabled: bool = True


@dataclass(frozen=True)
class ModuleEntry:
    key: str
    name: str
    description: str
    route: str
    default_path: str
    nav: list[NavItem]
    frontend: FrontendInfo
    backend: BackendInfo
    indexing: IndexingInfo
    embed: EmbedInfo


@dataclass(frozen=True)
class PlatformInfo:
    port: int
    origin: str
    shell_port: int
    shell_origin: str


# ---------------------------------------------------------------------------
# Loader
# ---------------------------------------------------------------------------


def _config_path() -> Path:
    """Return the absolute path to ``config/modules.json``."""
    return Path(__file__).resolve().parent.parent.parent / "config" / "modules.json"


def _parse_nav(raw: list[dict[str, Any]]) -> list[NavItem]:
    return [NavItem(path=n["path"], label=n["label"]) for n in raw]


def _parse_frontend(raw: dict[str, Any]) -> FrontendInfo:
    return FrontendInfo(
        port=raw["port"],
        origin=raw["origin"],
        cwd=raw["cwd"],
        start_command=raw["startCommand"],
    )


def _parse_backend(raw: dict[str, Any]) -> BackendInfo:
    return BackendInfo(
        port=raw["port"],
        origin=raw["origin"],
        cwd=raw["cwd"],
        health_path=raw["healthPath"],
        start_command=raw["startCommand"],
        uvicorn_module=raw["uvicornModule"],
    )


def _parse_indexing(raw: dict[str, Any]) -> IndexingInfo:
    return IndexingInfo(
        data_dirs=raw.get("dataDirs", []),
        retention_days=raw.get("retentionDays", 30),
    )


def _parse_embed(raw: dict[str, Any]) -> EmbedInfo:
    return EmbedInfo(enabled=raw.get("enabled", True))


def _parse_module(raw: dict[str, Any]) -> ModuleEntry:
    return ModuleEntry(
        key=raw["key"],
        name=raw["name"],
        description=raw["description"],
        route=raw["route"],
        default_path=raw["defaultPath"],
        nav=_parse_nav(raw.get("nav", [])),
        frontend=_parse_frontend(raw["frontend"]),
        backend=_parse_backend(raw["backend"]),
        indexing=_parse_indexing(raw.get("indexing", {})),
        embed=_parse_embed(raw.get("embed", {})),
    )


def _parse_platform(raw: dict[str, Any]) -> PlatformInfo:
    return PlatformInfo(
        port=raw["port"],
        origin=raw["origin"],
        shell_port=raw["shellPort"],
        shell_origin=raw["shellOrigin"],
    )


def load_registry(path: Path | None = None) -> tuple[list[ModuleEntry], PlatformInfo]:
    """Read and parse the module registry JSON.  Returns (modules, platform)."""
    p = path or _config_path()
    data = json.loads(p.read_text(encoding="utf-8"))
    modules = [_parse_module(m) for m in data["modules"]]
    platform = _parse_platform(data["platform"])
    return modules, platform


# ---------------------------------------------------------------------------
# Module-level singletons — importable from anywhere in platform_api
# ---------------------------------------------------------------------------

MODULES, PLATFORM = load_registry()

MODULE_KEYS: frozenset[str] = frozenset(m.key for m in MODULES)

_BY_KEY: dict[str, ModuleEntry] = {m.key: m for m in MODULES}
_BY_ROUTE: dict[str, ModuleEntry] = {m.route: m for m in MODULES}


def get_module(key: str) -> ModuleEntry | None:
    return _BY_KEY.get(key)


def get_module_by_route(route: str) -> ModuleEntry | None:
    return _BY_ROUTE.get(route)
