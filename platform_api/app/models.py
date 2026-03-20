from pydantic import BaseModel, Field


# ---------------------------------------------------------------------------
# Sub-models for enriched module info
# ---------------------------------------------------------------------------

class ModuleNavItem(BaseModel):
    path: str
    label: str


class ModuleFrontendInfo(BaseModel):
    port: int
    origin: str
    cwd: str
    start_command: str


class ModuleBackendInfo(BaseModel):
    port: int
    origin: str
    cwd: str
    health_path: str
    start_command: str
    uvicorn_module: str


class ModuleIndexingInfo(BaseModel):
    data_dirs: list[str] = Field(default_factory=list)
    retention_days: int = 30


class ModuleEmbedInfo(BaseModel):
    enabled: bool = True


# ---------------------------------------------------------------------------
# Core module model — enriched with nav / frontend / backend details
# ---------------------------------------------------------------------------

class ModuleInfo(BaseModel):
    key: str
    name: str
    description: str
    route: str
    default_path: str = "/"
    nav: list[ModuleNavItem] = Field(default_factory=list)

    # Computed / convenience URLs (kept for backward compat with existing consumers)
    frontend_url: str
    backend_url: str
    health_url: str
    status: str = "unknown"

    # Structured sub-configs
    frontend: ModuleFrontendInfo | None = None
    backend: ModuleBackendInfo | None = None
    indexing: ModuleIndexingInfo | None = None
    embed: ModuleEmbedInfo | None = None

    # Legacy flat fields (still populated for backward compat)
    data_dirs: list[str] = Field(default_factory=list)
    retention_days: int | None = None


# ---------------------------------------------------------------------------
# Other models (unchanged)
# ---------------------------------------------------------------------------

class ProjectIndexItem(BaseModel):
    id: str
    module: str
    module_name: str
    title: str
    subtitle: str | None = None
    status: str
    created_at: str | None = None
    updated_at: str | None = None
    detail_url: str
    source_path: str
    metrics: dict[str, int] = Field(default_factory=dict)


class DashboardSummary(BaseModel):
    total_projects: int
    module_counts: dict[str, int]
    running_services: int
    recent_projects: list[ProjectIndexItem]


class ServiceStatus(BaseModel):
    key: str
    backend_running: bool = False
    frontend_running: bool = False
    backend_pid: int | None = None
    frontend_pid: int | None = None


class SettingsPayload(BaseModel):
    shell_url: str
    platform_api_url: str
    modules: list[ModuleInfo]
