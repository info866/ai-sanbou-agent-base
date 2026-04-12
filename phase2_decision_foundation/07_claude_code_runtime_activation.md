# Claude Code Runtime 基盤（最終状態）

> **最終更新**: 2026-04-12

---

## 概要

Claude Code 公式機能をプロジェクト標準の作業基盤として project scope に実装した。全て無料・ローカル完結・可逆・安全。

---

## 導入済み機能

### 1. 正本文書保護 Hook

| 項目 | 内容 |
|------|------|
| ファイル | `.claude/hooks/protect-canonical.sh` |
| 設定 | `.claude/settings.json` hooks.PreToolUse |
| 発動条件 | Edit / Write で正本文書のパスにマッチした場合 |
| 動作 | exit 2 でブロック。成果物ファイルは exit 0 で通す |

**保護対象**: 大分類要件提起書、大分類作業指示書、フェーズ1要件定義書、フェーズ1作業指示書、フェーズ２要件定義書、フェーズ２作業指示書

### 2. catalog-checker（subagent）

| 項目 | 内容 |
|------|------|
| ファイル | `.claude/agents/catalog-checker.md` |
| 呼び出し | Agent tool（model: haiku） |
| ツール | Read, Grep, Glob（読取専用） |
| 用途 | 候補カタログの整合性を5項目で検査 |
| 使用時機 | 候補追加後、参照修正後、コミット前 |

検査項目: item_id連番、参照整合性、所属マップ整合、current_status妥当性、必須フィールド

### 3. scope-guard（subagent）

| 項目 | 内容 |
|------|------|
| ファイル | `.claude/agents/scope-guard.md` |
| 呼び出し | Agent tool（model: haiku）。作業説明を prompt に含める |
| ツール | Read, Grep, Glob（読取専用） |
| 用途 | 作業範囲の逸脱監査 |
| 使用時機 | グループ完了時、コミット前 |

監査内容: 作業契約との照合、成果物一覧確認、正本文書補助確認（hookが主防御）、禁止キーワード検索

### 4. phase-reporter（subagent）

| 項目 | 内容 |
|------|------|
| ファイル | `.claude/agents/phase-reporter.md` |
| 呼び出し | Agent tool（model: haiku）。git情報と作業概要を prompt に含める |
| ツール | Read, Grep, Glob（読取専用） |
| 用途 | 完了報告書を定型6セクションで生成 |
| 使用時機 | グループ完了報告時 |

出力セクション: 実施概要、ファイル一覧、成果物要点、逸脱防止確認、GitHub情報、後続引き継ぎ

### 5. Project Settings

| 項目 | 内容 |
|------|------|
| ファイル | `.claude/settings.json` |
| hooks | PreToolUse で正本保護を自動実行 |
| allow | Read, Glob, Grep, 公式ドメインWebFetch, WebSearch |
| deny | rm -rf, git push --force/-f, git reset --hard, git checkout --, git clean -fd |

---

## 導入見送り

| 機能 | 理由 |
|------|------|
| SessionStart hook | CLAUDE.md のコンテキスト注入と重複 |
| PostToolUse hook | 全ツール後のログは性能影響大 |
| Stop hook | ユーザーのグローバル Stop hook と競合 |
| Agent Teams | experimental。安定性に不安 |
| Memory Tool API | API呼び出し前提。無料・ローカル完結の条件外 |

---

## 巻き戻し方法

```bash
# 全巻き戻し（settings.local.json は保持）
rm -r .claude/hooks/ .claude/agents/ && rm .claude/settings.json

# 個別巻き戻し
rm .claude/hooks/protect-canonical.sh    # hook だけ無効化
rm .claude/agents/catalog-checker.md     # catalog-checker だけ無効化
rm .claude/agents/scope-guard.md         # scope-guard だけ無効化
rm .claude/agents/phase-reporter.md      # phase-reporter だけ無効化
```
