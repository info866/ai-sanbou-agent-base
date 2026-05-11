#!/usr/bin/env python3
"""
グローバル UserPromptSubmit フック
==================================
全プロジェクトで動作。プロジェクト内に「オーケストラエージェント/orchestrator.py」
があれば自動実行。なければ何もしない（{} を返す）。

出力は Claudeが従うべき行動指示として生成する（JSONダンプではない）。
"""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

MIN_PROMPT_LEN = 2

# 分類コードの意味
RC_LABELS = {
    "AU-1": "監査・独立検証",
    "RC-1": "調査・確認",
    "RC-2": "比較・選定",
    "RC-3": "構築・実装",
    "RC-4": "修正・バグ修正",
    "RC-5": "設計・アーキテクチャ",
    "RC-6": "自動化・効率化",
}


def _find_orchestrator(cwd: Path) -> tuple[Path, Path] | None:
    for base in [cwd, *cwd.parents]:
        orch = base / "オーケストラエージェント" / "orchestrator.py"
        if orch.is_file():
            return base.resolve(), orch.resolve()
    return None


def _build_directive(result: dict) -> str:
    """orchestrator の結果から **本当に行動が変わる情報** だけを抽出する。
    沈黙が黄金 — 何も指示することがなければ空文字を返す。"""
    steps = result.get("steps", {})
    outcome = result.get("outcome", "unknown")
    rc = steps.get("classification", "RC-1")

    lines: list[str] = []

    # ── AU-1: 監査モード（強制指示・必ず出力） ──
    if rc == "AU-1":
        lines.append("## オーケストラ: AU-1 監査モード")
        lines.append("- **攻撃的に検証せよ**：全ての仮定を疑い、独立して証拠収集し、反証を試みること")
        lines.append("- スクリプト・コード本体を読み切ってから判断すること（表面確認は不十分）")

    # ── 接続ブロック警告（本当に止まっている場合のみ） ──
    if outcome == "blocked_by_connections":
        blocking = steps.get("blocking_connections", [])
        if blocking:
            if lines:
                lines.append("")
            lines.append("## オーケストラ: 接続ブロック")
            for gap in blocking:
                lines.append(f"- {gap}")

    # ── 品質ゲート違反警告 ──
    if outcome == "blocked_by_quality_gate":
        issues = steps.get("blocking", [])
        if issues:
            if lines:
                lines.append("")
            lines.append("## オーケストラ: 品質ゲート違反")
            for issue in issues:
                lines.append(f"- {issue}")
            lines.append("- ユーザーに確認を求めてから実行せよ")

    # ── 実装タスクの未コミット変更通知 ──
    if rc in ("RC-3", "RC-4", "RC-6"):
        execution = steps.get("execution", {})
        for er in execution.get("results", []):
            if (er.get("status") == "success"
                    and "git status" in er.get("target", "")):
                output = er.get("output", "").strip()
                changed = [l for l in output.split("\n")
                           if l.strip() and not l.strip().startswith("??")]
                if changed:
                    if lines:
                        lines.append("")
                    lines.append(f"## オーケストラ: 未コミット変更 {len(changed)} 件")
                break

    return "\n".join(lines)


def main() -> None:
    try:
        data = json.load(sys.stdin)
    except json.JSONDecodeError:
        print("{}", end="")
        return

    prompt_in: str = data.get("prompt") or ""
    cwd_raw: str = data.get("cwd") or "."
    cwd = Path(cwd_raw).resolve()

    user_request = prompt_in.strip()
    if len(user_request) < MIN_PROMPT_LEN:
        print("{}", end="")
        return

    found = _find_orchestrator(cwd)
    if not found:
        print("{}", end="")
        return

    project_root, orch_py = found

    try:
        r = subprocess.run(
            [sys.executable, str(orch_py), user_request],
            cwd=str(project_root),
            capture_output=True,
            text=True,
            timeout=118,
        )
        raw = r.stdout.strip()

        try:
            result = json.loads(raw)
            ctx = _build_directive(result)
        except json.JSONDecodeError:
            # JSON解析失敗 → 生テキスト注入
            if len(raw) > 9500:
                raw = raw[:9000] + "\n...(truncated)..."
            ctx = f"## オーケストラ（JSON解析失敗）\n```\n{raw}\n```\n"

        if r.stderr:
            ctx += f"\n[orchestrator stderr: {r.stderr.strip()[:500]}]\n"

    except subprocess.TimeoutExpired:
        ctx = "## オーケストラ指示\norchestratorがタイムアウト（118秒）。通常通り対応せよ。"
    except Exception as e:
        ctx = f"## オーケストラ指示\nフック内エラー: {e!s}。通常通り対応せよ。"

    if len(ctx) > 9500:
        ctx = ctx[:9000] + "\n...(truncated)..."

    # 空指示なら何も注入しない（コンテキスト保護）
    if not ctx.strip():
        print("{}", end="")
        return

    print(json.dumps({
        "hookSpecificOutput": {
            "hookEventName": "UserPromptSubmit",
            "additionalContext": ctx,
        }
    }, ensure_ascii=False), end="")


if __name__ == "__main__":
    main()
