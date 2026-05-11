#!/usr/bin/env python3
"""
Orchestra Agent — Project Setup
================================
One-time initializer: wire the orchestrator into a project's Claude Code
hooks and slash commands.

Usage:
  python3 オーケストラエージェント/setup.py          (from project root)
  python3 setup.py                                  (from inside package)
  python3 setup.py --project-root /path/to/project  (explicit root)
  python3 setup.py --no-hook                        (slash commands only; skip all hooks)
  python3 setup.py --slash-only                     (alias for --no-hook)

What it does:
  1. Detects project root (git root, or parent directory)
  2. Checks prerequisites (Python 3.10+, git)
  3. Installs .claude/commands/orchestrate.md      → /orchestrate
  4. Installs .claude/commands/orchestra-status.md  → /orchestra-status
  5. Merges SessionStart hook  → セッション開始時に --status/--runtime を自動注入
  6. Merges UserPromptSubmit hook → 全プロンプトでオーケストレータを自動実行（Zero-Slash）
  7. Verifies the orchestrator is reachable from project root

フックコマンドは $CLAUDE_PROJECT_DIR を使うため、コピー先に依存しません。
このリポジトリを丸ごとコピーすれば .claude/settings.json が同梱されているので
setup.py すら不要です。setup.py は「既存プロジェクトにオーケストラだけ追加する」場合に使います。

After setup (or copy), inside Claude Code:
  普通にテキストを入力するだけでオーケストレータが走ります（スラッシュ不要）。
  /orchestrate … /orchestra-status も引き続き使用可能。
"""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

PKG = Path(__file__).parent.resolve()


# ── Project Root Detection ──────────────────────────────────────────

def find_project_root(explicit: str | None = None) -> Path:
    """Find the project root directory.

    Strategy:
      1. Explicit --project-root argument
      2. Walk up from package dir looking for .git / .claude / CLAUDE.md
      3. Fall back to immediate parent of package
    """
    if explicit:
        p = Path(explicit).resolve()
        if not p.is_dir():
            print(f"  Error: --project-root '{explicit}' is not a directory")
            sys.exit(1)
        return p

    current = PKG.parent
    while current != current.parent:
        if any((current / marker).exists()
               for marker in [".git", ".claude", "CLAUDE.md"]):
            return current
        current = current.parent
    return PKG.parent


# ── Prerequisite Checks ────────────────────────────────────────────

def check_prerequisites() -> tuple[list[dict], bool]:
    """Check environment prerequisites. Returns (checks, all_required_ok)."""
    checks = []

    # Python 3.9+ (all modules use `from __future__ import annotations` for 3.9 compat)
    v = sys.version_info
    checks.append({
        "name": "Python 3.9+",
        "ok": v >= (3, 9),
        "detail": f"{v.major}.{v.minor}.{v.micro}",
        "required": True,
    })

    # git
    checks.append({
        "name": "git",
        "ok": shutil.which("git") is not None,
        "detail": shutil.which("git") or "not found",
        "required": True,
    })

    # Claude Code CLI
    claude = shutil.which("claude")
    checks.append({
        "name": "Claude Code CLI",
        "ok": claude is not None,
        "detail": claude or "not found — subagent features will be deferred",
        "required": False,
    })

    # gh CLI
    gh = shutil.which("gh")
    checks.append({
        "name": "gh CLI",
        "ok": gh is not None,
        "detail": gh or "not found — GitHub features will require setup",
        "required": False,
    })

    all_required = all(c["ok"] for c in checks if c["required"])
    return checks, all_required


# ── Command Installation ───────────────────────────────────────────

def install_commands(project_root: Path, pkg_rel: str) -> list[str]:
    """Install Claude Code slash commands into .claude/commands/."""
    commands_dir = project_root / ".claude" / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)

    installed = []

    # ── /orchestrate ──
    (commands_dir / "orchestrate.md").write_text(f"""\
---
name: orchestrate
description: "AI Orchestra agent — classify, plan, and execute any request through the full autonomous pipeline"
argument-hint: "<natural language request>"
---

# /orchestrate — AI Orchestra Agent

Process the following request through the full autonomous pipeline
(classification -> model selection -> capability selection -> planning ->
quality gates -> connection check -> execution -> evaluation).

**Request**: $ARGUMENTS

## Execution

Run the orchestrator from the project root:

```bash
python3 {pkg_rel}/orchestrator.py '$ARGUMENTS'
```

## Result Handling

Parse the JSON output. Based on the `outcome` field:

- **success**: Report what was accomplished. Summarize key actions.
- **partial**: Report succeeded and failed actions. If failures are
  environment-specific (subagent timeout, no git repo), note them as
  non-blocking. If failures indicate real problems, investigate.
- **blocked_by_connections**: Show each blocking gap with its setup hint.
  Offer to help fix (e.g., "run `gh auth login`").
- **blocked_by_quality_gate**: Show the risk details. Ask for user
  confirmation before proceeding with risky operations.
- **failure**: Show error details. Investigate root cause.

## Harness Actions

If the execution result includes deferred actions of type `hook` or
`slash_command`, you are running inside Claude Code and CAN execute these
directly. Offer to run them.
""", encoding="utf-8")
    installed.append(".claude/commands/orchestrate.md")

    # ── /orchestra-status ──
    (commands_dir / "orchestra-status.md").write_text(f"""\
---
name: orchestra-status
description: "Show AI Orchestra agent system status and readiness"
---

# /orchestra-status — System Status

Show the current AI Orchestra agent system status.

```bash
python3 {pkg_rel}/orchestrator.py --status
```

Parse the JSON output and present a readable summary:

- **Runtime**: Claude CLI availability, subagent capability
- **Watch**: monitored targets, pending events
- **Evaluator**: recorded executions, improvement state
- **Readiness**: whether the system is ready for requests

Also run a quick prerequisite check:

```bash
python3 {pkg_rel}/orchestrator.py --runtime
```
""", encoding="utf-8")
    installed.append(".claude/commands/orchestra-status.md")

    return installed


# ── Claude Code hooks（$CLAUDE_PROJECT_DIR: どこにコピーしても動く）──

USER_PROMPT_HOOK = "user_prompt_orchestrate_hook.py"
SESSION_START_HOOK = "session_start_orchestra_hook.py"


def hook_command_for_script(script_name: str, pkg_rel: str) -> str:
    """settings.json の command 用。

    $CLAUDE_PROJECT_DIR を使い、プロジェクトをどこにコピーしても
    フックが動くようにする。絶対パスは使わない。
    """
    return f'python3 "$CLAUDE_PROJECT_DIR"/{pkg_rel}/claude_cc_hook/{script_name}'


def merge_session_start_hook(project_root: Path, pkg_rel: str) -> tuple[str, str]:
    """Merge SessionStart hook (startup|resume). Idempotent."""
    settings_path = project_root / ".claude" / "settings.json"
    data: dict = {}
    if settings_path.exists():
        try:
            raw = settings_path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return "error", "invalid JSON in .claude/settings.json"

    hooks = data.setdefault("hooks", {})
    ss = hooks.get("SessionStart")
    if not isinstance(ss, list):
        ss = []
        hooks["SessionStart"] = ss

    for group in ss:
        if not isinstance(group, dict):
            continue
        for h in group.get("hooks", []):
            if isinstance(h, dict) and SESSION_START_HOOK in str(h.get("command", "")):
                return "skipped", "SessionStart orchestra hook already present"

    cmd = hook_command_for_script(SESSION_START_HOOK, pkg_rel)
    ss.append({
        "matcher": "startup|resume",
        "hooks": [
            {
                "type": "command",
                "command": cmd,
                "timeout": 60,
            },
        ],
    })

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return "installed", str(settings_path.relative_to(project_root))


def merge_user_prompt_hook(project_root: Path, pkg_rel: str) -> tuple[str, str]:
    """Merge UserPromptSubmit hook into .claude/settings.json. Idempotent."""
    settings_path = project_root / ".claude" / "settings.json"
    data: dict = {}
    if settings_path.exists():
        try:
            raw = settings_path.read_text(encoding="utf-8")
            data = json.loads(raw) if raw.strip() else {}
        except json.JSONDecodeError:
            return "error", "invalid JSON in .claude/settings.json (hook not installed)"

    hooks = data.setdefault("hooks", {})
    ups = hooks.get("UserPromptSubmit")
    if not isinstance(ups, list):
        ups = []
        hooks["UserPromptSubmit"] = ups

    for group in ups:
        if not isinstance(group, dict):
            continue
        for h in group.get("hooks", []):
            if isinstance(h, dict) and USER_PROMPT_HOOK in str(h.get("command", "")):
                return "skipped", "UserPromptSubmit hook already present"

    cmd = hook_command_for_script(USER_PROMPT_HOOK, pkg_rel)
    ups.append({
        "hooks": [
            {
                "type": "command",
                "command": cmd,
                "timeout": 120,
            },
        ],
    })

    settings_path.parent.mkdir(parents=True, exist_ok=True)
    settings_path.write_text(
        json.dumps(data, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return "installed", str(settings_path.relative_to(project_root))


# ── Orchestrator Verification ──────────────────────────────────────

def verify_orchestrator(project_root: Path) -> tuple[bool, str]:
    """Verify the orchestrator is reachable and starts clean."""
    try:
        r = subprocess.run(
            [sys.executable, str(PKG / "orchestrator.py"), "--status"],
            capture_output=True, text=True, timeout=30,
            cwd=str(project_root),
        )
        if r.returncode != 0:
            return False, f"exit code {r.returncode}: {r.stderr[:200]}"
        data = json.loads(r.stdout)
        records = data.get("evaluator", {}).get("records", "?")
        return True, f"OK (records={records})"
    except json.JSONDecodeError:
        return False, "invalid JSON output"
    except subprocess.TimeoutExpired:
        return False, "timeout (30s)"
    except Exception as e:
        return False, str(e)


# ── Main ───────────────────────────────────────────────────────────

def main():
    # Parse args
    explicit_root = None
    skip_hook = False
    for i, arg in enumerate(sys.argv[1:], 1):
        if arg == "--project-root" and i < len(sys.argv) - 1:
            explicit_root = sys.argv[i + 1]
        elif arg in ("--no-hook", "--slash-only"):
            skip_hook = True
        elif arg == "--with-prompt-hook":
            pass  # deprecated: now the default — kept for backward compat
        elif arg == "--check":
            # Just check, don't install
            checks, ok = check_prerequisites()
            for c in checks:
                mark = "ok" if c["ok"] else "MISSING"
                print(f"  {c['name']}: {mark} ({c['detail']})")
            sys.exit(0 if ok else 1)

    project_root = find_project_root(explicit_root)

    # Ensure package is inside or reachable from project root
    try:
        pkg_rel = PKG.relative_to(project_root)
    except ValueError:
        # Package is not under project root — use absolute path
        pkg_rel = PKG

    print()
    print("=" * 60)
    print("  Orchestra Agent — Project Setup")
    print("=" * 60)
    print(f"  Package:       {PKG}")
    print(f"  Project root:  {project_root}")
    print(f"  Relative path: {pkg_rel}")
    print()

    # Step 1: Prerequisites
    print("  [1/4] Prerequisites")
    checks, all_ok = check_prerequisites()
    for c in checks:
        req = c.get("required", True)
        if c["ok"]:
            mark = "ok"
        elif req:
            mark = "MISSING"
        else:
            mark = "optional"
        print(f"    [{mark:>8}] {c['name']}: {c['detail']}")

    if not all_ok:
        print()
        print("  SETUP FAILED: required prerequisites missing.")
        print("  Fix the items marked MISSING and re-run setup.")
        sys.exit(1)
    print()

    # Step 2: Install commands
    print("  [2/4] Installing Claude Code slash commands")
    installed = install_commands(project_root, str(pkg_rel))
    for path in installed:
        print(f"    installed: {path}")
    print()

    # Step 3: Claude Code hooks（SessionStart + UserPromptSubmit full-auto）
    print("  [3/4] Installing Claude Code hooks")
    if skip_hook:
        print("    skipped (--no-hook / --slash-only)")
    else:
        # SessionStart: lightweight status injection on open/resume
        st, det = merge_session_start_hook(project_root, str(pkg_rel))
        if st == "error":
            print(f"    ERROR (SessionStart): {det}")
            sys.exit(1)
        print(f"    SessionStart: {st} — {det}")

        # UserPromptSubmit: full-auto — every non-trivial prompt drives orchestrator
        st2, det2 = merge_user_prompt_hook(project_root, str(pkg_rel))
        if st2 == "error":
            print(f"    ERROR (UserPromptSubmit): {det2}")
            sys.exit(1)
        print(f"    UserPromptSubmit (full-auto): {st2} — {det2}")
    print()

    # Step 4: Verify orchestrator
    print("  [4/4] Verifying orchestrator")
    ok, detail = verify_orchestrator(project_root)
    print(f"    orchestrator --status: {detail}")
    if not ok:
        print()
        print("  SETUP FAILED: orchestrator is not reachable.")
        sys.exit(1)
    print()

    # Summary
    print("=" * 60)
    print("  Setup complete.")
    print()
    print("  Usage (inside Claude Code):")
    if not skip_hook:
        print("    普通にテキストを入力するだけで orchestrator が自動実行されます。")
        print("    スラッシュコマンドやプレフィックスは不要です。")
        print()
    print("  Slash commands (optional):")
    print("    /orchestrate <request>    オーケストレータを明示的に実行")
    print("    /orchestra-status         システム状態を確認")
    print()
    print("  Example:")
    print("    GitHub Actionsの自動PRレビューを実装してほしい")
    print("    （普通に送信するだけ — /orchestrate 不要）")
    print("=" * 60)
    print()


if __name__ == "__main__":
    main()
