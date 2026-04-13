#!/usr/bin/env python3
"""
Layer 8: Automatic Quality Gate (自動品質ゲート層)
=================================================
Auto-injects test/diff/risk-detection/fail-stop gates into execution plans.
Uses Layer 7 ExecutionPlan.inject_gate() to insert checks.

goal: Auto-insert verification at every execution stage
inputs: Layer 7 ExecutionPlan + Phase 4 QA rules + Phase 5 verification reqs
core_logic: Risk scoring + gate injection + pass/fail decision
activation_rule: Every ExecutionPlan passes through quality gates before execution
verification: Gates present, risk detected, low-quality blocked
handoff: Gated ExecutionPlan → Layer 9 (connection checks prepended)
"""

from __future__ import annotations

import sys
from pathlib import Path
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional

# Import Layer 7
sys.path.insert(0, str(Path(__file__).parent.parent / "layer7_execution_control"))
from execution_controller import ExecutionAction, ExecutionPlan


# ── Risk Classification ─────────────────────────────────────────────

RiskLevel = Literal["low", "medium", "high", "critical"]

DANGEROUS_PATTERNS = {
    "critical": [
        "rm -rf", "git push --force", "git push -f",
        "git reset --hard", "DROP TABLE", "DELETE FROM",
        "git checkout -- .", "format /", "fdisk", "mkfs",
    ],
    "high": [
        "npm publish", "chmod 777", "sudo rm",
        "docker rm -f", "ALTER TABLE", "TRUNCATE",
        "git branch -D", "git clean -fd",
    ],
    "medium": [
        "git merge", "git rebase",
        "npm install", "overwrite",
    ],
}


@dataclass
class GateResult:
    """Result of a quality gate check."""
    gate_name: str
    passed: bool
    risk_level: RiskLevel = "low"
    details: str = ""
    blocking: bool = False  # if True, execution must stop

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class QualityReport:
    """Aggregated quality report for an execution plan."""
    gates_applied: int = 0
    gates_passed: int = 0
    gates_failed: int = 0
    risk_level: RiskLevel = "low"
    blocking_issues: list[str] = field(default_factory=list)
    results: list[GateResult] = field(default_factory=list)

    @property
    def can_proceed(self) -> bool:
        return len(self.blocking_issues) == 0

    def to_dict(self) -> dict:
        return {
            "gates_applied": self.gates_applied,
            "gates_passed": self.gates_passed,
            "gates_failed": self.gates_failed,
            "risk_level": self.risk_level,
            "can_proceed": self.can_proceed,
            "blocking_issues": self.blocking_issues,
            "results": [r.to_dict() for r in self.results],
        }


# ── Quality Gate Definitions ────────────────────────────────────────

# Classification → required verification depth
VERIFICATION_DEPTH = {
    "RC-1": ["syntax"],                              # investigation
    "RC-2": ["syntax", "functional"],                # comparison
    "RC-3": ["syntax", "import", "functional", "perf_sec"],  # implementation
    "RC-4": ["syntax", "import", "functional", "impact"],    # fixing
    "RC-5": ["syntax", "consistency"],               # design
    "RC-6": ["functional", "operational"],            # operational improvement
}

# Phase 4 QA 4-layer mapping
QA_GATES = {
    "syntax":      {"name": "構文検証",         "desc": "Syntax/format validation"},
    "import":      {"name": "インポート検証",     "desc": "Dependency/import check"},
    "functional":  {"name": "機能検証",         "desc": "Functional correctness test"},
    "perf_sec":    {"name": "性能・セキュリティ", "desc": "Performance and security audit"},
    "impact":      {"name": "影響範囲確認",      "desc": "Change impact analysis"},
    "consistency": {"name": "一貫性確認",        "desc": "Design consistency check"},
    "operational": {"name": "動作確認",         "desc": "Operational verification"},
}


# ── Quality Gate Engine ─────────────────────────────────────────────

class QualityGateEngine:
    """Injects quality gates into Layer 7 execution plans.

    Usage:
        controller = ExecutionController()
        plan = controller.plan(handoff)
        engine = QualityGateEngine()
        gated_plan, report = engine.apply(plan, classification)
    """

    def assess_risk(self, plan: ExecutionPlan) -> RiskLevel:
        """Scan all actions for dangerous patterns."""
        max_risk = "low"
        risk_order = {"low": 0, "medium": 1, "high": 2, "critical": 3}

        for action in plan.actions:
            target_lower = action.target.lower()
            desc_lower = action.description.lower()
            params_str = str(action.params).lower()
            combined = f"{target_lower} {desc_lower} {params_str}"

            for level in ["critical", "high", "medium"]:
                for pattern in DANGEROUS_PATTERNS[level]:
                    if pattern.lower() in combined:
                        if risk_order[level] > risk_order[max_risk]:
                            max_risk = level

        return max_risk

    def determine_gates(self, classification: str) -> list[str]:
        """Determine which quality gates apply based on classification."""
        # Extract RC from classification string
        rc = classification
        for key in VERIFICATION_DEPTH:
            if key in classification:
                rc = key
                break
        return VERIFICATION_DEPTH.get(rc, ["syntax", "functional"])

    def apply(self, plan: ExecutionPlan, classification: str) -> tuple[ExecutionPlan, QualityReport]:
        """Apply quality gates to an execution plan.

        1. Assess overall risk
        2. Determine required gates
        3. Inject gate actions into plan
        4. Return gated plan + quality report
        """
        report = QualityReport()

        # Step 1: Risk assessment
        report.risk_level = self.assess_risk(plan)

        # Critical risk = blocking
        if report.risk_level == "critical":
            result = GateResult(
                gate_name="risk_assessment",
                passed=False,
                risk_level="critical",
                details="Critical risk detected: destructive operations in plan",
                blocking=True,
            )
            report.results.append(result)
            report.gates_applied += 1
            report.gates_failed += 1
            report.blocking_issues.append(result.details)
            return plan, report

        # Step 2: Determine required gates
        gate_keys = self.determine_gates(classification)

        # Step 3: Inject gates into plan
        for gate_key in gate_keys:
            gate_def = QA_GATES.get(gate_key, {})
            gate_name = gate_def.get("name", gate_key)

            # Determine where to inject (after 実装/修正 for functional, after all for syntax)
            inject_after = "検証"
            if gate_key in ("syntax", "import"):
                inject_after = "実装" if "実装" in plan.steps_covered else "修正"
                if inject_after not in plan.steps_covered:
                    inject_after = plan.steps_covered[-1] if plan.steps_covered else None
            elif gate_key in ("perf_sec", "impact"):
                inject_after = "検証"

            if inject_after and inject_after in plan.steps_covered:
                gate_action = ExecutionAction(
                    action_type="bash",
                    target=f"quality_gate_{gate_key}",
                    params={"gate": gate_key, "gate_name": gate_name},
                    step=inject_after,
                    order=0,  # will be set by inject_gate
                    description=f"Quality Gate: {gate_name} — {gate_def.get('desc', '')}",
                    gate_before=True,
                )
                plan.inject_gate(inject_after, gate_action)

            # Record gate application
            result = GateResult(
                gate_name=gate_name,
                passed=True,  # gates pass by default until execution
                risk_level=report.risk_level,
                details=f"Gate '{gate_name}' injected after step '{inject_after}'",
            )
            report.results.append(result)
            report.gates_applied += 1
            report.gates_passed += 1

        # High risk = add extra diff review gate
        if report.risk_level == "high":
            diff_gate = ExecutionAction(
                action_type="bash",
                target="git diff --staged",
                params={"gate": "diff_review", "gate_name": "差分レビュー"},
                step="GitHub反映",
                order=0,
                description="Quality Gate: Staged diff review before push",
                gate_before=True,
            )
            if "GitHub反映" in plan.steps_covered:
                plan.inject_gate("GitHub反映", diff_gate)
                report.gates_applied += 1
                report.gates_passed += 1
                report.results.append(GateResult(
                    gate_name="差分レビュー",
                    passed=True,
                    risk_level="high",
                    details="Extra diff review gate added due to high risk",
                ))

        return plan, report

    def check_action_safety(self, action: ExecutionAction) -> GateResult:
        """Pre-flight safety check for a single action."""
        combined = f"{action.target} {action.description} {str(action.params)}".lower()

        for level in ["critical", "high"]:
            for pattern in DANGEROUS_PATTERNS[level]:
                if pattern.lower() in combined:
                    return GateResult(
                        gate_name=f"safety_{action.order}",
                        passed=level != "critical",
                        risk_level=level,
                        details=f"Pattern '{pattern}' found in action #{action.order}",
                        blocking=level == "critical",
                    )

        return GateResult(
            gate_name=f"safety_{action.order}",
            passed=True,
            risk_level="low",
            details="No dangerous patterns detected",
        )
