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
import os
import sys
import time
from datetime import datetime
from pathlib import Path

PKG = Path(__file__).parent

# ── Per-project state isolation ─────────────────────────────────────
# Knowledge that's globally relevant lives in SHARED_STATE_DIR.
# Project-specific learning (eval records, learned floors) is isolated
# under PER_PROJECT_STATE_ROOT/<project>/ to prevent cross-contamination.

PROJECT_PARENT_ROOTS = [
    Path.home() / "プログラム開発",
    Path.home() / "workspace",
]


def detect_project_name(user_cwd: Path | None) -> str:
    """cwd → project name. Returns '_default' if outside known parents."""
    if user_cwd is None:
        return "_default"
    try:
        resolved = user_cwd.resolve()
    except OSError:
        return "_default"
    for parent in PROJECT_PARENT_ROOTS:
        try:
            parent_resolved = parent.resolve()
            rel = resolved.relative_to(parent_resolved)
            if rel.parts:
                return rel.parts[0]
        except (ValueError, OSError):
            continue
    return "_default"

# Add all layer paths
for subdir in ["phase6_model_selection", "layer7_execution_control",
               "layer8_quality_gates", "layer9_connection_bootstrap",
               "layer10_watch_sync", "layer11_continuous_eval"]:
    sys.path.insert(0, str(PKG / subdir))

from execution_controller import (
    ExecutionController, ExecutionPlan, ActionDispatcher,
    ExecutionResult, detect_runtime, load_dynamic_actions,
)
from quality_gate_engine import QualityGateEngine
from connection_bootstrap import ConnectionBootstrap
from watch_sync_engine import WatchSyncEngine
from catalog_updater import CatalogUpdater
from evaluation_engine import (
    EvaluationEngine, ExecutionRecord, ImprovementLoop,
)
from model_selector import ModelSelector, rc_to_model_input

SHARED_STATE_DIR = PKG / ".orchestra_state"
PER_PROJECT_STATE_ROOT = PKG / ".orchestra_state_per_project"

# Legacy alias — kept for any external references.
STATE_DIR = SHARED_STATE_DIR


class Orchestrator:
    """Full pipeline coordinator with closed feedback loops.

    State layout (hybrid isolation):
      - SHARED_STATE_DIR:        watch/releases/capabilities (global knowledge)
      - project_state_dir:       eval/improvement/conn-cache (per-project learning)
    """

    def __init__(self, project_root: Path | None = None,
                 user_cwd: Path | None = None):
        self.project_root = (project_root or PKG).resolve()

        # Resolve user_cwd from env if not explicitly passed (hook sets this)
        if user_cwd is None:
            env_cwd = os.environ.get("ORCHESTRA_USER_CWD", "")
            if env_cwd:
                try:
                    user_cwd = Path(env_cwd)
                except Exception:
                    user_cwd = None

        # Set up the two-tier state directories
        SHARED_STATE_DIR.mkdir(exist_ok=True)
        self.shared_state_dir = SHARED_STATE_DIR
        self.project_name = detect_project_name(user_cwd)
        if self.project_name == "_default":
            self.project_state_dir = SHARED_STATE_DIR
        else:
            self.project_state_dir = PER_PROJECT_STATE_ROOT / self.project_name
            self.project_state_dir.mkdir(parents=True, exist_ok=True)

        dyn_actions = load_dynamic_actions(self.shared_state_dir)
        self.controller = ExecutionController(dynamic_actions=dyn_actions)
        self.dispatcher = ActionDispatcher(project_root=self.project_root)
        self.gate_engine = QualityGateEngine()
        self.bootstrap = ConnectionBootstrap(project_root=self.project_root)

        # Shared state engines (global knowledge)
        self.watch_engine = WatchSyncEngine(
            state_path=self.shared_state_dir / "watch_state.json",
        )
        self.catalog_updater = CatalogUpdater(
            state_dir=self.shared_state_dir,
            catalog_path=PKG / "phase1_information_foundation" / "02_candidate_catalog.md",
        )

        # Per-project engines (project-specific learning)
        self.evaluator = EvaluationEngine(
            state_path=self.project_state_dir / "eval_state.json",
        )
        self.improvement_loop = ImprovementLoop(
            config_path=self.project_state_dir / "improvement_config.json",
            evaluator=self.evaluator,
        )

        self._runtime = detect_runtime()
        self._dynamic_caps = self.catalog_updater.get_dynamic_capabilities()

    def run(self, request: str) -> dict:
        """Full pipeline: request -> execution -> feedback."""
        result = {"request": request, "steps": {}, "outcome": ""}

        # Step 1: Classify
        classification = self._classify(request)
        result["steps"]["classification"] = classification

        # Lite mode: research/comparison tasks skip the execution pipeline entirely
        _LITE_RCS = {"RC-1", "RC-2"}
        if classification in _LITE_RCS:
            model_input = rc_to_model_input(classification, request)
            model_output = ModelSelector().select(model_input)
            result["steps"]["model"] = {
                "recommended": model_output.recommended_model,
                "fallback": model_output.fallback_model,
                "overrides_applied": False,
            }
            result["steps"]["capabilities"] = [
                c["item_id"] for c in self._select_capabilities(classification, request)
            ]
            result["outcome"] = "success"
            return result

        # Step 2: Model selection WITH Layer 11 overrides (closed loop)
        # Map Layer 11 improvement keys → Phase 6 SelectionInput keys
        VALID_OVERRIDE_KEYS = {
            "reasoning_weight", "ambiguity", "failure_cost",
            "speed_priority", "context_size", "plan_weight",
        }
        OVERRIDE_KEY_MAP = {
            "speed_priority_boost": "speed_priority",
            "reasoning_boost": "reasoning_weight",
        }
        raw_overrides = self.improvement_loop.get_active_overrides().get("model_overrides", {})
        overrides = {}
        for k, v in raw_overrides.items():
            if k in VALID_OVERRIDE_KEYS:
                overrides[k] = v
            elif k in OVERRIDE_KEY_MAP and isinstance(v, (int, float)):
                mapped_key = OVERRIDE_KEY_MAP[k]
                # Boost: add to existing default or use as delta
                overrides[mapped_key] = overrides.get(mapped_key, 0.5) + v
        model_input = rc_to_model_input(classification, request, overrides or None)
        selector = ModelSelector()
        model_output = selector.select(model_input)

        # Floor application: default → per-RC learned floor (both can elevate)
        _TIER = {"haiku": 0, "sonnet": 1, "opusplan": 2, "opus": 3}

        # 1) User-preferred default floor (e.g. "opus everywhere")
        default_floor = raw_overrides.get("default_model_floor", "")
        if default_floor and _TIER.get(model_output.recommended_model, 1) < _TIER.get(default_floor, 1):
            model_output.recommended_model = default_floor
            model_output.reason = f"{model_output.reason} [default-floor: {default_floor}]"

        # 2) Per-RC learned floor (Phase 2 closed loop)
        floor_map = raw_overrides.get("rc_model_floor", {})
        learned_floor = floor_map.get(classification)
        if learned_floor and _TIER.get(model_output.recommended_model, 1) < _TIER.get(learned_floor, 1):
            model_output.recommended_model = learned_floor
            model_output.reason = f"{model_output.reason} [learned-floor: {classification}→{learned_floor}]"

        result["steps"]["model"] = {
            "recommended": model_output.recommended_model,
            "fallback": model_output.fallback_model,
            "overrides_applied": bool(overrides),
            "default_floor_applied": bool(default_floor),
            "learned_floor_applied": bool(learned_floor),
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

        # Step 6: Connection prep — TTL-cached (startup + explicit request only)
        cached_ready = self._conn_cache_get()
        if cached_ready is True:
            result["steps"]["connections"] = {"cached": True, "ready": True}
        elif cached_ready is False:
            result["outcome"] = "blocked_by_connections"
            result["steps"]["connections"] = {"cached": True, "ready": False}
            result["steps"]["blocking_connections"] = ["(cached) MCP接続が利用不可 — /orchestrate-statusで再確認"]
            return result
        else:
            reqs = self.bootstrap.extract_requirements(gated_plan)
            prep = self.bootstrap.prepare(reqs)
            result["steps"]["connections"] = prep.to_dict()
            final_check = prep.recheck_report or prep.check_report
            ready = bool(final_check and final_check.ready)
            self._conn_cache_set(ready)
            if not ready:
                result["outcome"] = "blocked_by_connections"
                result["steps"]["blocking_connections"] = getattr(final_check, "blocking_gaps", [])
                return result

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

        # Step 9: Improvement cycle — daily TTL (was: every prompt, generating noise)
        if self._improvement_ttl_expired():
            applied = self.improvement_loop.run_cycle()
            result["steps"]["improvements"] = {"applied": len(applied)}
            self._improvement_ttl_mark()
        else:
            result["steps"]["improvements"] = {"skipped": "daily_ttl"}

        return result

    _IMPROVEMENT_TTL_SECONDS = 86400  # 24 hours

    def _improvement_ttl_expired(self) -> bool:
        p = self.project_state_dir / "last_improvement_cycle.json"
        if not p.exists():
            return True
        try:
            ts = datetime.fromisoformat(json.loads(p.read_text())["ts"])
            return (datetime.now() - ts).total_seconds() >= self._IMPROVEMENT_TTL_SECONDS
        except Exception:
            return True

    def _improvement_ttl_mark(self) -> None:
        p = self.project_state_dir / "last_improvement_cycle.json"
        p.write_text(json.dumps({"ts": datetime.now().isoformat()}))

    def watch_cycle(self) -> dict:
        """Watch/sync with Phase 5 re-assessment + auto-catalog update."""
        report = self.watch_engine.check_all()

        recheck_results = []
        for event_dict in self.watch_engine.get_pending_reeval():
            raw = event_dict.get("raw_data", {})
            recheck_results.append({
                "target": raw.get("name"),
                "change_type": raw.get("change_type", "update"),
            })

        if recheck_results:
            self.watch_engine.clear_pending()

        # Auto-catalog update: fetch releases and discover new capabilities
        catalog_result = self.catalog_updater.update_from_releases()
        if catalog_result.get("catalog_entries_added", 0) > 0:
            # Reload dynamic capabilities
            self._dynamic_caps = self.catalog_updater.get_dynamic_capabilities()

        return {
            "targets_checked": report.targets_checked,
            "changes_detected": report.changes_detected,
            "important_changes": report.important_changes,
            "reeval_processed": len(recheck_results),
            "catalog_update": {
                "releases_checked": catalog_result.get("releases_checked", 0),
                "new_capabilities": catalog_result.get("new_capabilities", []),
                "entries_added": catalog_result.get("catalog_entries_added", 0),
            },
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
            (self.shared_state_dir / "last_continuous_cycle.json").write_text(
                json.dumps(status, indent=2, ensure_ascii=False, default=str),
            )
            cycles += 1
            if cycles < max_cycles:
                time.sleep(1)
        return {"cycles_completed": cycles}

    def status(self) -> dict:
        dyn_caps = self._dynamic_caps.get("capabilities", [])
        return {
            "runtime": self._runtime,
            "project": self.project_name,
            "shared_state_dir": str(self.shared_state_dir),
            "project_state_dir": str(self.project_state_dir),
            "watch_state": {
                "targets": len(self.watch_engine.targets),
                "known_hashes": len(self.watch_engine.state.known_hashes),
                "pending_events": len(self.watch_engine.state.pending_events),
            },
            "dynamic_capabilities": {
                "count": len(dyn_caps),
                "ids": [c.get("item_id", "") for c in dyn_caps],
                "last_release": self._dynamic_caps.get("last_release_tag", ""),
                "last_updated": self._dynamic_caps.get("last_updated", ""),
            },
            "improvement": self.improvement_loop.get_active_overrides(),
            "evaluator": {
                "records": len(self.evaluator.state.records),
            },
        }

    # ── Internal ────────────────────────────────────────────────────

    _CONN_CACHE_TTL = 600  # seconds

    def _conn_cache_get(self) -> bool | None:
        """Return cached ready-state (True/False) or None if cache miss/expired."""
        p = self.project_state_dir / "conn_check_cache.json"
        if not p.exists():
            return None
        try:
            d = json.loads(p.read_text())
            age = (datetime.now() - datetime.fromisoformat(d["ts"])).total_seconds()
            if age < self._CONN_CACHE_TTL:
                return bool(d["ready"])
        except Exception:
            pass
        return None

    def _conn_cache_set(self, ready: bool) -> None:
        p = self.project_state_dir / "conn_check_cache.json"
        p.write_text(json.dumps({"ts": datetime.now().isoformat(), "ready": ready}))

    def _classify(self, request: str) -> str:
        req_lower = request.lower()
        keywords = {
            "AU-1": ["監査", "独立検証", "疑って", "裏どり", "ゼロベース", "脆弱性"],
            "RC-4": ["直して", "バグ", "動かない", "修正", "fix", "bug", "修繕", "回収"],
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
        """Phase 5 準拠の3段階能力選定。

        段階1: 分類に応じた候補プール決定
        段階2: 依頼内容に基づくキーワード適合判定
        段階3: 基盤能力 + キーワード適合能力を最終決定
        """
        # ── 段階1: 候補プール（03_capability_selection.md 準拠）──
        CANDIDATE_POOLS: dict[str, list[tuple[str, str]]] = {
            "AU-1": [
                ("F-003", "Subagents"), ("F-025", "Memory Tool"), ("F-032", "promptfoo"),
            ],
            "RC-1": [
                ("F-002", "MCP"), ("F-003", "Subagents"), ("F-005", "Skills"),
                ("F-019", "MCP Servers"), ("F-025", "Memory Tool"), ("F-032", "promptfoo"),
            ],
            "RC-2": [
                ("F-002", "MCP"), ("F-003", "Subagents"), ("F-013", "anthropics/skills"),
                ("F-019", "MCP Servers"), ("F-025", "Memory Tool"), ("F-032", "promptfoo"),
            ],
            "RC-3": [
                ("F-002", "MCP"), ("F-003", "Subagents"), ("F-004", "Hooks"),
                ("F-005", "Skills"), ("F-009", "Agent SDK"),
                ("F-010", "GitHub Actions"), ("F-014", "claude-code-action"),
                ("F-015", "claude-agent-sdk-python"), ("F-025", "Memory Tool"),
            ],
            "RC-4": [
                ("F-002", "MCP"), ("F-003", "Subagents"), ("F-004", "Hooks"),
                ("F-010", "GitHub Actions"), ("F-025", "Memory Tool"),
            ],
            "RC-5": [
                ("F-002", "MCP"), ("F-003", "Subagents"), ("F-009", "Agent SDK"),
                ("F-015", "claude-agent-sdk-python"), ("F-019", "MCP Servers"),
                ("F-025", "Memory Tool"),
            ],
            "RC-6": [
                ("F-002", "MCP"), ("F-004", "Hooks"), ("F-005", "Skills"),
                ("F-010", "GitHub Actions"), ("F-011", "Scheduled Tasks"),
                ("F-014", "claude-code-action"), ("F-025", "Memory Tool"),
            ],
        }

        # ── 段階2: 基盤能力 + キーワード適合 ──
        # 基盤能力（キーワード不要で選定される最小セット）
        BASE_CAPABILITIES: dict[str, list[str]] = {
            "AU-1": ["F-003", "F-032"],            # Subagents + promptfoo (audit requires both)
            "RC-1": ["F-003"],                     # Subagents
            "RC-2": ["F-032"],                     # promptfoo
            "RC-3": ["F-002", "F-004"],            # MCP, Hooks
            "RC-4": ["F-003"],                     # Subagents
            "RC-5": ["F-002", "F-009"],            # MCP, Agent SDK
            "RC-6": [],                            # なし（依頼内容で特定）
        }

        # 能力ごとのキーワード（依頼文にこれらが含まれていれば選定）
        CAPABILITY_KEYWORDS: dict[str, list[str]] = {
            "F-002": ["mcp", "プロトコル", "サーバー接続", "接続"],
            "F-003": ["サブエージェント", "並列", "subagent", "agent", "調査"],
            "F-004": ["hook", "フック", "イベント", "自動チェック"],
            "F-005": ["skill", "スキル"],
            "F-009": ["agent sdk", "sdk", "エージェント構築"],
            "F-010": ["github action", "ci", "cd", "pr", "プルリクエスト",
                       "レビュー", "自動テスト", "ワークフロー", "actions"],
            "F-011": ["schedule", "定期", "cron", "スケジュール", "タイマー"],
            "F-013": ["marketplace", "マーケットプレイス", "公開skill"],
            "F-014": ["claude-code-action", "github action", "ci/cd"],
            "F-015": ["python agent", "python sdk"],
            "F-019": ["mcp server", "mcpサーバー", "外部サーバー"],
            "F-025": ["memory", "メモリ", "記憶", "永続"],
            "F-032": ["eval", "評価", "promptfoo", "比較テスト"],
        }

        pool = list(CANDIDATE_POOLS.get(classification, CANDIDATE_POOLS["RC-1"]))
        base_ids = set(BASE_CAPABILITIES.get(classification, []))
        req_lower = request.lower()

        # ── 動的能力の統合: dynamic_capabilities.json から追加 ──
        dynamic_keywords = dict(CAPABILITY_KEYWORDS)
        for dcap in self._dynamic_caps.get("capabilities", []):
            dcap_id = dcap.get("item_id", "")
            dcap_name = dcap.get("name", "")
            dcap_rcs = dcap.get("applicable_rcs", [])
            dcap_kws = dcap.get("keywords", [])

            # このRCに適用可能なら候補プールに追加
            if classification in dcap_rcs and not any(f == dcap_id for f, _ in pool):
                pool.append((dcap_id, dcap_name))
                dynamic_keywords[dcap_id] = dcap_kws

        selected = []
        for fid, name in pool:
            is_base = fid in base_ids
            # キーワード適合チェック
            keywords = dynamic_keywords.get(fid, [])
            keyword_matched = any(kw in req_lower for kw in keywords)

            if is_base or keyword_matched:
                match_type = "base capability" if is_base else "keyword match"
                selected.append({
                    "item_id": fid, "name": name,
                    "step": name, "role": name,
                    "matched": match_type,
                })

        # 最低1つは選定する（調査系のフォールバック）
        if not selected:
            selected.append({
                "item_id": "F-003", "name": "Subagents",
                "step": "Subagents", "role": "Subagents",
                "matched": "fallback",
            })

        return selected

    def _build_handoff(self, classification, capabilities, model_output) -> dict:
        step_map = {
            "AU-1": ["独立調査", "証拠収集", "反証試行", "検証レポート"],
            "RC-1": ["調査", "記録", "GitHub反映"],
            "RC-2": ["調査", "比較", "記録", "GitHub反映"],
            "RC-3": ["調査", "実装", "検証", "GitHub反映"],
            "RC-4": ["調査", "修正", "検証", "GitHub反映"],
            "RC-5": ["調査", "比較", "設計", "記録"],
            "RC-6": ["調査", "実装", "検証", "GitHub反映"],
        }
        return {
            "classification": classification,
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
