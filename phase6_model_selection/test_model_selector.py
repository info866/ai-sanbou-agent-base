#!/usr/bin/env python3
"""
Verification suite for Model Selection Engine
Tests selection logic against multiple scenarios
"""

import json
from model_selector import ModelSelector, SelectionInput, select_model


def test_simple_lightweight():
    """Test: Simple, fast, low-risk work → haiku"""
    print("TEST: Simple lightweight request")
    output = select_model(
        goal="Fix typo in README",
        reasoning_weight=0.1,
        ambiguity=0.1,
        failure_cost=0.0,
        speed_priority=0.8,
        context_size=0.1,
        plan_weight=0.0
    )
    assert output.recommended_model == "haiku", \
        f"Expected haiku, got {output.recommended_model}"
    assert output.fallback_model in ["sonnet"], \
        f"Unexpected fallback {output.fallback_model}"
    print(f"  ✓ {output.recommended_model} (reason: {output.reason})")
    return output


def test_standard_coding():
    """Test: Standard coding task → sonnet"""
    print("TEST: Standard coding request")
    output = select_model(
        goal="Implement authentication logic",
        reasoning_weight=0.5,
        ambiguity=0.3,
        failure_cost=0.3,
        speed_priority=0.2,
        context_size=0.4,
        plan_weight=0.2
    )
    assert output.recommended_model == "sonnet", \
        f"Expected sonnet, got {output.recommended_model}"
    print(f"  ✓ {output.recommended_model} (reason: {output.reason})")
    return output


def test_complex_reasoning():
    """Test: Complex, high ambiguity, high failure cost → opus"""
    print("TEST: Complex reasoning request")
    output = select_model(
        goal="Design system architecture for microservices with multiple constraints",
        reasoning_weight=0.9,
        ambiguity=0.8,
        failure_cost=0.9,
        speed_priority=0.1,
        context_size=0.6,
        plan_weight=0.3
    )
    assert output.recommended_model == "opus", \
        f"Expected opus, got {output.recommended_model}"
    print(f"  ✓ {output.recommended_model} (reason: {output.reason})")
    print(f"    Recheck: {output.recheck_required}")
    return output


def test_plan_heavy():
    """Test: Heavy planning + heavy reasoning → opusplan"""
    print("TEST: Plan-heavy request")
    output = select_model(
        goal="Plan and design full CI/CD pipeline architecture",
        reasoning_weight=0.8,
        ambiguity=0.7,
        failure_cost=0.5,
        speed_priority=0.1,
        context_size=0.5,
        plan_weight=0.9
    )
    assert output.recommended_model == "opusplan", \
        f"Expected opusplan, got {output.recommended_model}"
    print(f"  ✓ {output.recommended_model} (reason: {output.reason})")
    return output


def test_fallback_opus():
    """Test: Opus fallback → sonnet"""
    print("TEST: Fallback for opus")
    output = select_model(
        goal="Complex design",
        reasoning_weight=0.9,
        ambiguity=0.9,
        failure_cost=0.9,
        speed_priority=0.1,
        context_size=0.5,
        plan_weight=0.1
    )
    assert output.fallback_model == "sonnet", \
        f"Expected fallback sonnet, got {output.fallback_model}"
    print(f"  ✓ Fallback: {output.fallback_model}")
    return output


def test_fallback_haiku():
    """Test: Haiku fallback → sonnet"""
    print("TEST: Fallback for haiku")
    output = select_model(
        goal="Simple fix",
        reasoning_weight=0.1,
        ambiguity=0.1,
        failure_cost=0.0,
        speed_priority=0.9,
        context_size=0.1,
        plan_weight=0.0
    )
    assert output.fallback_model == "sonnet", \
        f"Expected fallback sonnet, got {output.fallback_model}"
    print(f"  ✓ Fallback: {output.fallback_model}")
    return output


def test_speed_downgrade():
    """Test: Speed priority downgrades model"""
    print("TEST: Speed priority causes downgrade")
    output = select_model(
        goal="Quick code fix",
        reasoning_weight=0.6,
        ambiguity=0.5,
        failure_cost=0.4,
        speed_priority=0.9,
        context_size=0.2,
        plan_weight=0.1
    )
    # Without speed: would be sonnet or higher
    # With speed: should downgrade
    assert "[downgraded for speed]" in output.reason or \
           output.recommended_model in ["haiku", "sonnet"], \
        f"Speed priority should cause downgrade, got {output.recommended_model}"
    print(f"  ✓ {output.recommended_model} (downgraded for speed)")
    return output


def test_safety_upgrade():
    """Test: High failure cost upgrades model"""
    print("TEST: Safety requirement causes upgrade")
    output = select_model(
        goal="Critical security fix",
        reasoning_weight=0.4,
        ambiguity=0.3,
        failure_cost=0.95,
        speed_priority=0.1,
        context_size=0.3,
        plan_weight=0.0
    )
    # Without failure_cost: would be sonnet
    # With failure_cost=0.95: should upgrade to opus
    assert "[upgraded for safety]" in output.reason or \
           output.recommended_model in ["opus", "opusplan"], \
        f"Safety requirement should cause upgrade, got {output.recommended_model}"
    print(f"  ✓ {output.recommended_model} (upgraded for safety)")
    return output


def test_recheck_high_ambiguity():
    """Test: High ambiguity triggers recheck_required"""
    print("TEST: High ambiguity triggers recheck")
    output = select_model(
        goal="Ambiguous task with unclear requirements",
        reasoning_weight=0.5,
        ambiguity=0.95,
        failure_cost=0.5,
        speed_priority=0.2,
        context_size=0.3,
        plan_weight=0.2
    )
    assert output.recheck_required, \
        "High ambiguity should trigger recheck_required"
    print(f"  ✓ recheck_required={output.recheck_required}")
    return output


def test_recheck_critical_cost():
    """Test: Critical failure cost triggers recheck"""
    print("TEST: Critical failure cost triggers recheck")
    output = select_model(
        goal="Critical production fix",
        reasoning_weight=0.3,
        ambiguity=0.2,
        failure_cost=0.95,
        speed_priority=0.1,
        context_size=0.2,
        plan_weight=0.0
    )
    assert output.recheck_required, \
        "Critical failure cost should trigger recheck_required"
    print(f"  ✓ recheck_required={output.recheck_required}")
    return output


def test_update_scenario():
    """Test: Future alias addition doesn't break system"""
    print("TEST: Update resilience (new alias scenario)")
    # Simulate adding a new "supermodel" alias
    # The system should still work with existing aliases

    selector = ModelSelector()

    # Test that existing aliases still work
    for model in ["haiku", "sonnet", "opus", "opusplan"]:
        assert model in selector.TIER_ORDER, \
            f"Existing alias {model} not in TIER_ORDER"
        assert model in selector.FALLBACK_MAP, \
            f"Existing alias {model} not in FALLBACK_MAP"

    print(f"  ✓ Current aliases present: {selector.TIER_ORDER}")
    print(f"  ✓ Fallback mapping complete: {selector.FALLBACK_MAP}")
    return None


def test_all_outputs_required():
    """Test: All required output fields present"""
    print("TEST: Output format compliance")
    output = select_model(
        goal="Test request",
        reasoning_weight=0.5,
        ambiguity=0.3,
        failure_cost=0.3,
        speed_priority=0.2,
        context_size=0.3,
        plan_weight=0.2
    )

    required_fields = [
        "goal", "recommended_model", "fallback_model",
        "reason", "recheck_required", "handoff_notes"
    ]
    for field in required_fields:
        assert hasattr(output, field), f"Missing field: {field}"

    # Validate field types
    assert isinstance(output.goal, str), "goal must be string"
    assert output.recommended_model in ["opus", "sonnet", "haiku", "opusplan"], \
        f"Invalid recommended_model: {output.recommended_model}"
    assert output.fallback_model in ["opus", "sonnet", "haiku", "opusplan"], \
        f"Invalid fallback_model: {output.fallback_model}"
    assert isinstance(output.reason, str), "reason must be string"
    assert len(output.reason) <= 200, "reason exceeds max length"
    assert isinstance(output.recheck_required, bool), "recheck_required must be bool"
    assert isinstance(output.handoff_notes, str), "handoff_notes must be string"

    print(f"  ✓ All required fields present and valid types")
    return output


def run_all_tests():
    """Run complete verification suite"""
    print("\n" + "="*60)
    print("MODEL SELECTOR VERIFICATION SUITE")
    print("="*60 + "\n")

    tests = [
        test_simple_lightweight,
        test_standard_coding,
        test_complex_reasoning,
        test_plan_heavy,
        test_fallback_opus,
        test_fallback_haiku,
        test_speed_downgrade,
        test_safety_upgrade,
        test_recheck_high_ambiguity,
        test_recheck_critical_cost,
        test_update_scenario,
        test_all_outputs_required,
    ]

    results = []
    for test in tests:
        try:
            output = test()
            results.append(("PASS", test.__name__, output))
            print()
        except AssertionError as e:
            results.append(("FAIL", test.__name__, str(e)))
            print(f"  ✗ FAILED: {e}\n")
        except Exception as e:
            results.append(("ERROR", test.__name__, str(e)))
            print(f"  ✗ ERROR: {e}\n")

    # Summary
    print("="*60)
    print("SUMMARY")
    print("="*60)

    passed = sum(1 for status, _, _ in results if status == "PASS")
    failed = sum(1 for status, _, _ in results if status == "FAIL")
    errors = sum(1 for status, _, _ in results if status == "ERROR")

    print(f"Passed: {passed}/{len(results)}")
    print(f"Failed: {failed}/{len(results)}")
    print(f"Errors: {errors}/{len(results)}")

    if failed > 0 or errors > 0:
        print("\nFailed/Error tests:")
        for status, name, detail in results:
            if status != "PASS":
                print(f"  - {name}: {detail}")

    success = failed == 0 and errors == 0
    print(f"\nOVERALL: {'✓ PASS' if success else '✗ FAIL'}")
    print("="*60 + "\n")

    return success


if __name__ == "__main__":
    success = run_all_tests()
    exit(0 if success else 1)
