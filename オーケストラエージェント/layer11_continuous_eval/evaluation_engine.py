#!/usr/bin/env python3
"""
Layer 11: Continuous Evaluation & Improvement (継続評価・改善層)
============================================================
Measures execution results. Re-evaluates model/capability/tool selection.
Feeds improvements back into standards. Uses all prior layers.

goal: Measure results, improve selections, close the feedback loop
inputs: Execution records from Layers 7-10 + Phase 5/6 decisions
core_logic: Metrics collection → accuracy assessment → improvement proposals
activation_rule: After every execution cycle; periodic summary analysis
verification: Results measured, improvements identified, fed back into operations
handoff: Improvement signals → Phase 5 absorb_update + Phase 6 recheck
"""

from __future__ import annotations

import json
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from datetime import datetime
from pathlib import Path


Outcome = Literal["success", "partial", "failure", "skipped"]


@dataclass
class ExecutionRecord:
    """Record of a single execution cycle's results."""
    record_id: str
    classification: str          # RC-1 to RC-6
    model_used: str              # actual model alias
    model_recommended: str       # what Phase 6 recommended
    capabilities_used: list[str] # F-XXX IDs actually used
    capabilities_recommended: list[str]  # what Phase 5 recommended
    outcome: Outcome
    quality_gate_passed: bool
    connection_issues: list[str] = field(default_factory=list)
    duration_seconds: float = 0.0
    error_details: str = ""
    created_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class AccuracyMetrics:
    """Accuracy metrics for a decision type."""
    total_decisions: int = 0
    correct_decisions: int = 0
    overqualified: int = 0    # used heavier resource than needed
    underqualified: int = 0   # used lighter resource than needed
    mismatches: int = 0       # recommended != used

    @property
    def accuracy(self) -> float:
        if self.total_decisions == 0:
            return 1.0
        return self.correct_decisions / self.total_decisions

    @property
    def efficiency(self) -> float:
        if self.total_decisions == 0:
            return 1.0
        return 1.0 - (self.overqualified / self.total_decisions)

    def to_dict(self) -> dict:
        return {
            "total": self.total_decisions,
            "correct": self.correct_decisions,
            "accuracy": round(self.accuracy, 3),
            "efficiency": round(self.efficiency, 3),
            "overqualified": self.overqualified,
            "underqualified": self.underqualified,
            "mismatches": self.mismatches,
        }


@dataclass
class ImprovementProposal:
    """A concrete improvement recommendation."""
    target: str          # what to improve (model_selection, capability_selection, etc.)
    action: str          # what to do
    reason: str          # why
    priority: Literal["high", "medium", "low"] = "medium"
    evidence: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class EvaluationReport:
    """Full evaluation report."""
    period_start: str = ""
    period_end: str = ""
    total_executions: int = 0
    success_rate: float = 0.0
    model_accuracy: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    capability_accuracy: AccuracyMetrics = field(default_factory=AccuracyMetrics)
    proposals: list[ImprovementProposal] = field(default_factory=list)
    classification_stats: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return {
            "period": f"{self.period_start} → {self.period_end}",
            "total_executions": self.total_executions,
            "success_rate": round(self.success_rate, 3),
            "model_accuracy": self.model_accuracy.to_dict(),
            "capability_accuracy": self.capability_accuracy.to_dict(),
            "proposals": [p.to_dict() for p in self.proposals],
            "classification_stats": self.classification_stats,
        }


@dataclass
class EvaluationState:
    """Persisted evaluation state."""
    records: list[dict] = field(default_factory=list)
    last_report: dict = field(default_factory=dict)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"records": self.records, "last_report": self.last_report},
                      f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "EvaluationState":
        if not path.exists():
            return cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            records=data.get("records", []),
            last_report=data.get("last_report", {}),
        )


# ── Model tier for accuracy comparison ──────────────────────────────

MODEL_TIERS = {"haiku": 0, "sonnet": 1, "opusplan": 2, "opus": 3}


# ── Evaluation Engine ──────────────────────────────────────────────

class EvaluationEngine:
    """Measures execution results, assesses selection accuracy, proposes improvements.

    Usage:
        engine = EvaluationEngine(state_path)
        engine.record(execution_record)
        report = engine.analyze()
        for proposal in report.proposals:
            # feed back into Phase 5/6
    """

    def __init__(self, state_path: Path | None = None):
        self.state_path = state_path or Path("evaluation_state.json")
        self.state = EvaluationState.load(self.state_path)

    def record(self, record: ExecutionRecord):
        """Record a completed execution for evaluation."""
        self.state.records.append(record.to_dict())
        self.state.save(self.state_path)

    def analyze(self, last_n: int = 50) -> EvaluationReport:
        """Analyze recent execution records and generate report."""
        records_raw = self.state.records[-last_n:]
        if not records_raw:
            return EvaluationReport()

        records = [self._dict_to_record(r) for r in records_raw]

        report = EvaluationReport(
            period_start=records[0].created_at if records else "",
            period_end=records[-1].created_at if records else "",
            total_executions=len(records),
        )

        # Success rate
        successes = sum(1 for r in records if r.outcome == "success")
        report.success_rate = successes / len(records) if records else 0.0

        # Model selection accuracy
        report.model_accuracy = self._assess_model_accuracy(records)

        # Capability selection accuracy
        report.capability_accuracy = self._assess_capability_accuracy(records)

        # Classification stats
        rc_counts = {}
        for r in records:
            rc_counts[r.classification] = rc_counts.get(r.classification, 0) + 1
        report.classification_stats = rc_counts

        # Generate improvement proposals
        report.proposals = self._generate_proposals(records, report)

        # Persist
        self.state.last_report = report.to_dict()
        self.state.save(self.state_path)

        return report

    def get_last_report(self) -> dict:
        """Return the most recent evaluation report."""
        return self.state.last_report

    def _assess_model_accuracy(self, records: list[ExecutionRecord]) -> AccuracyMetrics:
        """Assess how well model selection matched actual needs."""
        metrics = AccuracyMetrics()

        for r in records:
            if not r.model_recommended:
                continue
            metrics.total_decisions += 1
            rec_tier = MODEL_TIERS.get(r.model_recommended, 1)
            used_tier = MODEL_TIERS.get(r.model_used, 1)

            if r.model_used == r.model_recommended:
                if r.outcome == "success":
                    metrics.correct_decisions += 1
                elif r.outcome == "failure":
                    metrics.underqualified += 1
            elif used_tier > rec_tier:
                metrics.overqualified += 1
            elif used_tier < rec_tier:
                metrics.mismatches += 1
                if r.outcome == "failure":
                    metrics.underqualified += 1

        return metrics

    def _assess_capability_accuracy(self, records: list[ExecutionRecord]) -> AccuracyMetrics:
        """Assess how well capability selection matched actual usage."""
        metrics = AccuracyMetrics()

        for r in records:
            if not r.capabilities_recommended:
                continue
            metrics.total_decisions += 1
            rec_set = set(r.capabilities_recommended)
            used_set = set(r.capabilities_used)

            if rec_set == used_set and r.outcome == "success":
                metrics.correct_decisions += 1
            elif rec_set > used_set:
                metrics.overqualified += 1
            elif used_set > rec_set:
                metrics.mismatches += 1

        return metrics

    def _generate_proposals(self, records: list[ExecutionRecord],
                           report: EvaluationReport) -> list[ImprovementProposal]:
        """Generate concrete improvement proposals from analysis."""
        proposals = []

        # Proposal 1: Model accuracy too low
        if report.model_accuracy.total_decisions > 3 and report.model_accuracy.accuracy < 0.7:
            proposals.append(ImprovementProposal(
                target="model_selection",
                action="Review Phase 6 scoring weights — accuracy below 70%",
                reason=f"Model accuracy: {report.model_accuracy.accuracy:.0%}",
                priority="high",
                evidence=report.model_accuracy.to_dict(),
            ))

        # Proposal 2: Too many overqualified selections (wasting resources)
        if report.model_accuracy.total_decisions > 3 and report.model_accuracy.efficiency < 0.8:
            proposals.append(ImprovementProposal(
                target="model_selection",
                action="Lower scoring thresholds — too many opus/opusplan for simple tasks",
                reason=f"Efficiency: {report.model_accuracy.efficiency:.0%}",
                priority="medium",
                evidence=report.model_accuracy.to_dict(),
            ))

        # Proposal 3: Capability mismatch
        if report.capability_accuracy.total_decisions > 3 and report.capability_accuracy.mismatches > 2:
            proposals.append(ImprovementProposal(
                target="capability_selection",
                action="Review Phase 5 capability scoring — significant mismatch between recommended and used",
                reason=f"Mismatches: {report.capability_accuracy.mismatches}",
                priority="medium",
                evidence=report.capability_accuracy.to_dict(),
            ))

        # Proposal 4: High failure rate
        if report.total_executions > 3 and report.success_rate < 0.8:
            proposals.append(ImprovementProposal(
                target="execution_flow",
                action="Review execution pipeline — success rate below 80%",
                reason=f"Success rate: {report.success_rate:.0%}",
                priority="high",
                evidence={"success_rate": report.success_rate, "total": report.total_executions},
            ))

        # Proposal 5: Connection issues recurring
        conn_issues = [i for r in records for i in r.connection_issues]
        if len(conn_issues) > 2:
            from collections import Counter
            top_issues = Counter(conn_issues).most_common(3)
            proposals.append(ImprovementProposal(
                target="connection_bootstrap",
                action=f"Fix recurring connection issues: {', '.join(i[0] for i in top_issues)}",
                reason=f"{len(conn_issues)} connection issues in {len(records)} executions",
                priority="high" if len(conn_issues) > 5 else "medium",
                evidence={"top_issues": dict(top_issues)},
            ))

        return proposals

    def _dict_to_record(self, d: dict) -> ExecutionRecord:
        """Convert dict back to ExecutionRecord."""
        return ExecutionRecord(
            record_id=d.get("record_id", ""),
            classification=d.get("classification", ""),
            model_used=d.get("model_used", ""),
            model_recommended=d.get("model_recommended", ""),
            capabilities_used=d.get("capabilities_used", []),
            capabilities_recommended=d.get("capabilities_recommended", []),
            outcome=d.get("outcome", "failure"),
            quality_gate_passed=d.get("quality_gate_passed", False),
            connection_issues=d.get("connection_issues", []),
            duration_seconds=d.get("duration_seconds", 0.0),
            error_details=d.get("error_details", ""),
            created_at=d.get("created_at", ""),
        )


# ── Closed Improvement Loop ────────────────────────────────────────

@dataclass
class ImprovementConfig:
    """Persisted configuration adjustments from the feedback loop.
    Stored separately from source code — rollback-safe."""
    model_weight_overrides: dict = field(default_factory=dict)
    capability_priority_overrides: dict = field(default_factory=dict)
    applied_proposals: list[dict] = field(default_factory=list)
    rollback_snapshots: list[dict] = field(default_factory=list)
    version: int = 0

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w", encoding="utf-8") as f:
            json.dump(asdict(self), f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "ImprovementConfig":
        if not path.exists():
            return cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            model_weight_overrides=data.get("model_weight_overrides", {}),
            capability_priority_overrides=data.get("capability_priority_overrides", {}),
            applied_proposals=data.get("applied_proposals", []),
            rollback_snapshots=data.get("rollback_snapshots", []),
            version=data.get("version", 0),
        )

    def snapshot(self) -> dict:
        """Create rollback snapshot of current state."""
        return {
            "version": self.version,
            "model_weight_overrides": dict(self.model_weight_overrides),
            "capability_priority_overrides": dict(self.capability_priority_overrides),
            "timestamp": datetime.now().isoformat(),
        }


# Minimum evidence thresholds before auto-applying
APPLY_THRESHOLDS = {
    "model_selection": {"min_decisions": 5, "min_accuracy_gap": 0.15},
    "capability_selection": {"min_decisions": 5, "min_mismatches": 3},
    "execution_flow": {"min_executions": 5, "min_failure_rate": 0.25},
    "connection_bootstrap": {"min_issues": 3},
}


class ImprovementLoop:
    """Closed-loop improvement: analyze → propose → apply → verify → commit/rollback.

    Safety:
      - Threshold-based: only applies when evidence exceeds thresholds
      - Rollback-safe: snapshots config before every change
      - Audit trail: records every applied proposal with evidence
      - Bounded: adjustments are clamped to safe ranges

    Usage:
        loop = ImprovementLoop(config_path, eval_engine)
        applied = loop.run_cycle()
        # applied = list of proposals that were applied
    """

    def __init__(self, config_path: Path, evaluator: EvaluationEngine):
        self.config_path = config_path
        self.config = ImprovementConfig.load(config_path)
        self.evaluator = evaluator

    def run_cycle(self) -> list[dict]:
        """Full improvement cycle: analyze → filter → apply → verify."""
        report = self.evaluator.analyze()
        applied = []

        for proposal in report.proposals:
            if self._meets_threshold(proposal):
                success = self._apply_proposal(proposal)
                if success:
                    applied.append({
                        "proposal": proposal.to_dict(),
                        "applied_at": datetime.now().isoformat(),
                        "config_version": self.config.version,
                    })

        return applied

    def _meets_threshold(self, proposal: ImprovementProposal) -> bool:
        """Check if a proposal has enough evidence to be auto-applied."""
        thresholds = APPLY_THRESHOLDS.get(proposal.target, {})
        evidence = proposal.evidence

        if proposal.target == "model_selection":
            total = evidence.get("total", 0)
            accuracy = evidence.get("accuracy", 1.0)
            return (total >= thresholds.get("min_decisions", 5)
                    and (1.0 - accuracy) >= thresholds.get("min_accuracy_gap", 0.15))

        if proposal.target == "capability_selection":
            total = evidence.get("total", 0)
            mismatches = evidence.get("mismatches", 0)
            return (total >= thresholds.get("min_decisions", 5)
                    and mismatches >= thresholds.get("min_mismatches", 3))

        if proposal.target == "execution_flow":
            total = evidence.get("total", 0)
            rate = evidence.get("success_rate", 1.0)
            return (total >= thresholds.get("min_executions", 5)
                    and (1.0 - rate) >= thresholds.get("min_failure_rate", 0.25))

        if proposal.target == "connection_bootstrap":
            issues = evidence.get("top_issues", {})
            return sum(issues.values()) >= thresholds.get("min_issues", 3)

        return False

    def _apply_proposal(self, proposal: ImprovementProposal) -> bool:
        """Apply a single proposal with rollback safety."""
        # 1. Snapshot current state
        snapshot = self.config.snapshot()
        self.config.rollback_snapshots.append(snapshot)
        # Keep only last 10 snapshots
        self.config.rollback_snapshots = self.config.rollback_snapshots[-10:]

        # 2. Apply adjustment
        try:
            if proposal.target == "model_selection":
                self._adjust_model_weights(proposal)
            elif proposal.target == "capability_selection":
                self._adjust_capability_priorities(proposal)
            elif proposal.target == "execution_flow":
                self._record_execution_issue(proposal)
            elif proposal.target == "connection_bootstrap":
                self._record_connection_issue(proposal)
            else:
                return False

            # 3. Bump version and persist
            self.config.version += 1
            self.config.applied_proposals.append({
                "target": proposal.target,
                "action": proposal.action,
                "reason": proposal.reason,
                "applied_version": self.config.version,
                "timestamp": datetime.now().isoformat(),
            })
            self.config.save(self.config_path)
            return True

        except Exception:
            # 4. Rollback on failure
            self.rollback()
            return False

    def _adjust_model_weights(self, proposal: ImprovementProposal):
        """Adjust model selection weight overrides (clamped to safe range)."""
        evidence = proposal.evidence
        overqualified = evidence.get("overqualified", 0)
        underqualified = evidence.get("underqualified", 0)

        # If overqualified: slightly increase speed_priority weight
        if overqualified > underqualified:
            current = self.config.model_weight_overrides.get("speed_priority_boost", 0.0)
            self.config.model_weight_overrides["speed_priority_boost"] = min(current + 0.05, 0.2)
            self.config.model_weight_overrides["direction"] = "downgrade_bias"

        # If underqualified: slightly increase reasoning_weight
        elif underqualified > overqualified:
            current = self.config.model_weight_overrides.get("reasoning_boost", 0.0)
            self.config.model_weight_overrides["reasoning_boost"] = min(current + 0.05, 0.2)
            self.config.model_weight_overrides["direction"] = "upgrade_bias"

    def _adjust_capability_priorities(self, proposal: ImprovementProposal):
        """Record capability selection adjustment signals."""
        mismatches = proposal.evidence.get("mismatches", 0)
        self.config.capability_priority_overrides["needs_review"] = True
        self.config.capability_priority_overrides["mismatch_count"] = mismatches
        self.config.capability_priority_overrides["last_flagged"] = datetime.now().isoformat()

    def _record_execution_issue(self, proposal: ImprovementProposal):
        """Record execution flow issues for human review."""
        self.config.model_weight_overrides["execution_issues_flagged"] = True
        self.config.model_weight_overrides["success_rate"] = proposal.evidence.get("success_rate", 0)

    def _record_connection_issue(self, proposal: ImprovementProposal):
        """Record recurring connection issues."""
        self.config.capability_priority_overrides["connection_issues"] = proposal.evidence.get("top_issues", {})

    def rollback(self) -> bool:
        """Rollback to the last known-good configuration."""
        if not self.config.rollback_snapshots:
            return False
        snapshot = self.config.rollback_snapshots.pop()
        self.config.model_weight_overrides = snapshot.get("model_weight_overrides", {})
        self.config.capability_priority_overrides = snapshot.get("capability_priority_overrides", {})
        self.config.version = snapshot.get("version", 0)
        self.config.save(self.config_path)
        return True

    def get_active_overrides(self) -> dict:
        """Return current active overrides for integration with Phase 5/6."""
        return {
            "version": self.config.version,
            "model_overrides": self.config.model_weight_overrides,
            "capability_overrides": self.config.capability_priority_overrides,
            "applied_count": len(self.config.applied_proposals),
        }
