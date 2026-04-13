#!/usr/bin/env python3
"""
Model Selection Engine for AI Orchestration
============================================
Selects optimal model alias based on request characteristics.

Integrated into Phase 5 AI Advisor → Phase 4 Execution Handoff flow.

Canon: 13.モデル選定機能 要件定義書.md
Guide: 14.モデル選定機能 作業指示書.md

Recheck logic follows canon update-sensitive conditions:
  - new alias added
  - alias meaning changed
  - recommended usage changed
  - available model mapping changed
"""

from __future__ import annotations

import json
import subprocess
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from datetime import datetime
from pathlib import Path


ModelAlias = Literal["opus", "sonnet", "haiku", "opusplan"]


# ── Alias Registry (the single source of truth for alias roles) ──────────

ALIAS_REGISTRY: dict[str, dict] = {
    "haiku": {
        "role": "Simple, fast, low-risk, lightweight support work",
        "tier": 0,
        "known_env_var": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
    },
    "sonnet": {
        "role": "Normal coding and balanced execution",
        "tier": 1,
        "known_env_var": "ANTHROPIC_DEFAULT_SONNET_MODEL",
    },
    "opusplan": {
        "role": "Planning is heavy but execution is ordinary",
        "tier": 2,
        "known_env_var": None,  # hybrid alias
    },
    "opus": {
        "role": "Heavy reasoning, high ambiguity, or high failure cost",
        "tier": 3,
        "known_env_var": "ANTHROPIC_DEFAULT_OPUS_MODEL",
    },
}

FALLBACK_MAP: dict[str, str] = {
    "opus": "sonnet",
    "opusplan": "sonnet",
    "sonnet": "haiku",
    "haiku": "sonnet",
}


# ── Update-sensitive state for recheck canon compliance ──────────────

@dataclass
class AliasState:
    """Tracks known alias state for detecting update-sensitive changes."""
    known_aliases: set = field(default_factory=lambda: set(ALIAS_REGISTRY.keys()))
    alias_roles: dict = field(default_factory=lambda: {
        k: v["role"] for k, v in ALIAS_REGISTRY.items()
    })
    last_checked: Optional[str] = None  # ISO datetime of last official check


# ── Data classes ─────────────────────────────────────────────────────

@dataclass
class SelectionInput:
    """Input characteristics for model selection."""
    goal: str
    reasoning_weight: float   # 0.0 (simple) ~ 1.0 (heavy)
    ambiguity: float          # 0.0 (clear) ~ 1.0 (high)
    failure_cost: float       # 0.0 (low) ~ 1.0 (critical)
    speed_priority: float     # 0.0 (normal) ~ 1.0 (urgent)
    context_size: float       # 0.0 (small <10K) ~ 1.0 (huge >500K)
    plan_weight: float        # 0.0 (exec only) ~ 1.0 (heavy plan)


@dataclass
class RecheckDetail:
    """Structured recheck information for canon compliance."""
    required: bool = False
    triggers: list = field(default_factory=list)
    description: str = ""


@dataclass
class SelectionOutput:
    """Model selection decision — the required output shape."""
    goal: str
    recommended_model: str
    fallback_model: str
    reason: str
    recheck_required: bool
    handoff_notes: str = ""
    # Extended fields for Phase 5 integration
    recheck_detail: Optional[RecheckDetail] = None

    def to_dict(self) -> dict:
        d = {
            "goal": self.goal,
            "recommended_model": self.recommended_model,
            "fallback_model": self.fallback_model,
            "reason": self.reason,
            "recheck_required": self.recheck_required,
            "handoff_notes": self.handoff_notes,
        }
        if self.recheck_detail:
            d["recheck_detail"] = {
                "required": self.recheck_detail.required,
                "triggers": self.recheck_detail.triggers,
                "description": self.recheck_detail.description,
            }
        return d


# ── Official Recheck Path ────────────────────────────────────────────

class OfficialRecheckPath:
    """Real path to consult current official Claude Code / model alias information.

    When recheck is needed, this class can:
    1. Attempt to query Claude Code for current model aliases (via `claude --version` etc.)
    2. Check environment variables for alias→version mappings
    3. Return structured findings or mark recheck as deferred
    """

    @staticmethod
    def check_current_aliases() -> dict:
        """Attempt to discover current alias state from the environment."""
        import os
        findings = {
            "method": "environment_and_cli",
            "timestamp": datetime.now().isoformat(),
            "aliases_found": {},
            "env_overrides": {},
            "cli_available": False,
            "status": "unknown",
        }

        # Check environment variables for version mappings
        env_vars = {
            "opus": "ANTHROPIC_DEFAULT_OPUS_MODEL",
            "sonnet": "ANTHROPIC_DEFAULT_SONNET_MODEL",
            "haiku": "ANTHROPIC_DEFAULT_HAIKU_MODEL",
        }
        for alias, var in env_vars.items():
            val = os.environ.get(var)
            if val:
                findings["env_overrides"][alias] = val

        # Check ANTHROPIC_MODEL for default override
        default_model = os.environ.get("ANTHROPIC_MODEL")
        if default_model:
            findings["env_overrides"]["default"] = default_model

        # Attempt to check Claude Code CLI availability
        try:
            result = subprocess.run(
                ["claude", "--version"],
                capture_output=True, text=True, timeout=5
            )
            if result.returncode == 0:
                findings["cli_available"] = True
                findings["cli_version"] = result.stdout.strip()
        except (FileNotFoundError, subprocess.TimeoutExpired):
            findings["cli_available"] = False

        # Determine status
        if findings["env_overrides"]:
            findings["status"] = "env_overrides_found"
        elif findings["cli_available"]:
            findings["status"] = "cli_available_no_overrides"
        else:
            findings["status"] = "no_live_info_available"

        return findings

    @staticmethod
    def verify_alias_still_valid(alias: str) -> dict:
        """Check whether a specific alias is still recognized."""
        import os
        result = {"alias": alias, "valid": True, "notes": ""}

        # Check if alias is in our registry
        if alias not in ALIAS_REGISTRY:
            result["valid"] = False
            result["notes"] = f"Alias '{alias}' not in current registry"
            return result

        # Check for environment override
        env_var = ALIAS_REGISTRY[alias].get("known_env_var")
        if env_var:
            override = os.environ.get(env_var)
            if override:
                result["notes"] = f"Env override: {env_var}={override}"

        return result

    @staticmethod
    def detect_changes(previous_state: AliasState) -> RecheckDetail:
        """Compare current alias state against a previous snapshot.
        Returns recheck detail with canon-compliant triggers."""
        current_aliases = set(ALIAS_REGISTRY.keys())
        triggers = []

        # Canon trigger 1: New alias added
        new_aliases = current_aliases - previous_state.known_aliases
        if new_aliases:
            triggers.append(f"new_alias_added: {', '.join(sorted(new_aliases))}")

        # Canon trigger 2: Alias meaning changed
        for alias in current_aliases & previous_state.known_aliases:
            current_role = ALIAS_REGISTRY[alias]["role"]
            previous_role = previous_state.alias_roles.get(alias, "")
            if current_role != previous_role:
                triggers.append(f"alias_meaning_changed: {alias}")

        # Canon trigger 3: Recommended usage changed
        # (detected via environment variable differences)
        import os
        for alias, info in ALIAS_REGISTRY.items():
            env_var = info.get("known_env_var")
            if env_var and os.environ.get(env_var):
                triggers.append(f"version_mapping_changed: {alias} via {env_var}")

        # Canon trigger 4: Available model mapping changed
        removed_aliases = previous_state.known_aliases - current_aliases
        if removed_aliases:
            triggers.append(f"alias_removed: {', '.join(sorted(removed_aliases))}")

        required = len(triggers) > 0
        desc = "; ".join(triggers) if triggers else "No update-sensitive changes detected"

        return RecheckDetail(required=required, triggers=triggers, description=desc)


# ── Model Selector ───────────────────────────────────────────────────

class ModelSelector:
    """Alias-based model selection engine.

    Selection is role-based, not version-pinned.
    Recheck logic follows canon update-sensitive conditions.
    """

    def __init__(self, alias_state: Optional[AliasState] = None):
        self._alias_state = alias_state or AliasState()
        self._recheck_path = OfficialRecheckPath()

    @property
    def tier_order(self) -> list[str]:
        """Dynamic tier order from registry."""
        return sorted(ALIAS_REGISTRY.keys(), key=lambda a: ALIAS_REGISTRY[a]["tier"])

    def select(self, input_: SelectionInput) -> SelectionOutput:
        """Select optimal model alias for the request."""

        # Stage 1: Filter by blocking conditions
        if input_.speed_priority >= 0.8 and input_.context_size < 0.3:
            recommended = "haiku"
            reason = "Speed priority + small context → Haiku"

        elif (input_.plan_weight >= 0.7
              and (input_.reasoning_weight + input_.ambiguity) >= 1.2):
            recommended = "opusplan"
            reason = "Heavy planning + complex reasoning → OpusPlan"

        else:
            # Stage 2: Weighted scoring
            total_weight = (
                input_.reasoning_weight * 0.3
                + input_.ambiguity * 0.2
                + input_.failure_cost * 0.3
                + input_.context_size * 0.1
                + (1 - input_.speed_priority) * 0.1
            )

            if total_weight >= 0.7:
                recommended = "opus"
                reason = f"High complexity (score={total_weight:.2f}) → Opus"
            elif total_weight >= 0.4 and input_.plan_weight < 0.5:
                recommended = "sonnet"
                reason = f"Balanced complexity (score={total_weight:.2f}) → Sonnet"
            else:
                recommended = "haiku"
                reason = f"Low complexity (score={total_weight:.2f}) → Haiku"

        # Stage 3: Safety adjustments
        if input_.failure_cost >= 0.8:
            recommended = self._bump_up(recommended)
            reason += " [upgraded for safety]"

        if input_.speed_priority >= 0.7:
            recommended = self._bump_down(recommended)
            reason += " [downgraded for speed]"

        # Determine fallback
        fallback = self._select_fallback(recommended, input_)

        # Determine recheck — canon-compliant update-sensitive logic
        recheck_detail = self._check_recheck(input_, recommended)

        # Generate execution notes
        notes = self._generate_notes(input_, recommended, recheck_detail)

        return SelectionOutput(
            goal=input_.goal,
            recommended_model=recommended,
            fallback_model=fallback,
            reason=reason,
            recheck_required=recheck_detail.required,
            handoff_notes=notes,
            recheck_detail=recheck_detail,
        )

    def _bump_up(self, model: str) -> str:
        order = self.tier_order
        idx = order.index(model) if model in order else 1
        return order[min(idx + 1, len(order) - 1)]

    def _bump_down(self, model: str) -> str:
        order = self.tier_order
        idx = order.index(model) if model in order else 1
        return order[max(idx - 1, 0)]

    def _select_fallback(self, recommended: str, input_: SelectionInput) -> str:
        base_fallback = FALLBACK_MAP.get(recommended, "sonnet")
        if input_.failure_cost >= 0.8 and recommended == "opus":
            return "sonnet"
        if input_.speed_priority >= 0.7 and recommended == "haiku":
            return "sonnet"
        return base_fallback

    def _check_recheck(self, input_: SelectionInput, recommended: str) -> RecheckDetail:
        """Canon-compliant recheck logic.

        Primary triggers (from 13.モデル選定機能 要件定義書.md 更新追従ルール):
          1. new alias added
          2. alias meaning changed
          3. recommended usage changed
          4. available model mapping changed

        Practical safeguards (secondary):
          - context size near alias limits
        """
        # Primary: detect canon update-sensitive conditions
        recheck_detail = self._recheck_path.detect_changes(self._alias_state)

        # Secondary safeguard: context size near alias limits
        if input_.context_size >= 0.8 and recommended in ("haiku", "sonnet"):
            recheck_detail.triggers.append(
                "context_near_limit: verify alias supports required context window"
            )
            recheck_detail.required = True
            recheck_detail.description = "; ".join(recheck_detail.triggers)

        return recheck_detail

    def _generate_notes(self, input_: SelectionInput,
                        recommended: str,
                        recheck: RecheckDetail) -> str:
        notes = []
        if input_.context_size >= 0.8:
            notes.append(f"Large context ({input_.context_size:.0%})")
        if input_.failure_cost >= 0.8:
            notes.append("High safety requirement")
        if recheck.required:
            notes.append(f"Recheck needed: {recheck.description[:80]}")
        return "; ".join(notes) if notes else ""

    # ── Registry mutation for update-robustness testing ──

    @staticmethod
    def add_alias(name: str, role: str, tier: int, env_var: Optional[str] = None,
                  fallback: Optional[str] = "sonnet"):
        """Add a new alias to the registry. Demonstrates safe alias addition."""
        ALIAS_REGISTRY[name] = {
            "role": role,
            "tier": tier,
            "known_env_var": env_var,
        }
        if fallback:
            FALLBACK_MAP[name] = fallback

    @staticmethod
    def update_alias_role(name: str, new_role: str):
        """Update an alias's role description. Demonstrates safe role change."""
        if name in ALIAS_REGISTRY:
            ALIAS_REGISTRY[name]["role"] = new_role

    @staticmethod
    def remove_alias(name: str):
        """Remove an alias from the registry."""
        ALIAS_REGISTRY.pop(name, None)
        FALLBACK_MAP.pop(name, None)


# ── Request Classification → Model Selection Mapping ─────────────────

# Default parameter sets per request classification
# These connect Phase 5 RC-1~RC-6 to Phase 6 model selection input
RC_TO_PARAMS: dict[str, dict] = {
    "RC-1": {  # 調査中心: simple, fast
        "reasoning_weight": 0.2, "ambiguity": 0.2, "failure_cost": 0.1,
        "speed_priority": 0.7, "context_size": 0.2, "plan_weight": 0.1,
    },
    "RC-2": {  # 比較中心: moderate reasoning
        "reasoning_weight": 0.5, "ambiguity": 0.4, "failure_cost": 0.3,
        "speed_priority": 0.2, "context_size": 0.4, "plan_weight": 0.3,
    },
    "RC-3": {  # 実装中心: standard coding
        "reasoning_weight": 0.5, "ambiguity": 0.3, "failure_cost": 0.4,
        "speed_priority": 0.3, "context_size": 0.4, "plan_weight": 0.2,
    },
    "RC-4": {  # 修正中心: moderate, speed matters
        "reasoning_weight": 0.4, "ambiguity": 0.3, "failure_cost": 0.5,
        "speed_priority": 0.4, "context_size": 0.3, "plan_weight": 0.1,
    },
    "RC-5": {  # 設計中心: heavy reasoning, planning
        "reasoning_weight": 0.8, "ambiguity": 0.6, "failure_cost": 0.7,
        "speed_priority": 0.1, "context_size": 0.5, "plan_weight": 0.8,
    },
    "RC-6": {  # 運用改善中心: moderate
        "reasoning_weight": 0.4, "ambiguity": 0.3, "failure_cost": 0.3,
        "speed_priority": 0.4, "context_size": 0.3, "plan_weight": 0.2,
    },
}


def rc_to_model_input(classification: str, goal: str,
                      overrides: Optional[dict] = None) -> SelectionInput:
    """Convert Phase 5 request classification to Phase 6 model selection input."""
    params = dict(RC_TO_PARAMS.get(classification, RC_TO_PARAMS["RC-3"]))
    if overrides:
        params.update(overrides)
    return SelectionInput(goal=goal, **params)


# ── Convenience function ─────────────────────────────────────────────

def select_model(goal: str,
                 reasoning_weight: float,
                 ambiguity: float,
                 failure_cost: float,
                 speed_priority: float,
                 context_size: float,
                 plan_weight: float,
                 alias_state: Optional[AliasState] = None) -> SelectionOutput:
    """Convenience function for model selection."""
    selector = ModelSelector(alias_state=alias_state)
    input_ = SelectionInput(
        goal=goal,
        reasoning_weight=reasoning_weight,
        ambiguity=ambiguity,
        failure_cost=failure_cost,
        speed_priority=speed_priority,
        context_size=context_size,
        plan_weight=plan_weight,
    )
    return selector.select(input_)


def select_model_for_rc(classification: str, goal: str,
                        overrides: Optional[dict] = None,
                        alias_state: Optional[AliasState] = None) -> SelectionOutput:
    """Select model based on Phase 5 request classification."""
    selector = ModelSelector(alias_state=alias_state)
    input_ = rc_to_model_input(classification, goal, overrides)
    return selector.select(input_)
