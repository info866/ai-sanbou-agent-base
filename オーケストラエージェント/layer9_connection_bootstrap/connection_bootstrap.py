#!/usr/bin/env python3
"""
Layer 9: Connection/Auth/Permission Bootstrap (接続・認証・権限自動化層)
=====================================================================
Auto-prepares MCP, API, GitHub, tools into working state.
Uses Layers 7+8 to verify connections with quality gates.

goal: Auto-prepare all required connections before execution
inputs: Capability list from plan + available config + environment
core_logic: Requirement extraction → health check → auto-setup → verify
activation_rule: Before every ExecutionPlan execution, verify prerequisites
verification: All required connections healthy, gaps detected early
handoff: Verified connection state → Layer 10 (watch targets derived from connections)
"""

from __future__ import annotations

import os
import json
import shutil
import subprocess
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from pathlib import Path


ConnectionType = Literal["mcp", "api", "github", "cli", "env_var", "python_module"]
ConnectionStatus = Literal["healthy", "degraded", "missing", "error"]


@dataclass
class ConnectionRequirement:
    """A single connection needed for execution."""
    conn_type: ConnectionType
    name: str
    target: str         # what to check (server name, env var, CLI tool)
    required_by: str    # capability ID or step name
    optional: bool = False


@dataclass
class ConnectionHealth:
    """Health check result for a single connection."""
    requirement: ConnectionRequirement
    status: ConnectionStatus
    details: str = ""
    setup_hint: str = ""  # what to do if missing

    @property
    def is_ok(self) -> bool:
        return self.status in ("healthy", "degraded")

    def to_dict(self) -> dict:
        return {
            "type": self.requirement.conn_type,
            "name": self.requirement.name,
            "target": self.requirement.target,
            "status": self.status,
            "is_ok": self.is_ok,
            "details": self.details,
            "setup_hint": self.setup_hint,
            "required_by": self.requirement.required_by,
            "optional": self.requirement.optional,
        }


@dataclass
class BootstrapReport:
    """Full connection bootstrap report."""
    total: int = 0
    healthy: int = 0
    degraded: int = 0
    missing: int = 0
    errors: int = 0
    results: list[ConnectionHealth] = field(default_factory=list)
    blocking_gaps: list[str] = field(default_factory=list)

    @property
    def ready(self) -> bool:
        return len(self.blocking_gaps) == 0

    def to_dict(self) -> dict:
        return {
            "ready": self.ready,
            "total": self.total,
            "healthy": self.healthy,
            "degraded": self.degraded,
            "missing": self.missing,
            "errors": self.errors,
            "blocking_gaps": self.blocking_gaps,
            "results": [r.to_dict() for r in self.results],
        }


# ── Capability → Connection Requirements ────────────────────────────

CAPABILITY_CONNECTIONS: dict[str, list[dict]] = {
    "F-002": [
        {"type": "mcp", "name": "MCP Protocol", "target": "mcp_server",
         "hint": "Ensure MCP server is running and configured in .claude/settings.json"},
    ],
    "F-003": [
        {"type": "cli", "name": "Claude CLI", "target": "claude",
         "hint": "Claude Code CLI must be available for subagent dispatch"},
    ],
    "F-004": [
        {"type": "env_var", "name": "Hooks Config", "target": ".claude/settings.json",
         "hint": "Configure hooks in .claude/settings.json"},
    ],
    "F-009": [
        {"type": "python_module", "name": "anthropic SDK", "target": "anthropic",
         "hint": "pip install anthropic"},
    ],
    "F-010": [
        {"type": "cli", "name": "GitHub CLI", "target": "gh",
         "hint": "brew install gh && gh auth login"},
        {"type": "github", "name": "GitHub Auth", "target": "gh auth status",
         "hint": "Run 'gh auth login' to authenticate"},
    ],
    "F-014": [
        {"type": "cli", "name": "GitHub CLI", "target": "gh",
         "hint": "brew install gh"},
    ],
    "F-015": [
        {"type": "python_module", "name": "anthropic SDK", "target": "anthropic",
         "hint": "pip install anthropic"},
        {"type": "cli", "name": "Python 3", "target": "python3",
         "hint": "Install Python 3.10+"},
    ],
    "F-019": [
        {"type": "mcp", "name": "MCP Servers", "target": "mcp_server",
         "hint": "Configure MCP servers in settings"},
    ],
    "F-025": [
        {"type": "cli", "name": "Claude CLI", "target": "claude",
         "hint": "Memory tool requires Claude Code CLI"},
    ],
    "F-032": [
        {"type": "cli", "name": "promptfoo", "target": "promptfoo",
         "hint": "npm install -g promptfoo", "optional": True},
    ],
}

# Standard connections always checked
STANDARD_CONNECTIONS = [
    {"type": "cli", "name": "Git", "target": "git", "hint": "Install git"},
    {"type": "cli", "name": "Python 3", "target": "python3", "hint": "Install Python 3"},
]


class ConnectionBootstrap:
    """Auto-prepares all required connections before execution.

    Usage:
        bootstrap = ConnectionBootstrap()
        requirements = bootstrap.extract_requirements(plan)
        report = bootstrap.check_all(requirements)
        if not report.ready:
            # report.blocking_gaps tells what's missing
    """

    def __init__(self, project_root: Path | None = None):
        self.project_root = project_root or Path.cwd()

    def extract_requirements(self, plan) -> list[ConnectionRequirement]:
        """Extract connection requirements from an ExecutionPlan."""
        requirements = []
        seen = set()

        # Standard connections
        for conn in STANDARD_CONNECTIONS:
            key = f"{conn['type']}:{conn['target']}"
            if key not in seen:
                requirements.append(ConnectionRequirement(
                    conn_type=conn["type"],
                    name=conn["name"],
                    target=conn["target"],
                    required_by="standard",
                ))
                seen.add(key)

        # Capability-driven connections
        for action in plan.actions:
            cap_id = action.capability_id
            if cap_id in CAPABILITY_CONNECTIONS:
                for conn in CAPABILITY_CONNECTIONS[cap_id]:
                    key = f"{conn['type']}:{conn['target']}"
                    if key not in seen:
                        requirements.append(ConnectionRequirement(
                            conn_type=conn["type"],
                            name=conn["name"],
                            target=conn["target"],
                            required_by=cap_id,
                            optional=conn.get("optional", False),
                        ))
                        seen.add(key)

        return requirements

    def check_single(self, req: ConnectionRequirement) -> ConnectionHealth:
        """Health-check a single connection requirement."""
        checkers = {
            "cli": self._check_cli,
            "python_module": self._check_python_module,
            "env_var": self._check_env_or_file,
            "github": self._check_github,
            "mcp": self._check_mcp,
            "api": self._check_api,
        }
        checker = checkers.get(req.conn_type, self._check_unknown)
        return checker(req)

    def check_all(self, requirements: list[ConnectionRequirement]) -> BootstrapReport:
        """Check all requirements and produce bootstrap report."""
        report = BootstrapReport()

        for req in requirements:
            health = self.check_single(req)
            report.results.append(health)
            report.total += 1

            if health.status == "healthy":
                report.healthy += 1
            elif health.status == "degraded":
                report.degraded += 1
            elif health.status == "missing":
                report.missing += 1
                if not req.optional:
                    report.blocking_gaps.append(
                        f"{req.name} ({req.conn_type}): {health.setup_hint}"
                    )
            else:
                report.errors += 1
                if not req.optional:
                    report.blocking_gaps.append(
                        f"{req.name} ({req.conn_type}): {health.details}"
                    )

        return report

    # ── Individual Checkers ──────────────────────────────────────────

    def _check_cli(self, req: ConnectionRequirement) -> ConnectionHealth:
        hint = CAPABILITY_CONNECTIONS.get(req.required_by, [{}])
        hint_str = next((c.get("hint", "") for c in hint if c.get("target") == req.target), "")
        if shutil.which(req.target):
            return ConnectionHealth(req, "healthy", f"{req.target} found in PATH")
        return ConnectionHealth(req, "missing", f"{req.target} not in PATH", hint_str)

    def _check_python_module(self, req: ConnectionRequirement) -> ConnectionHealth:
        try:
            __import__(req.target)
            return ConnectionHealth(req, "healthy", f"Module '{req.target}' importable")
        except ImportError:
            return ConnectionHealth(req, "missing",
                                    f"Module '{req.target}' not found",
                                    f"pip install {req.target}")

    def _check_env_or_file(self, req: ConnectionRequirement) -> ConnectionHealth:
        # Check as file path first
        path = self.project_root / req.target
        if path.exists():
            return ConnectionHealth(req, "healthy", f"File '{req.target}' exists")
        # Check as env var
        if os.environ.get(req.target):
            return ConnectionHealth(req, "healthy", f"Env var '{req.target}' set")
        hint = next(
            (c.get("hint", "") for conns in CAPABILITY_CONNECTIONS.values()
             for c in conns if c.get("target") == req.target),
            f"Set env var or create file: {req.target}",
        )
        return ConnectionHealth(req, "missing", f"'{req.target}' not found", hint)

    def _check_github(self, req: ConnectionRequirement) -> ConnectionHealth:
        if not shutil.which("gh"):
            return ConnectionHealth(req, "missing", "gh CLI not installed",
                                    "brew install gh && gh auth login")
        try:
            r = subprocess.run(["gh", "auth", "status"],
                               capture_output=True, text=True, timeout=10)
            if r.returncode == 0:
                return ConnectionHealth(req, "healthy", "GitHub authenticated")
            return ConnectionHealth(req, "degraded", "gh installed but not authenticated",
                                    "Run: gh auth login")
        except (subprocess.TimeoutExpired, FileNotFoundError):
            return ConnectionHealth(req, "error", "gh auth check failed")

    def _check_mcp(self, req: ConnectionRequirement) -> ConnectionHealth:
        settings_path = self.project_root / ".claude" / "settings.json"
        if settings_path.exists():
            try:
                data = json.loads(settings_path.read_text())
                mcp_servers = data.get("mcpServers", {})
                if mcp_servers:
                    return ConnectionHealth(req, "healthy",
                                            f"{len(mcp_servers)} MCP server(s) configured")
                return ConnectionHealth(req, "degraded",
                                        "settings.json exists but no MCP servers configured",
                                        "Add MCP servers to .claude/settings.json")
            except json.JSONDecodeError:
                return ConnectionHealth(req, "error", "settings.json is invalid JSON")
        return ConnectionHealth(req, "degraded",
                                "No .claude/settings.json found",
                                "Create .claude/settings.json with MCP server config")

    def _check_api(self, req: ConnectionRequirement) -> ConnectionHealth:
        api_key = os.environ.get("ANTHROPIC_API_KEY", "")
        if api_key:
            return ConnectionHealth(req, "healthy", "ANTHROPIC_API_KEY set")
        return ConnectionHealth(req, "missing", "ANTHROPIC_API_KEY not set",
                                "export ANTHROPIC_API_KEY=sk-...")

    def _check_unknown(self, req: ConnectionRequirement) -> ConnectionHealth:
        return ConnectionHealth(req, "degraded",
                                f"No checker for type '{req.conn_type}'")

    # ── Safe Auto-Preparation ────────────────────────────────────────

    def prepare(self, requirements: list[ConnectionRequirement]) -> PrepareReport:
        """Check all, then auto-prepare SAFE missing connections.

        Safety rules:
          - NEVER auto-install paid APIs or auth-gated services
          - NEVER auto-connect paid MCPs
          - Only auto-install free Python packages via pip
          - Only auto-create local config files
          - Skip anything requiring interactive login
        """
        check_report = self.check_all(requirements)
        prep = PrepareReport(check_report=check_report)

        for health in check_report.results:
            if health.is_ok:
                continue  # already working

            req = health.requirement
            action = self._try_prepare(req, health)
            prep.actions_taken.append(action)
            if action["status"] == "fixed":
                prep.fixed += 1
            elif action["status"] == "skipped_paid":
                prep.skipped_paid += 1
            elif action["status"] == "skipped_interactive":
                prep.skipped_interactive += 1
            else:
                prep.could_not_fix += 1

        # Re-check after preparation
        if prep.fixed > 0:
            prep.recheck_report = self.check_all(requirements)

        return prep

    def _try_prepare(self, req: ConnectionRequirement, health: ConnectionHealth) -> dict:
        """Attempt safe auto-preparation for a single missing connection."""
        action = {
            "name": req.name, "type": req.conn_type,
            "target": req.target, "status": "no_action",
            "detail": "",
        }

        # SAFETY: Never auto-activate paid APIs
        if req.conn_type == "api":
            action["status"] = "skipped_paid"
            action["detail"] = "Paid API key — requires manual setup"
            return action

        # SAFETY: Never auto-connect paid MCPs
        if req.conn_type == "mcp":
            action["status"] = "skipped_paid"
            action["detail"] = "MCP server — may incur costs, requires manual config"
            return action

        # SAFETY: Never auto-login
        if req.conn_type == "github" and health.status != "healthy":
            action["status"] = "skipped_interactive"
            action["detail"] = "GitHub auth requires interactive login (gh auth login)"
            return action

        # Safe: auto-install Python module
        if req.conn_type == "python_module" and health.status == "missing":
            return self._pip_install(req, action)

        # Safe: create local config file if template available
        if req.conn_type == "env_var" and health.status == "missing":
            return self._create_config(req, action)

        action["status"] = "could_not_fix"
        action["detail"] = f"No safe auto-fix for {req.conn_type}:{req.target}"
        return action

    def _pip_install(self, req: ConnectionRequirement, action: dict) -> dict:
        """Safely install a Python package."""
        # Safety: only allow known safe packages
        SAFE_PACKAGES = {"anthropic", "httpx", "pydantic", "requests", "pytest"}
        pkg = req.target
        if pkg not in SAFE_PACKAGES:
            action["status"] = "skipped_paid"
            action["detail"] = f"Package '{pkg}' not in safe-install list"
            return action

        try:
            r = subprocess.run(
                ["pip", "install", "--quiet", pkg],
                capture_output=True, text=True, timeout=60,
            )
            if r.returncode == 0:
                action["status"] = "fixed"
                action["detail"] = f"pip install {pkg} succeeded"
            else:
                action["status"] = "could_not_fix"
                action["detail"] = f"pip install {pkg} failed: {r.stderr[:200]}"
        except (subprocess.TimeoutExpired, FileNotFoundError) as e:
            action["status"] = "could_not_fix"
            action["detail"] = str(e)
        return action

    def _create_config(self, req: ConnectionRequirement, action: dict) -> dict:
        """Create a local config file if it's a known pattern."""
        target_path = self.project_root / req.target
        if target_path.exists():
            action["status"] = "fixed"
            action["detail"] = f"File already exists: {req.target}"
            return action

        # Only create .claude/settings.json with safe defaults
        if req.target == ".claude/settings.json":
            try:
                target_path.parent.mkdir(parents=True, exist_ok=True)
                target_path.write_text(json.dumps(
                    {"permissions": {}, "mcpServers": {}}, indent=2,
                ))
                action["status"] = "fixed"
                action["detail"] = "Created default .claude/settings.json"
            except OSError as e:
                action["status"] = "could_not_fix"
                action["detail"] = str(e)
            return action

        action["status"] = "could_not_fix"
        action["detail"] = f"No template for config: {req.target}"
        return action


@dataclass
class PrepareReport:
    """Result of safe auto-preparation."""
    check_report: BootstrapReport = field(default_factory=BootstrapReport)
    recheck_report: Optional[BootstrapReport] = None
    fixed: int = 0
    skipped_paid: int = 0
    skipped_interactive: int = 0
    could_not_fix: int = 0
    actions_taken: list[dict] = field(default_factory=list)

    @property
    def improved(self) -> bool:
        return self.fixed > 0

    def to_dict(self) -> dict:
        d = {
            "fixed": self.fixed,
            "skipped_paid": self.skipped_paid,
            "skipped_interactive": self.skipped_interactive,
            "could_not_fix": self.could_not_fix,
            "improved": self.improved,
            "actions": self.actions_taken,
        }
        if self.recheck_report:
            d["recheck"] = self.recheck_report.to_dict()
        return d
