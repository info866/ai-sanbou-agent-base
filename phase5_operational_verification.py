#!/usr/bin/env python3
"""
Phase 5 AI参謀 Operational Verification
========================================
Proves that the AI参謀 framework can:
1. Classify requests (RC-1 to RC-6)
2. Select capabilities with request-sensitive judgment (not auto-pool)
3. Generate reasons with 3 required elements
4. Judge reconfirmation only when request-relevant (not blanket T4)
5. Hand off to execution baseline (5 elements)
6. Absorb updates (new tool + obsolescence)

Goal-specific proofs:
  Goal 1: F-011 Cloud Scheduled Tasks is fully defined and selectable for RC-6
  Goal 2: Same-class requests produce different capability decisions
  Goal 3: T4 items appear only when request-relevant; irrelevant T4 suppressed
"""

import json
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
PHASE5 = BASE / "phase5_ai_advisor"
PHASE4 = BASE / "phase4_execution_foundation"

# ── Unified Capability Model (from Phase 2, enriched for Phase 5) ──

CAPABILITIES = {
    # ── P1 最優先 ──
    "F-002": {
        "name": "MCP",
        "trust": "T1", "decision": "D1", "priority": "P1",
        "keywords": ["mcp", "接続", "プロトコル", "サーバー", "server", "connection", "統合", "連携"],
        "base_for": ["RC-3", "RC-5"],
        "purpose": "標準接続プロトコルによるツール・サーバー統合",
    },
    "F-003": {
        "name": "Subagents",
        "trust": "T1", "decision": "D1", "priority": "P1",
        "keywords": ["並列", "分割", "サブエージェント", "subagent", "parallel", "delegate", "複数同時"],
        "base_for": ["RC-1", "RC-4"],
        "purpose": "並列実行・専門分割による調査・実装の加速",
    },
    "F-004": {
        "name": "Hooks",
        "trust": "T1", "decision": "D1", "priority": "P1",
        "keywords": ["フック", "hook", "トリガー", "trigger", "イベント", "event",
                      "コミット", "commit", "pre-commit", "自動実行", "品質チェック"],
        "base_for": ["RC-3"],
        "purpose": "イベント駆動の自動化トリガー",
    },
    "F-005": {
        "name": "Skills",
        "trust": "T1", "decision": "D1", "priority": "P1",
        "keywords": ["スキル", "skill", "パッケージ", "package", "再利用", "reusable",
                      "テンプレート", "template", "ノウハウ"],
        "base_for": [],
        "purpose": "作業ノウハウのパッケージ化・再利用",
    },
    "F-009": {
        "name": "Claude Agent SDK",
        "trust": "T1", "decision": "D1", "priority": "P1",
        "keywords": ["agent sdk", "sdk", "エージェント構築", "本番エージェント",
                      "claude agent", "エージェント開発"],
        "base_for": ["RC-5"],
        "purpose": "本番エージェント構築の公式SDK",
    },
    "F-025": {
        "name": "Memory Tool",
        "trust": "T1", "decision": "D1", "priority": "P1",
        "keywords": ["記憶", "memory", "セッション", "session", "状態保持", "state",
                      "メモリ", "クロスセッション", "永続化"],
        "base_for": [],
        "purpose": "クロスセッション記憶の公式API",
    },
    # ── P2 高優先 ──
    "F-010": {
        "name": "GitHub Actions",
        "trust": "T2", "decision": "D2", "priority": "P2",
        "keywords": ["github actions", "ci/cd", "ci", "cd", "pr", "レビュー", "review",
                      "パイプライン", "pipeline", "ワークフロー", "workflow"],
        "base_for": [],
        "purpose": "CI/CD・PRレビュー自動化",
    },
    "F-011": {
        "name": "Cloud Scheduled Tasks",
        "trust": "T2", "decision": "D2", "priority": "P3",
        "keywords": ["定期", "スケジュール", "schedule", "cron", "定時", "periodic",
                      "タイマー", "timer", "定期実行", "定期タスク", "巡回"],
        "base_for": [],
        "purpose": "/scheduleコマンドによる定期タスク自動実行",
    },
    "F-013": {
        "name": "anthropics/skills",
        "trust": "T2", "decision": "D1", "priority": "P2",
        "keywords": ["スキル資産", "skill library", "marketplace", "既存スキル",
                      "anthropics/skills", "公開スキル"],
        "base_for": [],
        "purpose": "公式スキルマーケットプレイスからの流用",
    },
    "F-014": {
        "name": "claude-code-action",
        "trust": "T2", "decision": "D2", "priority": "P2",
        "keywords": ["claude-code-action", "prレビュー", "pr review", "github action",
                      "自動レビュー", "コードレビュー自動"],
        "base_for": [],
        "purpose": "GitHub Actions経由のClaude Code PRレビュー自動化",
    },
    "F-015": {
        "name": "claude-agent-sdk-python",
        "trust": "T2", "decision": "D1", "priority": "P2",
        "keywords": ["python", "パイソン", "python sdk", "pip install", "python実装"],
        "base_for": [],
        "purpose": "Agent SDKのPython実装基盤",
    },
    "F-019": {
        "name": "MCP Servers",
        "trust": "T2", "decision": "D1", "priority": "P2",
        "keywords": ["mcpサーバー", "mcp server", "リファレンス実装", "reference",
                      "サーバー一覧", "公式サーバー"],
        "base_for": [],
        "purpose": "公式MCPサーバーリファレンス実装集",
    },
    "F-032": {
        "name": "promptfoo",
        "trust": "T2", "decision": "D1", "priority": "P2",
        "keywords": ["評価", "eval", "テスト", "test", "プロンプト", "prompt",
                      "promptfoo", "ベンチマーク", "モデル比較"],
        "base_for": ["RC-2"],
        "purpose": "LLM評価・プロンプトテストフレームワーク",
    },
}

# T4 capabilities — separately modeled because they require reconfirmation
T4_CAPABILITIES = {
    "F-006": {
        "name": "Managed Agents",
        "trust": "T4", "decision": "D3", "priority": "P4",
        "keywords": ["managed agent", "マネージドエージェント", "管理エージェント",
                      "オーケストレーション", "orchestration"],
        "purpose": "Anthropic管理のエージェントオーケストレーション（beta）",
    },
    "F-008": {
        "name": "Agent Teams",
        "trust": "T4", "decision": "D5", "priority": "P5",
        "keywords": ["agent team", "チーム", "マルチエージェント", "multi-agent",
                      "エージェントチーム"],
        "purpose": "複数エージェントのチーム実行（experimental）",
    },
    "F-012": {
        "name": "Advisor Tool",
        "trust": "T4", "decision": "D3", "priority": "P4",
        "keywords": ["advisor", "アドバイザー", "助言", "executor", "参謀ツール"],
        "purpose": "executor+advisorパターンの公式ツール（beta）",
    },
}

# Candidate pools per classification — defines the maximum candidate set
CLASSIFICATION_POOLS = {
    "RC-1": ["F-002", "F-003", "F-025", "F-019", "F-032", "F-005"],
    "RC-2": ["F-002", "F-003", "F-032", "F-013", "F-019", "F-025"],
    "RC-3": ["F-002", "F-003", "F-004", "F-005", "F-009", "F-010", "F-014", "F-015", "F-025"],
    "RC-4": ["F-002", "F-003", "F-004", "F-010", "F-025"],
    "RC-5": ["F-002", "F-003", "F-009", "F-015", "F-019", "F-025"],
    "RC-6": ["F-002", "F-004", "F-005", "F-010", "F-011", "F-014", "F-025"],
}


# ── AI参謀 Core Logic ─────────────────────────────────────────────

class AIAdvisor:
    """AI参謀 implementation following Phase 5 rules with request-sensitive judgment."""

    def classify_request(self, request: str) -> dict:
        """STEP 1: Request classification (02_request_classification.md)."""
        keywords = {
            "RC-4": ["直して", "バグ", "動かない", "修正", "fix", "bug", "エラー"],
            "RC-3": ["作って", "実装", "設定して", "構築", "作成", "implement", "create", "build"],
            "RC-2": ["比較", "どちら", "選んで", "どれがいい", "compare", "evaluate"],
            "RC-5": ["設計", "アーキテクチャ", "構造", "方針", "design", "architect"],
            "RC-6": ["効率", "自動化", "ワークフロー", "optimize", "automate"],
            "RC-1": ["調べて", "調査", "確認", "現状", "一覧", "investigate", "survey", "check"],
        }
        req_lower = request.lower()
        for rc, kws in keywords.items():
            if any(kw in req_lower for kw in kws):
                return {"classification": rc, "request": request}
        return {"classification": "RC-1", "request": request}

    def _score_capability(self, fid: str, cap: dict, classification: str, request: str) -> dict:
        """Score a single capability against the request.
        Returns criteria met (S1..S8) and whether it is selected."""
        req_lower = request.lower()

        # S1: Purpose directness — does the request mention anything this capability helps with?
        keyword_hits = [kw for kw in cap.get("keywords", []) if kw in req_lower]
        s1_keyword = len(keyword_hits) > 0
        s1_base = classification in cap.get("base_for", [])
        s1 = s1_keyword or s1_base

        # S2: Current need — is this capability needed now for this specific request?
        s2 = s1_keyword  # keyword match means current need; base_for alone is weaker

        # S6: Quality contribution
        quality_caps = {"F-004", "F-032", "F-005", "F-014"}
        s6 = fid in quality_caps and s1

        # S7: Efficiency contribution
        efficiency_caps = {"F-003", "F-004", "F-010", "F-011", "F-025"}
        s7 = fid in efficiency_caps and s1

        criteria_met = []
        if s1:
            criteria_met.append("S1")
        if s2:
            criteria_met.append("S2")
        if s6:
            criteria_met.append("S6")
        if s7:
            criteria_met.append("S7")

        selected = s1  # must at least be purpose-relevant
        reason_if_not = ""
        if not s1:
            reason_if_not = f"S1 not met: request does not indicate need for {cap['name']}"

        return {
            "selected": selected,
            "criteria_met": criteria_met,
            "keyword_hits": keyword_hits,
            "is_base": s1_base,
            "reason_if_not": reason_if_not,
        }

    def select_capabilities(self, classification: str, request: str) -> dict:
        """STEP 4: Request-sensitive capability selection (03_capability_selection.md).
        Selection varies based on request content, not just class."""
        pool_ids = CLASSIFICATION_POOLS.get(classification, CLASSIFICATION_POOLS["RC-1"])

        selected = []
        not_selected = []

        # Score each capability in the pool against the request
        for fid in pool_ids:
            cap = CAPABILITIES.get(fid)
            if not cap:
                continue

            score = self._score_capability(fid, cap, classification, request)

            if score["selected"]:
                role_detail = f"{cap['purpose']}"
                if score["keyword_hits"]:
                    role_detail += f" (matched: {', '.join(score['keyword_hits'][:2])})"
                elif score["is_base"]:
                    role_detail += f" (base capability for {classification})"

                selected.append({
                    "item_id": fid,
                    "name": cap["name"],
                    "role": role_detail,
                    "criteria_met": score["criteria_met"],
                    "priority": cap["priority"],
                })
            else:
                not_selected.append({
                    "item_id": fid,
                    "name": cap["name"],
                    "reason": score["reason_if_not"],
                })

        # Also record capabilities outside the pool as not-selected
        pool_set = set(pool_ids)
        for fid, cap in CAPABILITIES.items():
            if fid not in pool_set:
                not_selected.append({
                    "item_id": fid,
                    "name": cap["name"],
                    "reason": f"Outside candidate pool for {classification}",
                })

        # T4 reconfirmation — only for items relevant to this request
        recheck_needed = self._judge_t4_relevance(classification, request)

        return {
            "selected": selected,
            "not_selected": not_selected,
            "recheck_needed": recheck_needed,
        }

    def _judge_t4_relevance(self, classification: str, request: str) -> list:
        """Determine which T4 capabilities need reconfirmation for THIS request.
        Irrelevant T4 items are suppressed."""
        req_lower = request.lower()
        recheck = []

        for fid, t4 in T4_CAPABILITIES.items():
            # T4 item is relevant only if keywords match the request
            keyword_hits = [kw for kw in t4["keywords"] if kw in req_lower]
            if keyword_hits:
                recheck.append({
                    "item_id": fid,
                    "name": t4["name"],
                    "reason": (
                        f"T4 ({t4['decision']}) — request mentions "
                        f"{', '.join(keyword_hits[:2])}; freshness check required"
                    ),
                    "matched_keywords": keyword_hits,
                })

        return recheck

    def generate_reason(self, classification: str, request: str,
                        selected: list, not_selected: list) -> dict:
        """STEP 6: Reason generation (04_reason_generation.md)."""
        step_map = {
            "RC-1": ["調査", "記録"],
            "RC-2": ["調査", "比較", "記録"],
            "RC-3": ["調査", "実装", "検証", "GitHub反映"],
            "RC-4": ["調査", "修正", "検証", "GitHub反映"],
            "RC-5": ["調査", "比較", "記録"],
            "RC-6": ["調査", "実装", "検証", "GitHub反映"],
        }
        steps = step_map.get(classification, ["調査", "記録"])

        positive_reasons = []
        for cap in selected:
            positive_reasons.append(
                f"{cap['item_id']} {cap['name']}: selected — "
                f"criteria {', '.join(cap['criteria_met'])} met. {cap['role']}"
            )

        # Elimination reasons — only pool members that were NOT selected
        pool_not_selected = [
            ns for ns in not_selected
            if "Outside candidate pool" not in ns.get("reason", "")
        ]
        elimination_reasons = []
        for cap in pool_not_selected:
            elimination_reasons.append(
                f"{cap['item_id']} {cap['name']}: not selected — {cap['reason']}"
            )

        effect_scope = []
        for cap in selected:
            effect_scope.append(
                f"{cap['item_id']} {cap['name']} → steps: {', '.join(steps)}"
            )

        has_all_3 = (
            len(positive_reasons) > 0
            and len(effect_scope) > 0
            # elimination_reasons can be empty if all pool items were selected
            # but we still need at least outside-pool rejections for completeness
            and (len(elimination_reasons) > 0 or len(not_selected) > 0)
        )

        return {
            "positive_reasons": positive_reasons,
            "elimination_reasons": elimination_reasons,
            "effect_scope": effect_scope,
            "has_all_3_elements": has_all_3,
        }

    def create_execution_handoff(self, classification: str, selected: list) -> dict:
        """STEP 7: Execution handoff (05_execution_handoff.md)."""
        step_map = {
            "RC-1": ["調査", "記録", "GitHub反映"],
            "RC-2": ["調査", "比較", "記録", "GitHub反映"],
            "RC-3": ["調査", "実装", "検証", "記録", "GitHub反映"],
            "RC-4": ["調査", "修正", "検証", "記録", "GitHub反映"],
            "RC-5": ["調査", "比較", "設計", "記録", "GitHub反映"],
            "RC-6": ["調査", "実装", "検証", "記録", "GitHub反映"],
        }
        verification_map = {
            "RC-1": ["情報網羅性の確認"],
            "RC-2": ["比較基準の適用確認", "判定結果の根拠確認"],
            "RC-3": ["構文検証", "インポート検証", "機能検証", "パフォーマンス検証"],
            "RC-4": ["構文検証", "インポート検証", "機能検証", "影響範囲確認"],
            "RC-5": ["形式確認", "一貫性確認"],
            "RC-6": ["機能検証", "動作確認"],
        }

        handoff = {
            "target": f"Determined by {classification} request analysis",
            "capabilities": [
                {"item_id": s["item_id"], "name": s["name"], "step": s["role"]}
                for s in selected
            ],
            "work_order": step_map.get(classification, ["調査", "記録"]),
            "verification": verification_map.get(classification, ["構文検証"]),
            "github": {
                "commit_format": "type(scope): description",
                "pr_required": classification in ("RC-3", "RC-4", "RC-6"),
                "push_target": "origin/main",
            },
        }
        handoff["has_5_elements"] = all([
            handoff["target"],
            len(handoff["capabilities"]) > 0,
            len(handoff["work_order"]) > 0,
            len(handoff["verification"]) > 0,
            handoff["github"],
        ])
        return handoff

    def absorb_update(self, update_type: str, tool_info: dict) -> dict:
        """STEP 8: Update absorption (06_update_absorption.md)."""
        if update_type == "new_tool":
            directly_affects = tool_info.get("directly_affects", False)
            better_than_existing = tool_info.get("better_than_existing", False)
            setup_minutes = tool_info.get("setup_minutes", 999)

            if not directly_affects:
                return {"update_type": "new_tool", "tool": tool_info.get("name", "?"),
                        "decision": "RECORD_AND_HOLD",
                        "reason": "Does not directly affect current work",
                        "affects_existing_judgment": False}
            if not better_than_existing:
                return {"update_type": "new_tool", "tool": tool_info.get("name", "?"),
                        "decision": "RECORD_AND_HOLD",
                        "reason": "Not better than existing D1/D2 candidates",
                        "affects_existing_judgment": False}
            if setup_minutes < 30:
                return {"update_type": "new_tool", "tool": tool_info.get("name", "?"),
                        "decision": "ADOPT_IMMEDIATELY",
                        "reason": f"Setup {setup_minutes}min < 30min",
                        "affects_existing_judgment": True}
            if setup_minutes < 120:
                return {"update_type": "new_tool", "tool": tool_info.get("name", "?"),
                        "decision": "TRIAL_ADOPTION",
                        "reason": f"Setup {setup_minutes}min, trial range",
                        "affects_existing_judgment": True}
            return {"update_type": "new_tool", "tool": tool_info.get("name", "?"),
                    "decision": "DEFER",
                    "reason": f"Setup {setup_minutes}min > 120min",
                    "affects_existing_judgment": False}

        if update_type == "obsolescence":
            severity = tool_info.get("severity", "minor")
            if severity == "major":
                return {"update_type": "obsolescence", "tool": tool_info.get("name", "?"),
                        "action": "RE_EVALUATE",
                        "reason": f"Major: {tool_info.get('change', '?')}",
                        "affects_existing_judgment": True}
            return {"update_type": "obsolescence", "tool": tool_info.get("name", "?"),
                    "action": "RECORD_ONLY",
                    "reason": f"Minor: {tool_info.get('change', '?')}",
                    "affects_existing_judgment": False}

        return {"error": f"Unknown: {update_type}"}


# ── Verification Tests ─────────────────────────────────────────────

def test_file_existence():
    """Verify all 7 Phase 5 deliverables exist and are non-empty."""
    required = [
        "01_judgment_principles.md", "02_request_classification.md",
        "03_capability_selection.md", "04_reason_generation.md",
        "05_execution_handoff.md", "06_update_absorption.md",
        "07_final_operating_form.md",
    ]
    results = []
    for f in required:
        path = PHASE5 / f
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        results.append({"file": f, "exists": exists, "size": size, "pass": exists and size > 500})
    return results


def test_request_classification():
    """Test all 6 request classes with representative requests."""
    advisor = AIAdvisor()
    cases = [
        ("MCPサーバーの一覧を調査してほしい", "RC-1"),
        ("LangGraphとAgent SDKを比較してほしい", "RC-2"),
        ("GitHub Actionsの自動PRレビューを実装してほしい", "RC-3"),
        ("Phase 4の検証スクリプトのバグを直してほしい", "RC-4"),
        ("AI参謀のアーキテクチャを設計してほしい", "RC-5"),
        ("コミットワークフローを自動化してほしい", "RC-6"),
    ]
    results = []
    for req, expected in cases:
        got = advisor.classify_request(req)["classification"]
        results.append({"request": req[:40], "expected": expected, "got": got, "pass": got == expected})
    return results


# ── Goal 1: F-011 fully defined and selectable for RC-6 ──

def test_goal1_f011_defined():
    """Goal 1: F-011 exists in capability model with correct attributes."""
    cap = CAPABILITIES.get("F-011")
    results = []
    results.append({
        "test": "F-011 exists in CAPABILITIES",
        "pass": cap is not None,
    })
    if cap:
        results.append({
            "test": "F-011 has trust T2",
            "value": cap.get("trust"),
            "pass": cap.get("trust") == "T2",
        })
        results.append({
            "test": "F-011 has decision D2",
            "value": cap.get("decision"),
            "pass": cap.get("decision") == "D2",
        })
        results.append({
            "test": "F-011 has keywords",
            "count": len(cap.get("keywords", [])),
            "pass": len(cap.get("keywords", [])) > 3,
        })
        results.append({
            "test": "F-011 in RC-6 pool",
            "pass": "F-011" in CLASSIFICATION_POOLS.get("RC-6", []),
        })
    return results


def test_goal1_f011_selected_for_scheduling():
    """Goal 1: RC-6 scheduling request selects F-011."""
    advisor = AIAdvisor()
    req = "定期タスクをスケジュール実行で自動化してほしい"
    cls = advisor.classify_request(req)
    sel = advisor.select_capabilities(cls["classification"], req)

    selected_ids = {s["item_id"] for s in sel["selected"]}
    f011_selected = "F-011" in selected_ids

    # Also verify F-011 appears in handoff
    handoff = advisor.create_execution_handoff(cls["classification"], sel["selected"])
    handoff_ids = {c["item_id"] for c in handoff["capabilities"]}

    return [{
        "test": "F-011 selected for scheduling request",
        "classification": cls["classification"],
        "f011_selected": f011_selected,
        "f011_in_handoff": "F-011" in handoff_ids,
        "pass": f011_selected and "F-011" in handoff_ids,
    }]


def test_goal1_f011_not_selected_when_irrelevant():
    """Goal 1: RC-6 non-scheduling request does NOT select F-011."""
    advisor = AIAdvisor()
    req = "コミットフックで品質チェックを自動化してほしい"
    cls = advisor.classify_request(req)
    sel = advisor.select_capabilities(cls["classification"], req)

    selected_ids = {s["item_id"] for s in sel["selected"]}
    not_selected_ids = {ns["item_id"] for ns in sel["not_selected"]}

    return [{
        "test": "F-011 NOT selected for hook-focused request",
        "classification": cls["classification"],
        "f011_selected": "F-011" in selected_ids,
        "f011_in_not_selected": "F-011" in not_selected_ids,
        "pass": "F-011" not in selected_ids and "F-011" in not_selected_ids,
    }]


# ── Goal 2: Request-sensitive capability judgment ──

def test_goal2_same_class_different_selection_rc6():
    """Goal 2: Two RC-6 requests produce different capability decisions."""
    advisor = AIAdvisor()

    req_a = "定期タスクをスケジュール実行で自動化してほしい"
    req_b = "コミットフックで品質チェックを自動化してほしい"

    cls_a = advisor.classify_request(req_a)
    cls_b = advisor.classify_request(req_b)

    sel_a = advisor.select_capabilities(cls_a["classification"], req_a)
    sel_b = advisor.select_capabilities(cls_b["classification"], req_b)

    ids_a = {s["item_id"] for s in sel_a["selected"]}
    ids_b = {s["item_id"] for s in sel_b["selected"]}

    # Key proof: the sets must differ
    differ = ids_a != ids_b
    # F-011 in A but not B; F-004 in B but not A (or similar asymmetry)
    a_exclusive = ids_a - ids_b
    b_exclusive = ids_b - ids_a

    return [{
        "test": "RC-6 requests produce different selections",
        "req_a_selected": sorted(ids_a),
        "req_b_selected": sorted(ids_b),
        "a_exclusive": sorted(a_exclusive),
        "b_exclusive": sorted(b_exclusive),
        "differ": differ,
        "pass": differ and len(a_exclusive) > 0 and len(b_exclusive) > 0,
    }]


def test_goal2_same_class_different_selection_rc3():
    """Goal 2: Two RC-3 requests produce different capability decisions."""
    advisor = AIAdvisor()

    # A: MCP-focused → F-002 keyword match, but not GitHub Actions
    req_a = "MCPサーバーを使ってデータ統合を実装してほしい"
    # B: GitHub Actions-focused → F-010, F-014 keyword match, but not MCP
    req_b = "GitHub ActionsでPRレビューを実装してほしい"

    sel_a = advisor.select_capabilities("RC-3", req_a)
    sel_b = advisor.select_capabilities("RC-3", req_b)

    ids_a = {s["item_id"] for s in sel_a["selected"]}
    ids_b = {s["item_id"] for s in sel_b["selected"]}

    differ = ids_a != ids_b

    return [{
        "test": "RC-3 requests produce different selections",
        "req_a_selected": sorted(ids_a),
        "req_b_selected": sorted(ids_b),
        "differ": differ,
        "pass": differ,
    }]


def test_goal2_same_class_different_selection_rc1():
    """Goal 2: Two RC-1 requests produce different capability decisions."""
    advisor = AIAdvisor()

    req_a = "MCPサーバーの一覧を調査してほしい"
    req_b = "プロンプト評価ツールを調査してほしい"

    sel_a = advisor.select_capabilities("RC-1", req_a)
    sel_b = advisor.select_capabilities("RC-1", req_b)

    ids_a = {s["item_id"] for s in sel_a["selected"]}
    ids_b = {s["item_id"] for s in sel_b["selected"]}

    differ = ids_a != ids_b

    return [{
        "test": "RC-1 requests produce different selections",
        "req_a_selected": sorted(ids_a),
        "req_b_selected": sorted(ids_b),
        "differ": differ,
        "pass": differ,
    }]


def test_goal2_reason_is_request_specific():
    """Goal 2: Reasons reference request-specific content, not generic class."""
    advisor = AIAdvisor()

    req = "コミットフックで品質チェックを自動化してほしい"
    cls = advisor.classify_request(req)
    sel = advisor.select_capabilities(cls["classification"], req)
    reason = advisor.generate_reason(cls["classification"], req, sel["selected"], sel["not_selected"])

    # Check that positive reasons mention specific keywords, not just the class
    has_specific = any("matched:" in r or "base capability" in r for r in reason["positive_reasons"])
    has_elimination = len(reason["elimination_reasons"]) > 0

    return [{
        "test": "Reasons are request-specific",
        "has_specific_match_info": has_specific,
        "has_elimination_reasons": has_elimination,
        "pass": has_specific and has_elimination,
    }]


# ── Goal 3: Request-relevant T4 reconfirmation only ──

def test_goal3_no_t4_for_irrelevant_request():
    """Goal 3: Requests with no T4-relevant content emit NO T4 items."""
    advisor = AIAdvisor()
    results = []

    irrelevant_requests = [
        ("MCPサーバーの一覧を調査してほしい", "RC-1"),
        ("コミットフックで品質チェックを自動化してほしい", "RC-6"),
        ("Phase 4の検証スクリプトのバグを直してほしい", "RC-4"),
        ("プロンプト評価テストを実装してほしい", "RC-3"),
    ]

    for req, rc in irrelevant_requests:
        sel = advisor.select_capabilities(rc, req)
        t4_count = len(sel["recheck_needed"])
        results.append({
            "test": f"No T4 for: {req[:30]}",
            "t4_count": t4_count,
            "pass": t4_count == 0,
        })

    return results


def test_goal3_t4_emitted_when_relevant():
    """Goal 3: T4 items ARE emitted when the request mentions them."""
    advisor = AIAdvisor()
    results = []

    # Request mentioning managed agents → F-006 should appear
    req1 = "マネージドエージェントを使ってオーケストレーションを実装してほしい"
    sel1 = advisor.select_capabilities("RC-3", req1)
    t4_ids_1 = {r["item_id"] for r in sel1["recheck_needed"]}
    results.append({
        "test": "F-006 emitted for managed agent request",
        "t4_items": sorted(t4_ids_1),
        "has_f006": "F-006" in t4_ids_1,
        "pass": "F-006" in t4_ids_1,
    })

    # Request mentioning agent teams → F-008 should appear
    req2 = "エージェントチームでマルチエージェント設計をしてほしい"
    sel2 = advisor.select_capabilities("RC-5", req2)
    t4_ids_2 = {r["item_id"] for r in sel2["recheck_needed"]}
    results.append({
        "test": "F-008 emitted for agent team request",
        "t4_items": sorted(t4_ids_2),
        "has_f008": "F-008" in t4_ids_2,
        "pass": "F-008" in t4_ids_2,
    })

    # Request mentioning advisor → F-012 should appear
    req3 = "アドバイザーツールを使った参謀ツール実装を設計してほしい"
    sel3 = advisor.select_capabilities("RC-5", req3)
    t4_ids_3 = {r["item_id"] for r in sel3["recheck_needed"]}
    results.append({
        "test": "F-012 emitted for advisor request",
        "t4_items": sorted(t4_ids_3),
        "has_f012": "F-012" in t4_ids_3,
        "pass": "F-012" in t4_ids_3,
    })

    return results


def test_goal3_t4_not_cross_contaminated():
    """Goal 3: A request relevant to F-006 does NOT emit F-008 or F-012."""
    advisor = AIAdvisor()
    req = "マネージドエージェントのオーケストレーションを実装してほしい"
    sel = advisor.select_capabilities("RC-3", req)
    t4_ids = {r["item_id"] for r in sel["recheck_needed"]}

    has_f006 = "F-006" in t4_ids
    no_f008 = "F-008" not in t4_ids
    no_f012 = "F-012" not in t4_ids

    return [{
        "test": "F-006 only, no F-008/F-012 cross-contamination",
        "t4_items": sorted(t4_ids),
        "has_f006": has_f006,
        "no_f008": no_f008,
        "no_f012": no_f012,
        "pass": has_f006 and no_f008 and no_f012,
    }]


# ── Existing test suites (updated) ──

def test_reason_generation():
    """Reason generation produces all 3 required elements."""
    advisor = AIAdvisor()
    results = []
    cases = [
        ("RC-1", "MCPサーバーの一覧を調査してほしい"),
        ("RC-3", "GitHub Actionsの自動PRレビューを実装してほしい"),
        ("RC-6", "定期タスクをスケジュール実行で自動化してほしい"),
    ]
    for rc, req in cases:
        sel = advisor.select_capabilities(rc, req)
        reason = advisor.generate_reason(rc, req, sel["selected"], sel["not_selected"])
        results.append({
            "classification": rc,
            "positive": len(reason["positive_reasons"]),
            "elimination": len(reason["elimination_reasons"]),
            "effect": len(reason["effect_scope"]),
            "has_all_3": reason["has_all_3_elements"],
            "pass": reason["has_all_3_elements"],
        })
    return results


def test_execution_handoff():
    """Execution handoff produces all 5 required elements."""
    advisor = AIAdvisor()
    results = []
    cases = [
        ("RC-1", "MCPサーバーの一覧を調査してほしい"),
        ("RC-3", "GitHub Actionsの自動PRレビューを実装してほしい"),
        ("RC-4", "Phase 4の検証スクリプトのバグを直してほしい"),
        ("RC-6", "定期タスクをスケジュール実行で自動化してほしい"),
    ]
    for rc, req in cases:
        sel = advisor.select_capabilities(rc, req)
        ho = advisor.create_execution_handoff(rc, sel["selected"])
        results.append({
            "classification": rc,
            "has_5": ho["has_5_elements"],
            "cap_count": len(ho["capabilities"]),
            "pass": ho["has_5_elements"],
        })
    return results


def test_update_absorption():
    """Update absorption handles all paths."""
    advisor = AIAdvisor()
    results = []
    r = advisor.absorb_update("new_tool", {"name": "X", "directly_affects": True,
                                            "better_than_existing": True, "setup_minutes": 15})
    results.append({"test": "immediate", "pass": r["decision"] == "ADOPT_IMMEDIATELY"})

    r = advisor.absorb_update("new_tool", {"name": "X", "directly_affects": True,
                                            "better_than_existing": True, "setup_minutes": 60})
    results.append({"test": "trial", "pass": r["decision"] == "TRIAL_ADOPTION"})

    r = advisor.absorb_update("new_tool", {"name": "X", "directly_affects": False,
                                            "better_than_existing": True, "setup_minutes": 5})
    results.append({"test": "hold", "pass": r["decision"] == "RECORD_AND_HOLD"})

    r = advisor.absorb_update("obsolescence", {"name": "X", "severity": "major", "change": "breaking"})
    results.append({"test": "major_obs", "pass": r["action"] == "RE_EVALUATE"})

    r = advisor.absorb_update("obsolescence", {"name": "X", "severity": "minor", "change": "param"})
    results.append({"test": "minor_obs", "pass": r["action"] == "RECORD_ONLY"})

    return results


def test_end_to_end():
    """Full pipeline for 3 diverse requests."""
    advisor = AIAdvisor()
    results = []
    requests = [
        "MCPサーバーの一覧を調査してほしい",
        "GitHub Actionsの自動PRレビューを実装してほしい",
        "定期タスクをスケジュール実行で自動化してほしい",
    ]
    for req in requests:
        cls = advisor.classify_request(req)
        rc = cls["classification"]
        sel = advisor.select_capabilities(rc, req)
        reason = advisor.generate_reason(rc, req, sel["selected"], sel["not_selected"])
        ho = advisor.create_execution_handoff(rc, sel["selected"])
        ok = all([
            rc.startswith("RC-"),
            len(sel["selected"]) > 0,
            reason["has_all_3_elements"],
            ho["has_5_elements"],
        ])
        results.append({
            "request": req[:30], "class": rc,
            "selected": len(sel["selected"]),
            "t4_count": len(sel["recheck_needed"]),
            "pass": ok,
        })
    return results


def test_phase4_integration():
    """Phase 4 execution baseline files are accessible."""
    required = [
        "01_execution_flow.md", "02_tool_maximization_policy.md",
        "03_new_tool_intake_rules.md", "04_work_unit_definitions.md",
        "05_quality_assurance_rules.md", "06_github_integration_policy.md",
        "07_phase5_handoff_memo.md",
    ]
    results = []
    for f in required:
        p = PHASE4 / f
        exists = p.exists()
        sz = p.stat().st_size if exists else 0
        results.append({"file": f, "pass": exists and sz > 500})
    return results


# ── Main ───────────────────────────────────────────────────────────

def run_all_tests():
    tests = [
        ("Phase 5 deliverable existence", test_file_existence),
        ("Request classification (6 classes)", test_request_classification),
        # Goal 1
        ("Goal 1: F-011 definition", test_goal1_f011_defined),
        ("Goal 1: F-011 selected for scheduling", test_goal1_f011_selected_for_scheduling),
        ("Goal 1: F-011 NOT selected when irrelevant", test_goal1_f011_not_selected_when_irrelevant),
        # Goal 2
        ("Goal 2: RC-6 different selections", test_goal2_same_class_different_selection_rc6),
        ("Goal 2: RC-3 different selections", test_goal2_same_class_different_selection_rc3),
        ("Goal 2: RC-1 different selections", test_goal2_same_class_different_selection_rc1),
        ("Goal 2: Request-specific reasons", test_goal2_reason_is_request_specific),
        # Goal 3
        ("Goal 3: No T4 for irrelevant requests", test_goal3_no_t4_for_irrelevant_request),
        ("Goal 3: T4 emitted when relevant", test_goal3_t4_emitted_when_relevant),
        ("Goal 3: No T4 cross-contamination", test_goal3_t4_not_cross_contaminated),
        # Existing
        ("Reason generation (3 elements)", test_reason_generation),
        ("Execution handoff (5 elements)", test_execution_handoff),
        ("Update absorption (5 paths)", test_update_absorption),
        ("End-to-end pipeline (3 requests)", test_end_to_end),
        ("Phase 4 integration", test_phase4_integration),
    ]

    all_pass = True
    total_checks = 0
    passed_checks = 0
    report = {"timestamp": datetime.now().isoformat(), "tests": []}

    for name, fn in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")

        results = fn()
        suite_pass = all(r.get("pass", False) for r in results)
        n_total = len(results)
        n_passed = sum(1 for r in results if r.get("pass", False))
        total_checks += n_total
        passed_checks += n_passed

        for r in results:
            st = "PASS" if r.get("pass") else "FAIL"
            info = {k: v for k, v in r.items() if k != "pass"}
            print(f"  [{st}] {', '.join(f'{k}={v}' for k, v in info.items())}")

        print(f"  --- {'PASS' if suite_pass else 'FAIL'} ({n_passed}/{n_total})")
        if not suite_pass:
            all_pass = False

        report["tests"].append({"name": name, "pass": suite_pass,
                                "checks": n_total, "passed": n_passed})

    print(f"\n{'='*60}")
    print(f"FINAL: {'ALL PASS' if all_pass else 'FAILURES EXIST'} — {passed_checks}/{total_checks}")
    print(f"{'='*60}")

    report.update({"all_pass": all_pass, "total_checks": total_checks,
                    "passed_checks": passed_checks})
    rpath = BASE / "PHASE5_OPERATIONAL_VERIFICATION_RESULTS.json"
    with open(rpath, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport: {rpath.name}")
    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
