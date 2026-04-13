# AI参謀の最終運用形（Final Operating Form）

> **正本**: 11.フェーズ5要件定義書.md  
> **最終更新**: 2026-04-13

---

## この文書の役割

AI参謀の全機能を統合した最終運用手順を定義する。他の成果物（01〜06）を一つの流れに統合し、依頼受付から実行橋渡しまでの完全なフローを示す。

---

## AI参謀とは何か

AI参謀は、ユーザーの依頼に対して以下を一貫して実行する統合判断エンジンである。

1. 依頼を分類する
2. 必要な能力を選定する
3. 選定理由を説明する
4. 再確認の要否を判断する
5. 実行基盤へ橋渡しする
6. 新しい能力を取り込む

AI参謀は単独のソフトウェアではない。Claude Codeが依頼を処理する際に従うべき判断フレームワークであり、Phase 1〜4の全基盤を統合して運用する。

---

## 統合実行フロー

```
依頼受付
  │
  ├─ STEP 1: 依頼分類 [02_request_classification.md]
  │    └─ RC-1〜RC-6のいずれかに分類
  │
  ├─ STEP 2: 目的固定
  │    ├─ 今回の目的（1〜2文）
  │    ├─ 完了条件
  │    ├─ 制約
  │    └─ 今回除外するもの
  │
  ├─ STEP 3: 知識確認 [Phase 3知識活用フロー F1〜F6]
  │    ├─ 関連する既存候補の確認
  │    ├─ 過去の比較・評価結果の参照
  │    └─ 未解決論点の有無確認
  │
  ├─ STEP 4: 能力選定 [03_capability_selection.md]
  │    ├─ 候補プールの絞り込み（分類別）
  │    ├─ 適合判定（S1〜S8）
  │    ├─ 使う能力 / 使わない能力の確定
  │    └─ 再確認要否の判定
  │
  ├─ STEP 5: 再確認実行（必要時のみ）
  │    ├─ T4候補の最新状態確認
  │    ├─ 90日超過候補の鮮度確認
  │    └─ 確認結果に応じた判断更新
  │
  ├─ STEP 6: 提案形成 [04_reason_generation.md]
  │    ├─ 8項目の提案出力
  │    ├─ 理由の3要素（正の理由・消去理由・効果範囲）
  │    └─ 提案テンプレートに基づく出力
  │
  ├─ STEP 7: 実行橋渡し [05_execution_handoff.md]
  │    ├─ 5要素の確定（対象・能力・作業順・検証・GitHub）
  │    ├─ Phase 4実行基盤への接続
  │    └─ 橋渡し品質確認（5項目チェック）
  │
  └─ STEP 8: 更新反映（該当時のみ）[06_update_absorption.md]
       ├─ 新機能発見時の評価・取り込み
       └─ 既存判断の陳腐化検知・再評価
```

---

## Phase 1〜4基盤との統合関係

```
AI参謀（Phase 5）
  │
  ├─ 知識参照 ← Phase 1 情報基盤
  │    └─ phase1_information_foundation/02_candidate_catalog.md
  │       （候補一覧・分類・状態）
  │
  ├─ 判断参照 ← Phase 2 判断基盤
  │    ├─ phase2_decision_foundation/01_evaluation_criteria.md
  │    │   （評価基準E1〜E10）
  │    ├─ phase2_decision_foundation/04_candidate_evaluations.md
  │    │   （評価結果）
  │    └─ phase2_decision_foundation/05_adoption_build_vs_buy_priority.md
  │       （採用状態D1〜D5・優先順位P1〜P5）
  │
  ├─ 知識活用 ← Phase 3 知識活用基盤
  │    ├─ phase3_knowledge_foundation/04_knowledge_utilization_flow.md
  │    │   （知識活用フローF1〜F6）
  │    └─ phase3_knowledge_foundation/06_recheck_rules_and_trust.md
  │       （再確認ルール・信頼区分T1〜T4）
  │
  └─ 実行接続 ← Phase 4 実行基盤
       ├─ phase4_execution_foundation/01_execution_flow.md
       │   （7ステップ実行フロー）
       ├─ phase4_execution_foundation/02_tool_maximization_policy.md
       │   （ツール最大活用方針）
       ├─ phase4_execution_foundation/03_new_tool_intake_rules.md
       │   （新規ツール即時投入ルール）
       ├─ phase4_execution_foundation/04_work_unit_definitions.md
       │   （作業単位定義）
       ├─ phase4_execution_foundation/05_quality_assurance_rules.md
       │   （品質保証ルール）
       └─ phase4_execution_foundation/06_github_integration_policy.md
           （GitHub統合方針）
```

---

## AI参謀の6つのコア機能と完了条件対応

| # | コア機能 | 定義文書 | 完了条件 |
|---|---------|---------|---------|
| A | 依頼分類 | 02_request_classification.md | 依頼を見て必要能力を選べる |
| B | 能力選定 | 03_capability_selection.md | 依頼を見て必要能力を選べる |
| C | 理由生成 | 04_reason_generation.md | 選定理由を説明できる |
| D | 再確認判断 | 03_capability_selection.md | 再確認の要否を判断できる |
| E | 実行橋渡し | 05_execution_handoff.md | 実行基盤へ渡せる |
| F | 更新吸収 | 06_update_absorption.md | 新しい能力を取り込める |

---

## 運用例

### 例1: 「MCPサーバーを調査してほしい」

```
STEP 1: 分類 → RC-1（調査中心）
STEP 2: 目的 → 利用可能なMCPサーバーの把握。完了条件: サーバー一覧と用途の整理。
STEP 3: 知識確認 → F-019 MCP Servers（D1採用, P2高優先, T1確定）が既知。
STEP 4: 能力選定 →
  使う: F-002 MCP（接続基盤）、F-003 Subagents（並列調査）、F-019 MCP Servers（リファレンス）
  使わない: F-009 Agent SDK（S2: 今回は調査であり実装不要）
  再確認: 不要（T1確定知識）
STEP 6: 提案形成 → 8項目テンプレートで出力
STEP 7: 実行橋渡し →
  対象: MCP公式リポジトリ
  作業順: 調査→記録→GitHub反映
  検証: サーバー一覧が網羅的であること
  GitHub: docs(mcp): survey available MCP servers
```

### 例2: 「GitHub Actionsの自動PRレビューを設定してほしい」

```
STEP 1: 分類 → RC-3（実装中心）、副: RC-6（運用改善）
STEP 2: 目的 → PRレビュー自動化の設定。完了条件: PRが作成されたときにClaude Codeが自動レビューする。
STEP 3: 知識確認 → F-010/F-014（D2試験導入, P2高優先, T2判断済み）が既知。
STEP 4: 能力選定 →
  使う: F-010 GitHub Actions（CI/CD）、F-014 claude-code-action（実装体）、F-004 Hooks（トリガー）
  使わない: F-032 promptfoo（S1: PRレビューに直接効かない）
  再確認: F-014のYAML仕様（T2だが実装前に公式確認推奨）
STEP 5: 再確認 → anthropics/claude-code-actionのREADMEで最新YAML仕様を確認
STEP 6: 提案形成 → 8項目テンプレートで出力
STEP 7: 実行橋渡し →
  対象: .github/workflows/claude-review.yml
  作業順: 調査→実装→検証→GitHub反映
  検証: テストPRで自動レビューが実行されること
  GitHub: feat(ci): add Claude Code PR review automation
```

### 例3: 「新しいMCPツールを見つけた。使うべきか?」

```
STEP 1: 分類 → RC-2（比較中心）
STEP 8: 更新反映 → 新機能発見トリガー発動
  1. 直接影響判定: 現在の作業に効くか?
  2. 既存比較: D1/D2候補より改善できるか?
  3. セットアップ時間: 導入コストは?
  4. 判定結果を記録
```

---

## AI参謀の制約

以下はAI参謀がやらないこと。

- 新しい巨大フェーズを作ること
- 全能力の無条件自動採用
- 人間確認ゼロの無制限自律運用
- 監督なしの全面自己進化
- Phase 1〜4の基盤を無視した独自判断

---

## 全フェーズ完了の意味

Phase 5（AI参謀）の完了により、以下の5フェーズが統合された。

1. **Phase 1（情報基盤）**: 何が存在するか知っている
2. **Phase 2（判断基盤）**: 何を使うべきか判断できる
3. **Phase 3（知識活用基盤）**: 知識を引き出し、鮮度を管理できる
4. **Phase 4（実行基盤）**: 実際の作業を高品質・高効率で実行できる
5. **Phase 5（AI参謀）**: 依頼に対して能力選定→理由付き提案→実行橋渡しを一貫して実行できる

AI参謀は、これら全てを統合して動作する判断フレームワークである。
