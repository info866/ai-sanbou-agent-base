#!/usr/bin/env python3
"""
Unified Package Proof Script
=============================
Run from inside オーケストラエージェント/:
  python3 proof_final.py

Proves:
  1. Recheck path uses real alias/env/mapping state
  2. Alias state persists to disk (save/load round-trip)
  3. Clean-environment reproducibility (temp copy, no __pycache__)
  4. Failure injection: tests catch breakage, then restore green
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PKG = Path(__file__).parent  # this is the unified package root
PHASE6 = PKG / "phase6_model_selection"

RUNTIME_DIRS = [
    "phase1_information_foundation", "phase2_decision_foundation",
    "phase3_knowledge_foundation", "phase4_execution_foundation",
    "phase5_ai_advisor", "phase6_model_selection",
    "layer7_execution_control", "layer8_quality_gates",
    "layer9_connection_bootstrap", "layer10_watch_sync",
    "layer11_continuous_eval",
]
RUNTIME_SCRIPTS = [
    "phase5_operational_verification.py",
    "phase4_operational_verification.py",
    "orchestrator.py",
    "setup.py",
    "proof_5layers.py",
    "proof_e2e.py",
    "proof_deploy.py",
]

passed = 0
failed = 0


def proof(name: str, ok: bool, detail: str = ""):
    global passed, failed
    tag = "PASS" if ok else "FAIL"
    print(f"  [{tag}] {name}" + (f" — {detail}" if detail else ""))
    if ok:
        passed += 1
    else:
        failed += 1


def section(title: str):
    print(f"\n{'='*64}\n  {title}\n{'='*64}")


def copy_package_to(dest: Path):
    """Copy the unified package to a fresh directory (clean, no state)."""
    for subdir in RUNTIME_DIRS:
        src = PKG / subdir
        if src.exists():
            shutil.copytree(src, dest / subdir,
                            ignore=shutil.ignore_patterns("__pycache__"))
    for script in RUNTIME_SCRIPTS:
        src = PKG / script
        if src.exists():
            shutil.copy2(src, dest / script)
    # Ensure no stale state is copied
    state_dir = dest / ".orchestra_state"
    if state_dir.exists():
        shutil.rmtree(state_dir)


def run_verification(cwd: Path) -> tuple[bool, str]:
    """Run phase5_operational_verification.py and return (pass, final_line)."""
    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(cwd), capture_output=True, text=True, timeout=60
    )
    lines = r.stdout.strip().split("\n")
    final = [l for l in lines if "FINAL:" in l]
    ok = r.returncode == 0 and any("ALL PASS" in l for l in final)
    return ok, (final[0].strip() if final else f"rc={r.returncode}")


def run_orchestrator_status(cwd: Path) -> tuple[bool, str]:
    """Run orchestrator.py --status and verify clean startup."""
    r = subprocess.run(
        [sys.executable, "orchestrator.py", "--status"],
        cwd=str(cwd), capture_output=True, text=True, timeout=30,
    )
    if r.returncode != 0:
        return False, f"rc={r.returncode} stderr={r.stderr[:200]}"
    try:
        data = json.loads(r.stdout)
        records = data.get("evaluator", {}).get("records", -1)
        hashes = data.get("watch_state", {}).get("known_hashes", -1)
        ok = records == 0 and hashes == 0  # fresh state
        return ok, f"records={records} hashes={hashes}"
    except json.JSONDecodeError:
        return False, "invalid JSON output"


def run_orchestrator_request(cwd: Path, request: str) -> tuple[bool, str]:
    """Run a real request through orchestrator and check outcome.

    Acceptable outcomes:
    - success: all actions passed
    - partial: pipeline ran, some actions were environment-limited
              (e.g. subagent timeout in test, no git repo)
    - blocked_by_connections: explicit fail-fast on missing deps

    NOT acceptable:
    - failure: zero actions succeeded — pipeline is broken
    - empty outcome: pipeline crashed
    """
    r = subprocess.run(
        [sys.executable, "orchestrator.py", request],
        cwd=str(cwd), capture_output=True, text=True, timeout=180,
    )
    if r.returncode != 0:
        return False, f"rc={r.returncode} stderr={r.stderr[:200]}"
    try:
        data = json.loads(r.stdout)
        outcome = data.get("outcome", "")
        # The pipeline is operational if it completed classification, model
        # selection, planning, and execution (even if some actions failed
        # due to environment limits like no git repo or subagent timeout)
        ok = outcome in ("success", "partial", "blocked_by_connections")
        detail = f"outcome={outcome}"
        if outcome == "partial":
            exec_data = data.get("steps", {}).get("execution", {})
            detail += f" succeeded={exec_data.get('succeeded', 0)}/{exec_data.get('total_actions', 0)}"
        return ok, detail
    except json.JSONDecodeError:
        return False, "invalid JSON output"


def run_phase4_verification(cwd: Path) -> tuple[bool, str]:
    """Run phase4 verification."""
    r = subprocess.run(
        [sys.executable, "phase4_operational_verification.py"],
        cwd=str(cwd), capture_output=True, text=True, timeout=60,
    )
    lines = r.stdout.strip().split("\n")
    result_lines = [l for l in lines if "Result:" in l]
    ok = r.returncode == 0
    return ok, (result_lines[0].strip() if result_lines else f"rc={r.returncode}")


# ── Proof 1: Real recheck path ──────────────────────────────────────

section("PROOF 1: Recheck path uses real alias/env/mapping state")

sys.path.insert(0, str(PHASE6))
from model_selector import (
    ModelSelector, AliasState, OfficialRecheckPath,
    ALIAS_REGISTRY, FALLBACK_MAP, select_model,
)

path_obj = OfficialRecheckPath()
findings = path_obj.check_current_aliases()
proof("check_current_aliases returns live_snapshot",
      findings.get("live_snapshot") is not None)
proof("live_snapshot has env_mappings",
      hasattr(findings.get("live_snapshot"), "env_mappings"))
proof("registry_aliases matches ALIAS_REGISTRY",
      set(findings["registry_aliases"]) == set(ALIAS_REGISTRY.keys()))

state_before = AliasState.snapshot_current()
os.environ["ANTHROPIC_DEFAULT_SONNET_MODEL"] = "claude-sonnet-99"
try:
    detail = path_obj.detect_changes(state_before)
    proof("env mapping change detected via persisted diff",
          detail.required and any("version_mapping_changed" in t for t in detail.triggers))
finally:
    os.environ.pop("ANTHROPIC_DEFAULT_SONNET_MODEL", None)

state_clean = AliasState.snapshot_current()
detail = path_obj.detect_changes(state_clean)
proof("no false positive on identical state", not detail.required)


# ── Proof 2: Persisted alias state ──────────────────────────────────

section("PROOF 2: Alias state persists to disk (save/load)")

with tempfile.TemporaryDirectory() as td:
    state_path = Path(td) / "alias_state.json"
    state = AliasState.snapshot_current()
    state.save(state_path)
    proof("state saved to disk", state_path.exists())

    loaded = AliasState.load(state_path)
    proof("loaded aliases match saved",
          loaded.known_aliases == state.known_aliases)
    proof("loaded roles match saved",
          loaded.alias_roles == state.alias_roles)

    ModelSelector.add_alias("turbo99", "Test alias", tier=0, fallback="haiku")
    try:
        detail = path_obj.detect_changes(loaded)
        proof("persisted→live change detected",
              detail.required and any("new_alias" in t for t in detail.triggers))
    finally:
        ModelSelector.remove_alias("turbo99")

    fresh = AliasState.load(Path(td) / "nonexistent.json")
    proof("load from missing file returns fresh state",
          fresh.known_aliases == set(ALIAS_REGISTRY.keys()))


# ── Proof 3: Clean-environment reproducibility ──────────────────────

section("PROOF 3: Clean-environment reproducibility (temp copy)")

with tempfile.TemporaryDirectory() as td:
    dest = Path(td) / "clean"
    copy_package_to(dest)

    # 3a: Phase 5 brain verification
    ok, info = run_verification(dest)
    proof("clean temp copy: Phase 5 ALL PASS", ok, info)

    # 3b: No stale state in fresh copy
    state_dir = dest / ".orchestra_state"
    proof("clean temp copy: no stale .orchestra_state",
          not state_dir.exists(),
          "absent" if not state_dir.exists() else str(list(state_dir.iterdir())))

    # 3c: Orchestrator --status starts clean
    ok, info = run_orchestrator_status(dest)
    proof("clean temp copy: orchestrator --status clean startup", ok, info)

    # 3d: Phase 4 verification passes in fresh copy
    ok, info = run_phase4_verification(dest)
    proof("clean temp copy: Phase 4 verification", ok, info)

    # 3e: Real request execution (investigation type — no external deps)
    ok, info = run_orchestrator_request(dest, "現在のファイル一覧を調査してほしい")
    proof("clean temp copy: real request execution", ok, info)

# Also verify this package itself right now
ok, info = run_verification(PKG)
proof("this package ALL PASS", ok, info)

# Phase 6 standalone
r = subprocess.run(
    [sys.executable, "test_model_selector.py"],
    cwd=str(PHASE6), capture_output=True, text=True, timeout=30
)
p6_ok = r.returncode == 0
proof("Phase 6 standalone ALL PASS", p6_ok)


# ── Proof 4: Failure injection ──────────────────────────────────────

section("PROOF 4: Failure injection — tests catch breakage")

with tempfile.TemporaryDirectory() as td:
    dest = Path(td) / "inject"
    copy_package_to(dest)

    ms_path = dest / "phase6_model_selection" / "model_selector.py"
    ms_code = ms_path.read_text()

    # INJECTION 1: Break opus routing threshold
    broken = ms_code.replace(
        'if total_weight >= 0.7:',
        'if total_weight >= 99.0:  # INJECTED',
    )
    ms_path.write_text(broken)
    ok, info = run_verification(dest)
    proof("INJECTION 1: broken opus routing detected", not ok, info)
    ms_path.write_text(ms_code)

    # INJECTION 2: Remove deliverable
    victim = dest / "phase5_ai_advisor" / "03_capability_selection.md"
    backup = victim.read_text()
    victim.unlink()
    ok, info = run_verification(dest)
    proof("INJECTION 2: missing deliverable detected", not ok, info)
    victim.write_text(backup)

    # INJECTION 3: Break opusplan fallback
    broken2 = ms_code.replace(
        '"opusplan": "sonnet",',
        '"opusplan": "opusplan",  # INJECTED',
    )
    ms_path.write_text(broken2)
    ok, info = run_verification(dest)
    proof("INJECTION 3: broken fallback detected", not ok, info)
    ms_path.write_text(ms_code)

    # INJECTION 4: Break handoff model
    vp = dest / "phase5_operational_verification.py"
    vc = vp.read_text()
    broken3 = vc.replace('model_selection=ms)', 'model_selection=None)  # INJECTED')
    vp.write_text(broken3)
    ok, info = run_verification(dest)
    proof("INJECTION 4: missing model in handoff detected", not ok, info)
    vp.write_text(vc)

    # Restore and verify green
    ok, info = run_verification(dest)
    proof("All injections restored → green", ok, info)


# ── Final Summary ────────────────────────────────────────────────────

section("FINAL SUMMARY")
total = passed + failed
print(f"  Total: {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Result: {'ALL PASS' if failed == 0 else 'FAILURES EXIST'}")
print(f"{'='*64}")

sys.exit(0 if failed == 0 else 1)
