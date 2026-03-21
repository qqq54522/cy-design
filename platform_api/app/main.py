import logging
from collections import Counter
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from .config import settings
from .indexer import MODULES, build_project_index
from .models import DashboardSummary, ModuleInfo, ServiceStatus, SettingsPayload
from .module_registry import MODULE_KEYS, PLATFORM
from .process_manager import process_manager

logger = logging.getLogger("lingqiao.platform")


def _configure_logging() -> None:
    if logger.handlers:
        return

    settings.logs_dir.mkdir(parents=True, exist_ok=True)
    logfile = settings.logs_dir / "platform.log"
    handler = logging.FileHandler(logfile, encoding="utf-8")
    formatter = logging.Formatter("%(asctime)s %(levelname)s %(message)s")
    handler.setFormatter(formatter)
    logger.setLevel(logging.INFO)
    logger.addHandler(handler)


@asynccontextmanager
async def lifespan(app: FastAPI):
    _configure_logging()
    app.state.http_client = httpx.AsyncClient(timeout=5)
    logger.info("platform_api_started")
    yield
    process_manager.shutdown()
    await app.state.http_client.aclose()


app = FastAPI(
    title="Lingqiao Platform API",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        PLATFORM.shell_origin,
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def log_requests(request, call_next):
    response = await call_next(request)
    logger.info("%s %s -> %s", request.method, request.url.path, response.status_code)
    return response


@app.exception_handler(Exception)
async def handle_unexpected_error(_request, exc: Exception):
    logger.exception("platform_api_error: %s", exc)
    return JSONResponse(
        status_code=500,
        content={"error": {"code": "INTERNAL_ERROR", "message": "平台服务异常"}},
    )


async def _with_statuses(client: httpx.AsyncClient) -> list[ModuleInfo]:
    modules: list[ModuleInfo] = []
    for module in MODULES:
        try:
            response = await client.get(module.health_url)
            status = "online" if response.is_success else "degraded"
        except Exception:
            status = "offline"
        modules.append(module.model_copy(update={"status": status}))
    return modules


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/api/platform/modules")
async def get_modules():
    modules = await _with_statuses(app.state.http_client)
    return {"data": modules}


@app.get("/api/platform/projects")
async def get_projects():
    projects = build_project_index(settings.workspace_dir)
    return {"data": {"projects": projects, "total": len(projects)}}


@app.get("/api/platform/summary", response_model=DashboardSummary)
async def get_summary():
    client: httpx.AsyncClient = app.state.http_client
    modules = await _with_statuses(client)
    projects = build_project_index(settings.workspace_dir)
    module_counts = Counter(project.module for project in projects)
    return DashboardSummary(
        total_projects=len(projects),
        module_counts=dict(module_counts),
        running_services=sum(1 for module in modules if module.status == "online"),
        recent_projects=projects[:8],
    )


@app.get("/api/platform/settings", response_model=SettingsPayload)
async def get_settings():
    modules = await _with_statuses(app.state.http_client)
    return SettingsPayload(
        shell_url=PLATFORM.shell_origin,
        platform_api_url=PLATFORM.origin,
        modules=modules,
    )


@app.get("/api/platform/logs/recent")
async def get_recent_logs():
    logfile = settings.logs_dir / "platform.log"
    if not logfile.exists():
        return {"data": {"lines": []}}

    lines = logfile.read_text(encoding="utf-8").splitlines()[-100:]
    return {"data": {"lines": lines}}


# --------------- Service management endpoints ---------------


@app.get("/api/platform/services/status", response_model=list[ServiceStatus])
async def get_service_status():
    return [ServiceStatus(**s) for s in process_manager.get_all_status()]


@app.post("/api/platform/services/start-all")
async def start_all_services():
    results = process_manager.start_all()
    logger.info("start_all: launched %d services", len(results))
    return {"message": f"已启动 {len(results)} 个服务", "count": len(results)}


@app.post("/api/platform/services/stop-all")
async def stop_all_services():
    stopped = process_manager.stop_all()
    logger.info("stop_all: stopped %d services", stopped)
    return {"message": f"已停止 {stopped} 个服务", "count": stopped}


@app.post("/api/platform/services/{key}/start")
async def start_module_services(key: str):
    if key not in MODULE_KEYS:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"code": "MODULE_NOT_FOUND", "message": f"模块 {key} 不存在"}
            },
        )
    results = process_manager.start_module(key)
    logger.info("start_module %s: launched %d services", key, len(results))
    return {"message": f"已启动 {key} 模块", "count": len(results)}


@app.post("/api/platform/services/{key}/stop")
async def stop_module_services(key: str):
    if key not in MODULE_KEYS:
        return JSONResponse(
            status_code=404,
            content={
                "error": {"code": "MODULE_NOT_FOUND", "message": f"模块 {key} 不存在"}
            },
        )
    stopped = process_manager.stop_module(key)
    logger.info("stop_module %s: stopped %d services", key, stopped)
    return {"message": f"已停止 {key} 模块", "count": stopped}
