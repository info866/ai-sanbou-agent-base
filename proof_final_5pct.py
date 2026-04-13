#!/usr/bin/env python3
"""
Final 5% Proof Script
=====================
Proves:
  1. Recheck path uses real alias/env/mapping state (not local assumptions)
  2. Alias state persists to disk and recheck uses actual before/after diff
  3. Clean-environment reproducibility (temp copy, no __pycache__)
  4. Deployment package works standalone
  5. Failure injection: tests catch breakage, then restore green

Run from project root:
  python3 proof_final_5pct.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).parent
PHASE6 = ROOT / "phase6_model_selection"
DEPLOY = ROOT / "オーケストラエージェント"

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


# ── Proof 1: Real recheck path ──────────────────────────────────────

section("PROOF 1: Recheck path uses real alias/env/mapping state")

sys.path.insert(0, str(PHASE6))
from model_selector import (
    ModelSelector, AliasState, OfficialRecheckPath,
    ALIAS_REGISTRY, FALLBACK_MAP, select_model,
)

# 1a. check_current_aliases returns live snapshot with real state
path = OfficialRecheckPath()
findings = path.check_current_aliases()
proof("check_current_aliases returns live_snapshot",
      findings.get("live_snapshot") is not None,
      f"type={type(findings.get('live_snapshot')).__name__}")
proof("live_snapshot has known_aliases",
      hasattr(findings.get("live_snapshot"), "known_aliases"))
proof("live_snapshot has env_mappings",
      hasattr(findings.get("live_snapshot"), "env_mappings"))
proof("registry_aliases matches ALIAS_REGISTRY",
      set(findings["registry_aliases"]) == set(ALIAS_REGISTRY.keys()))

# 1b. detect_changes compares against persisted env_mappings
state_before = AliasState.snapshot_current()
os.environ["ANTHROPIC_DEFAULT_SONNET_MODEL"] = "claude-sonnet-99"
try:
    detail = path.detect_changes(state_before)
    proof("env mapping change detected via persisted diff",
          detail.required and any("version_mapping_changed" in t for t in detail.triggers),
          f"triggers={detail.triggers}")
finally:
    os.environ.pop("ANTHROPIC_DEFAULT_SONNET_MODEL", None)

# 1c. No false positive when nothing changed
state_clean = AliasState.snapshot_current()
detail = path.detect_changes(state_clean)
proof("no false positive on identical state",
      not detail.required, f"triggers={detail.triggers}")


# ── Proof 2: Persisted alias state ──────────────────────────────────

section("PROOF 2: Alias state persists to disk (save/load round-trip)")

with tempfile.TemporaryDirectory() as td:
    state_path = Path(td) / "alias_state.json"

    # Save current state
    state = AliasState.snapshot_current()
    state.save(state_path)
    proof("state saved to disk", state_path.exists(), f"size={state_path.stat().st_size}")

    # Load it back
    loaded = AliasState.load(state_path)
    proof("loaded aliases match saved",
          loaded.known_aliases == state.known_aliases,
          f"saved={sorted(state.known_aliases)} loaded={sorted(loaded.known_aliases)}")
    proof("loaded roles match saved",
          loaded.alias_roles == state.alias_roles)
    proof("loaded env_mappings match saved",
          loaded.env_mappings == state.env_mappings)

    # Now mutate registry, detect changes against persisted state
    ModelSelector.add_alias("turbo99", "Test alias", tier=0, fallback="haiku")
    try:
        detail = path.detect_changes(loaded)
        proof("persisted→live change detected after alias add",
              detail.required and any("new_alias" in t for t in detail.triggers))
    finally:
        ModelSelector.remove_alias("turbo99")

    # Load from non-existent path returns fresh state
    fresh = AliasState.load(Path(td) / "nonexistent.json")
    proof("load from missing file returns fresh state",
          fresh.known_aliases == set(ALIAS_REGISTRY.keys()))


# ── Proof 3: Fresh-environment reproducibility ──────────────────────

section("PROOF 3: Clean-environment reproducibility (temp copy)")

with tempfile.TemporaryDirectory() as td:
    dest = Path(td) / "orchestra"
    # Copy only the needed runtime files
    for subdir in ["phase1_information_foundation", "phase2_decision_foundation",
                   "phase3_knowledge_foundation", "phase4_execution_foundation",
                   "phase5_ai_advisor", "phase6_model_selection"]:
        src = ROOT / subdir
        if src.exists():
            shutil.copytree(src, dest / subdir, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "phase5_operational_verification.py", dest / "phase5_operational_verification.py")
    shutil.copy2(ROOT / "phase4_operational_verification.py", dest / "phase4_operational_verification.py")

    # Run verification in the clean copy
    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(dest), capture_output=True, text=True, timeout=60
    )
    lines = r.stdout.strip().split("\n")
    final_line = [l for l in lines if "FINAL:" in l]
    clean_pass = r.returncode == 0 and any("ALL PASS" in l for l in final_line)
    proof("clean temp copy ALL PASS",
          clean_pass,
          final_line[0].strip() if final_line else f"rc={r.returncode}")
    if not clean_pass and r.stderr:
        print(f"    stderr: {r.stderr[:200]}")


# ── Proof 4: Deployment package standalone ──────────────────────────

section("PROOF 4: Deployment package works standalone")

# First sync latest changes
for subdir in ["phase6_model_selection"]:
    src = ROOT / subdir
    dst = DEPLOY / subdir
    if dst.exists():
        shutil.rmtree(dst)
    shutil.copytree(src, dst, ignore=shutil.ignore_patterns("__pycache__"))
shutil.copy2(ROOT / "phase5_operational_verification.py", DEPLOY / "phase5_operational_verification.py")

# Run from deployment directory as a standalone package
r = subprocess.run(
    [sys.executable, "phase5_operational_verification.py"],
    cwd=str(DEPLOY), capture_output=True, text=True, timeout=60
)
lines = r.stdout.strip().split("\n")
final_line = [l for l in lines if "FINAL:" in l]
deploy_pass = r.returncode == 0 and any("ALL PASS" in l for l in final_line)
proof("deployment package ALL PASS standalone",
      deploy_pass,
      final_line[0].strip() if final_line else f"rc={r.returncode}")

# Also run Phase 6 standalone tests from deployment
r2 = subprocess.run(
    [sys.executable, "test_model_selector.py"],
    cwd=str(DEPLOY / "phase6_model_selection"), capture_output=True, text=True, timeout=30
)
p6_lines = r2.stdout.strip().split("\n")
p6_final = [l for l in p6_lines if "OVERALL:" in l]
p6_pass = r2.returncode == 0 and any("PASS" in l for l in p6_final)
proof("deployment Phase 6 standalone ALL PASS",
      p6_pass,
      p6_final[0].strip() if p6_final else f"rc={r2.returncode}")


# ── Proof 5: Failure injection ──────────────────────────────────────

section("PROOF 5: Failure injection — tests catch breakage")

# We'll inject failures into a temp copy and verify the test suite catches them.

with tempfile.TemporaryDirectory() as td:
    dest = Path(td) / "inject"
    for subdir in ["phase1_information_foundation", "phase2_decision_foundation",
                   "phase3_knowledge_foundation", "phase4_execution_foundation",
                   "phase5_ai_advisor", "phase6_model_selection"]:
        src = ROOT / subdir
        if src.exists():
            shutil.copytree(src, dest / subdir, ignore=shutil.ignore_patterns("__pycache__"))
    shutil.copy2(ROOT / "phase5_operational_verification.py", dest / "phase5_operational_verification.py")
    shutil.copy2(ROOT / "phase4_operational_verification.py", dest / "phase4_operational_verification.py")

    # INJECTION 1: Break model routing by forcing haiku for everything
    ms_path = dest / "phase6_model_selection" / "model_selector.py"
    ms_code = ms_path.read_text()
    # Sabotage: replace the opus threshold to force everything to haiku
    broken = ms_code.replace(
        'if total_weight >= 0.7:',
        'if total_weight >= 99.0:  # INJECTED BREAK',
    )
    ms_path.write_text(broken)

    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(dest), capture_output=True, text=True, timeout=60
    )
    injection1_caught = r.returncode != 0
    fail_count = sum(1 for l in r.stdout.split("\n") if "[FAIL]" in l)
    proof("INJECTION 1: broken opus routing detected",
          injection1_caught,
          f"exit={r.returncode}, FAIL_lines={fail_count}")

    # Restore for next injection
    ms_path.write_text(ms_code)

    # INJECTION 2: Remove a Phase 5 deliverable
    victim = dest / "phase5_ai_advisor" / "03_capability_selection.md"
    victim_backup = victim.read_text()
    victim.unlink()

    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(dest), capture_output=True, text=True, timeout=60
    )
    injection2_caught = r.returncode != 0
    proof("INJECTION 2: missing deliverable detected",
          injection2_caught,
          f"exit={r.returncode}")

    # Restore
    victim.write_text(victim_backup)

    # INJECTION 3: Break fallback map so opusplan fallback == opusplan
    broken2 = ms_code.replace(
        '"opusplan": "sonnet",',
        '"opusplan": "opusplan",  # INJECTED BREAK',
    )
    ms_path.write_text(broken2)

    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(dest), capture_output=True, text=True, timeout=60
    )
    injection3_caught = r.returncode != 0
    proof("INJECTION 3: broken opusplan fallback detected",
          injection3_caught,
          f"exit={r.returncode}")

    # Restore
    ms_path.write_text(ms_code)

    # INJECTION 4: Break handoff (remove model from handoff)
    verif_path = dest / "phase5_operational_verification.py"
    verif_code = verif_path.read_text()
    broken3 = verif_code.replace(
        'model_selection=ms)',
        'model_selection=None)  # INJECTED BREAK',
    )
    verif_path.write_text(broken3)

    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(dest), capture_output=True, text=True, timeout=60
    )
    injection4_caught = r.returncode != 0
    proof("INJECTION 4: missing model in handoff detected",
          injection4_caught,
          f"exit={r.returncode}")

    # Restore and verify green
    verif_path.write_text(verif_code)
    ms_path.write_text(ms_code)
    r = subprocess.run(
        [sys.executable, "phase5_operational_verification.py"],
        cwd=str(dest), capture_output=True, text=True, timeout=60
    )
    restored_green = r.returncode == 0
    proof("All injections restored → green again",
          restored_green,
          f"exit={r.returncode}")


# ── Final Summary ────────────────────────────────────────────────────

section("FINAL SUMMARY")
total = passed + failed
print(f"  Total: {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Result: {'ALL PASS' if failed == 0 else 'FAILURES EXIST'}")
print(f"{'='*64}")

sys.exit(0 if failed == 0 else 1)
