# Claude Code公式機能 実行基盤活性化記録

> **担当**: フェーズ2補正タスク  
> **最終更新**: 2026-04-12

---

## 今回の目的

Claude Code公式のHooks / Subagents / Skills / project settings を「後で評価する候補」ではなく、**プロジェクト標準の作業基盤**としてこのリポジトリに実装し、即時常用化すること。

無料・ローカル完結・可逆・安全なものに限定し、project scopeで実装した。

---

## 導入対象候補一覧

| 機能 | 判定 | 理由 |
|------|------|------|
| **Hooks（PreToolUse）** | **導入済み** | 正本文書保護。ローカル完結・可逆・安全 |
| **Subagents（catalog-checker）** | **導入済み** | 候補カタログ整合性検査。Read/Grep/Globのみ使用 |
| **Subagents（scope-guard）** | **導入済み** | 作業範囲逸脱監査。Read/Grep/Globのみ使用 |
| **Skills（phase-report）** | **導入済み** | 完了報告定型化。user-invocable |
| **Project settings** | **導入済み** | permissions + hooks設定 |
| Hooks（SessionStart） | 導入見送り | コンテキスト注入は有用だが、CLAUDE.mdと重複する。過剰な自動注入はコンテキスト消費の原因になるため見送り |
| Hooks（PostToolUse） | 導入見送り | ログ記録は有用だが、全ツール実行後にログを取ると性能影響が大きい。必要時にスポット導入 |
| Hooks（Stop） | 導入見送り | セッション完了時の自動記録はユーザーのグローバルStop hookと競合する可能性がある |
| Agent Teams | 導入見送り | experimental機能。環境変数設定が必要で可逆性に不安。成熟後に再検討 |
| Memory Tool（API） | 導入見送り | API呼び出しが必要で無料・ローカル完結の条件を満たさない |

---

## 導入したもの

### 1. Hooks: 正本文書保護（PreToolUse）

**ファイル**: `.claude/hooks/protect-canonical.sh`  
**設定**: `.claude/settings.json` の hooks.PreToolUse

**機能**: Edit/Write ツールが正本文書（要件定義書・作業指示書・上位文書）を対象にした場合、exit 2 でブロックする。

**保護対象パターン**:
- 大分類要件提起書
- 大分類作業指示書
- フェーズ1 要件定義書
- フェーズ1作業指示書
- フェーズ２ 要件定義書
- フェーズ２作業指示書

**動作原理**: 
1. PreToolUse イベントでEdit/Writeが呼ばれると、stdin にJSON（tool_name, tool_input）が渡される
2. python3 でfile_pathを抽出
3. 保護パターンとマッチすればexit 2（ブロック）、マッチしなければexit 0（許可）

---

### 2. Subagent: catalog-checker

**ファイル**: `.claude/agents/catalog-checker.md`  
**モデル**: haiku  
**ツール**: Read, Grep, Glob（読取専用）

**機能**: 候補カタログ（02_candidate_catalog.md）の整合性を5項目で検査する
1. item_id連番確認（欠番・重複検出）
2. 参照整合性（引き継ぎ文書との整合）
3. 比較グループ所属マップとの整合
4. current_status妥当性（9状態のいずれかか）
5. 必須フィールド欠落チェック

---

### 3. Subagent: scope-guard

**ファイル**: `.claude/agents/scope-guard.md`  
**モデル**: haiku  
**ツール**: Read, Grep, Glob（読取専用）

**機能**: 直近の作業が現在のフェーズ/グループの範囲内かを監査する
- 正本文書の変更有無
- 本番構築への踏み込み有無
- フェーズ前倒し有無
- 有料API/SaaS前提有無
- 判断範囲の逸脱有無

---

### 4. Skill: phase-report

**ファイル**: `.claude/skills/phase-report/SKILL.md`  
**呼び出し**: `/phase-report` + グループ番号

**機能**: フェーズのグループ完了報告書を定型フォーマットで生成する。以下のセクションを含む:
1. 実施概要
2. 作成・更新ファイル一覧
3. 成果物の要点
4. 逸脱防止確認チェックリスト
5. GitHub確認情報
6. 後続グループへの引き継ぎ

---

### 5. Project Settings

**ファイル**: `.claude/settings.json`

**内容**:
- **hooks**: PreToolUse で正本保護hookを有効化
- **permissions.allow**: Read, Glob, Grep, 公式ドメインWebFetch, WebSearch を自動許可
- **permissions.deny**: `rm -rf /`, `git push --force`, `git reset --hard`, `git checkout -- .` を拒否

---

## 導入しなかったものと理由

| 機能 | 見送り理由 |
|------|-----------|
| SessionStart hook | CLAUDE.mdによるコンテキスト注入と重複。追加するとコンテキストトークンを無駄に消費する |
| PostToolUse hook | 全ツール実行後のログは性能影響が大きい。スポット的に追加すべき |
| Stop hook | ユーザーのグローバルStop hook（会話ログ自動保存）と競合する可能性がある |
| Agent Teams | experimental機能（CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 必要）。安定性に不安 |
| Memory Tool API | API呼び出し前提で無料・ローカル完結の条件を満たさない |
| HTTP/Prompt型hook | 外部サーバーまたはLLM呼び出しが必要。ローカル完結の条件を満たさない |

---

## 実際にこのタスク中で使った証跡

### catalog-checker の実行結果

**検出された問題（3件）**:
1. **F-032〜F-038が比較グループ所属マップ（02_comparison_units_and_matrix_plan.md パート4）に未反映** → グループ3以降で02のパート4を更新する必要がある
2. F-032〜F-038は05（引き継ぎ文書）で参照されていない → フェーズ2内で整合させる必要がある
3. 上記以外の項目は全て問題なし（item_id連番OK、current_status妥当、必須フィールド完備）

### scope-guard の実行結果

**監査結果: 合格**
- 正本文書の変更なし
- 本番構築への踏み込みなし
- フェーズ前倒しなし
- 有料API/SaaS前提なし
- rename/move/deleteなし
- 軽微注意: 02_candidate_catalogへの候補追加はグループ2の許可範囲内だが、今後は控えるのが工程明確性に寄与

### phase-report スキルの確認

- SKILL.md のフォーマットを確認し、フロントマター（name, description, user-invocable, argument-hint）が正しく設定されていることを検証
- 出力フォーマットテンプレートが完了報告の必須項目をカバーしていることを確認

### 正本保護hookの動作確認

- **テスト1**: 正本文書（フェーズ２要件定義書）への編集 → **ブロック成功（exit 2）**
  ```
  正本文書の直接編集をブロックしました: ５.フェーズ２ 要件定義書.md
  ```
- **テスト2**: 成果物ファイルへの編集 → **許可成功（exit 0）**

---

## 安全性確認

| 確認項目 | 結果 |
|---------|------|
| project scope限定か | ✅ 全て `.claude/` 配下または `phase2_decision_foundation/` 内 |
| user-global 変更がないか | ✅ `~/.claude/` は一切変更していない |
| 可逆性があるか | ✅ `.claude/settings.json` 削除 + `.claude/agents/` `.claude/skills/` `.claude/hooks/` 削除で完全復元 |
| 有料APIを使っていないか | ✅ 全てローカル完結（hookはbash、subagentsはhaiku+読取専用ツール、skillは定型テンプレート） |
| 危険な自動実行がないか | ✅ hookはブロック方向のみ（許可は何もしない）。subagentsは読取専用。deny設定で破壊コマンド拒否 |
| 既存設定との競合がないか | ✅ `.claude/settings.local.json`（既存）とは別ファイル。settings.jsonはproject scope |

---

## 後続作業での使い方

### catalog-checker
```
グループ完了時にAgent toolで呼び出し、候補カタログの整合性を検証する。
特に新候補追加後やitem_id参照修正後に実行推奨。
```

### scope-guard
```
グループ作業の途中または完了時にAgent toolで呼び出し、作業範囲の逸脱がないか監査する。
コミット前の自己検査として利用推奨。
```

### phase-report
```
/phase-report group3 のように呼び出し、定型フォーマットの完了報告書を生成する。
```

### 正本保護hook
```
自動実行。Edit/Writeで正本文書を編集しようとすると自動的にブロックされる。
新しい正本文書が追加された場合は .claude/hooks/protect-canonical.sh のパターンに追記する。
```

---

## 巻き戻し方法

全ての導入を完全に巻き戻すには:

```bash
# 1. hookスクリプトを削除
rm -r .claude/hooks/

# 2. subagentsを削除
rm -r .claude/agents/

# 3. skillsを削除
rm -r .claude/skills/

# 4. project設定を削除（settings.local.jsonは保持）
rm .claude/settings.json

# 5. コミットで記録
git add -A && git commit -m "revert: Claude Code runtime activation を巻き戻し"
```

個別に巻き戻す場合:
- hookだけ無効化: `.claude/settings.json` の hooks セクションを空にする
- subagentだけ無効化: `.claude/agents/` 内の対象ファイルを削除
- skillだけ無効化: `.claude/skills/` 内の対象ディレクトリを削除
