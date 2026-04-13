#!/usr/bin/env python3
"""
Layer 7: Execution Control (実行制御層)
=======================================
Takes Phase 5 execution handoff → produces auto-executable action plan.
No manual slash commands. AI fires everything.

goal: AI auto-selects and auto-fires slash commands, subagents, hooks, tools
inputs: Phase 5 handoff (5-element structure)
core_logic: Capability→Action mapping + Step→Tool sequencing
activation_rule: Every Phase 5 handoff triggers this layer
verification: Plan completeness, action validity, ordering correctness
handoff: ExecutionPlan → Layer 8 (quality gate injection point)
"""

from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from datetime import datetime


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
