# 未解決論点・フェーズ3引き継ぎ（Unresolved Points & Phase3 Handoff）

> **担当**: グループ5  
> **インプット**: `00`〜`05` を全て読み込んでから着手すること  
> **ステップ対応**: フェーズ2作業指示書 ステップ11（フェーズ3引き継ぎ整理）  
> **最終更新**: 2026-04-12（グループ5）

---

## パート1｜未解決論点の最終整理

### フェーズ2内で解消できなかった論点

| # | 論点 | 未解消の理由 | フェーズ3での扱い |
|---|------|------------|-----------------|
| 1 | Claude Agent SDK単体でのorchestration能力の限界値 | 実際に複雑ワークフローを実装していないため境界が不明。実装なしに論争を解決できない | フェーズ3でAgent SDKを使ったエージェントを実装し、LangGraph/mcp-agentが必要になる条件を実証的に確認する |
| 2 | Memory Tool API と CLAUDE.mdのauto memoryの役割分担 | 両機能が並行して使われているが、保存スコープ・検索方法・データ形式の詳細比較が未実施 | フェーズ3の知識活用基盤設計で役割分担を明示的に定義する。重複管理のリスクを排除する |
| 3 | Langfuse vs Arize Phoenixの選択 | フェーズ2では両方ともD3（保留）。実際のオブザーバビリティ要件が未定 | フェーズ3でオブザーバビリティ基盤を設計するときに両者を試用比較して選択する |
| 4 | ant CLI（F-024）の詳細機能 | リリースノートの記載のみでドキュメントURLが未確認。2026-04-08リリースで情報が少ない | フェーズ3開始前にドキュメントを確認。「APIリソースのYAMLバージョン管理」機能が本プロジェクトのIaC管理に有用か評価する |
| 5 | D-004 Braintrust・D-005 W&B Weaveの詳細評価 | SaaS型のためGitHub探索でヒットせず。サイト訪問が必要だったが現フェーズでは他候補で代替可能 | promptfoo確立後に評価が不足している場合のみ調査。基本的には不要の可能性が高い |

---

### 再調査条件

| # | 対象 | 再調査トリガー | 次のアクション |
|---|------|-------------|--------------|
| 1 | F-027 LangGraph | Agent SDK単体では実現できないワークフロー要件が発生したとき | LangGraphの詳細API・Claude Code/Agent SDKとの統合方法を確認し、採用判断を行う |
| 2 | F-006 Claude Managed Agents | betaヘッダーが不要になりGAになったとき | 基本的なエージェントタスクで試験導入し、SubagentsとのコストパフォーマンスをBenchmarkする |
| 3 | F-012 Advisor Tool | betaヘッダーが不要になりGAになったとき | executor+advisorペアリングを本番エージェントタスクで試験し、コスト削減効果を計測する |
| 4 | F-029 AutoGen | コスト問題の改善報告があったとき | LLMコール数の削減をベンチマークし、フェーズ5の高精度推論候補として再評価する |
| 5 | F-024 ant CLI | 公式ドキュメントURLが確認できたとき | 機能一覧を確認し、本プロジェクトのAPIリソース管理への適用可能性を評価する |

---

### 継続監視対象

| item_id | 候補名 | 監視理由 | 確認タイミング |
|---------|--------|---------|-------------|
| F-006 | Claude Managed Agents | betaのGA移行タイムライン | Anthropicリリースノート・月1回 |
| F-008 | Agent Teams | 実験的機能のGA移行 | Claude Codeリリースノート・月1回 |
| F-012 | Advisor Tool | betaのGA移行タイムライン | Anthropicリリースノート・月1回 |
| F-021 | mcp-agent | LastMile AIの保守継続性（mcp-eval停止の先例） | GitHubのcommit履歴・月1回 |
| F-027 | LangGraph | LangChain社の開発状況とClaude Agent SDKとのエコシステム関係 | LangGraphリリースノート・月1回 |
| F-029 | AutoGen | コスト最適化の改善報告（AutoGen 0.4系） | AutoGen GitHubリリースノート・月1回 |
| F-036 | Portkey Gateway | MCPガードレール機能の成熟度 | Portkeyリリースノート・3ヶ月に1回 |
| F-007 | Cowork | Research previewからGA移行・API仕様公開 | Anthropicプロダクト発表・随時 |

---

## パート2｜フェーズ3引き継ぎ対象

### フェーズ3で知識資産として活かすべき候補

> 知識活用基盤フェーズで、検索・参照・再利用可能な形で管理すべき候補

| item_id | 候補名 | 知識活用での役割 | 優先度 |
|---------|--------|----------------|--------|
| F-002 | MCP | 外部システム接続の中核。RAGサーバー・DB接続・ファイルシステム連携の基盤 | P1 |
| F-019 | MCP Servers | リファレンス実装集。必要なMCPサーバーをここから流用 | P1 |
| F-025 | Memory Tool | クロスセッション記憶の永続化。参謀エージェントの状態継続に必須 | P1 |
| F-009 | Claude Agent SDK | 知識検索・評価・推論パイプラインの実装基盤 | P1 |
| F-015 | claude-agent-sdk-python | Python実装のエージェント知識検索パイプライン | P2 |
| F-026 | MCP Connector | API側からのMCPサーバー接続。プログラマブルなRAG統合 | P2 |
| F-018 | MCP Registry | 必要なMCPサーバーの発見・選定 | P2 |
| F-032 | promptfoo | 知識活用の品質評価・RAGの精度測定 | P2 |
| F-038 | MCP Inspector | MCPサーバーの開発・デバッグツール | P3 |
| F-003 | Subagents | 知識検索タスクの専門化・並列実行 | P1（継続） |
| F-004 | Hooks | 知識活用フローの自動化・品質ゲート | P1（継続） |
| F-005 | Skills | 知識活用パターンのスキルパッケージ化 | P1（継続） |

---

### RAG候補 / 検索対象になりうる情報資産

| 情報資産 | source_id | RAG化の価値 | 備考 |
|---------|-----------|-----------|------|
| フェーズ1候補カタログ（02_candidate_catalog.md） | phase1/02 | 38候補の詳細情報をベクトル検索可能にすることで、技術選定時の参照が高速化 | フェーズ2評価結果を含めたマスターデータベースとして管理 |
| フェーズ2評価記録（04_candidate_evaluations.md） | phase2/04 | 評価スコア・判断根拠・比較結果をRAGで参照することで将来の再評価を効率化 | 判断根拠が構造化されているためRAG化の精度が高い |
| Anthropic公式ドキュメント（code.claude.com, platform.claude.com） | A-001, A-002 | 最新の機能仕様を常に参照可能にする。Hooks/Skills/Subagentsの詳細はここから | 定期更新（更新追跡ルールに従い月1回再クロール） |
| GitHubリポジトリのREADME集（採用候補のD1/D2） | 各B-xxx | 実装詳細・APIリファレンスを検索可能にする | promptfoo・LiteLLM・anthropics/skillsが最優先 |
| フェーズ1〜2の全成果物 | phase1/*, phase2/* | 過去の判断の文脈を参謀エージェントが参照できるようにする | プロジェクト知識ベースの中核 |

---

### よく参照すべき公式ソース

| source_id | source_name | 参照理由 |
|-----------|-------------|---------|
| A-001 | code.claude.com/docs/en | Claude Code公式ドキュメント。Hooks/Skills/Subagents/Agent Teamsの最新仕様 |
| A-002 | platform.claude.com/docs/en | Anthropic Platform API公式ドキュメント。Memory Tool・MCP Connector・Managed Agents・Advisor Toolの仕様 |
| A-003 | modelcontextprotocol.io/introduction | MCPプロトコル公式仕様。接続層設計の根拠 |
| B-001 | anthropics/skills（GitHub） | Skills公式リポジトリ。流用可能なスキルのカタログ |
| B-007 | modelcontextprotocol/servers（GitHub） | MCPサーバーリファレンス実装集。フェーズ3の接続実装の参照元 |
| A-004 | platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool | Advisor Tool仕様。GA移行後に参謀エージェントのコスト最適化で参照 |

---

### 評価結果ごと検索可能にすべき項目

フェーズ3の知識活用基盤で以下の検索クエリに答えられるように評価結果を構造化する：

- 「〇〇の機能を持つ候補はどれか」（primary_use_casesの検索）
- 「採用候補（D1）の中でGA済みの候補はどれか」（decision_state + beta_or_ga の複合検索）
- 「オーケストレーション系の候補を比較したい」（比較グループ別の絞り込み）
- 「今すぐ使えて導入が容易な候補はどれか」（E5スコア高 + E10スコア高の複合検索）
- 「保留中の候補の解消条件は何か」（next_review_conditionの参照）

---

### 次フェーズで重点化すべき候補群

| 優先度 | 候補群 | 理由 |
|--------|--------|------|
| 最優先 | F-002（MCP）、F-025（Memory Tool）、F-019（MCP Servers）、F-026（MCP Connector） | 知識活用基盤の接続・記憶・検索の核心。フェーズ3の定義そのもの |
| 高優先 | F-009/F-015（Agent SDK/Python SDK）、F-003（Subagents）、F-032（promptfoo） | 知識活用パイプラインの実装基盤と品質評価基盤 |
| 中優先（比較評価） | F-034（Langfuse）、F-035（Arize Phoenix） | オブザーバビリティ基盤の選択をフェーズ3で決定する |
| 中優先（GA待ち） | F-006（Managed Agents）、F-012（Advisor Tool） | GAになった時点でフェーズ3の実装に組み込む |

---

## パート3｜フェーズ2完了確認

### 完了条件チェックリスト

- [x] 評価基準が固定されている（→01: 10軸E1〜E10、5スコア段階定義済み）
- [x] 同役割候補の比較が可能になっている（→02: CG-01〜CG-06の比較グループ確定、→04: 各CGで比較評価実施）
- [x] 各候補が採用状態のどれかへ分類されている（→05 パート1: 全40件にD1〜D5を付与）
- [x] 各候補について自作/流用判断の方向性が出ている（→05 パート2: 全候補にB1〜B5を付与）
- [x] 今後の優先順位が整理されている（→05 パート3: 全候補にP1〜P5を付与）
- [x] 判断理由と未解決点が記録されている（→04: 全候補にreason_summary・unresolved_points記録、→05 パート5・06 パート1で整理）
- [x] フェーズ3以降で再利用できる評価資産になっている（→本ファイル パート2: RAG化対象・参照ソース・検索クエリ設計を記録）
- [x] 「感覚で決める」状態から脱却している（→全候補に10軸スコア・根拠・compared_with・reason_summaryを記録。比較なし・根拠なしの採用判断なし）

**全8条件: 充足**

---

### フェーズ3着手判断

**判断結果**: フェーズ3着手可能

**整備済み資産:**

- `00_scope_and_execution_contract.md`: フェーズ2の作業契約・範囲定義（グループ1作成済み）
- `01_evaluation_criteria.md`: 10軸評価基準の定義（グループ1作成済み）
- `02_comparison_units_and_matrix_plan.md`: 比較単位・CG-01〜CG-06の比較グループ（グループ1/2作成済み）
- `03_revalidation_and_github_research.md`: 公式再確認・GitHub追加探索・支援部品評価（グループ2作成済み）
- `04_candidate_evaluations.md`: 全40候補の10軸評価・判断状態・優先順位（グループ3作成済み）
- `05_adoption_build_vs_buy_priority.md`: 採用状態一覧・自作流用判断・優先順位・未解決論点（グループ4作成済み）
- `06_unresolved_points_and_phase3_handoff.md`: 未解決論点・フェーズ3引き継ぎ・完了確認（本ファイル、グループ5作成済み）
- `.claude/` runtime基盤: Hooks（protect-canonical.sh）・Subagents（catalog-checker/scope-guard/phase-reporter）・settings.json（全件動作確認済み）

**フェーズ3の着手前に解消しておくべき残課題:**

1. **Node.js更新（v22.22+）**: promptfooの試用に必要。優先度高
2. **ant CLIのドキュメント確認**: platform.claude.comまたはcode.claude.comでドキュメントURLを特定する。フェーズ3開始前に実施
3. **anthropics/claude-agent-sdk-demosの内容確認**: 具体的なデモ一覧（email assistant・research agent等）を確認し、AI参謀基盤への流用可能性を把握しておく
4. **Memory Tool API vs auto memoryの役割分担定義**: フェーズ3の知識活用基盤設計の前提として必要。CLAUDE.mdのauto memoryとMemory Tool APIの保存スコープ・データ形式の差異を明確化する

**フェーズ3の主要着手内容（参考）:**

> フェーズ2はここで完結。フェーズ3の内容は正本（大分類要件提起書・大分類作業指示書）に従い、別途フェーズ3作業契約書で定義すること。以下は引き継ぎ情報として記録するのみ。

- MCP接続基盤の実装（F-002・F-019・F-026を使った外部システム接続）
- クロスセッション知識活用パイプラインの構築（F-025 Memory Toolの本格活用）
- オブザーバビリティ基盤の選択・実装（F-034 Langfuse vs F-035 Arize Phoenix の比較評価）
- Agent SDK（F-009/F-015）を使った最初の本番エージェントパイプラインの構築
- promptfoo（F-032）を使った評価基盤の確立
- anthropics/skills（F-013）からの既製スキル流用と独自スキルの追加定義
