#!/usr/bin/env python3
"""
Proof: Copy-and-Use Deployment
==============================
Verifies the complete "copy folder into project -> setup -> use" workflow.

Run from inside オーケストラエージェント/:
  python3 proof_deploy.py

Proves:
  1. Package can be copied into a fresh project directory
  2. setup.py runs and installs Claude Code slash commands
  3. Orchestrator is invocable from project root
  4. Commands have correct content and paths
  5. Real request execution works through the installed path
  6. No stale state in fresh deployment
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path

PKG = Path(__file__).parent

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


# ── Source directories and files to copy ────────────────────────────

COPY_DIRS = [
    "phase1_information_foundation", "phase2_decision_foundation",
    "phase3_knowledge_foundation", "phase4_execution_foundation",
    "phase5_ai_advisor", "phase6_model_selection",
    "layer7_execution_control", "layer8_quality_gates",
    "layer9_connection_bootstrap", "layer10_watch_sync",
    "layer11_continuous_eval",
    "claude_cc_hook",
]

COPY_FILES = [
    "orchestrator.py", "setup.py",
    "phase5_operational_verification.py",
    "phase4_operational_verification.py",
    "proof_final.py", "proof_5layers.py", "proof_e2e.py",
    "proof_deploy.py", "README.md", ".gitignore",
]


def copy_package_to(dest: Path):
    """Copy the package into dest/<package_name>/ (simulating user copy)."""
    pkg_name = PKG.name  # "オーケストラエージェント"
    pkg_dest = dest / pkg_name
    pkg_dest.mkdir(parents=True, exist_ok=True)

    for subdir in COPY_DIRS:
        src = PKG / subdir
        if src.exists():
            shutil.copytree(src, pkg_dest / subdir,
                            ignore=shutil.ignore_patterns("__pycache__"))
    for fname in COPY_FILES:
        src = PKG / fname
        if src.exists():
            shutil.copy2(src, pkg_dest / fname)

    # Ensure no stale state
    state_dir = pkg_dest / ".orchestra_state"
    if state_dir.exists():
        shutil.rmtree(state_dir)

    return pkg_dest


# ════════════════════════════════════════════════════════════════════
#  PROOF 1: CLEAN COPY
# ════════════════════════════════════════════════════════════════════

section("PROOF 1: Clean Package Copy")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)

    proof("Package copied to project directory",
          pkg_dest.exists() and (pkg_dest / "orchestrator.py").exists(),
          str(pkg_dest.relative_to(project_root)))

    proof("No stale .orchestra_state",
          not (pkg_dest / ".orchestra_state").exists())

    proof("No stale result artifacts",
          not any(pkg_dest.glob("*_RESULTS.json")))


# ════════════════════════════════════════════════════════════════════
#  PROOF 2: SETUP.PY EXECUTION
# ════════════════════════════════════════════════════════════════════

section("PROOF 2: Setup Execution")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)

    # Run setup.py from project root
    r = subprocess.run(
        [sys.executable, str(pkg_dest / "setup.py"),
         "--project-root", str(project_root)],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )

    proof("setup.py exits successfully",
          r.returncode == 0,
          f"rc={r.returncode}")

    if r.returncode != 0:
        print(f"    stdout: {r.stdout[-300:]}")
        print(f"    stderr: {r.stderr[-300:]}")

    proof("setup.py reports 'Setup complete'",
          "Setup complete" in r.stdout,
          r.stdout.split("\n")[-5].strip() if r.stdout else "no output")

    # Verify commands were created
    cmd_dir = project_root / ".claude" / "commands"

    proof("Commands directory created",
          cmd_dir.exists() and cmd_dir.is_dir())

    orchestrate_md = cmd_dir / "orchestrate.md"
    proof("/orchestrate command installed",
          orchestrate_md.exists(),
          str(orchestrate_md.relative_to(project_root)) if orchestrate_md.exists() else "missing")

    status_md = cmd_dir / "orchestra-status.md"
    proof("/orchestra-status command installed",
          status_md.exists())


# ════════════════════════════════════════════════════════════════════
#  PROOF 3: COMMAND CONTENT VALIDATION
# ════════════════════════════════════════════════════════════════════

section("PROOF 3: Command Content Validation")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)
    pkg_rel = pkg_dest.relative_to(project_root)

    subprocess.run(
        [sys.executable, str(pkg_dest / "setup.py"),
         "--project-root", str(project_root)],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )

    # Validate orchestrate.md content
    orchestrate_md = project_root / ".claude" / "commands" / "orchestrate.md"
    if orchestrate_md.exists():
        content = orchestrate_md.read_text()

        proof("orchestrate.md has YAML frontmatter",
              content.startswith("---") and "name: orchestrate" in content)

        proof("orchestrate.md has $ARGUMENTS placeholder",
              "$ARGUMENTS" in content)

        proof("orchestrate.md references correct package path",
              str(pkg_rel) + "/orchestrator.py" in content,
              f"expected path: {pkg_rel}/orchestrator.py")

        proof("orchestrate.md has result handling instructions",
              "blocked_by_connections" in content and "partial" in content)
    else:
        for _ in range(4):
            proof("orchestrate.md content check", False, "file missing")

    # Validate status command
    status_md = project_root / ".claude" / "commands" / "orchestra-status.md"
    if status_md.exists():
        content = status_md.read_text()
        proof("orchestra-status.md has correct path",
              str(pkg_rel) + "/orchestrator.py --status" in content)
    else:
        proof("orchestra-status.md content check", False, "file missing")


# ════════════════════════════════════════════════════════════════════
#  PROOF 4: ORCHESTRATOR INVOCATION FROM PROJECT ROOT
# ════════════════════════════════════════════════════════════════════

section("PROOF 4: Orchestrator Invocation from Project Root")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)
    pkg_rel = pkg_dest.relative_to(project_root)

    # --status from project root (same path as in command file)
    r = subprocess.run(
        [sys.executable, f"{pkg_rel}/orchestrator.py", "--status"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )

    proof("orchestrator --status from project root",
          r.returncode == 0)

    if r.returncode == 0:
        data = json.loads(r.stdout)
        proof("Fresh state: zero records",
              data.get("evaluator", {}).get("records", -1) == 0)
        proof("Fresh state: zero watch hashes",
              data.get("watch_state", {}).get("known_hashes", -1) == 0)

    # --runtime from project root
    r2 = subprocess.run(
        [sys.executable, f"{pkg_rel}/orchestrator.py", "--runtime"],
        capture_output=True, text=True, timeout=30,
        cwd=str(project_root),
    )
    proof("orchestrator --runtime from project root",
          r2.returncode == 0)


# ════════════════════════════════════════════════════════════════════
#  PROOF 5: REAL REQUEST EXECUTION VIA INSTALLED PATH
# ════════════════════════════════════════════════════════════════════

section("PROOF 5: Real Request Execution via Installed Path")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)
    pkg_rel = pkg_dest.relative_to(project_root)

    # Run setup first
    subprocess.run(
        [sys.executable, str(pkg_dest / "setup.py"),
         "--project-root", str(project_root)],
        capture_output=True, text=True, timeout=30,
    )

    # Execute the EXACT command from orchestrate.md
    # (simulating what Claude would run when /orchestrate is invoked)
    request = "ファイル構成を確認してほしい"
    r = subprocess.run(
        [sys.executable, f"{pkg_rel}/orchestrator.py", request],
        capture_output=True, text=True, timeout=180,
        cwd=str(project_root),
    )

    proof("Request execution completes",
          r.returncode == 0,
          f"rc={r.returncode}")

    if r.returncode == 0:
        data = json.loads(r.stdout)
        outcome = data.get("outcome", "")
        classification = data.get("steps", {}).get("classification", "")
        caps = data.get("steps", {}).get("capabilities", [])
        exec_data = data.get("steps", {}).get("execution", {})

        proof("Classification works",
              classification.startswith("RC-"),
              classification)

        proof("Capabilities selected",
              len(caps) > 0,
              str(caps))

        proof("Execution ran actions",
              exec_data.get("executed", 0) > 0,
              f"executed={exec_data.get('executed', 0)}/{exec_data.get('total_actions', 0)}")

        # Acceptable outcomes: success, partial (env-limited), blocked_by_connections
        proof("Outcome is operational (not failure)",
              outcome in ("success", "partial", "blocked_by_connections"),
              f"outcome={outcome}")

        proof("Result was recorded to Layer 11",
              data.get("steps", {}).get("recorded", False))


# ════════════════════════════════════════════════════════════════════
#  PROOF 6: FAIL-FAST ON MISSING PREREQUISITES
# ════════════════════════════════════════════════════════════════════

section("PROOF 6: Prerequisite Checking")

# Verify setup.py --check works
r = subprocess.run(
    [sys.executable, str(PKG / "setup.py"), "--check"],
    capture_output=True, text=True, timeout=10,
)
proof("setup.py --check runs",
      r.returncode == 0,
      "prerequisites OK" if r.returncode == 0 else r.stdout[:100])


# ════════════════════════════════════════════════════════════════════
#  PROOF 7: IDEMPOTENT RE-SETUP
# ════════════════════════════════════════════════════════════════════

section("PROOF 7: Idempotent Re-Setup")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)

    # Run setup twice
    for run_num in (1, 2):
        r = subprocess.run(
            [sys.executable, str(pkg_dest / "setup.py"),
             "--project-root", str(project_root)],
            capture_output=True, text=True, timeout=30,
        )
        if run_num == 1:
            proof("First setup succeeds", r.returncode == 0)
        else:
            proof("Re-setup succeeds (idempotent)", r.returncode == 0)

    # Verify only expected files exist (no duplicates)
    cmd_dir = project_root / ".claude" / "commands"
    if cmd_dir.exists():
        cmd_files = list(cmd_dir.iterdir())
        proof("Exactly 2 command files after re-setup",
              len(cmd_files) == 2,
              str([f.name for f in cmd_files]))
    else:
        proof("Exactly 2 command files after re-setup",
              False,
              ".claude/commands directory not created by setup.py")


# ════════════════════════════════════════════════════════════════════
#  PROOF 8: HOOK DEPLOYMENT & EXECUTION
# ════════════════════════════════════════════════════════════════════

section("PROOF 8: Hook Deployment & Execution")

with tempfile.TemporaryDirectory() as td:
    project_root = Path(td)
    pkg_dest = copy_package_to(project_root)

    # Verify hook scripts are copied
    hook_dir = pkg_dest / "claude_cc_hook"
    proof("claude_cc_hook/ directory copied",
          hook_dir.exists() and hook_dir.is_dir())

    ups_hook = hook_dir / "user_prompt_orchestrate_hook.py"
    ss_hook = hook_dir / "session_start_orchestra_hook.py"
    proof("UserPromptSubmit hook script exists", ups_hook.exists())
    proof("SessionStart hook script exists", ss_hook.exists())

    # Run setup to install hooks into settings.json
    subprocess.run(
        [sys.executable, str(pkg_dest / "setup.py"),
         "--project-root", str(project_root)],
        capture_output=True, text=True, timeout=30,
    )

    # Verify settings.json has both hooks
    settings_path = project_root / ".claude" / "settings.json"
    if settings_path.exists():
        sdata = json.loads(settings_path.read_text())
        hooks = sdata.get("hooks", {})

        has_ups = any(
            "user_prompt_orchestrate_hook.py" in str(h.get("command", ""))
            for g in hooks.get("UserPromptSubmit", [])
            for h in g.get("hooks", [])
        )
        proof("settings.json has UserPromptSubmit hook", has_ups)

        has_ss = any(
            "session_start_orchestra_hook.py" in str(h.get("command", ""))
            for g in hooks.get("SessionStart", [])
            for h in g.get("hooks", [])
        )
        proof("settings.json has SessionStart hook", has_ss)

        # Verify hook commands use $CLAUDE_PROJECT_DIR (portable)
        for hook_type in ("UserPromptSubmit", "SessionStart"):
            for g in hooks.get(hook_type, []):
                for h in g.get("hooks", []):
                    cmd = h.get("command", "")
                    if "orchestra" in cmd:
                        proof(f"{hook_type} hook uses $CLAUDE_PROJECT_DIR",
                              "$CLAUDE_PROJECT_DIR" in cmd,
                              cmd[:70])
    else:
        for _ in range(4):
            proof("settings.json hook check", False, "file missing")

    # Functional test: hook scripts point to valid orchestrator paths
    # Simulate UserPromptSubmit with empty prompt → should return {}
    hook_input = json.dumps({
        "hook_event_name": "UserPromptSubmit",
        "prompt": "",
        "cwd": str(project_root),
    })
    r_empty = subprocess.run(
        [sys.executable, str(ups_hook)],
        input=hook_input, capture_output=True, text=True, timeout=10,
    )
    proof("Hook: empty prompt returns {}",
          r_empty.returncode == 0 and r_empty.stdout.strip() == "{}")

    # Simulate UserPromptSubmit with real prompt → should return additionalContext
    hook_input = json.dumps({
        "hook_event_name": "UserPromptSubmit",
        "prompt": "ステータスを確認",
        "cwd": str(project_root),
    })
    r_real = subprocess.run(
        [sys.executable, str(ups_hook)],
        input=hook_input, capture_output=True, text=True, timeout=90,
    )
    if r_real.returncode == 0 and r_real.stdout.strip() != "{}":
        try:
            hook_out = json.loads(r_real.stdout)
            ctx = hook_out.get("hookSpecificOutput", {}).get("additionalContext", "")
            proof("Hook: real prompt returns orchestrator context",
                  "オーケストラ" in ctx and len(ctx) > 100,
                  f"ctx_len={len(ctx)}")
        except json.JSONDecodeError:
            proof("Hook: real prompt returns valid JSON", False,
                  r_real.stdout[:80])
    else:
        proof("Hook: real prompt fires orchestrator",
              False,
              f"rc={r_real.returncode}, stdout={r_real.stdout[:60]}")


# ── Final Summary ────────────────────────────────────────────────────

section("FINAL SUMMARY")
total = passed + failed
print(f"  Total: {total}")
print(f"  Passed: {passed}")
print(f"  Failed: {failed}")
print(f"  Result: {'ALL PASS' if failed == 0 else 'FAILURES EXIST'}")
print(f"{'='*64}")

sys.exit(0 if failed == 0 else 1)
