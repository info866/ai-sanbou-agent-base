# 分類軸・状態管理・記録項目定義（Taxonomy, State & Record Schema）

> **担当**: グループ3  
> **インプット**: `01_information_sources.md` と `02_candidate_catalog.md` を読んでから着手すること  
> **ステップ対応**: フェーズ1作業指示書 ステップ5（分類軸確定）＋ ステップ6（候補管理状態）＋ ステップ7（記録項目）

---

## パート1｜分類軸定義

### 分類F1｜種別

<!-- グループ3が記入 -->
<!-- 定義する種別例: 公式機能 / 公式実装 / 仕様・規格 / MCP server / API / OSS / 公開エージェント / router・gateway / evaluation・observability / orchestration・workflow / 実装パターン -->

### 分類F2｜機能層

<!-- グループ3が記入 -->
<!-- 定義する機能層例: 情報収集層 / 接続層 / 推論・改善補助層 / 実行層 / 監督層 / 評価層 / 検索・再利用層 / 運用管理層 -->

### 分類F3｜利用段階

<!-- グループ3が記入 -->
<!-- 定義する段階例: 調査段階 / 評価段階 / 試験導入段階 / 実運用段階 / 監視継続段階 -->

### 分類F4｜作業適用先

<!-- グループ3が記入 -->
<!-- 定義する適用先例: 調査 / プロンプト改善 / GitHub運用 / 実装 / 外部接続 / 非同期作業 / 継続監視 / 参謀判断支援 -->

---

## パート2｜候補管理状態定義

> 各状態について「意味 / 次にすべきこと / 次状態への遷移条件」を定義すること

### 状態一覧

| 状態名 | 意味 | 次のアクション | 遷移条件 |
|--------|------|--------------|---------|
| 未確認 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 調査中 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 候補 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 比較待ち | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 保留 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 不採用候補 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 採用候補 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 監視継続 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |
| 試験導入候補 | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> | <!-- グループ3が記入 --> |

---

## パート3｜記録項目定義（レコードスキーマ）

### 共通必須項目

<!-- グループ3が記入 -->
<!-- 定義する必須項目: item_id / item_name / item_type / layer_category / source_url / source_type / vendor_owner / summary / primary_use_cases / prerequisites / related_items / current_status / first_seen_at / last_checked_at / evidence_links / notes -->

### 追加管理項目

<!-- グループ3が記入 -->
<!-- 定義する追加項目: update_frequency_note / alternative_candidates / risk_note / unknowns / revisit_condition / revisit_date / phase_relevance / future_action -->

### 公式機能の追加項目

<!-- グループ3が記入 -->
<!-- 定義する公式機能専用項目: beta_or_ga / product_area / usage_form / limitations / diff_from_existing -->

### OSS・公開エージェントの追加項目

<!-- グループ3が記入 -->
<!-- 定義するOSS専用項目: repo_url / maintenance_status / activity_level / readme_clarity / adoption_difficulty / purpose_alignment / reuse_possibility / partial_reuse_note / risk_areas -->
