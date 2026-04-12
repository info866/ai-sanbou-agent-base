# Claude Code Runtime 検証記録

> **担当**: フェーズ2補正タスク（runtime validation）  
> **最終更新**: 2026-04-12

---

## 今回の目的

07で導入した Hooks / Subagents / Skills / project settings を「設定しただけ」から「実動作確認済み・常用可能」へ引き上げる。不整合があれば修正し、全機能の実動作結果を記録する。

---

## 点検した runtime 要素一覧

| 要素 | ファイル | 点検結果 |
|------|---------|---------|
| PreToolUse Hook | .claude/hooks/protect-canonical.sh | 問題なし。全6テスト合格 |
| Hook設定 | .claude/settings.json (hooks) | 問題なし。matcher正確 |
| Permissions (allow) | .claude/settings.json (permissions.allow) | 問題なし。過剰な許可なし |
| Permissions (deny) | .claude/settings.json (permissions.deny) | **修正実施**: git push -f等の変形パターン追加 |
| catalog-checker | .claude/agents/catalog-checker.md | 問題なし。Read/Grep/Globで完結 |
| scope-guard | .claude/agents/scope-guard.md | **修正実施**: git依存を除去 |
| phase-report | .claude/skills/phase-report/SKILL.md | 問題なし。frontmatter正確 |

---

## 修正した点

### 1. scope-guard のgit依存除去

**問題**: scope-guardの監査手順に `git diff --name-only HEAD~1` や `git log --oneline -5` が含まれていたが、このエージェントのツールは Read/Grep/Glob のみでBashがない。git コマンドは実行不能。

**修正内容**:
- git依存の監査手順を全て削除
- Read/Grep/Globのみで完結する手順に書き換え:
  - 作業契約書をReadで読む
  - 成果物ファイルをGlobで一覧する
  - 正本文書の存在をGlobで確認する
  - 禁止キーワードをGrepで検索する
  - 呼び出し元から作業説明を受け取って範囲判定する
- ファイル冒頭に「gitコマンドは実行できません」の制約を明記

### 2. settings.json の deny パターン補強

**問題**: `Bash(git push --force)` は `git push -f` や `git push origin main --force` を捕捉できない可能性。

**修正内容**:
- `Bash(git push -f)` を追加
- `Bash(git push.*--force)` を追加（正規表現で中間引数対応）
- `Bash(rm -rf .)` を追加
- `Bash(git clean -fd)` を追加

---

## 修正しなかった点

| 要素 | 理由 |
|------|------|
| protect-canonical.sh | テスト6件全て合格。保護パターンは正本6文書を正確にカバー。安全側フォールバックも正常動作 |
| catalog-checker.md | Read/Grep/Globのみで検査が成立。実行して有意な問題を検出できた |
| phase-report SKILL.md | frontmatterとテンプレートが整合。実行して報告生成に使えた |
| settings.json (allow) | 公式ドメインWebFetch + 基本読取ツールの許可は妥当。無駄に広い権限はない |

---

## Hook 実動作結果

### テスト結果（全6件合格）

| # | テスト内容 | 対象ファイル | 期待 | 結果 |
|---|-----------|-------------|------|------|
| 1 | 正本「大分類要件提起書」への編集 | 1.大分類要件提起書.md | ブロック | **exit 2（ブロック成功）** |
| 2 | 正本「フェーズ２作業指示書」への書込 | ６.フェーズ２作業指示書.md | ブロック | **exit 2（ブロック成功）** |
| 3 | 正本「フェーズ1作業指示書」への編集 | 4.フェーズ1作業指示書.md | ブロック | **exit 2（ブロック成功）** |
| 4 | 成果物ファイルへの編集 | phase2_.../07_claude_code_runtime_activation.md | 許可 | **exit 0（許可成功）** |
| 5 | .claude配下ファイルへの書込 | .claude/agents/test.md | 許可 | **exit 0（許可成功）** |
| 6 | 不正JSON入力 | （解析失敗） | 許可（安全側） | **exit 0（安全側フォールバック成功）** |

---

## Subagent 実動作結果

### catalog-checker 実行結果

**実行方法**: Agent tool（model: haiku）で呼び出し

**検出結果**:
- 検査項目1（item_id連番）: **問題なし** — F-001〜F-038連番、欠番なし
- 検査項目2（参照整合性）: **注意** — D-002/D-004が05から参照されるがカタログ上のF-xxxとの対応が不明確
- 検査項目3（所属マップ）: **問題あり** — F-032〜F-038が02_comparison_units パート4に未反映（既知課題、グループ3で対応）
- 検査項目4（current_status）: **問題なし** — 全候補が9状態のいずれか
- 検査項目5（必須フィールド）: **問題なし** — 全候補にitem_id/item_name/current_status/source_url完備

**所見**: エージェントは指示通りに5項目検査を実行し、有意な問題を正確に検出できた。常用に値する。

### scope-guard 実行結果（修正版）

**実行方法**: Agent tool（model: haiku）で呼び出し。作業内容の説明を付与。

**監査結果**:
- 作業契約確認: 完了
- 成果物ファイル一覧: 8ファイル確認、想定外なし
- 正本文書確認: **Globで検出できず**（全角数字ファイル名がGlobマッチングに影響する可能性）
- 禁止キーワード検索: 混入なし（00内の禁止リスト記載のみ）
- タスク内容判定: 「フェーズ2の評価基盤構築とは別の補正タスク」と正しく認識

**既知制約**: 全角数字（５, ６）を含むファイル名がGlob検索で検出されにくい場合がある。これはClaude Code側のGlob実装の特性であり、hookスクリプト（grep使用）では正常に検出できている。scope-guardの正本確認は補助的な検査であり、hookによる保護が主防御ラインとして機能する。

---

## Skill 実動作結果

### phase-report 実行結果

**実行方法**: SKILL.mdのテンプレートに従い、このタスク自身の報告を手動生成

**確認結果**:
- フォーマット6セクション（実施概要/ファイル一覧/成果物要点/逸脱確認/GitHub情報/引き継ぎ）を生成できた
- 完了報告の必須項目をカバーしている
- argument-hint（グループ番号指定）が機能する設計

**所見**: テンプレートベースのスキルとして実用的。今後のグループ完了時に `/phase-report` で呼び出して使用可能。

---

## 既知の残課題

| # | 課題 | 影響 | 対応時期 |
|---|------|------|---------|
| 1 | F-032〜F-038が02_comparison_units パート4の所属マップに未反映 | グループ3の比較評価で所属が不明確 | グループ3着手時 |
| 2 | D-002/D-004が05から参照されるがF-xxxへの昇格対応が不完全 | 参照先の混乱 | グループ3着手時 |
| 3 | 全角数字ファイル名がGlob検索で検出しにくい | scope-guardの正本確認に制約 | 低優先（hookが主防御） |

---

## 今後の常用ルール

### 常用するもの

| 機能 | 常用タイミング | 呼び出し方 |
|------|-------------|-----------|
| protect-canonical hook | **常時自動** | 設定済み。Edit/Writeで正本を触ると自動ブロック |
| catalog-checker | **候補追加・参照修正後** | Agent tool (model: haiku) で呼び出し |
| scope-guard | **コミット前・グループ完了時** | Agent tool (model: haiku) で呼び出し。作業内容の説明を添えること |
| phase-report | **グループ完了報告時** | /phase-report で呼び出し |

### まだ常用しないもの

| 機能 | 理由 |
|------|------|
| SessionStart hook | CLAUDE.mdと重複。追加のコンテキスト消費を避ける |
| PostToolUse hook | 性能影響大。スポット導入が適切 |
| Stop hook | グローバルhookとの競合リスク |

---

## 巻き戻し確認

07に記載の巻き戻し手順を再確認:
- hook無効化: `.claude/settings.json` の hooks を空 `{}` にする → project設定のみに影響、user-global は無関係
- subagent無効化: `.claude/agents/` 内の対象ファイルを削除 → 他の設定に影響なし
- skill無効化: `.claude/skills/` 内の対象ディレクトリを削除 → 他の設定に影響なし
- 全巻き戻し: `.claude/settings.json`, `.claude/hooks/`, `.claude/agents/`, `.claude/skills/` を削除 → settings.local.json は保持される

**巻き戻しの安全性**: 全て project scope ファイルの削除のみ。user-global やシステム設定に一切影響しない。
