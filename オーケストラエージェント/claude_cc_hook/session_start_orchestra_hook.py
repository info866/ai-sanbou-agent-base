#!/usr/bin/env python3
"""
Claude Code — SessionStart hook
===============================
セッション開始時に **必要な情報だけ** を1行で通知する。
さらに、最終 watch サイクルから 12 時間以上経過していれば
バックグラウンドで watch サイクルを発火させる（Codex/Ruflo/SDK の自動更新検知）。
"""

from __future__ import annotations

import json
import subprocess
import sys
from datetime import datetime, timedelta
from pathlib import Path

WATCH_TTL_HOURS = 12


def _find_orchestrator(cwd: Path) -> tuple[Path, Path] | None:
    for base in [cwd, *cwd.parents]:
        orch = base / "オーケストラエージェント" / "orchestrator.py"
        if orch.is_file():
            return base.resolve(), orch.resolve()
    return None


def _watch_is_stale(project_root: Path) -> bool:
    """last_continuous_cycle.json の timestamp を読んで TTL 超過か判定。"""
    cycle_file = project_root / "オーケストラエージェント" / ".orchestra_state" / "last_continuous_cycle.json"
    if not cycle_file.exists():
        return True
    try:
        data = json.loads(cycle_file.read_text())
        ts = datetime.fromisoformat(data.get("timestamp", "2000-01-01"))
        return (datetime.now() - ts) > timedelta(hours=WATCH_TTL_HOURS)
    except Exception:
        return True


def _trigger_watch_bg(project_root: Path, orch_py: Path) -> None:
    """バックグラウンドで watch サイクルを発火（応答をブロックしない）。"""
    try:
        subprocess.Popen(
            [sys.executable, str(orch_py), "--continuous", "1"],
            cwd=str(project_root),
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
    except Exception:
        pass


def _status_oneliner(project_root: Path, orch_py: Path) -> str:
    """軽量な1行ステータス。"""
    try:
        r = subprocess.run(
            [sys.executable, str(orch_py), "--status"],
            cwd=str(project_root),
            capture_output=True, text=True, timeout=15,
        )
        data = json.loads(r.stdout or "{}")
        targets = data.get("watch_state", {}).get("targets", 0)
        dyn = data.get("dynamic_capabilities", {}).get("count", 0)
        records = data.get("evaluator", {}).get("records", 0)
        return f"Orchestra ready · watch_targets={targets} · capabilities={dyn} · eval_records={records}"
    except Exception as e:
        return f"Orchestra status unavailable ({e!s})"


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}", end="")
        return

    cwd = Path(data.get("cwd") or ".").resolve()
    found = _find_orchestrator(cwd)
    if not found:
        print("{}", end="")
        return

    project_root, orch_py = found

    # 必要なら watch をバックグラウンドで走らせる（応答はブロックしない）
    watch_note = ""
    if _watch_is_stale(project_root):
        _trigger_watch_bg(project_root, orch_py)
        watch_note = " · 🔄 background watch dispatched"

    status = _status_oneliner(project_root, orch_py)
    ctx = f"## オーケストラ: {status}{watch_note}"

    out = {
        "hookSpecificOutput": {
            "hookEventName": "SessionStart",
            "additionalContext": ctx,
        }
    }
    print(json.dumps(out, ensure_ascii=False), end="")


if __name__ == "__main__":
    main()
