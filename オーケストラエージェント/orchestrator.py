#!/usr/bin/env python3
"""
Orchestrator: Full Autonomous Pipeline Coordinator
===================================================
Closes every loop: Phase 5 → Layer 7-11 → Phase 5/6 feedback.

Usage:
  python3 orchestrator.py "natural language request"
  python3 orchestrator.py --watch       # single watch/sync cycle
  python3 orchestrator.py --improve     # single improvement cycle
  python3 orchestrator.py --status      # current system status
  python3 orchestrator.py --runtime     # detect runtime capabilities
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime
from pathlib import Path

PKG = Path(__file__).parent

# Add all layer paths
for subdir in ["phase6_model_selection", "layer7_execution_control",
               "layer8_quality_gates", "layer9_connection_bootstrap",
               "layer10_watch_sync", "layer11_continuous_eval"]:
    sys.path.insert(0, str(PKG / subdir))

from execution_controller import (
    ExecutionController, ExecutionPlan, ActionDispatcher,
    ExecutionResult, detect_runtime,
)
from quality_gate_engine import QualityGateEngine
from connection_bootstrap import ConnectionBootstrap
from watch_sync_engine import WatchSyncEngine
from evaluation_engine import (
    EvaluationEngine, ExecutionRecord, ImprovementLoop,
)
from model_selector import ModelSelector, rc_to_model_input

STATE_DIR = PKG / ".orchestra_state"


class Orchestrator:
    """Full pipeline coordinator with closed feedback loops."""

    def __init__(self, project_root: Path | None = None):
        self.project_root = (project_root or PKG).resolve()
        STATE_DIR.mkdir(exist_ok=True)

        self.controller = ExecutionController()
        self.dispatcher = ActionDispatcher(project_root=self.project_root)
        self.gate_engine = QualityGateEngine()
        self.bootstrap = ConnectionBootstrap(project_root=self.project_root)

        self.watch_engine = WatchSyncEngine(
            state_path=STATE_DIR / "watch_state.json",
        )
        self.evaluator = EvaluationEngine(
            state_path=STATE_DIR / "eval_state.json",
        )
        self.improvement_loop = ImprovementLoop(
            config_path=STATE_DIR / "improvement_config.json",
            evaluator=self.evaluator,
        )
        self._runtime = detect_runtime()

    def run(self, request: str) -> dict:
        """Full pipeline: request -> execution -> feedback."""
        result = {"request": request, "steps": {}, "outcome": ""}

        # Step 1: Classify
        classification = self._classify(request)
        result["steps"]["classification"] = classification

        # Step 2: Model selection WITH Layer 11 overrides (closed loop)
        overrides = self.improvement_loop.get_active_overrides().get("model_overrides", {})
        model_input = rc_to_model_input(classification, request, overrides or None)
        selector = ModelSelector()
        model_output = selector.select(model_input)
        result["steps"]["model"] = {
            "recommended": model_output.recommended_model,
            "fallback": model_output.fallback_model,
            "overrides_applied": bool(overrides),
        }

        # Step 3: Capabilities
        capabilities = self._select_capabilities(classification, request)
        result["steps"]["capabilities"] = [c["item_id"] for c in capabilities]

        # Step 4: Plan
        handoff = self._build_handoff(classification, capabilities, model_output)
        plan = self.controller.plan(handoff)
        result["steps"]["plan"] = {
            "actions": plan.action_count, "steps": plan.steps_covered,
        }

        # Step 5: Quality gates
        gated_plan, qreport = self.gate_engine.apply(plan, classification)
        result["steps"]["quality_gates"] = {
            "applied": qreport.gates_applied,
            "can_proceed": qreport.can_proceed,
            "risk": qreport.risk_level,
        }
        if not qreport.can_proceed:
            result["outcome"] = "blocked_by_quality_gate"
            result["steps"]["blocking"] = qreport.blocking_issues
            return result

        # Step 6: Connection prep
        reqs = self.bootstrap.extract_requirements(gated_plan)
        prep = self.bootstrap.prepare(reqs)
        result["steps"]["connections"] = prep.to_dict()

        # Step 7: Execute
        exec_result = self.dispatcher.execute(gated_plan)
        result["steps"]["execution"] = exec_result.to_dict()
        result["outcome"] = exec_result.outcome

        # Step 8: Record (auto-convert Layer 7 -> Layer 11)
        record = self._result_to_record(
            exec_result, classification,
            model_output.recommended_model,
            [c["item_id"] for c in capabilities],
            qreport.can_proceed,
        )
        self.evaluator.record(record)
        result["steps"]["recorded"] = True

        # Step 9: Improvement cycle
        applied = self.improvement_loop.run_cycle()
        result["steps"]["improvements"] = {"applied": len(applied)}

        return result

    def watch_cycle(self) -> dict:
        """Watch/sync with Phase 5 re-evaluation integration."""
        report = self.watch_engine.check_all()

        reeval_results = []
        for event_dict in self.watch_engine.get_pending_reeval():
            raw = event_dict.get("raw_data", {})
            reeval_results.append({
                "target": raw.get("name"),
                "change_type": raw.get("change_type", "update"),
            })

        if reeval_results:
            self.watch_engine.clear_pending()

        return {
            "targets_checked": report.targets_checked,
            "changes_detected": report.changes_detected,
            "important_changes": report.important_changes,
            "reeval_processed": len(reeval_results),
        }

    def improve_cycle(self) -> dict:
        """Improvement cycle with feedback into Phase 6."""
        applied = self.improvement_loop.run_cycle()
        overrides = self.improvement_loop.get_active_overrides()
        return {"applied": len(applied), "active_overrides": overrides}

    def start_continuous(self, max_cycles: int = 1):
        """Run watch+improve loop."""
        cycles = 0
        while cycles < max_cycles:
            watch = self.watch_cycle()
            improve = self.improve_cycle()
            status = {
                "cycle": cycles, "timestamp": datetime.now().isoformat(),
                "watch": watch, "improve": improve,
            }
            (STATE_DIR / "last_continuous_cycle.json").write_text(
                json.dumps(status, indent=2, ensure_ascii=False, default=str),
            )
            cycles += 1
            if cycles < max_cycles:
                time.sleep(1)
        return {"cycles_completed": cycles}

    def status(self) -> dict:
        return {
            "runtime": self._runtime,
            "state_dir": str(STATE_DIR),
            "watch_state": {
                "targets": len(self.watch_engine.targets),
                "known_hashes": len(self.watch_engine.state.known_hashes),
                "pending_events": len(self.watch_engine.state.pending_events),
            },
            "improvement": self.improvement_loop.get_active_overrides(),
            "evaluator": {
                "records": len(self.evaluator.state.records),
            },
        }

    # ── Internal ────────────────────────────────────────────────────

    def _classify(self, request: str) -> str:
        req_lower = request.lower()
        keywords = {
            "RC-4": ["直して", "バグ", "動かない", "修正", "fix", "bug"],
            "RC-3": ["作って", "実装", "設定して", "構築", "作成", "implement", "build"],
            "RC-2": ["比較", "どちら", "選んで", "compare"],
            "RC-5": ["設計", "アーキテクチャ", "構造", "design"],
            "RC-6": ["効率", "自動化", "ワークフロー", "automate"],
            "RC-1": ["調べて", "調査", "確認", "現状", "check"],
        }
        for rc, kws in keywords.items():
            if any(kw in req_lower for kw in kws):
                return rc
        return "RC-1"

    def _select_capabilities(self, classification: str, request: str) -> list[dict]:
        pools = {
            "RC-1": [("F-003", "Subagents"), ("F-025", "Memory")],
            "RC-2": [("F-003", "Subagents"), ("F-032", "promptfoo")],
            "RC-3": [("F-002", "MCP"), ("F-003", "Subagents"), ("F-004", "Hooks")],
            "RC-4": [("F-003", "Subagents"), ("F-004", "Hooks")],
            "RC-5": [("F-003", "Subagents"), ("F-009", "Agent SDK")],
            "RC-6": [("F-004", "Hooks"), ("F-011", "Scheduled Tasks")],
        }
        pool = pools.get(classification, pools["RC-1"])
        return [{"item_id": fid, "name": name, "step": name, "role": name}
                for fid, name in pool]

    def _build_handoff(self, classification, capabilities, model_output) -> dict:
        step_map = {
            "RC-1": ["調査", "記録", "GitHub反映"],
            "RC-2": ["調査", "比較", "記録", "GitHub反映"],
            "RC-3": ["調査", "実装", "検証", "GitHub反映"],
            "RC-4": ["調査", "修正", "検証", "GitHub反映"],
            "RC-5": ["調査", "比較", "設計", "記録"],
            "RC-6": ["調査", "実装", "検証", "GitHub反映"],
        }
        return {
            "target": f"Determined by {classification} request analysis",
            "capabilities": capabilities,
            "work_order": step_map.get(classification, ["調査", "記録"]),
            "verification": ["構文検証", "機能検証"],
            "github": {"commit_format": "type(scope): description",
                        "pr_required": classification in ("RC-3", "RC-4", "RC-6"),
                        "push_target": "origin/main"},
            "model": {"recommended": model_output.recommended_model,
                       "fallback": model_output.fallback_model,
                       "reason": model_output.reason,
                       "recheck_required": model_output.recheck_required,
                       "handoff_notes": model_output.handoff_notes},
        }

    def _result_to_record(self, exec_result, classification,
                          model_recommended, caps_recommended,
                          quality_gate_passed) -> ExecutionRecord:
        return ExecutionRecord(
            record_id=f"orch-{datetime.now().strftime('%Y%m%d-%H%M%S')}",
            classification=classification,
            model_used=exec_result.model_used,
            model_recommended=model_recommended,
            capabilities_used=caps_recommended,
            capabilities_recommended=caps_recommended,
            outcome=exec_result.outcome,
            quality_gate_passed=quality_gate_passed,
        )


def main():
    orch = Orchestrator()
    if len(sys.argv) < 2:
        print("Usage: python3 orchestrator.py 'request' | --watch | --improve | --status | --runtime")
        sys.exit(0)

    arg = sys.argv[1]
    if arg == "--status":
        print(json.dumps(orch.status(), indent=2, ensure_ascii=False))
    elif arg == "--runtime":
        print(json.dumps(detect_runtime(), indent=2))
    elif arg == "--watch":
        print(json.dumps(orch.watch_cycle(), indent=2, ensure_ascii=False, default=str))
    elif arg == "--improve":
        print(json.dumps(orch.improve_cycle(), indent=2, ensure_ascii=False, default=str))
    elif arg == "--continuous":
        cycles = int(sys.argv[2]) if len(sys.argv) > 2 else 1
        print(json.dumps(orch.start_continuous(max_cycles=cycles), indent=2))
    else:
        print(json.dumps(orch.run(arg), indent=2, ensure_ascii=False, default=str))

if __name__ == "__main__":
    main()
