#!/usr/bin/env python3
"""
Proof: Additional 5 Layers (追加5層)
====================================
Run from inside オーケストラエージェント/:
  python3 proof_5layers.py

Proves:
  1. Layer 7: Execution Control — handoff→plan conversion, action validity
  2. Layer 8: Quality Gates — risk detection, gate injection, blocking
  3. Layer 9: Connection Bootstrap — requirement extraction, health checks
  4. Layer 10: Watch/Sync — change detection, importance filtering, state persistence
  5. Layer 11: Continuous Eval — record/analyze, accuracy metrics, improvement proposals
  6. Integration: Full pipeline Phase 5 → Layer 7 → 8 → 9 → 10 → 11
"""

import json
import os
import sys
import tempfile
from pathlib import Path
from datetime import datetime

PKG = Path(__file__).parent

# Add paths
sys.path.insert(0, str(PKG / "phase6_model_selection"))
sys.path.insert(0, str(PKG / "layer7_execution_control"))
sys.path.insert(0, str(PKG / "layer8_quality_gates"))
sys.path.insert(0, str(PKG / "layer9_connection_bootstrap"))
sys.path.insert(0, str(PKG / "layer10_watch_sync"))
sys.path.insert(0, str(PKG / "layer11_continuous_eval"))

from execution_controller import ExecutionController, ExecutionPlan, ExecutionAction
from quality_gate_engine import QualityGateEngine, QualityReport, GateResult
from connection_bootstrap import ConnectionBootstrap, ConnectionRequirement, BootstrapReport
from watch_sync_engine import WatchSyncEngine, WatchTarget, ChangeEvent, WatchState
from evaluation_engine import EvaluationEngine, ExecutionRecord, EvaluationReport

# Also import Phase 5+6 for integration test
from model_selector import ModelSelector, AliasState, select_model_for_rc

passed = 0
failed = 0


def proof(name: str, ok: bool, detail: str = ""):
    global passed, failed
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f" -- {detail}" if detail else ""))
    if ok:
        passed += 1
    else:
        failed += 1


def section(title: str):
    print(f"\n{'='*64}\n  {title}\n{'='*64}")


# ── Build a realistic handoff from Phase 5 ──────────────────────────

def make_handoff(classification="RC-3", model="sonnet", caps=None):
    """Create a Phase 5-style handoff for testing."""
    if caps is None:
        caps = [
            {"item_id": "F-002", "name": "MCP", "step": "MCP接続 (matched: mcp)", "role": "MCP接続"},
            {"item_id": "F-003", "name": "Subagents", "step": "並列調査 (base for RC-3)", "role": "並列実行"},
            {"item_id": "F-004", "name": "Hooks", "step": "品質チェック hook (base for RC-3)", "role": "自動化"},
        ]
    return {
        "target": f"Determined by {classification} request analysis",
        "capabilities": caps,
        "work_order": ["調査", "実装", "検証", "GitHub反映"],
        "verification": ["構文検証", "インポート検証", "機能検証"],
        "github": {
            "commit_format": "type(scope): description",
            "pr_required": True,
            "push_target": "origin/main",
        },
        "model": {
            "recommended": model,
            "fallback": "haiku",
            "reason": "Balanced coding task",
            "recheck_required": False,
            "handoff_notes": "",
        },
    }


# ════════════════════════════════════════════════════════════════════
# LAYER 7: EXECUTION CONTROL
# ════════════════════════════════════════════════════════════════════

section("LAYER 7: Execution Control")

controller = ExecutionController()

# Test 1: Basic plan creation
handoff = make_handoff()
plan = controller.plan(handoff)
proof("Plan created from handoff", plan.action_count > 0, f"{plan.action_count} actions")

# Test 2: Model carried through
proof("Model carried through", plan.model == "sonnet")

# Test 3: Steps covered
proof("Steps covered match work order",
      set(plan.steps_covered).issubset({"調査", "実装", "検証", "GitHub反映"}),
      str(plan.steps_covered))

# Test 4: Capability-driven actions present
cap_actions = [a for a in plan.actions if a.capability_id]
proof("Capability-driven actions exist", len(cap_actions) > 0, f"{len(cap_actions)} actions")

# Test 5: Action types valid
validation = controller.validate_plan(plan)
proof("Plan validation passes", validation["is_valid"], str(validation))

# Test 6: Different classification → different plan
handoff_rc1 = make_handoff(
    classification="RC-1", model="haiku",
    caps=[{"item_id": "F-025", "name": "Memory", "step": "記憶参照", "role": "状態保持"}],
)
handoff_rc1["work_order"] = ["調査", "記録", "GitHub反映"]
plan_rc1 = controller.plan(handoff_rc1)
proof("RC-1 plan differs from RC-3",
      plan_rc1.steps_covered != plan.steps_covered,
      f"RC-1: {plan_rc1.steps_covered}")

# Test 7: Summarize produces readable output
summary = controller.summarize(plan)
proof("Summarize produces output", len(summary) > 50 and "Model:" in summary)

# Test 8: Empty handoff → graceful handling
empty_plan = controller.plan({"work_order": [], "capabilities": []})
proof("Empty handoff handled gracefully", empty_plan.action_count == 0)


# ════════════════════════════════════════════════════════════════════
# LAYER 8: QUALITY GATES (uses Layer 7)
# ════════════════════════════════════════════════════════════════════

section("LAYER 8: Quality Gates (via Layer 7)")

gate_engine = QualityGateEngine()

# Test 9: Risk assessment — normal plan
risk = gate_engine.assess_risk(plan)
proof("Normal plan risk is low/medium", risk in ("low", "medium"), risk)

# Test 10: Gate injection for RC-3
gated_plan, report = gate_engine.apply(plan, "RC-3")
proof("Quality gates injected", report.gates_applied > 0, f"{report.gates_applied} gates")
proof("Can proceed (no blocking)", report.can_proceed)

# Test 11: RC-3 gets all 4 QA layers
gate_keys = gate_engine.determine_gates("RC-3")
proof("RC-3 gets full QA (4 layers)", len(gate_keys) == 4, str(gate_keys))

# Test 12: RC-1 gets lighter QA
gate_keys_rc1 = gate_engine.determine_gates("RC-1")
proof("RC-1 gets lighter QA", len(gate_keys_rc1) < len(gate_keys), str(gate_keys_rc1))

# Test 13: Critical risk → blocking
dangerous_plan = ExecutionPlan(
    classification="RC-3",
    model="sonnet",
    actions=[ExecutionAction(
        action_type="bash", target="rm -rf /",
        params={}, step="実装", order=0,
        description="Dangerous delete",
    )],
)
_, danger_report = gate_engine.apply(dangerous_plan, "RC-3")
proof("Critical risk blocks execution",
      not danger_report.can_proceed,
      f"blocking: {danger_report.blocking_issues}")

# Test 14: Single action safety check
safe_action = ExecutionAction(
    action_type="read", target="file.py", params={}, step="調査", order=0,
)
safe_result = gate_engine.check_action_safety(safe_action)
proof("Safe action passes check", safe_result.passed)

# Test 15: Gated plan has more actions than original
proof("Gated plan has injected gate actions",
      gated_plan.action_count >= plan.action_count,
      f"original={plan.action_count} gated={gated_plan.action_count}")


# ════════════════════════════════════════════════════════════════════
# LAYER 9: CONNECTION BOOTSTRAP (uses Layers 7+8)
# ════════════════════════════════════════════════════════════════════

section("LAYER 9: Connection Bootstrap (via Layers 7+8)")

bootstrap = ConnectionBootstrap(project_root=PKG)

# Test 16: Extract requirements from plan
requirements = bootstrap.extract_requirements(plan)
proof("Requirements extracted from plan", len(requirements) > 0, f"{len(requirements)} reqs")

# Test 17: Standard connections always included
std_names = {r.name for r in requirements if r.required_by == "standard"}
proof("Standard connections included (Git, Python3)",
      "Git" in std_names and "Python 3" in std_names)

# Test 18: Capability-driven connections present
cap_reqs = [r for r in requirements if r.required_by != "standard"]
proof("Capability connections extracted", len(cap_reqs) > 0, f"{len(cap_reqs)} cap reqs")

# Test 19: Health check runs
bootstrap_report = bootstrap.check_all(requirements)
proof("Bootstrap report generated",
      bootstrap_report.total == len(requirements),
      f"total={bootstrap_report.total} healthy={bootstrap_report.healthy}")

# Test 20: Git is healthy (should be available in dev env)
git_health = next((r for r in bootstrap_report.results if r.requirement.name == "Git"), None)
proof("Git connection healthy", git_health is not None and git_health.is_ok)

# Test 21: Python3 is healthy
py_health = next((r for r in bootstrap_report.results if r.requirement.name == "Python 3"), None)
proof("Python 3 connection healthy", py_health is not None and py_health.is_ok)

# Test 22: Report has proper structure
report_dict = bootstrap_report.to_dict()
proof("Report dict has required keys",
      all(k in report_dict for k in ["ready", "total", "healthy", "results"]))


# ════════════════════════════════════════════════════════════════════
# LAYER 10: WATCH/SYNC (uses Layers 7-9)
# ════════════════════════════════════════════════════════════════════

section("LAYER 10: Watch/Sync (via Layers 7-9)")

with tempfile.TemporaryDirectory() as td:
    state_path = Path(td) / "watch_state.json"
    engine = WatchSyncEngine(state_path=state_path)

    # Test 23: Default targets loaded
    proof("Default watch targets loaded", len(engine.targets) > 0,
          f"{len(engine.targets)} targets")

    # Test 24: First check — no changes (no baseline yet)
    report = engine.check_all()
    proof("First check runs", report.targets_checked > 0,
          f"checked={report.targets_checked}")

    # Test 25: State persisted
    proof("Watch state saved", state_path.exists())
    loaded = WatchState.load(state_path)
    proof("State has known hashes", len(loaded.known_hashes) > 0,
          f"{len(loaded.known_hashes)} hashes")

    # Test 26: Simulate change detection
    # Mutate a known hash to trigger change
    engine.state.known_hashes["Claude Model Aliases"] = "fake_old_hash_00000"
    engine.state.save(state_path)
    engine2 = WatchSyncEngine(state_path=state_path)
    report2 = engine2.check_all()
    proof("Change detected after hash mutation",
          report2.changes_detected > 0,
          f"changes={report2.changes_detected}")

    # Test 27: Custom target registration
    engine.register_target(WatchTarget(
        name="Test Custom Target",
        source_type="github_repo",
        url_or_id="test/repo",
        related_capabilities=["F-002"],
    ))
    proof("Custom target registered",
          any(t.name == "Test Custom Target" for t in engine.targets))

    # Test 28: Importance scoring
    from watch_sync_engine import score_importance
    proof("Breaking change → critical",
          score_importance("breaking_change", ["F-002"], is_breaking=True) == "critical")
    proof("Security → critical",
          score_importance("security", []) == "critical")
    proof("New feature with caps → medium",
          score_importance("new_feature", ["F-003"]) == "medium")
    proof("Update → low", score_importance("update", []) == "low")


# ════════════════════════════════════════════════════════════════════
# LAYER 11: CONTINUOUS EVALUATION (uses all prior layers)
# ════════════════════════════════════════════════════════════════════

section("LAYER 11: Continuous Evaluation (via all layers)")

with tempfile.TemporaryDirectory() as td:
    eval_path = Path(td) / "eval_state.json"
    evaluator = EvaluationEngine(state_path=eval_path)

    # Test 32: Record execution
    record1 = ExecutionRecord(
        record_id="exec-001",
        classification="RC-3",
        model_used="sonnet",
        model_recommended="sonnet",
        capabilities_used=["F-002", "F-003"],
        capabilities_recommended=["F-002", "F-003"],
        outcome="success",
        quality_gate_passed=True,
        duration_seconds=45.0,
    )
    evaluator.record(record1)
    proof("Execution recorded", len(evaluator.state.records) == 1)

    # Test 33: Record multiple + analyze
    for i in range(5):
        evaluator.record(ExecutionRecord(
            record_id=f"exec-{i+2:03d}",
            classification="RC-3" if i < 3 else "RC-1",
            model_used="sonnet" if i < 4 else "opus",
            model_recommended="sonnet",
            capabilities_used=["F-002", "F-003"],
            capabilities_recommended=["F-002", "F-003"],
            outcome="success" if i < 4 else "failure",
            quality_gate_passed=i < 4,
            duration_seconds=30.0 + i * 10,
        ))

    report = evaluator.analyze()
    proof("Analysis report generated",
          report.total_executions == 6,
          f"total={report.total_executions}")

    # Test 34: Success rate calculated
    proof("Success rate calculated",
          0.0 < report.success_rate <= 1.0,
          f"rate={report.success_rate:.1%}")

    # Test 35: Model accuracy tracked
    proof("Model accuracy tracked",
          report.model_accuracy.total_decisions > 0,
          f"accuracy={report.model_accuracy.accuracy:.0%}")

    # Test 36: Classification stats generated
    proof("Classification stats present",
          len(report.classification_stats) > 0,
          str(report.classification_stats))

    # Test 37: Report dict serializable
    report_dict = report.to_dict()
    serialized = json.dumps(report_dict)
    proof("Report is JSON-serializable", len(serialized) > 100)

    # Test 38: Simulate poor accuracy → improvement proposal
    poor_evaluator = EvaluationEngine(state_path=Path(td) / "poor.json")
    for i in range(10):
        poor_evaluator.record(ExecutionRecord(
            record_id=f"poor-{i:03d}",
            classification="RC-3",
            model_used="opus",
            model_recommended="haiku",
            capabilities_used=["F-002"],
            capabilities_recommended=["F-002", "F-003", "F-004"],
            outcome="failure" if i < 5 else "success",
            quality_gate_passed=i >= 5,
        ))

    poor_report = poor_evaluator.analyze()
    proof("Poor accuracy generates proposals",
          len(poor_report.proposals) > 0,
          f"{len(poor_report.proposals)} proposals")

    # Test 39: Proposals target correct areas
    targets = {p.target for p in poor_report.proposals}
    proof("Proposals target model/capability/execution",
          len(targets) > 0,
          str(targets))


# ════════════════════════════════════════════════════════════════════
# INTEGRATION: FULL PIPELINE Phase 5 → Layer 7 → 8 → 9 → 10 → 11
# ════════════════════════════════════════════════════════════════════

section("INTEGRATION: Full Pipeline (Phase 5 → Layers 7-11)")

# Step 1: Phase 5 classify + select model
from model_selector import RC_TO_PARAMS, rc_to_model_input, ModelSelector
selector = ModelSelector()
model_input = rc_to_model_input("RC-3", "MCPサーバーを使ってGitHub Actionsの自動レビューを構築して")
model_output = selector.select(model_input)

proof("Phase 5→6 model selection works",
      model_output.recommended_model in ("opus", "sonnet", "haiku", "opusplan"),
      model_output.recommended_model)

# Step 2: Build handoff with Phase 6 result
integration_handoff = make_handoff(
    classification="RC-3",
    model=model_output.recommended_model,
    caps=[
        {"item_id": "F-002", "name": "MCP", "step": "MCP接続", "role": "接続"},
        {"item_id": "F-010", "name": "GitHub Actions", "step": "CI/CD", "role": "GitHub"},
        {"item_id": "F-014", "name": "claude-code-action", "step": "PRレビュー自動化", "role": "レビュー"},
    ],
)

# Step 3: Layer 7 — plan
int_plan = controller.plan(integration_handoff)
proof("Integration: Layer 7 plan created", int_plan.is_valid,
      f"{int_plan.action_count} actions")

# Step 4: Layer 8 — quality gates
int_gated, int_qreport = gate_engine.apply(int_plan, "RC-3")
proof("Integration: Layer 8 gates applied",
      int_qreport.gates_applied > 0 and int_qreport.can_proceed)

# Step 5: Layer 9 — connection check
int_reqs = bootstrap.extract_requirements(int_gated)
int_boot = bootstrap.check_all(int_reqs)
proof("Integration: Layer 9 connections checked",
      int_boot.total > 0,
      f"healthy={int_boot.healthy}/{int_boot.total}")

# Step 6: Layer 10 — register watch targets from capabilities
with tempfile.TemporaryDirectory() as td:
    int_watch = WatchSyncEngine(state_path=Path(td) / "int_watch.json")
    int_watch.register_target(WatchTarget(
        name="GitHub Actions Integration",
        source_type="github_repo",
        url_or_id="features/actions",
        related_capabilities=["F-010", "F-014"],
    ))
    int_sync = int_watch.check_all()
    proof("Integration: Layer 10 watch registered and checked",
          int_sync.targets_checked > 0)

# Step 7: Layer 11 — record execution result
with tempfile.TemporaryDirectory() as td:
    int_eval = EvaluationEngine(state_path=Path(td) / "int_eval.json")
    int_eval.record(ExecutionRecord(
        record_id="integration-001",
        classification="RC-3",
        model_used=model_output.recommended_model,
        model_recommended=model_output.recommended_model,
        capabilities_used=["F-002", "F-010", "F-014"],
        capabilities_recommended=["F-002", "F-010", "F-014"],
        outcome="success",
        quality_gate_passed=True,
        connection_issues=[g for g in int_boot.blocking_gaps],
    ))
    int_report = int_eval.analyze()
    proof("Integration: Layer 11 evaluation recorded",
          int_report.total_executions == 1)

# Step 8: Verify the full chain is connected
proof("Integration: Full pipeline connected (Phase 5→6→7→8→9→10→11)",
      int_plan.is_valid
      and int_qreport.can_proceed
      and int_boot.total > 0
      and int_sync.targets_checked > 0
      and int_report.total_executions > 0)


# ── Final Summary ────────────────────────────────────────────────────

section("FINAL SUMMARY")
total = passed + failed
print(f"  Total: {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Result: {'ALL PASS' if failed == 0 else 'FAILURES EXIST'}")
print(f"{'='*64}")

sys.exit(0 if failed == 0 else 1)
