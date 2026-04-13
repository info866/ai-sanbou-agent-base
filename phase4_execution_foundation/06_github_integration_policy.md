# GitHub統合方針（GitHub Integration Policy）

> **ステップ対応**: フェーズ4要件定義書 完了条件5  
> **最終更新**: 2026-04-13

---

## この文書の役割

フェーズ4で実行した全ての作業が GitHub へ正確に記録され、変更内容が追跡可能・復帰可能・比較可能になることを保証する。

---

## 原則1：全ての変更は GitHub 差分で見える

### 要件
- 全実装・修正は git add/commit で段階的に記録
- 各コミットは 1タスク単位で独立した履歴になる
- git diff で意図通りの変更か確認可能

### 実行方法

```bash
# 変更確認
$ git status
$ git diff [ファイル]

# ステージング（各タスク単位で分割）
$ git add [ファイル]

# コミット（1タスク = 1コミット）
$ git commit -m "[タイプ](対象): 簡潔な説明

詳細説明: [何をどう変えたか、なぜか]

変更ファイル:
- [ファイルA]: [変更内容]
- [ファイルB]: [変更内容]

関連PR: [参照があれば]"

# 複数コミット場合は origin/main へ
$ git push origin main
```

### コミットメッセージフォーマット

```
[タイプ](スコープ): [簡潔なタイトル（< 50文字）]

[詳細説明（70文字幅で折り返し）]
- 何をしたか
- なぜしたか
- 技術的な背景

変更ファイル:
  追加: [新規ファイル一覧]
  修正: [編集ファイル一覧]
  削除: [削除ファイル一覧]

関連チケット: [PR/Issue参照]
```

### タイプの定義

| タイプ | 用途 | 例 |
|-------|------|-----|
| feat | 新機能・新ツール統合 | feat(litellm): LiteLLM統合を実装 |
| fix | バグ修正・問題解決 | fix(agent): SubagentのエラーハンドリングをPASS化 |
| refactor | コード再構成 | refactor(config): 設定ファイル構造を整理 |
| docs | ドキュメント作成・更新 | docs(phase4): 品質保証ルールを作成 |
| test | テスト追加 | test(integration): GitHubAPI統合テストを追加 |
| chore | 保守・ビルド | chore(deps): 依存ライブラリを更新 |

---

## 原則2：1タスク単位で履歴が追える

### 定義

「1つの調査→比較→実装→検証→記録の完全サイクル」 = 「1つのコミット or 複数の関連コミット」

### 実装方法

#### パターンA: 小規模タスク（1ファイル修正）
```bash
# 単一コミット
$ git commit -m "feat(tool_selection): MCP Server X の選定判定を実装"
```

#### パターンB: 中規模タスク（複数ファイル関連修正）
```bash
# 関連ファイルを 1コミット にまとめる
$ git add [file1] [file2] [file3]
$ git commit -m "feat(integration): Tool X の完全統合（インストール・設定・検証）"
```

#### パターンC: 大規模タスク（複数の論理段階）
```bash
# 論理段階ごとに分割コミット
$ git commit -m "feat(integration_step1): Tool X のインストール・依存関係確認"
$ git commit -m "feat(integration_step2): Tool X の初期設定・API接続"
$ git commit -m "feat(integration_step3): Tool X の機能テスト・統合検証"

# PR の関連コミット設定で1タスクとして追跡
```

### チェックポイント

| 項目 | 確認内容 |
|-----|--------|
| **粒度** | 1コミットで「何をしたか」が明確か |
| **独立性** | 各コミットは独立して動作可能か（中間状態でも） |
| **追跡性** | `git log --oneline` で作業フローが見えるか |
| **復帰可能性** | 任意の時点にチェックアウト可能か |

---

## 原則3：比較対象 OSS・参考実装に接続できる

### 外部リソース参照の記録

#### パターン1: 参考実装の引用
```bash
# コミットメッセージに参照
$ git commit -m "feat(mcp_integration): 参考: anthropics/mcp-examples#42

参考リソース:
- GitHub: https://github.com/anthropics/mcp-examples
- コミット: abc1234
- 理由: [なぜこのOSSを参考にしたか]
- 採用部分: [どこを参考にしたか]
- 変更点: [どう改変したか]"
```

#### パターン2: 比較対象候補の記録
```bash
# チェックアウト用メモを残す
$ git notes add -m "比較対象: vercel/next.js vs astro/astro (2026-04-13時点)
  - 選定理由: [why next.js]
  - 比較対象: https://github.com/astro/astro
  - 比較結果: ../phase2_decision_foundation/02_comparison_units_and_matrix_plan.md
```

#### パターン3: OSS 学習リンク
```markdown
# ファイルヘッダーに記録
"""
参考実装と学習リソース:

OSS参考:
- MCP Spec: https://modelcontextprotocol.io
- Reference: https://github.com/anthropics/mcp-examples

学習資料:
- [Claude API Docs](https://docs.anthropic.com)
- [LiteLLM Docs](https://litellm.ai)

比較検証:
- ../phase2_decision_foundation/02_comparison_units_and_matrix_plan.md
"""
```

### チェックポイント

| 項目 | 確認内容 |
|-----|--------|
| **参照明確性** | 外部リソースへのリンクが明記されているか |
| **採用理由** | 「なぜこれを選んだか」が説明されているか |
| **変更追跡** | 参考実装からの変更点が記録されているか |
| **時点記録** | 参照時点のバージョン・コミットが明記されているか |

---

## 原則4：正常状態へ戻せる（復帰可能性）

### 復帰戦略

#### Level 1: 最後のコミットに戻す
```bash
$ git reset --soft HEAD~1       # コミット取り消し（ファイルは保持）
$ git reset --hard HEAD~1       # コミット+変更を完全取り消し（危険）
```

#### Level 2: 特定コミットまで戻す
```bash
$ git log --oneline | head -20
$ git reset --hard abc1234      # 指定コミット時点に戻す
```

#### Level 3: ブランチで隔離して試験
```bash
# 試験ブランチで作業
$ git checkout -b feature/trial-toolX
[... 試験作業 ...]
$ git commit -m "trial(toolX): 試験実装"

# うまくいったらmerge、ダメなら削除
$ git checkout main
$ git merge feature/trial-toolX          # 成功時
$ git branch -D feature/trial-toolX      # 失敗時
```

#### Level 4: タグで安全ポイントを標記
```bash
# フェーズ4各セクション完了時にタグ作成
$ git tag -a "phase4_section1_complete" -m "Phase 4 Section 1 完了（品質検証済み）"
$ git push origin phase4_section1_complete

# 後で参照
$ git diff phase4_section1_complete...HEAD
```

### チェックポイント

| 項目 | 確認内容 |
|-----|--------|
| **コミット原子性** | 各コミットは独立した復帰ポイントか |
| **ブランチ隔離** | リスク高い試験は別ブランチか |
| **タグ記録** | 重要な達成ポイントにタグがあるか |
| **復帰テスト** | 実際に戻してテストしたか |

---

## 原則5：進捗確認ができる

### 進捗追跡方法

#### フロー1: コミット履歴で段階を見える化
```bash
$ git log --oneline --decorate --graph | head -30

# 出力例:
* abc1234 (HEAD -> main) docs(phase4): 品質保証ルール完成
* def5678 feat(intake_rules): 新規ツール即時投入ルール実装
* ghi9012 feat(work_units): 作業単位定義完成
* jkl3456 feat(tools): ツール最大活用方針実装
* mno7890 feat(flow): 実行フロー定義完成
```

#### フロー2: Pull Request での進捗管理
```bash
# 大規模作業の場合は PR で進捗表示
$ gh pr create --title "Phase 4 実行基盤整備" \
  --body "## 進捗
  
- [ ] 実行フロー定義
- [ ] ツール最大活用方針
- [ ] 新規ツール即時投入ルール
- [ ] 作業単位定義
- [ ] 品質保証ルール
- [ ] GitHub統合方針
- [ ] フェーズ5接続メモ

## ステータス
現在: 品質保証ルール実装中"

# チェックリスト更新
$ gh pr edit <PR_NUMBER> --body "..."
```

#### フロー3: 進捗レポート（各セクション完了時）
```markdown
## フェーズ4進捗レポート

### 完了項目
- ✅ 実行フロー定義 (abc1234)
- ✅ ツール最大活用方針 (def5678)
- ✅ 新規ツール即時投入ルール (ghi9012)

### 進行中
- 🔄 品質保証ルール (current branch)

### 計画
- ⬜ GitHub統合方針
- ⬜ フェーズ5接続メモ

### 関連リソース
- 要件定義: 9.フェーズ4 要件定義書.md
- 作業指示: 10.フェーズ4作業指示書.md
```

### チェックポイント

| 項目 | 確認内容 |
|-----|--------|
| **可視化** | コミット履歴で段階が見えるか |
| **更新頻度** | 進捗が定期的に更新されているか |
| **トレーサビリティ** | 各セクションのコミットが追跡できるか |
| **チェックリスト** | 完了/未完了が明確に区別されているか |

---

## GitHub 作業の標準フロー

### フロー全体

```
1. 変更前準備
   ├─ 最新コードをpull
   ├─ 今回の対象範囲を固定
   └─ 完了条件を定義

2. 作業実行
   ├─ コードを修正・追加
   ├─ 自己検証（テスト・ビルド）
   └─ 差分確認

3. Git記録
   ├─ git status で確認
   ├─ git add で段階的にステージ
   └─ git commit で詳細記録

4. 推送
   ├─ git push origin main (単純作業の場合)
   ├─ または git push で PR 用ブランチ (大型作業の場合)
   └─ PR 作成・レビュー (複数ファイル or 影響大きい場合)

5. 進捗確認
   ├─ git log で履歴確認
   ├─ GitHub web で diff 確認
   └─ 影響範囲の副作用確認
```

### パターン別実行手順

#### パターン1: 単純な1ファイル修正
```bash
$ git pull origin main
$ git diff HEAD                  # 現在の状態確認
$ [ファイル編集]
$ git add [ファイル]
$ git commit -m "[タイプ](スコープ): [説明]"
$ git push origin main
$ git log -1                     # 確認
```

#### パターン2: 複数ファイルの関連修正
```bash
$ git pull origin main
$ git checkout -b feature/task-name
$ [複数ファイル編集]
$ git add [file1] [file2]
$ git commit -m "feat(scope): 複数ファイルの統合修正"
$ git push origin feature/task-name
$ gh pr create --fill            # PR自動作成
$ # レビュー・マージ
$ git checkout main && git pull origin main
```

#### パターン3: リスク高い大型修正
```bash
$ git pull origin main
$ git tag "before_risky_change"  # 復帰ポイント作成
$ git checkout -b feature/risky-refactor
$ [大型修正実行]
$ git commit -m "feat(refactor): 大型リファクタリング"
$ [テスト・検証を十分に実施]
$ git push origin feature/risky-refactor
$ gh pr create                   # PR作成・詳細説明
$ # マージ後
$ git tag -a "phase4_section_complete" -m "..."
```

---

## GitHub PR（プルリクエスト）フォーマット

### PR作成時の標準フォーマット

```markdown
## 概要
[何をしたか、なぜしたか（2-3行）]

## 対象
- [ ] フェーズ4 実行基盤整備
- [ ] 新ツール統合
- [ ] 品質保証ルール適用

## 変更内容

### 追加ファイル
- [ファイルA]: [目的]
- [ファイルB]: [目的]

### 修正ファイル
- [ファイルC]: [何をどう変えたか]

### 削除ファイル
- [ファイルD]: [理由]

## 検証方法

### 実施した検証
- [ ] 構文チェック: PASS
- [ ] インポート確認: PASS
- [ ] 機能テスト: PASS
- [ ] パフォーマンス: < 5秒
- [ ] セキュリティ: API key隔離 ✓

### 副作用確認
- [ ] 関連ファイルへの影響: なし
- [ ] 既存機能への破壊: なし

## 関連リソース
- 要件定義: 9.フェーズ4 要件定義書.md
- 作業指示: 10.フェーズ4作業指示書.md
- コンパイル結果: [GitHub Actions結果]

## チェックリスト
- [ ] すべての検証が PASS している
- [ ] コミットメッセージが明確
- [ ] 不要なファイルが含まれていない
- [ ] ドキュメント更新済み（該当時）
```

---

## マージ戦略

### マージ方法の選択

| 状況 | 推奨方法 | 理由 |
|-----|--------|------|
| 単一コミット | Squash & Merge | 履歴が簡潔、ロールバック容易 |
| 複数の論理段階 | Create a Merge Commit | 各段階が歴史に残る |
| リスク高い修正 | Rebase & Merge | 直線的な履歴、conflicts明確 |

### マージ実行

```bash
# コマンドラインでマージ
$ git checkout main
$ git pull origin main
$ git merge feature/branch-name

# または GitHub web UI で Merge button を使用
# その場合、マージコミットメッセージを確認
```

### マージ後クリーンアップ
```bash
$ git branch -d feature/branch-name          # ローカル削除
$ git push origin --delete feature/branch-name  # リモート削除
$ git log --oneline | head -10               # 履歴確認
```

---

## 次の成果物

このファイル（GitHub統合方針）をベースに、以下を順に作成：

1. ✅ 01_execution_flow.md
2. ✅ 02_tool_maximization_policy.md
3. ✅ 03_new_tool_intake_rules.md
4. ✅ 04_work_unit_definitions.md
5. ✅ 05_quality_assurance_rules.md
6. ✅ 06_github_integration_policy.md
7. ⬜ 07_phase5_handoff_memo.md
