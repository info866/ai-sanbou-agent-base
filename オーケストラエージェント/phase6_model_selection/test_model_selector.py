#!/usr/bin/env python3
"""
Verification suite for Model Selection Engine (Phase 6)
Standalone tests — run from phase6_model_selection/ directory.
"""

import os
from model_selector import (
    ModelSelector, SelectionInput, SelectionOutput, AliasState,
    OfficialRecheckPath, RecheckDetail,
    ALIAS_REGISTRY, FALLBACK_MAP,
    select_model, select_model_for_rc,
)


def test_simple_routes_haiku():
    print("TEST: Simple → haiku")
    ms = select_model(goal="Fix typo", reasoning_weight=0.1, ambiguity=0.1,
                      failure_cost=0.0, speed_priority=0.8, context_size=0.1, plan_weight=0.0)
    assert ms.recommended_model == "haiku", f"Got {ms.recommended_model}"
    print(f"  ✓ {ms.recommended_model}")


def test_standard_routes_sonnet():
    print("TEST: Standard → sonnet")
    ms = select_model(goal="Implement auth", reasoning_weight=0.5, ambiguity=0.3,
                      failure_cost=0.3, speed_priority=0.2, context_size=0.4, plan_weight=0.2)
    assert ms.recommended_model == "sonnet", f"Got {ms.recommended_model}"
    print(f"  ✓ {ms.recommended_model}")


def test_complex_routes_opus():
    print("TEST: Complex → opus")
    ms = select_model(goal="Design architecture", reasoning_weight=0.9, ambiguity=0.8,
                      failure_cost=0.9, speed_priority=0.1, context_size=0.6, plan_weight=0.3)
    assert ms.recommended_model == "opus", f"Got {ms.recommended_model}"
    print(f"  ✓ {ms.recommended_model}")


def test_plan_routes_opusplan():
    print("TEST: Plan-heavy → opusplan")
    ms = select_model(goal="Plan CI/CD", reasoning_weight=0.8, ambiguity=0.7,
                      failure_cost=0.5, speed_priority=0.1, context_size=0.5, plan_weight=0.9)
    assert ms.recommended_model == "opusplan", f"Got {ms.recommended_model}"
    print(f"  ✓ {ms.recommended_model}")


def test_fallback_always_present():
    print("TEST: Fallback always present and different")
    cases = [
        (0.1, 0.1, 0.0, 0.8, 0.1, 0.0),
        (0.5, 0.3, 0.3, 0.2, 0.4, 0.2),
        (0.9, 0.8, 0.9, 0.1, 0.6, 0.3),
        (0.8, 0.7, 0.5, 0.1, 0.5, 0.9),
    ]
    for rw, a, fc, sp, cs, pw in cases:
        ms = select_model(goal="test", reasoning_weight=rw, ambiguity=a,
                          failure_cost=fc, speed_priority=sp, context_size=cs, plan_weight=pw)
        assert ms.fallback_model != ms.recommended_model, \
            f"Same: {ms.recommended_model} == {ms.fallback_model}"
    print(f"  ✓ All 4 cases have distinct fallback")


def test_output_shape():
    print("TEST: Output shape")
    ms = select_model(goal="test", reasoning_weight=0.5, ambiguity=0.3,
                      failure_cost=0.3, speed_priority=0.2, context_size=0.3, plan_weight=0.2)
    d = ms.to_dict()
    required = ["goal", "recommended_model", "fallback_model", "reason",
                "recheck_required", "handoff_notes"]
    for key in required:
        assert key in d, f"Missing: {key}"
    assert len(ms.reason) <= 200, f"Reason too long: {len(ms.reason)}"
    print(f"  ✓ All fields present, reason {len(ms.reason)} chars")


def test_recheck_no_change():
    print("TEST: No change → no recheck")
    state = AliasState()
    ms = select_model(goal="Normal", reasoning_weight=0.5, ambiguity=0.3,
                      failure_cost=0.3, speed_priority=0.2, context_size=0.3,
                      plan_weight=0.2, alias_state=state)
    assert not ms.recheck_required, "Should not recheck when nothing changed"
    print(f"  ✓ recheck_required={ms.recheck_required}")


def test_recheck_new_alias():
    print("TEST: New alias → recheck")
    state = AliasState()
    ModelSelector.add_alias("turbo", "Fast model", tier=0, fallback="haiku")
    try:
        ms = select_model(goal="Test", reasoning_weight=0.5, ambiguity=0.3,
                          failure_cost=0.3, speed_priority=0.2, context_size=0.3,
                          plan_weight=0.2, alias_state=state)
        assert ms.recheck_required, "Should recheck when new alias added"
        assert any("new_alias" in t for t in ms.recheck_detail.triggers)
        print(f"  ✓ recheck triggered: {ms.recheck_detail.triggers}")
    finally:
        ModelSelector.remove_alias("turbo")


def test_recheck_role_change():
    print("TEST: Role change → recheck")
    state = AliasState()
    orig = ALIAS_REGISTRY["haiku"]["role"]
    ModelSelector.update_alias_role("haiku", "Now a heavy reasoning model")
    try:
        ms = select_model(goal="Test", reasoning_weight=0.5, ambiguity=0.3,
                          failure_cost=0.3, speed_priority=0.2, context_size=0.3,
                          plan_weight=0.2, alias_state=state)
        assert ms.recheck_required, "Should recheck when role changed"
        assert any("alias_meaning_changed" in t for t in ms.recheck_detail.triggers)
        print(f"  ✓ recheck triggered: {ms.recheck_detail.triggers}")
    finally:
        ModelSelector.update_alias_role("haiku", orig)


def test_recheck_version_mapping():
    print("TEST: Version mapping change → recheck")
    state = AliasState()
    os.environ["ANTHROPIC_DEFAULT_OPUS_MODEL"] = "claude-opus-5-0"
    try:
        ms = select_model(goal="Test", reasoning_weight=0.5, ambiguity=0.3,
                          failure_cost=0.3, speed_priority=0.2, context_size=0.3,
                          plan_weight=0.2, alias_state=state)
        assert ms.recheck_required, "Should recheck when version mapping changed"
        assert any("version_mapping" in t for t in ms.recheck_detail.triggers)
        print(f"  ✓ recheck triggered: {ms.recheck_detail.triggers}")
    finally:
        os.environ.pop("ANTHROPIC_DEFAULT_OPUS_MODEL", None)


def test_official_recheck_path():
    print("TEST: Official recheck path")
    path = OfficialRecheckPath()
    findings = path.check_current_aliases()
    assert "method" in findings and "status" in findings
    v = path.verify_alias_still_valid("opus")
    assert v["valid"]
    v = path.verify_alias_still_valid("nonexistent")
    assert not v["valid"]
    print(f"  ✓ Path works: status={findings['status']}")


def test_rc_integration():
    print("TEST: RC → model selection")
    ms1 = select_model_for_rc("RC-1", "調査タスク")
    assert ms1.recommended_model in ("haiku", "sonnet")
    ms5 = select_model_for_rc("RC-5", "設計タスク")
    assert ms5.recommended_model in ("opusplan", "opus")
    print(f"  ✓ RC-1→{ms1.recommended_model}, RC-5→{ms5.recommended_model}")


def run_all():
    print("\n" + "=" * 60)
    print("PHASE 6 MODEL SELECTOR STANDALONE VERIFICATION")
    print("=" * 60 + "\n")

    tests = [
        test_simple_routes_haiku,
        test_standard_routes_sonnet,
        test_complex_routes_opus,
        test_plan_routes_opusplan,
        test_fallback_always_present,
        test_output_shape,
        test_recheck_no_change,
        test_recheck_new_alias,
        test_recheck_role_change,
        test_recheck_version_mapping,
        test_official_recheck_path,
        test_rc_integration,
    ]

    passed = 0
    failed = 0
    for t in tests:
        try:
            t()
            passed += 1
        except AssertionError as e:
            print(f"  ✗ FAIL: {e}")
            failed += 1
        except Exception as e:
            print(f"  ✗ ERROR: {e}")
            failed += 1
        print()

    print("=" * 60)
    print(f"RESULT: {passed}/{passed + failed} PASS")
    print(f"OVERALL: {'✓ PASS' if failed == 0 else '✗ FAIL'}")
    print("=" * 60)
    return failed == 0


if __name__ == "__main__":
    success = run_all()
    exit(0 if success else 1)
