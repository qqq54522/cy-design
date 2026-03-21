import json
from pathlib import Path

from .models import (
    ModuleBackendInfo,
    ModuleEmbedInfo,
    ModuleFrontendInfo,
    ModuleIndexingInfo,
    ModuleInfo,
    ModuleNavItem,
    ProjectIndexItem,
)
from .module_registry import MODULES as _REGISTRY_MODULES

# ---------------------------------------------------------------------------
# Build the Pydantic ModuleInfo list from the single-source registry
# ---------------------------------------------------------------------------


def _to_module_info(entry) -> ModuleInfo:
    """Convert a registry ModuleEntry dataclass into a Pydantic ModuleInfo."""
    return ModuleInfo(
        key=entry.key,
        name=entry.name,
        description=entry.description,
        route=entry.route,
        default_path=entry.default_path,
        nav=[ModuleNavItem(path=n.path, label=n.label) for n in entry.nav],
        frontend_url=entry.frontend.origin,
        backend_url=entry.backend.origin,
        health_url=f"{entry.backend.origin}{entry.backend.health_path}",
        frontend=ModuleFrontendInfo(
            port=entry.frontend.port,
            origin=entry.frontend.origin,
            cwd=entry.frontend.cwd,
            start_command=entry.frontend.start_command,
        ),
        backend=ModuleBackendInfo(
            port=entry.backend.port,
            origin=entry.backend.origin,
            cwd=entry.backend.cwd,
            health_path=entry.backend.health_path,
            start_command=entry.backend.start_command,
            uvicorn_module=entry.backend.uvicorn_module,
        ),
        indexing=ModuleIndexingInfo(
            data_dirs=list(entry.indexing.data_dirs),
            retention_days=entry.indexing.retention_days,
        ),
        embed=ModuleEmbedInfo(enabled=entry.embed.enabled),
        data_dirs=list(entry.indexing.data_dirs),
        retention_days=entry.indexing.retention_days,
    )


MODULES: list[ModuleInfo] = [_to_module_info(e) for e in _REGISTRY_MODULES]


def _read_json(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except Exception:
        return None


def _content_status_label(raw: str) -> str:
    mapping = {
        "draft": "草稿",
        "analyzing": "分析中",
        "copywriting_done": "文案完成",
        "generating_visual": "生成视觉中",
        "completed": "已完成",
    }
    return mapping.get(raw, raw or "未知")


def _kv_detail_url(module: ModuleInfo, project: dict) -> str:
    project_id = project.get("id", "")
    status = project.get("status", "")
    if status in {"completed", "editing"}:
        return f"{module.frontend_url.rstrip('/')}/editor/{project_id}"
    if status in {"generating", "ready"}:
        return f"{module.frontend_url.rstrip('/')}/generate/{project_id}"
    return f"{module.frontend_url.rstrip('/')}/strategy/{project_id}"


def _emoji_detail_url(module: ModuleInfo, task: dict) -> str:
    task_id = task.get("id", "")
    status = task.get("status", "")
    base = module.frontend_url.rstrip("/")
    if status == "completed":
        return f"{base}/generate/{task_id}"
    if status in {"analyzing", "generating"}:
        return f"{base}/analysis/{task_id}"
    return f"{base}/history"


def index_content_projects(
    workspace_dir: Path, module: ModuleInfo
) -> list[ProjectIndexItem]:
    base_dir = workspace_dir / "素材抓取" / "content-marketing" / "data" / "projects"
    items: list[ProjectIndexItem] = []
    if not base_dir.exists():
        return items

    for project_dir in base_dir.iterdir():
        data = _read_json(project_dir / "project.json")
        if not data:
            continue
        items.append(
            ProjectIndexItem(
                id=data.get("id", project_dir.name),
                module=module.key,
                module_name=module.name,
                title=data.get("topic") or f"素材任务 {project_dir.name}",
                subtitle="、".join(data.get("platforms", []) or []) or None,
                status=_content_status_label(data.get("status", "")),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                detail_url=f"{module.frontend_url.rstrip('/')}/history",
                source_path=str(project_dir / "project.json"),
                metrics={"copies": int(data.get("copies_count", 0))},
            )
        )
    return items


def index_kv_projects(
    workspace_dir: Path, module: ModuleInfo
) -> list[ProjectIndexItem]:
    base_dir = workspace_dir / "KV生成" / "data" / "projects"
    items: list[ProjectIndexItem] = []
    if not base_dir.exists():
        return items

    for project_dir in base_dir.iterdir():
        data = _read_json(project_dir / "project.json")
        if not data:
            continue
        input_data = data.get("input", {})
        items.append(
            ProjectIndexItem(
                id=data.get("id", project_dir.name),
                module=module.key,
                module_name=module.name,
                title=input_data.get("name") or f"KV 项目 {project_dir.name}",
                subtitle=input_data.get("eventType") or None,
                status=data.get("status", "unknown"),
                created_at=data.get("createdAt"),
                updated_at=data.get("updatedAt"),
                detail_url=_kv_detail_url(module, data),
                source_path=str(project_dir / "project.json"),
                metrics={
                    "generations": len(data.get("generations", [])),
                    "materials": len(data.get("materials", [])),
                },
            )
        )
    return items


def index_emoji_tasks(
    workspace_dir: Path, module: ModuleInfo
) -> list[ProjectIndexItem]:
    base_dir = workspace_dir / "表情包" / "data" / "uploads"
    items: list[ProjectIndexItem] = []
    if not base_dir.exists():
        return items

    for task_dir in base_dir.iterdir():
        data = _read_json(task_dir / "task.json")
        if not data:
            continue
        items.append(
            ProjectIndexItem(
                id=data.get("id", task_dir.name),
                module=module.key,
                module_name=module.name,
                title=data.get("character_desc") or f"表情任务 {task_dir.name}",
                subtitle=f"{len(data.get('reference_images', []))} 张参考图",
                status=data.get("status", "unknown"),
                created_at=data.get("created_at"),
                updated_at=data.get("updated_at"),
                detail_url=_emoji_detail_url(module, data),
                source_path=str(task_dir / "task.json"),
                metrics={
                    "references": len(data.get("reference_images", [])),
                    "results": len(data.get("generation_results", [])),
                },
            )
        )
    return items


def build_project_index(workspace_dir: Path) -> list[ProjectIndexItem]:
    items: list[ProjectIndexItem] = []
    module_by_key = {module.key: module for module in MODULES}
    items.extend(index_content_projects(workspace_dir, module_by_key["content"]))
    items.extend(index_kv_projects(workspace_dir, module_by_key["kv"]))
    items.extend(index_emoji_tasks(workspace_dir, module_by_key["emoji"]))
    items.sort(key=lambda item: item.updated_at or item.created_at or "", reverse=True)
    return items
