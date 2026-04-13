# 知識項目スキーマ定義（Knowledge Item Schema）

> **ステップ対応**: フェーズ3作業指示書 ステップ10  
> **最終更新**: 2026-04-13

---

## この文書の役割

知識資産を保存・検索・再利用するための最低限の項目を固定する。フェーズ1の記録スキーマ（phase1/03）とフェーズ2の評価スキーマ（phase2/01, 04）を統合し、知識活用基盤として拡張する。

---

## パート1｜知識項目スキーマ

### 必須項目

| フィールド名 | 型 | 説明 | 知識層 |
|------------|-----|------|--------|
| knowledge_id | string | 知識項目の一意識別子（K-001形式） | KL-1 |
| source_item_id | string | 元となる候補のitem_id（F-001等）または情報源のsource_id（A-001等） | KL-1 |
| knowledge_type | enum | 候補情報 / 評価結果 / 比較結果 / 判断記録 / 運用ルール / 仕様要約 / 調査メモ | KL-1 |
| layer_type | enum | KL-1 / KL-2 / KL-3 / KL-4 | KL-1 |
| summary | text | 知識の要約（2〜3文） | KL-2/KL-3 |
| structured_fields | object | 構造化された項目群（下記参照） | KL-1 |
| evidence_links | list[URL] | 根拠となった情報源のURL一覧 | KL-1 |
| originating_comparisons | list[string] | この知識の元となった比較グループID（CG-01等） | KL-2 |
| originating_decisions | list[string] | この知識の元となった判断（D1, B1等） | KL-2 |
| freshness_level | enum | stable / evolving / volatile | KL-4 |
| last_verified_at | date | 最後に一次情報で確認した日付（YYYY-MM-DD） | KL-1 |
| recheck_required_flag | boolean | 再確認が必要かどうか | KL-1 |
| recheck_condition | text | 再確認をトリガーする条件の記述 | KL-4 |
| trust_level | enum | T1 / T2 / T3 / T4 | KL-1 |
| usage_scope | list[enum] | この知識が有用なフェーズ（phase3 / phase4 / phase5 / all） | KL-1 |
| retrieval_priority | enum | high / medium / low | KL-1 |
| notes | text | 補足・注意事項 | KL-2/KL-3 |

### 補助項目（必要に応じて付与）

| フィールド名 | 型 | 説明 | 知識層 |
|------------|-----|------|--------|
| source_repo | URL | GitHubリポジトリURL | KL-1 |
| source_doc | URL | 公式ドキュメントURL | KL-1 |
| source_vendor | string | 提供元ベンダー名 | KL-1 |
| linked_candidates | list[string] | 関連する候補のitem_id一覧 | KL-1 |
| linked_tasks | list[string] | 関連するタスク・アクション | KL-2 |
| linked_phase_outputs | list[string] | 関連するフェーズ成果物のファイルパス | KL-1 |

---

## パート2｜structured_fieldsの内容

structured_fieldsオブジェクトには、knowledge_typeに応じて以下の項目を格納する。

### knowledge_type = 候補情報

フェーズ1の記録スキーマ（phase1/03）の全項目を引き継ぐ。

| フィールド | 元のフィールド | 説明 |
|-----------|-------------|------|
| item_type | item_type | 種別コード（T01〜T11） |
| layer_category | layer_category | 機能層コード（L01〜L08） |
| current_status | current_status | 管理状態 |
| vendor_owner | vendor_owner | 提供元 |
| primary_use_cases | primary_use_cases | 主な活用場面 |
| beta_or_ga | beta_or_ga | beta/public_beta/ga/experimental |
| maintenance_status | maintenance_status | active/slow/stale/archived |

### knowledge_type = 評価結果

フェーズ2の評価スキーマ（phase2/01, 04）を引き継ぐ。

| フィールド | 元のフィールド | 説明 |
|-----------|-------------|------|
| evaluation_scores | E1〜E10 | 10軸評価スコア |
| decision_state | decision_state | 採用状態（D1〜D5） |
| build_vs_buy_state | build_vs_buy_state | 自作/流用判断（B1〜B5） |
| current_priority | current_priority | 優先順位（P1〜P5） |
| compared_with | compared_with | 比較対象 |
| reason_summary | reason_summary | 判断理由要約 |
| unresolved_points | unresolved_points | 未解決論点 |
| next_review_condition | next_review_condition | 再確認条件 |
| next_action | next_action | 次アクション |

---

## パート3｜freshness_levelの定義

| レベル | 意味 | 例 | 再確認頻度 |
|--------|------|-----|-----------|
| stable | 安定した知識。変更頻度が低い | GA済み公式機能の基本仕様、プロジェクト内定義 | 6ヶ月毎 |
| evolving | 発展途上の知識。定期的に変化する | 活発なOSSの現状、公式機能のマイナーアップデート | 3ヶ月毎 |
| volatile | 不安定な知識。頻繁に変化しうる | beta/experimental機能、pricing未確定、新興OSS | 利用のたびに確認 |

---

## パート4｜フェーズ1・2スキーマとの互換性

### 設計方針

知識項目スキーマはフェーズ1・2のスキーマを**包含する**設計とする。既存の記録を破棄せず、拡張項目（knowledge_id, layer_type, trust_level, freshness_level, recheck_required_flag, recheck_condition, usage_scope, retrieval_priority）を追加する形で移行する。

### 移行時のマッピング

| 既存項目 | 知識スキーマ上の位置 |
|---------|-------------------|
| phase1/02のitem_id | source_item_id |
| phase1/02のcurrent_status | structured_fields.current_status |
| phase1/02のlast_checked_at | last_verified_at |
| phase2/04のdecision_state | structured_fields.decision_state |
| phase2/04のreason_summary | summary + originating_decisions |
| phase2/04のnext_review_condition | recheck_condition |
| phase1/04の再確認条件 | recheck_condition + freshness_level |

### 非破壊的拡張の原則

- フェーズ1・2の成果物ファイルはそのまま保持する
- 知識項目スキーマは新たな知識資産を作成するときに適用する
- 既存成果物の参照は、source_item_idとlinked_phase_outputsで辿れるようにする
