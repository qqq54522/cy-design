from __future__ import annotations

import contextlib
import logging
import os
import signal
import subprocess
import sys
from dataclasses import dataclass, field
from typing import Literal

from .config import settings
from .module_registry import MODULES as _REGISTRY_MODULES

logger = logging.getLogger("lingqiao.platform")

ServiceRole = Literal["backend", "frontend"]


@dataclass
class ServiceDef:
    key: str
    role: ServiceRole
    cwd: str
    port: int | None = None
    uvicorn_module: str | None = None


@dataclass
class RunningService:
    definition: ServiceDef
    process: subprocess.Popen
    pid: int


def _build_service_defs() -> list[ServiceDef]:
    """Derive SERVICE_DEFS from the module registry instead of hard-coding."""
    defs: list[ServiceDef] = []
    for m in _REGISTRY_MODULES:
        defs.append(ServiceDef(
            key=m.key,
            role="backend",
            cwd=m.backend.cwd,
            port=m.backend.port,
            uvicorn_module=m.backend.uvicorn_module,
        ))
        defs.append(ServiceDef(
            key=m.key,
            role="frontend",
            cwd=m.frontend.cwd,
        ))
    return defs


SERVICE_DEFS: list[ServiceDef] = _build_service_defs()


def _svc_id(key: str, role: ServiceRole) -> str:
    return f"{key}:{role}"


def _find_venv_python() -> str | None:
    """Locate the venv python executable relative to workspace root."""
    candidates = [
        settings.workspace_dir / "venv" / "Scripts" / "python.exe",
        settings.workspace_dir / "venv" / "bin" / "python",
        settings.workspace_dir / ".venv" / "Scripts" / "python.exe",
        settings.workspace_dir / ".venv" / "bin" / "python",
    ]
    for c in candidates:
        if c.exists():
            return str(c)
    return None


def _find_npm() -> str:
    return "npm.cmd" if sys.platform == "win32" else "npm"


def _popen_kwargs() -> dict:
    """Platform-specific Popen kwargs: suppress output, isolate process group."""
    kwargs: dict = {"stdout": subprocess.DEVNULL, "stderr": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    return kwargs


@dataclass
class ProcessManager:
    _running: dict[str, RunningService] = field(default_factory=dict)

    def _spawn_backend(self, svc: ServiceDef) -> subprocess.Popen:
        cwd = settings.workspace_dir / svc.cwd
        python = _find_venv_python() or sys.executable
        cmd = [
            python, "-m", "uvicorn",
            svc.uvicorn_module,
            "--host", "0.0.0.0",
            "--port", str(svc.port),
            "--reload",
        ]
        return subprocess.Popen(cmd, cwd=str(cwd), **_popen_kwargs())

    def _spawn_frontend(self, svc: ServiceDef) -> subprocess.Popen:
        cwd = settings.workspace_dir / svc.cwd
        npm = _find_npm()
        cmd = [npm, "run", "dev"]
        return subprocess.Popen(cmd, cwd=str(cwd), **_popen_kwargs())

    def _is_alive(self, sid: str) -> bool:
        rs = self._running.get(sid)
        if rs is None:
            return False
        return rs.process.poll() is None

    def start_service(self, svc: ServiceDef) -> RunningService:
        sid = _svc_id(svc.key, svc.role)
        if self._is_alive(sid):
            return self._running[sid]

        if sid in self._running:
            del self._running[sid]

        if svc.role == "backend":
            proc = self._spawn_backend(svc)
        else:
            proc = self._spawn_frontend(svc)

        rs = RunningService(definition=svc, process=proc, pid=proc.pid)
        self._running[sid] = rs
        logger.info("started %s  pid=%d", sid, proc.pid)
        return rs

    def stop_service(self, key: str, role: ServiceRole) -> bool:
        sid = _svc_id(key, role)
        rs = self._running.pop(sid, None)
        if rs is None:
            return False
        return self._kill(rs)

    def _kill(self, rs: RunningService) -> bool:
        if rs.process.poll() is not None:
            return True
        sid = _svc_id(rs.definition.key, rs.definition.role)
        try:
            if sys.platform == "win32":
                subprocess.run(
                    ["taskkill", "/T", "/F", "/PID", str(rs.pid)],
                    stdout=subprocess.DEVNULL,
                    stderr=subprocess.DEVNULL,
                )
            else:
                os.killpg(rs.process.pid, signal.SIGTERM)
            rs.process.wait(timeout=5)
        except Exception:
            with contextlib.suppress(Exception):
                rs.process.kill()
        logger.info("stopped %s  pid=%d", sid, rs.pid)
        return True

    def start_module(self, key: str) -> list[RunningService]:
        results = []
        for svc in SERVICE_DEFS:
            if svc.key == key:
                results.append(self.start_service(svc))
        return results

    def stop_module(self, key: str) -> int:
        stopped = 0
        for role in ("backend", "frontend"):
            if self.stop_service(key, role):
                stopped += 1
        return stopped

    def start_all(self) -> list[RunningService]:
        results = []
        for svc in SERVICE_DEFS:
            results.append(self.start_service(svc))
        return results

    def stop_all(self) -> int:
        stopped = 0
        for sid in list(self._running.keys()):
            rs = self._running.pop(sid, None)
            if rs and self._kill(rs):
                stopped += 1
        return stopped

    def get_module_status(self, key: str) -> dict:
        be_sid = _svc_id(key, "backend")
        fe_sid = _svc_id(key, "frontend")
        be_alive = self._is_alive(be_sid)
        fe_alive = self._is_alive(fe_sid)
        return {
            "key": key,
            "backend_running": be_alive,
            "frontend_running": fe_alive,
            "backend_pid": self._running[be_sid].pid if be_alive else None,
            "frontend_pid": self._running[fe_sid].pid if fe_alive else None,
        }

    def get_all_status(self) -> list[dict]:
        keys = sorted({svc.key for svc in SERVICE_DEFS})
        return [self.get_module_status(k) for k in keys]

    def shutdown(self) -> None:
        """Stop all managed processes — called on platform API shutdown."""
        self.stop_all()


process_manager = ProcessManager()
