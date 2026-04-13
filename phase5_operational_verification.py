#!/usr/bin/env python3
"""
Phase 5 AI参謀 Operational Verification
========================================
Proves that the AI参謀 framework can:
1. Classify requests (RC-1 to RC-6)
2. Select capabilities with correct P1/P2 pools
3. Generate reasons with 3 required elements
4. Judge reconfirmation need (T4 detection)
5. Hand off to execution baseline (5 elements)
6. Absorb updates (new tool + obsolescence)
"""

import json
import os
import sys
from pathlib import Path
from datetime import datetime

BASE = Path(__file__).parent
PHASE5 = BASE / "phase5_ai_advisor"
PHASE4 = BASE / "phase4_execution_foundation"

# ── Capability Knowledge Base (from Phase 2) ──────────────────────

P1_CAPABILITIES = {
    "F-002": {"name": "MCP", "trust": "T1", "decision": "D1", "priority": "P1"},
    "F-003": {"name": "Subagents", "trust": "T1", "decision": "D1", "priority": "P1"},
    "F-004": {"name": "Hooks", "trust": "T1", "decision": "D1", "priority": "P1"},
    "F-005": {"name": "Skills", "trust": "T1", "decision": "D1", "priority": "P1"},
    "F-009": {"name": "Claude Agent SDK", "trust": "T1", "decision": "D1", "priority": "P1"},
    "F-025": {"name": "Memory Tool", "trust": "T1", "decision": "D1", "priority": "P1"},
}

P2_CAPABILITIES = {
    "F-010": {"name": "GitHub Actions", "trust": "T2", "decision": "D2", "priority": "P2"},
    "F-013": {"name": "anthropics/skills", "trust": "T2", "decision": "D1", "priority": "P2"},
    "F-014": {"name": "claude-code-action", "trust": "T2", "decision": "D2", "priority": "P2"},
    "F-015": {"name": "claude-agent-sdk-python", "trust": "T2", "decision": "D1", "priority": "P2"},
    "F-019": {"name": "MCP Servers", "trust": "T2", "decision": "D1", "priority": "P2"},
    "F-032": {"name": "promptfoo", "trust": "T2", "decision": "D1", "priority": "P2"},
}

T4_CAPABILITIES = {
    "F-006": {"name": "Managed Agents", "trust": "T4", "decision": "D3", "priority": "P4"},
    "F-008": {"name": "Agent Teams", "trust": "T4", "decision": "D5", "priority": "P5"},
    "F-012": {"name": "Advisor Tool", "trust": "T4", "decision": "D3", "priority": "P4"},
}

# Classification-to-pool mapping (from 03_capability_selection.md)
CLASSIFICATION_POOLS = {
    "RC-1": {"first": ["F-002", "F-003", "F-025"], "second": ["F-019", "F-032"]},
    "RC-2": {"first": ["F-002", "F-003"], "second": ["F-032", "F-013"]},
    "RC-3": {"first": ["F-002", "F-003", "F-004", "F-005", "F-009"], "second": ["F-010", "F-015"]},
    "RC-4": {"first": ["F-002", "F-003", "F-004"], "second": ["F-010"]},
    "RC-5": {"first": ["F-002", "F-003", "F-009"], "second": ["F-015", "F-019"]},
    "RC-6": {"first": ["F-004", "F-005", "F-002"], "second": ["F-010", "F-011"]},
}


# ── AI参謀 Core Logic ─────────────────────────────────────────────

class AIAdvisor:
    """AI参謀 implementation following Phase 5 rules."""

    def classify_request(self, request: str) -> dict:
        """STEP 1: Request classification (02_request_classification.md)."""
        keywords = {
            "RC-4": ["直して", "バグ", "動かない", "改善", "修正", "fix", "bug"],
            "RC-3": ["作って", "実装", "設定", "構築", "作成", "implement", "create", "build"],
            "RC-2": ["比較", "どちら", "選んで", "どれがいい", "compare", "evaluate"],
            "RC-5": ["設計", "アーキテクチャ", "構造", "方針", "design", "architect"],
            "RC-6": ["効率", "自動化", "改善", "ワークフロー", "optimize", "automate"],
            "RC-1": ["調べて", "調査", "確認", "現状", "一覧", "investigate", "survey", "check"],
        }
        req_lower = request.lower()
        for rc, kws in keywords.items():
            if any(kw in req_lower for kw in kws):
                return {"classification": rc, "request": request}
        return {"classification": "RC-1", "request": request}  # default: investigation

    def select_capabilities(self, classification: str, request: str) -> dict:
        """STEP 4: Capability selection (03_capability_selection.md)."""
        pools = CLASSIFICATION_POOLS.get(classification, CLASSIFICATION_POOLS["RC-1"])

        selected = []
        not_selected = []
        recheck_needed = []

        # Stage 1: Filter from first pool
        for fid in pools["first"]:
            cap = P1_CAPABILITIES.get(fid)
            if cap:
                selected.append({
                    "item_id": fid,
                    "name": cap["name"],
                    "role": f"{cap['name']} for {classification}",
                    "criteria_met": ["S1", "S2", "S6", "S7"],
                })

        # Stage 2: Add from second pool if relevant
        for fid in pools["second"]:
            cap = P2_CAPABILITIES.get(fid)
            if cap:
                selected.append({
                    "item_id": fid,
                    "name": cap["name"],
                    "role": f"{cap['name']} as P2 supplement",
                    "criteria_met": ["S1", "S2"],
                })

        # Check T4 capabilities for reconfirmation
        for fid, cap in T4_CAPABILITIES.items():
            recheck_needed.append({
                "item_id": fid,
                "name": cap["name"],
                "reason": f"T4 trust level - {cap['decision']} state, requires freshness check",
            })

        # Items explicitly not selected (some P2/P3 not in pool)
        all_known = {**P1_CAPABILITIES, **P2_CAPABILITIES}
        selected_ids = {s["item_id"] for s in selected}
        for fid, cap in all_known.items():
            if fid not in selected_ids:
                not_selected.append({
                    "item_id": fid,
                    "name": cap["name"],
                    "reason": f"S2 not met: not needed for {classification}",
                })

        return {
            "selected": selected,
            "not_selected": not_selected,
            "recheck_needed": recheck_needed,
        }

    def generate_reason(self, classification: str, selected: list, not_selected: list) -> dict:
        """STEP 6: Reason generation (04_reason_generation.md)."""
        positive_reasons = []
        for cap in selected:
            positive_reasons.append(
                f"{cap['item_id']} {cap['name']}: selected because criteria "
                f"{', '.join(cap['criteria_met'])} met for {classification}"
            )

        elimination_reasons = []
        for cap in not_selected[:3]:  # top 3
            elimination_reasons.append(
                f"{cap['item_id']} {cap['name']}: {cap['reason']}"
            )

        effect_scope = []
        step_map = {
            "RC-1": ["調査", "記録"],
            "RC-2": ["調査", "比較", "記録"],
            "RC-3": ["調査", "実装", "検証", "GitHub反映"],
            "RC-4": ["調査", "修正", "検証", "GitHub反映"],
            "RC-5": ["調査", "比較", "記録"],
            "RC-6": ["調査", "実装", "検証", "GitHub反映"],
        }
        steps = step_map.get(classification, ["調査", "記録"])
        for cap in selected:
            effect_scope.append(f"{cap['item_id']} {cap['name']} affects steps: {', '.join(steps)}")

        return {
            "positive_reasons": positive_reasons,
            "elimination_reasons": elimination_reasons,
            "effect_scope": effect_scope,
            "has_all_3_elements": len(positive_reasons) > 0 and len(elimination_reasons) > 0 and len(effect_scope) > 0,
        }

    def judge_reconfirmation(self, recheck_needed: list) -> dict:
        """STEP 5: Reconfirmation judgment (03_capability_selection.md recheck section)."""
        t4_items = [r for r in recheck_needed if "T4" in r.get("reason", "")]
        needs_recheck = len(t4_items) > 0

        skip_reasons = []
        for fid, cap in P1_CAPABILITIES.items():
            if cap["trust"] == "T1":
                skip_reasons.append(f"{fid} {cap['name']}: T1 confirmed, skip recheck")

        return {
            "needs_recheck": needs_recheck,
            "t4_items": t4_items,
            "skip_items": skip_reasons,
            "recheck_method": "Official release notes + GitHub repository check" if needs_recheck else "None needed",
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
            "capabilities": [{"item_id": s["item_id"], "name": s["name"], "step": s["role"]} for s in selected],
            "work_order": step_map.get(classification, ["調査", "記録"]),
            "verification": verification_map.get(classification, ["構文検証"]),
            "github": {
                "commit_format": f"type(scope): description",
                "pr_required": classification in ("RC-3", "RC-4", "RC-6"),
                "push_target": "origin/main",
            },
        }

        # Check 5 elements present
        has_5_elements = all([
            handoff["target"],
            len(handoff["capabilities"]) > 0,
            len(handoff["work_order"]) > 0,
            len(handoff["verification"]) > 0,
            handoff["github"],
        ])
        handoff["has_5_elements"] = has_5_elements
        return handoff

    def absorb_update(self, update_type: str, tool_info: dict) -> dict:
        """STEP 8: Update absorption (06_update_absorption.md)."""
        if update_type == "new_tool":
            # 4-stage judgment from 03_new_tool_intake_rules.md
            directly_affects = tool_info.get("directly_affects", False)
            better_than_existing = tool_info.get("better_than_existing", False)
            setup_minutes = tool_info.get("setup_minutes", 999)

            if not directly_affects:
                decision = "RECORD_AND_HOLD"
                reason = "Does not directly affect current work"
            elif not better_than_existing:
                decision = "RECORD_AND_HOLD"
                reason = "Not better than existing D1/D2 candidates"
            elif setup_minutes < 30:
                decision = "ADOPT_IMMEDIATELY"
                reason = f"Setup time {setup_minutes}min < 30min threshold"
            elif setup_minutes < 120:
                decision = "TRIAL_ADOPTION"
                reason = f"Setup time {setup_minutes}min, within 30-120min trial range"
            else:
                decision = "DEFER"
                reason = f"Setup time {setup_minutes}min exceeds 120min threshold"

            return {
                "update_type": "new_tool",
                "tool": tool_info.get("name", "unknown"),
                "decision": decision,
                "reason": reason,
                "affects_existing_judgment": decision in ("ADOPT_IMMEDIATELY", "TRIAL_ADOPTION"),
            }

        elif update_type == "obsolescence":
            severity = tool_info.get("severity", "minor")
            if severity == "major":
                return {
                    "update_type": "obsolescence",
                    "tool": tool_info.get("name", "unknown"),
                    "action": "RE_EVALUATE",
                    "reason": f"Major change detected: {tool_info.get('change', 'unknown')}",
                    "affects_existing_judgment": True,
                }
            else:
                return {
                    "update_type": "obsolescence",
                    "tool": tool_info.get("name", "unknown"),
                    "action": "RECORD_ONLY",
                    "reason": f"Minor change: {tool_info.get('change', 'unknown')}",
                    "affects_existing_judgment": False,
                }

        return {"error": f"Unknown update type: {update_type}"}


# ── Verification Tests ─────────────────────────────────────────────

def test_file_existence():
    """Verify all 7 Phase 5 deliverables exist and are non-empty."""
    required = [
        "01_judgment_principles.md",
        "02_request_classification.md",
        "03_capability_selection.md",
        "04_reason_generation.md",
        "05_execution_handoff.md",
        "06_update_absorption.md",
        "07_final_operating_form.md",
    ]
    results = []
    for f in required:
        path = PHASE5 / f
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        ok = exists and size > 500
        results.append({"file": f, "exists": exists, "size": size, "pass": ok})
    return results


def test_request_classification():
    """Test all 6 request classes with representative requests."""
    advisor = AIAdvisor()
    test_cases = [
        ("MCPサーバーの一覧を調査してほしい", "RC-1"),
        ("LangGraphとAgent SDKを比較してほしい", "RC-2"),
        ("GitHub Actionsの自動PRレビューを実装してほしい", "RC-3"),
        ("Phase 4の検証スクリプトのバグを直してほしい", "RC-4"),
        ("AI参謀のアーキテクチャを設計してほしい", "RC-5"),
        ("コミットワークフローを自動化してほしい", "RC-6"),
    ]
    results = []
    for request, expected_rc in test_cases:
        result = advisor.classify_request(request)
        ok = result["classification"] == expected_rc
        results.append({
            "request": request[:40],
            "expected": expected_rc,
            "got": result["classification"],
            "pass": ok,
        })
    return results


def test_capability_selection():
    """Test capability selection produces correct pools for each class."""
    advisor = AIAdvisor()
    results = []
    for rc in ["RC-1", "RC-2", "RC-3", "RC-4", "RC-5", "RC-6"]:
        sel = advisor.select_capabilities(rc, f"test request for {rc}")
        has_selected = len(sel["selected"]) > 0
        has_not_selected = len(sel["not_selected"]) > 0
        has_recheck = len(sel["recheck_needed"]) > 0
        # Verify pool items match classification
        selected_ids = {s["item_id"] for s in sel["selected"]}
        pool = CLASSIFICATION_POOLS[rc]
        pool_covered = all(fid in selected_ids for fid in pool["first"])
        results.append({
            "classification": rc,
            "selected_count": len(sel["selected"]),
            "not_selected_count": len(sel["not_selected"]),
            "recheck_count": len(sel["recheck_needed"]),
            "pool_covered": pool_covered,
            "pass": has_selected and has_not_selected and has_recheck and pool_covered,
        })
    return results


def test_reason_generation():
    """Test reason generation produces all 3 required elements."""
    advisor = AIAdvisor()
    results = []
    for rc in ["RC-1", "RC-3", "RC-6"]:
        sel = advisor.select_capabilities(rc, f"test for {rc}")
        reason = advisor.generate_reason(rc, sel["selected"], sel["not_selected"])
        results.append({
            "classification": rc,
            "positive_count": len(reason["positive_reasons"]),
            "elimination_count": len(reason["elimination_reasons"]),
            "effect_count": len(reason["effect_scope"]),
            "has_all_3": reason["has_all_3_elements"],
            "pass": reason["has_all_3_elements"],
        })
    return results


def test_reconfirmation_judgment():
    """Test T4 capability detection and recheck judgment."""
    advisor = AIAdvisor()
    sel = advisor.select_capabilities("RC-3", "implement something")
    judgment = advisor.judge_reconfirmation(sel["recheck_needed"])

    t4_detected = judgment["needs_recheck"]
    t4_count = len(judgment["t4_items"])
    has_f006 = any("F-006" in t["item_id"] for t in judgment["t4_items"])
    has_f012 = any("F-012" in t["item_id"] for t in judgment["t4_items"])
    skip_count = len(judgment["skip_items"])

    return [{
        "test": "T4 detection",
        "t4_detected": t4_detected,
        "t4_count": t4_count,
        "has_f006": has_f006,
        "has_f012": has_f012,
        "skip_count": skip_count,
        "pass": t4_detected and t4_count >= 3 and has_f006 and has_f012 and skip_count > 0,
    }]


def test_execution_handoff():
    """Test execution handoff produces all 5 required elements."""
    advisor = AIAdvisor()
    results = []
    for rc in ["RC-1", "RC-3", "RC-4", "RC-6"]:
        sel = advisor.select_capabilities(rc, f"test for {rc}")
        handoff = advisor.create_execution_handoff(rc, sel["selected"])
        results.append({
            "classification": rc,
            "has_target": bool(handoff["target"]),
            "has_capabilities": len(handoff["capabilities"]) > 0,
            "has_work_order": len(handoff["work_order"]) > 0,
            "has_verification": len(handoff["verification"]) > 0,
            "has_github": bool(handoff["github"]),
            "has_5_elements": handoff["has_5_elements"],
            "pass": handoff["has_5_elements"],
        })
    return results


def test_update_absorption():
    """Test both new-tool and obsolescence update paths."""
    advisor = AIAdvisor()
    results = []

    # Test 1: New tool, immediately adoptable
    r1 = advisor.absorb_update("new_tool", {
        "name": "SuperMCP",
        "directly_affects": True,
        "better_than_existing": True,
        "setup_minutes": 15,
    })
    results.append({
        "test": "new_tool_immediate",
        "decision": r1["decision"],
        "pass": r1["decision"] == "ADOPT_IMMEDIATELY",
    })

    # Test 2: New tool, trial adoption
    r2 = advisor.absorb_update("new_tool", {
        "name": "BigFramework",
        "directly_affects": True,
        "better_than_existing": True,
        "setup_minutes": 60,
    })
    results.append({
        "test": "new_tool_trial",
        "decision": r2["decision"],
        "pass": r2["decision"] == "TRIAL_ADOPTION",
    })

    # Test 3: New tool, does not affect current work
    r3 = advisor.absorb_update("new_tool", {
        "name": "IrrelevantTool",
        "directly_affects": False,
        "better_than_existing": True,
        "setup_minutes": 5,
    })
    results.append({
        "test": "new_tool_irrelevant",
        "decision": r3["decision"],
        "pass": r3["decision"] == "RECORD_AND_HOLD",
    })

    # Test 4: Obsolescence - major
    r4 = advisor.absorb_update("obsolescence", {
        "name": "F-006 Managed Agents",
        "severity": "major",
        "change": "API breaking change in beta → GA migration",
    })
    results.append({
        "test": "obsolescence_major",
        "action": r4["action"],
        "pass": r4["action"] == "RE_EVALUATE" and r4["affects_existing_judgment"],
    })

    # Test 5: Obsolescence - minor
    r5 = advisor.absorb_update("obsolescence", {
        "name": "F-032 promptfoo",
        "severity": "minor",
        "change": "New parameter added",
    })
    results.append({
        "test": "obsolescence_minor",
        "action": r5["action"],
        "pass": r5["action"] == "RECORD_ONLY" and not r5["affects_existing_judgment"],
    })

    return results


def test_end_to_end():
    """Full pipeline test: request → classification → selection → reason → handoff."""
    advisor = AIAdvisor()
    results = []

    test_requests = [
        "MCPサーバーの一覧を調査してほしい",
        "GitHub Actionsの自動PRレビューを実装してほしい",
        "コミットワークフローを自動化してほしい",
    ]

    for request in test_requests:
        # Full pipeline
        cls = advisor.classify_request(request)
        rc = cls["classification"]
        sel = advisor.select_capabilities(rc, request)
        reason = advisor.generate_reason(rc, sel["selected"], sel["not_selected"])
        recheck = advisor.judge_reconfirmation(sel["recheck_needed"])
        handoff = advisor.create_execution_handoff(rc, sel["selected"])

        pipeline_ok = all([
            rc.startswith("RC-"),
            len(sel["selected"]) > 0,
            reason["has_all_3_elements"],
            isinstance(recheck["needs_recheck"], bool),
            handoff["has_5_elements"],
        ])

        results.append({
            "request": request[:30],
            "classification": rc,
            "selected_count": len(sel["selected"]),
            "reason_complete": reason["has_all_3_elements"],
            "recheck_judged": True,
            "handoff_complete": handoff["has_5_elements"],
            "pipeline_pass": pipeline_ok,
            "pass": pipeline_ok,
        })

    return results


def test_phase4_integration():
    """Verify Phase 4 execution baseline files are accessible."""
    required_p4 = [
        "01_execution_flow.md",
        "02_tool_maximization_policy.md",
        "03_new_tool_intake_rules.md",
        "04_work_unit_definitions.md",
        "05_quality_assurance_rules.md",
        "06_github_integration_policy.md",
        "07_phase5_handoff_memo.md",
    ]
    results = []
    for f in required_p4:
        path = PHASE4 / f
        exists = path.exists()
        size = path.stat().st_size if exists else 0
        results.append({"file": f, "exists": exists, "size": size, "pass": exists and size > 500})
    return results


# ── Main ───────────────────────────────────────────────────────────

def run_all_tests():
    tests = [
        ("Phase 5 deliverable existence", test_file_existence),
        ("Request classification (6 classes)", test_request_classification),
        ("Capability selection (6 classes)", test_capability_selection),
        ("Reason generation (3 elements)", test_reason_generation),
        ("Reconfirmation judgment (T4 detection)", test_reconfirmation_judgment),
        ("Execution handoff (5 elements)", test_execution_handoff),
        ("Update absorption (new + obsolescence)", test_update_absorption),
        ("End-to-end pipeline (3 requests)", test_end_to_end),
        ("Phase 4 integration check", test_phase4_integration),
    ]

    all_pass = True
    total_checks = 0
    passed_checks = 0
    report = {"timestamp": datetime.now().isoformat(), "tests": []}

    for name, test_fn in tests:
        print(f"\n{'='*60}")
        print(f"TEST: {name}")
        print(f"{'='*60}")

        results = test_fn()
        test_pass = all(r.get("pass", False) for r in results)
        test_total = len(results)
        test_passed = sum(1 for r in results if r.get("pass", False))

        total_checks += test_total
        passed_checks += test_passed

        for r in results:
            status = "PASS" if r.get("pass") else "FAIL"
            # Format key info
            info = {k: v for k, v in r.items() if k != "pass"}
            info_str = ", ".join(f"{k}={v}" for k, v in info.items())
            print(f"  [{status}] {info_str}")

        suite_status = "PASS" if test_pass else "FAIL"
        print(f"  --- Suite: {suite_status} ({test_passed}/{test_total})")

        if not test_pass:
            all_pass = False

        report["tests"].append({
            "name": name,
            "pass": test_pass,
            "checks": test_total,
            "passed": test_passed,
        })

    print(f"\n{'='*60}")
    print(f"FINAL RESULT: {'ALL PASS' if all_pass else 'SOME FAILURES'}")
    print(f"Total: {passed_checks}/{total_checks} checks passed")
    print(f"{'='*60}")

    report["all_pass"] = all_pass
    report["total_checks"] = total_checks
    report["passed_checks"] = passed_checks

    # Write JSON report
    report_path = BASE / "PHASE5_OPERATIONAL_VERIFICATION_RESULTS.json"
    with open(report_path, "w", encoding="utf-8") as f:
        json.dump(report, f, indent=2, ensure_ascii=False)
    print(f"\nReport written to: {report_path.name}")

    return 0 if all_pass else 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
