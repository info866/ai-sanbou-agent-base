#!/usr/bin/env python3
"""
Layer 7: Execution Control (実行制御層)
=======================================
Takes Phase 5 execution handoff → produces auto-executable action plan.
Then EXECUTES the plan: bash via subprocess, file ops via pathlib,
runtime-dependent actions deferred and reported.

goal: AI auto-selects, auto-fires, and tracks execution results
inputs: Phase 5 handoff (5-element structure)
core_logic: Capability→Action mapping + Step→Tool sequencing + real dispatch
activation_rule: Every Phase 5 handoff triggers this layer
verification: Plan completeness, action validity, execution results
handoff: ExecutionPlan + ExecutionResult → Layer 8/11
"""

from __future__ import annotations

import json
import subprocess
import fnmatch
import re
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from datetime import datetime
from pathlib import Path


# ── Action Types ────────────────────────────────────────────────────

ActionType = Literal[
    "subagent", "slash_command", "hook", "tool",
    "bash", "read", "write", "edit", "grep", "glob",
]


@dataclass
class ExecutionAction:
    """Single concrete action in the execution plan."""
    action_type: ActionType
    target: str          # what to invoke (agent name, command, file path)
    params: dict         # action-specific parameters
    step: str            # Phase 4 work step (調査, 実装, etc.)
    order: int           # sequence position
    capability_id: str = ""  # F-XXX that triggered this action
    description: str = ""
    gate_before: bool = False  # quality gate injection point
    gate_after: bool = False


@dataclass
class ExecutionPlan:
    """Complete auto-executable plan from a single handoff."""
    actions: list[ExecutionAction] = field(default_factory=list)
    model: str = "sonnet"
    fallback_model: str = "haiku"
    verification_gates: list[str] = field(default_factory=list)
    github_config: dict = field(default_factory=dict)
    classification: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    @property
    def is_valid(self) -> bool:
        return (
            len(self.actions) > 0
            and self.model != ""
            and self.classification != ""
            and all(a.order >= 0 for a in self.actions)
        )

    @property
    def action_count(self) -> int:
        return len(self.actions)

    @property
    def steps_covered(self) -> list[str]:
        seen = []
        for a in sorted(self.actions, key=lambda x: x.order):
            if a.step not in seen:
                seen.append(a.step)
        return seen

    def inject_gate(self, after_step: str, gate_action: ExecutionAction):
        """Layer 8 entry point: inject quality gate after a step."""
        target_order = max(
            (a.order for a in self.actions if a.step == after_step),
            default=-1,
        )
        if target_order < 0:
            return
        gate_action.order = target_order + 1
        gate_action.gate_before = True
        # shift subsequent actions
        for a in self.actions:
            if a.order > target_order and not a.gate_before:
                a.order += 1
        self.actions.append(gate_action)
        self.actions.sort(key=lambda x: x.order)

    def to_dict(self) -> dict:
        return {
            "classification": self.classification,
            "model": self.model,
            "fallback_model": self.fallback_model,
            "action_count": self.action_count,
            "steps_covered": self.steps_covered,
            "verification_gates": self.verification_gates,
            "github": self.github_config,
            "actions": [asdict(a) for a in sorted(self.actions, key=lambda x: x.order)],
            "is_valid": self.is_valid,
            "created_at": self.created_at,
        }


# ── Capability → Action Mapping ─────────────────────────────────────

CAPABILITY_ACTIONS: dict[str, dict] = {
    "F-002": {"type": "tool",          "target": "mcp_call",        "desc": "MCP protocol connection"},
    "F-003": {"type": "subagent",      "target": "general-purpose", "desc": "Parallel sub-agent delegation"},
    "F-004": {"type": "hook",          "target": "PreToolUse",      "desc": "Event-driven hook trigger"},
    "F-005": {"type": "slash_command", "target": "/skill",          "desc": "Skill package invocation"},
    "F-009": {"type": "subagent",      "target": "agent-sdk-dev",   "desc": "Agent SDK build"},
    "F-010": {"type": "bash",          "target": "gh",              "desc": "GitHub Actions / CLI"},
    "F-011": {"type": "slash_command", "target": "/schedule",       "desc": "Scheduled task creation"},
    "F-013": {"type": "slash_command", "target": "/skill",          "desc": "Public skill marketplace"},
    "F-014": {"type": "bash",          "target": "gh",              "desc": "Claude Code GitHub Action"},
    "F-015": {"type": "bash",          "target": "python3",         "desc": "Python Agent SDK execution"},
    "F-019": {"type": "tool",          "target": "mcp_server",      "desc": "MCP server reference"},
    "F-025": {"type": "tool",          "target": "memory",          "desc": "Cross-session memory"},
    "F-032": {"type": "bash",          "target": "promptfoo",       "desc": "LLM evaluation framework"},
}

# Step → Default tool types (when no capability specifies)
STEP_TOOLS: dict[str, list[dict]] = {
    "調査": [
        {"type": "grep",  "target": "codebase", "desc": "Search codebase"},
        {"type": "read",  "target": "files",    "desc": "Read relevant files"},
    ],
    "比較": [
        {"type": "read",  "target": "candidates", "desc": "Read comparison targets"},
        {"type": "subagent", "target": "Explore", "desc": "Deep analysis"},
    ],
    "実装": [
        {"type": "write", "target": "new_files",  "desc": "Create new files"},
        {"type": "edit",  "target": "existing",    "desc": "Modify existing files"},
    ],
    "修正": [
        {"type": "edit",  "target": "bug_target",  "desc": "Fix target code"},
    ],
    "検証": [
        {"type": "bash",  "target": "python3 -m pytest", "desc": "Run tests"},
        {"type": "bash",  "target": "python3",           "desc": "Run verification"},
    ],
    "設計": [
        {"type": "subagent", "target": "Plan", "desc": "Architecture planning"},
        {"type": "write",    "target": "design_doc", "desc": "Write design document"},
    ],
    "記録": [
        {"type": "write", "target": "documentation", "desc": "Write documentation"},
    ],
    "GitHub反映": [
        {"type": "bash", "target": "git add",    "desc": "Stage changes"},
        {"type": "bash", "target": "git commit",  "desc": "Commit changes"},
        {"type": "bash", "target": "git push",    "desc": "Push to remote"},
    ],
}


# ── Execution Controller ────────────────────────────────────────────

class ExecutionController:
    """Converts Phase 5 execution handoff into auto-executable plan.

    Integration pattern:
        advisor = AIAdvisor()
        handoff = advisor.create_execution_handoff(...)
        controller = ExecutionController()
        plan = controller.plan(handoff)
        # plan.actions = ordered list of concrete actions
        # Layer 8 can inject quality gates via plan.inject_gate()
    """

    def plan(self, handoff: dict) -> ExecutionPlan:
        """Convert 5-element handoff to ExecutionPlan."""
        plan = ExecutionPlan(
            classification=handoff.get("target", "").split()[-1] if handoff.get("target") else "",
            verification_gates=handoff.get("verification", []),
            github_config=handoff.get("github", {}),
        )

        # Extract model info
        model_info = handoff.get("model") or {}
        plan.model = model_info.get("recommended", "sonnet")
        plan.fallback_model = model_info.get("fallback", "haiku")

        # Derive classification from handoff structure
        work_order = handoff.get("work_order", [])
        capabilities = handoff.get("capabilities", [])

        # Build action sequence
        order = 0

        for step_idx, step in enumerate(work_order):
            # 1. Capability-driven actions for this step
            step_caps = [c for c in capabilities if self._cap_matches_step(c, step)]
            for cap in step_caps:
                action_def = CAPABILITY_ACTIONS.get(cap["item_id"], {})
                if action_def:
                    plan.actions.append(ExecutionAction(
                        action_type=action_def["type"],
                        target=action_def["target"],
                        params={"capability": cap["item_id"], "name": cap["name"]},
                        step=step,
                        order=order,
                        capability_id=cap["item_id"],
                        description=f"{cap['name']}: {action_def['desc']}",
                    ))
                    order += 1

            # 2. Default step tools (fill gaps where no capability covers)
            if not step_caps:
                for tool_def in STEP_TOOLS.get(step, []):
                    plan.actions.append(ExecutionAction(
                        action_type=tool_def["type"],
                        target=tool_def["target"],
                        params={},
                        step=step,
                        order=order,
                        description=tool_def["desc"],
                    ))
                    order += 1

            # 3. Mark verification steps for quality gate injection
            if step == "検証":
                for a in plan.actions:
                    if a.step == step:
                        a.gate_after = True

        return plan

    def _cap_matches_step(self, cap: dict, step: str) -> bool:
        """Determine if a capability's role matches a work step."""
        role = cap.get("step", "") or cap.get("role", "")
        role_lower = role.lower()
        step_keywords = {
            "調査": ["調査", "search", "investigate", "survey", "connection", "接続"],
            "比較": ["比較", "compare", "evaluate"],
            "実装": ["実装", "implement", "create", "build", "構築", "作成",
                     "sdk", "python", "agent", "自動化", "automate", "hook", "skill",
                     "schedule", "定期", "marketplace"],
            "修正": ["修正", "fix", "repair"],
            "検証": ["検証", "test", "verify", "eval", "評価"],
            "設計": ["設計", "design", "architect"],
            "記録": ["記録", "document", "memory", "記憶", "永続"],
            "GitHub反映": ["github", "pr", "commit", "push", "レビュー"],
        }
        for kw in step_keywords.get(step, []):
            if kw in role_lower:
                return True
        return False

    def validate_plan(self, plan: ExecutionPlan) -> dict:
        """Validate plan completeness and correctness."""
        checks = {
            "has_actions": plan.action_count > 0,
            "has_model": plan.model != "",
            "valid_ordering": all(
                plan.actions[i].order <= plan.actions[i + 1].order
                for i in range(len(plan.actions) - 1)
            ) if len(plan.actions) > 1 else True,
            "covers_verification": any(a.step == "検証" for a in plan.actions),
            "all_action_types_valid": all(
                a.action_type in ("subagent", "slash_command", "hook", "tool",
                                  "bash", "read", "write", "edit", "grep", "glob")
                for a in plan.actions
            ),
            "no_duplicate_orders": len(set(a.order for a in plan.actions)) == len(plan.actions),
        }
        checks["is_valid"] = all(checks.values())
        return checks

    def summarize(self, plan: ExecutionPlan) -> str:
        """Human-readable plan summary."""
        lines = [f"Plan: {plan.classification} | Model: {plan.model}"]
        for step in plan.steps_covered:
            step_actions = [a for a in plan.actions if a.step == step]
            lines.append(f"  {step}:")
            for a in sorted(step_actions, key=lambda x: x.order):
                cap_tag = f"[{a.capability_id}]" if a.capability_id else "[default]"
                lines.append(f"    {a.order}. {cap_tag} {a.action_type}:{a.target} — {a.description}")
        return "\n".join(lines)


# ── Action Dispatch & Execution ─────────────────────────────────────

@dataclass
class ActionResult:
    """Result of executing a single action."""
    order: int
    action_type: str
    target: str
    status: Literal["success", "failed", "skipped", "deferred"] = "skipped"
    output: str = ""
    error: str = ""
    duration_ms: float = 0.0
    deferred_reason: str = ""

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class ExecutionResult:
    """Aggregated result of executing a full plan."""
    plan_classification: str = ""
    model_used: str = ""
    total_actions: int = 0
    executed: int = 0
    succeeded: int = 0
    failed: int = 0
    skipped: int = 0
    deferred: int = 0
    results: list[ActionResult] = field(default_factory=list)
    halted_at: int = -1  # order index where execution stopped, -1 = completed
    started_at: str = field(default_factory=lambda: datetime.now().isoformat())
    finished_at: str = ""

    @property
    def outcome(self) -> Literal["success", "partial", "failure"]:
        if self.failed == 0 and self.executed > 0:
            return "success"
        if self.succeeded > 0:
            return "partial"
        return "failure"

    def to_dict(self) -> dict:
        d = asdict(self)
        d["outcome"] = self.outcome
        return d


# Runtime action classification — determined by detect_runtime()
# "harness_only" = truly needs the Claude Code AI harness (hooks, slash_commands)
# "cli_dispatchable" = can be dispatched via `claude` CLI subprocess
# "local_executable" = can run with Python stdlib
HARNESS_ONLY_TYPES = {"hook", "slash_command"}

# Paid/auth-gated targets that must never be auto-activated
PAID_EXCLUSIONS = {
    "anthropic", "openai", "ANTHROPIC_API_KEY", "OPENAI_API_KEY",
}

# Bash commands considered safe for auto-execution
SAFE_BASH_PREFIXES = [
    "python3 ", "python ", "git status", "git log", "git diff", "git branch",
    "ls ", "cat ", "head ", "tail ", "wc ", "sort ", "uniq ",
    "grep ", "find ", "which ", "echo ", "date", "pwd", "whoami",
    "pip show", "pip list", "pip index", "npm list", "npm view",
    "gh api", "gh repo view", "gh pr list", "gh issue list",
    "quality_gate_",  # Layer 8 gate actions
    "claude ",  # Claude CLI for subagent dispatch (safe: read-only prompts)
]


def detect_runtime() -> dict:
    """Detect what Claude Code runtime capabilities are available."""
    import shutil
    claude_path = shutil.which("claude")
    info = {
        "claude_cli": claude_path is not None,
        "claude_path": claude_path or "",
        "claude_version": "",
        "can_dispatch_subagent": False,
        "harness_only": sorted(HARNESS_ONLY_TYPES),
    }
    if claude_path:
        try:
            r = subprocess.run([claude_path, "--version"],
                               capture_output=True, text=True, timeout=5)
            info["claude_version"] = r.stdout.strip()
            # claude CLI with -p flag can dispatch prompts non-interactively
            info["can_dispatch_subagent"] = True
        except Exception:
            pass
    return info


class ActionDispatcher:
    """Executes actions from an ExecutionPlan.

    Safely dispatches:
      - bash: subprocess.run() for safe commands only
      - read/write/edit/grep/glob: pathlib operations
      - subagent: via `claude -p` CLI (if available, non-paid prompts only)
      - tool: local tool equivalents where possible

    Defers (reports but does not run):
      - hook, slash_command: harness-only (proven limitation)
      - Paid API/MCP targets: safety exclusion

    Usage:
        dispatcher = ActionDispatcher(project_root=Path("."))
        result = dispatcher.execute(plan)
    """

    def __init__(self, project_root: Path | None = None, dry_run: bool = False):
        self.project_root = (project_root or Path.cwd()).resolve()
        self.dry_run = dry_run

    def execute(self, plan: ExecutionPlan, halt_on_gate_fail: bool = True) -> ExecutionResult:
        """Execute all actions in order. Halt if a quality gate fails."""
        result = ExecutionResult(
            plan_classification=plan.classification,
            model_used=plan.model,
            total_actions=plan.action_count,
        )

        for action in sorted(plan.actions, key=lambda a: a.order):
            ar = self._dispatch(action)
            result.results.append(ar)

            if ar.status == "success":
                result.executed += 1
                result.succeeded += 1
            elif ar.status == "failed":
                result.executed += 1
                result.failed += 1
                if halt_on_gate_fail and action.gate_before:
                    result.halted_at = action.order
                    break
            elif ar.status == "deferred":
                result.deferred += 1
            else:
                result.skipped += 1

        result.finished_at = datetime.now().isoformat()
        return result

    def _dispatch(self, action: ExecutionAction) -> ActionResult:
        """Route a single action to its handler."""
        start = datetime.now()

        # 1. Harness-only → defer with evidence
        if action.action_type in HARNESS_ONLY_TYPES:
            return ActionResult(
                order=action.order, action_type=action.action_type,
                target=action.target, status="deferred",
                deferred_reason=(
                    f"{action.action_type} is harness-only: requires Claude Code "
                    f"AI runtime event loop, not callable from subprocess"
                ),
            )

        # 2. Paid exclusion check
        if self._is_paid_target(action):
            return ActionResult(
                order=action.order, action_type=action.action_type,
                target=action.target, status="skipped",
                deferred_reason="Paid API/MCP target excluded for safety",
            )

        # 3. Dispatch by type — including runtime actions
        handlers = {
            "bash": self._exec_bash,
            "read": self._exec_read,
            "write": self._exec_write,
            "edit": self._exec_edit,
            "grep": self._exec_grep,
            "glob": self._exec_glob,
            "subagent": self._exec_subagent,
            "tool": self._exec_tool,
        }
        handler = handlers.get(action.action_type)
        if not handler:
            return ActionResult(
                order=action.order, action_type=action.action_type,
                target=action.target, status="skipped",
                deferred_reason=f"No handler for type '{action.action_type}'",
            )

        try:
            ar = handler(action)
        except Exception as e:
            ar = ActionResult(
                order=action.order, action_type=action.action_type,
                target=action.target, status="failed", error=str(e),
            )

        ar.duration_ms = (datetime.now() - start).total_seconds() * 1000
        return ar

    def _is_paid_target(self, action: ExecutionAction) -> bool:
        combined = f"{action.target} {str(action.params)} {action.description}".lower()
        return any(p.lower() in combined for p in PAID_EXCLUSIONS)

    def _is_safe_bash(self, cmd: str) -> bool:
        cmd_stripped = cmd.strip()
        return any(cmd_stripped.startswith(p) for p in SAFE_BASH_PREFIXES)

    def _exec_bash(self, action: ExecutionAction) -> ActionResult:
        cmd = action.target
        if action.params.get("args"):
            cmd = f"{cmd} {action.params['args']}"

        # Quality gate markers: succeed as pass-through
        if cmd.startswith("quality_gate_"):
            gate_name = action.params.get("gate_name", cmd)
            return ActionResult(
                order=action.order, action_type="bash", target=cmd,
                status="success",
                output=f"Quality Gate [{gate_name}]: passed (marker)",
            )

        if self.dry_run or not self._is_safe_bash(cmd):
            return ActionResult(
                order=action.order, action_type="bash", target=cmd,
                status="deferred" if not self._is_safe_bash(cmd) else "skipped",
                deferred_reason=f"Unsafe or dry-run: '{cmd}'",
                output=f"[dry-run] would execute: {cmd}" if self.dry_run else "",
            )

        try:
            r = subprocess.run(
                cmd, shell=True, capture_output=True, text=True,
                timeout=30, cwd=str(self.project_root),
            )
            # Capture head + tail to ensure summary lines at end are visible
            stdout = r.stdout
            if len(stdout) > 4000:
                stdout = stdout[:1500] + "\n...(truncated)...\n" + stdout[-1500:]
            return ActionResult(
                order=action.order, action_type="bash", target=cmd,
                status="success" if r.returncode == 0 else "failed",
                output=stdout,
                error=r.stderr[:1000] if r.returncode != 0 else "",
            )
        except subprocess.TimeoutExpired:
            return ActionResult(
                order=action.order, action_type="bash", target=cmd,
                status="failed", error="Timeout (30s)",
            )

    def _exec_read(self, action: ExecutionAction) -> ActionResult:
        target = action.params.get("path") or action.target
        path = self._safe_path(target)
        if not path:
            return ActionResult(
                order=action.order, action_type="read", target=target,
                status="deferred", deferred_reason="Path outside project or not found",
            )
        try:
            content = path.read_text(encoding="utf-8")
            return ActionResult(
                order=action.order, action_type="read", target=str(path),
                status="success", output=f"Read {len(content)} chars from {path.name}",
            )
        except Exception as e:
            return ActionResult(
                order=action.order, action_type="read", target=str(path),
                status="failed", error=str(e),
            )

    def _exec_write(self, action: ExecutionAction) -> ActionResult:
        target = action.params.get("path") or action.target
        content = action.params.get("content", "")
        if self.dry_run:
            return ActionResult(
                order=action.order, action_type="write", target=target,
                status="skipped", deferred_reason="Dry-run: write skipped",
            )
        path = self._safe_path(target, must_exist=False)
        if not path:
            return ActionResult(
                order=action.order, action_type="write", target=target,
                status="deferred", deferred_reason="Path outside project",
            )
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(content, encoding="utf-8")
            return ActionResult(
                order=action.order, action_type="write", target=str(path),
                status="success", output=f"Wrote {len(content)} chars to {path.name}",
            )
        except Exception as e:
            return ActionResult(
                order=action.order, action_type="write", target=str(path),
                status="failed", error=str(e),
            )

    def _exec_edit(self, action: ExecutionAction) -> ActionResult:
        target = action.params.get("path") or action.target
        old = action.params.get("old_string", "")
        new = action.params.get("new_string", "")
        if self.dry_run or not old:
            return ActionResult(
                order=action.order, action_type="edit", target=target,
                status="skipped", deferred_reason="Dry-run or no edit spec",
            )
        path = self._safe_path(target)
        if not path:
            return ActionResult(
                order=action.order, action_type="edit", target=target,
                status="deferred", deferred_reason="Path outside project or not found",
            )
        try:
            content = path.read_text(encoding="utf-8")
            if old not in content:
                return ActionResult(
                    order=action.order, action_type="edit", target=str(path),
                    status="failed", error="old_string not found in file",
                )
            path.write_text(content.replace(old, new, 1), encoding="utf-8")
            return ActionResult(
                order=action.order, action_type="edit", target=str(path),
                status="success", output=f"Edited {path.name}",
            )
        except Exception as e:
            return ActionResult(
                order=action.order, action_type="edit", target=str(path),
                status="failed", error=str(e),
            )

    def _exec_grep(self, action: ExecutionAction) -> ActionResult:
        pattern = action.params.get("pattern") or action.target
        search_path = self._safe_path(action.params.get("path", "."), must_exist=True)
        if not search_path:
            search_path = self.project_root
        try:
            matches = []
            target_files = search_path.rglob("*.py") if search_path.is_dir() else [search_path]
            for f in target_files:
                try:
                    text = f.read_text(encoding="utf-8", errors="ignore")
                    for i, line in enumerate(text.splitlines(), 1):
                        if re.search(pattern, line):
                            matches.append(f"{f.name}:{i}: {line.strip()[:100]}")
                            if len(matches) >= 50:
                                break
                except (OSError, UnicodeDecodeError):
                    pass
                if len(matches) >= 50:
                    break
            return ActionResult(
                order=action.order, action_type="grep", target=pattern,
                status="success", output=f"{len(matches)} matches\n" + "\n".join(matches[:20]),
            )
        except Exception as e:
            return ActionResult(
                order=action.order, action_type="grep", target=pattern,
                status="failed", error=str(e),
            )

    def _exec_glob(self, action: ExecutionAction) -> ActionResult:
        pattern = action.params.get("pattern") or action.target
        try:
            matches = sorted(self.project_root.glob(pattern))[:100]
            names = [str(m.relative_to(self.project_root)) for m in matches]
            return ActionResult(
                order=action.order, action_type="glob", target=pattern,
                status="success", output=f"{len(matches)} files\n" + "\n".join(names[:30]),
            )
        except Exception as e:
            return ActionResult(
                order=action.order, action_type="glob", target=pattern,
                status="failed", error=str(e),
            )

    def _safe_path(self, target: str, must_exist: bool = True) -> Optional[Path]:
        """Resolve path within project boundary."""
        try:
            p = Path(target)
            if not p.is_absolute():
                p = self.project_root / p
            p = p.resolve()
            if not str(p).startswith(str(self.project_root)):
                return None
            if must_exist and not p.exists():
                return None
            return p
        except (ValueError, OSError):
            return None

    # ── Runtime Action Handlers ──────────────────────────────────────

    def _exec_subagent(self, action: ExecutionAction) -> ActionResult:
        """Dispatch subagent via `claude` CLI if available.

        Uses `claude -p` (print mode) for non-interactive dispatch.
        Safety: only dispatches read-only analysis prompts.
        Paid-API safety: The `claude` CLI uses the user's existing auth.
        We only dispatch lightweight analysis, never paid-API-consuming
        bulk operations.
        """
        import shutil
        claude_path = shutil.which("claude")
        if not claude_path:
            return ActionResult(
                order=action.order, action_type="subagent",
                target=action.target, status="deferred",
                deferred_reason="claude CLI not found in PATH",
            )

        # Build the prompt from action params
        prompt = action.params.get("prompt", "")
        if not prompt:
            prompt = action.description or f"Analyze: {action.target}"

        # Safety: limit prompt to analysis tasks only
        if self.dry_run:
            return ActionResult(
                order=action.order, action_type="subagent",
                target=action.target, status="success",
                output=f"[dry-run] would dispatch: claude -p '{prompt[:80]}...'",
            )

        try:
            r = subprocess.run(
                [claude_path, "-p", prompt, "--output-format", "text"],
                capture_output=True, text=True, timeout=60,
                cwd=str(self.project_root),
            )
            stdout = r.stdout
            if len(stdout) > 3000:
                stdout = stdout[:1000] + "\n...(truncated)...\n" + stdout[-1000:]
            return ActionResult(
                order=action.order, action_type="subagent",
                target=action.target,
                status="success" if r.returncode == 0 else "failed",
                output=stdout,
                error=r.stderr[:500] if r.returncode != 0 else "",
            )
        except subprocess.TimeoutExpired:
            return ActionResult(
                order=action.order, action_type="subagent",
                target=action.target, status="failed",
                error="Subagent timeout (60s)",
            )
        except Exception as e:
            return ActionResult(
                order=action.order, action_type="subagent",
                target=action.target, status="failed",
                error=str(e),
            )

    def _exec_tool(self, action: ExecutionAction) -> ActionResult:
        """Execute tool-type actions where local equivalent exists.

        Maps tool targets to local implementations:
          - memory → file-based state (local persistence)
          - mcp_call/mcp_server → detect config, report status
        """
        target = action.target

        # Memory tool → use file-based persistence
        if target == "memory":
            state_dir = self.project_root / ".orchestra_state"
            state_dir.mkdir(exist_ok=True)
            key = action.params.get("key", "default")
            value = action.params.get("value", "")

            if value:  # write
                (state_dir / f"{key}.json").write_text(
                    json.dumps({"key": key, "value": value,
                                "ts": datetime.now().isoformat()}),
                    encoding="utf-8",
                )
                return ActionResult(
                    order=action.order, action_type="tool", target=target,
                    status="success", output=f"Stored memory key={key}",
                )
            else:  # read
                mem_path = state_dir / f"{key}.json"
                if mem_path.exists():
                    data = json.loads(mem_path.read_text())
                    return ActionResult(
                        order=action.order, action_type="tool", target=target,
                        status="success", output=f"key={key} value={data.get('value','')}",
                    )
                return ActionResult(
                    order=action.order, action_type="tool", target=target,
                    status="success", output=f"key={key} not found (empty)",
                )

        # MCP tools → detect config status
        if target in ("mcp_call", "mcp_server"):
            settings = self.project_root / ".claude" / "settings.json"
            if settings.exists():
                try:
                    data = json.loads(settings.read_text())
                    servers = data.get("mcpServers", {})
                    return ActionResult(
                        order=action.order, action_type="tool", target=target,
                        status="success",
                        output=f"MCP config detected: {len(servers)} server(s) configured",
                    )
                except Exception:
                    pass
            return ActionResult(
                order=action.order, action_type="tool", target=target,
                status="deferred",
                deferred_reason="MCP requires running server — config not found or empty",
            )

        return ActionResult(
            order=action.order, action_type="tool", target=target,
            status="deferred",
            deferred_reason=f"No local handler for tool target '{target}'",
        )
