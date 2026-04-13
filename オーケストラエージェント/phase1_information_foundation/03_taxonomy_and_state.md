# 分類軸・状態管理・記録項目定義（Taxonomy, State & Record Schema）

> **担当**: グループ3  
> **インプット**: `01_information_sources.md` と `02_candidate_catalog.md` を読んでから着手すること  
> **ステップ対応**: フェーズ1作業指示書 ステップ5（分類軸確定）＋ ステップ6（候補管理状態）＋ ステップ7（記録項目）  
> **最終更新**: 2026-04-12（グループ3）

---

## パート1｜分類軸定義

### 分類F1｜種別

候補の「何であるか」を表す1次分類。候補1件につき1つだけ付与する。

| 種別コード | 種別名 | 説明 | 代表例 |
|-----------|--------|------|--------|
| T01 | 公式機能 | Anthropicが公式に提供する機能・ツール（APIやCLIの一部として動作） | Hooks, Skills, Subagents, Agent Teams, Advisor Tool |
| T02 | 公式実装 | Anthropicが公開するGitHubリポジトリの実装・ライブラリ | Claude Agent SDK, claude-code-action, anthropics/skills |
| T03 | 仕様・規格 | プロバイダー中立のオープン標準・プロトコル仕様 | MCP仕様, Agent Skills Open Standard |
| T04 | MCP server | MCPプロトコルで接続可能な外部サーバー実装 | Playwright MCP, Stripe MCP, Notion MCP |
| T05 | API | REST/GraphQL等のAPIエンドポイント（直接HTTP呼び出し可能なもの） | Claude Messages API, MCP Registry API |
| T06 | OSS | サードパーティが公開するオープンソースライブラリ・フレームワーク | LangGraph, CrewAI, AutoGen, litellm |
| T07 | 公開エージェント | 実行可能な状態で公開されているエージェント実装・デモ | claude-agent-sdk-demos, 各種公開エージェント |
| T08 | router・gateway | 複数モデル・プロバイダー間のルーティング・統合層 | claude-code-router, litellm |
| T09 | evaluation・observability | エージェント・LLMの評価・監視・トレーシング | Langfuse, Braintrust, Weights & Biases Weave |
| T10 | orchestration・workflow | 複数エージェントの協調・制御・ワークフロー管理 | LangGraph, CrewAI, AutoGen, mcp-agent |
| T11 | 実装パターン | 特定の設計パターン・アーキテクチャ的知見（実装物ではなくノウハウ） | executor+advisorパターン, マルチエージェント設計パターン |

> **注**: T08・T09・T10はT06と重複する場合がある。この場合は「目的が主体」の種別を優先する（例: litellmはrouter目的が主体のためT08）。

---

### 分類F2｜機能層

候補が「どの処理レイヤーに属するか」を表す。本プロジェクトのアーキテクチャ上の位置づけを示す。

| 層コード | 機能層名 | 役割 | 代表候補 |
|---------|---------|------|--------|
| L01 | 情報収集層 | 外部情報の取得・収集・検索を担当する | Playwright MCP, Stripe MCP, Notion MCP, Web検索MCP |
| L02 | 接続層 | 外部サービス・APIとのプロトコル接続を提供する | MCP仕様, MCP Registry, claude-code-router, litellm |
| L03 | 推論・改善補助層 | モデルの判断精度・出力品質を向上させる | Advisor Tool, Prompt Improver, Memory Tool |
| L04 | 実行層 | タスクを実際に実行する主体エージェント | Subagents, Skills, Agent Skills Standard, Managed Agents, claude-agent-sdk |
| L05 | 監督層 | 複数エージェントの協調・制御・全体統制を行う | Agent Teams, LangGraph, CrewAI, AutoGen, mcp-agent |
| L06 | 評価層 | エージェント・出力の品質評価・ベンチマーク | Langfuse, Braintrust, W&B Weave, mcp-eval |
| L07 | 検索・再利用層 | 過去の知識・成果物の蓄積・検索・再利用を行う | Memory Tool, RAG基盤（未確認） |
| L08 | 運用管理層 | CI/CD・デプロイ・権限管理・設定管理を担当する | claude-code-action, Managed Settings, Hooks（PreToolUse等） |

> **注**: 1つの候補が複数の層にまたがる場合は「主目的が属する層」を選び、secondary_layerとしてnotesに補足する。

---

### 分類F3｜利用段階

候補の「現在の利用可能状態」を表す。候補の熟成度合いと採用判断の進捗を示す。

| 段階コード | 段階名 | 意味 |
|-----------|--------|------|
| S1 | 調査段階 | 存在は把握しているが、詳細把握・評価が未完了の状態 |
| S2 | 評価段階 | 詳細調査が完了し、採用可否を検討している状態 |
| S3 | 試験導入段階 | 限定的な環境で実際に動作確認・試験導入を行っている状態 |
| S4 | 実運用段階 | 本プロジェクトの実環境に組み込まれ、稼働している状態 |
| S5 | 監視継続段階 | 現時点では採用しないが、将来の変化を監視し続ける状態 |

---

### 分類F4｜作業適用先

候補が「本プロジェクトのどの作業領域に適用されるか」を表す。1候補に複数付与可能。

| 適用先コード | 作業適用先名 | 説明 |
|------------|------------|------|
| W01 | 調査 | 情報収集・ウェブ検索・ドキュメント取得 |
| W02 | プロンプト改善 | プロンプトのデバッグ・最適化・品質向上 |
| W03 | GitHub運用 | PR作成・レビュー・CI/CD連携・コード管理 |
| W04 | 実装 | コード生成・実装支援・自動修正 |
| W05 | 外部接続 | 外部API・サービスとのデータ連携 |
| W06 | 非同期作業 | バックグラウンドでの長時間タスク・バッチ処理 |
| W07 | 継続監視 | ログ収集・パフォーマンス監視・アラート |
| W08 | 参謀判断支援 | 情報統合・提言生成・戦略的意思決定支援 |

---

## パート2｜候補管理状態定義

各状態について「意味 / 次にすべきこと / 次状態への遷移条件」を定義する。

| 状態名 | 意味 | 次のアクション | 遷移条件 |
|--------|------|--------------|---------|
| 未確認 | 候補として名前・URLは把握しているが、内容調査が一切行われていない | 基本情報の収集（README・ドキュメント読込） | 調査に着手した時点で「調査中」へ |
| 調査中 | 内容調査が進行中。記録が部分的または不完全 | 調査継続・記録項目を埋める | 必須項目が全て埋まり評価可能になったら「候補」へ |
| 候補 | 調査完了。本プロジェクトへの適用可能性が認められる状態 | 競合候補との比較・詳細評価を計画 | 比較対象が存在する場合は「比較待ち」へ。単独評価可能なら「採用候補」または「不採用候補」へ |
| 比較待ち | 複数の選択肢を並べた比較評価を待っている状態 | 比較評価の実施（フェーズ2で実施） | 比較評価が完了したら「採用候補」または「不採用候補」へ |
| 保留 | 評価継続の意思はあるが、現時点では判断を保留している状態（情報不足・beta・依存条件未充足等） | 保留理由の解消条件を記録し、条件成立時に再評価をトリガー | 保留理由が解消したら「候補」または「調査中」へ。解消見込みなしなら「不採用候補」へ |
| 不採用候補 | 現時点で本プロジェクトへの採用を見送ることが決定している状態 | 不採用理由の記録。将来の再評価条件があれば記録 | 状況変化（大型アップデート・競合不採用等）があれば「調査中」へ復帰可能 |
| 採用候補 | 採用することが決定しており、フェーズ3以降での実装を想定している状態 | 依存関係・実装方法の詳細化・試験導入計画 | 試験導入が始まったら「試験導入候補」へ |
| 監視継続 | 現時点では採用せず、動向を定期監視する状態（将来採用の可能性を残す） | 定期確認スケジュールに組み込む。更新検知時に再評価 | 重要アップデートが発生したら「候補」または「調査中」へ復帰 |
| 試験導入候補 | 限定的な試験環境での動作確認・プロトタイプ実装が決定している状態 | プロトタイプ実装・動作確認・評価レポート作成 | 試験導入が成功したら「採用候補」（実運用確定）へ。失敗・課題顕在化なら「保留」または「不採用候補」へ |

---

## パート3｜記録項目定義（レコードスキーマ）

### 共通必須項目

全候補に必ず記録する項目。

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| item_id | string | 候補の識別子（F-001 形式） |
| item_name | string | 正式名称（公式表記に準拠） |
| item_type | enum(F1) | 分類F1の種別コード（T01〜T11） |
| layer_category | enum(F2) | 分類F2の機能層コード（L01〜L08） |
| source_url | URL | 一次情報URL（公式ドキュメントまたは公式GitHub） |
| source_type | string | 公式docs / 公式GitHub / OSS / その他 |
| vendor_owner | string | 提供元・開発主体（Anthropic / Microsoft等） |
| summary | text | 何をするものか（2〜3文で明確に記述） |
| primary_use_cases | list | 本プロジェクトでの主な活用場面（W01〜W08から選択し具体例も記載） |
| prerequisites | list | 利用に必要な前提条件・依存 |
| related_items | list | 関連・競合する候補のitem_id一覧 |
| current_status | enum | 現在の管理状態（未確認/調査中/候補/比較待ち/保留/不採用候補/採用候補/監視継続/試験導入候補） |
| first_seen_at | date | 初めて候補として認識した日付（YYYY-MM-DD） |
| last_checked_at | date | 最後に情報を確認した日付（YYYY-MM-DD） |
| evidence_links | list | 判断の根拠となったURL・ドキュメントの参照先 |
| notes | text | 自由記述（特記事項・補足） |

---

### 追加管理項目

評価・管理の精度を上げるための補助項目。必要に応じて記録する。

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| update_frequency_note | text | 更新頻度の傾向（例: 毎月、不定期更新等） |
| alternative_candidates | list | 代替として検討できる候補のitem_id一覧 |
| risk_note | text | 採用にあたってのリスク・懸念事項 |
| unknowns | list | 判明していない重要事項（未解消の不確実性） |
| revisit_condition | text | 再確認・再評価をトリガーする条件の記述 |
| revisit_date | date | 次回確認予定日（YYYY-MM-DD） |
| phase_relevance | string | どのフェーズで最も重要になるか（例: フェーズ2優先、フェーズ3以降等） |
| future_action | text | 次に取るべき具体的アクション |

---

### 公式機能の追加項目

item_typeがT01（公式機能）またはT05（API）の候補に記録する。

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| beta_or_ga | enum | ベータ版か正式GA版か（beta / public_beta / ga / experimental） |
| product_area | string | 属するプロダクト領域（Claude Code / Claude Platform / MCP等） |
| usage_form | text | 呼び出し・設定の形式（CLI設定 / API呼び出し / YAML定義等） |
| limitations | list | 現時点での制限事項（レート制限・対応言語・tier制限等） |
| diff_from_existing | text | 既存の類似機能との差分・なぜこれが新しいか |

---

### OSS・公開エージェントの追加項目

item_typeがT06（OSS）・T07（公開エージェント）・T08（router）・T09（evaluation）・T10（orchestration）の候補に記録する。

| フィールド名 | 型 | 説明 |
|------------|-----|------|
| repo_url | URL | GitHubリポジトリURL |
| maintenance_status | enum | active / slow / stale / archived（更新頻度に基づく判定） |
| activity_level | text | スター数・直近更新日・コントリビュータ数等の活動指標 |
| readme_clarity | enum | high / medium / low（READMEの明瞭さの評価） |
| adoption_difficulty | enum | low / medium / high（本プロジェクトへの導入難易度） |
| purpose_alignment | enum | high / medium / low（本プロジェクト目的との適合度） |
| reuse_possibility | enum | full_reuse / partial_reuse / reference_only / no_reuse（活用形態） |
| partial_reuse_note | text | partial_reuseの場合、どの部分を活用するかの具体的記述 |
| risk_areas | list | 技術的リスク（API依存・メンテナンス停止リスク・ライセンス等） |
