# 未探索領域・フェーズ2引き継ぎ（Unexplored Areas & Phase2 Handoff）

> **担当**: グループ2（パート1記入）→ グループ3（パート2・3を完成させる）  
> **最終更新**: 2026-04-12（グループ2）

---

## パート1｜今回の調査状況の整理（グループ2記入）

### 調査済みの領域

今回グループ2が確認・記録した範囲は以下の通り。

#### 公式一次情報（確認済み）
- Claude Code公式ドキュメント全体構造（code.claude.com/docs/en/）
- Claude Platform APIリリースノート（2024年後半〜2026-04-12）
- Hooks: 全10種イベント、4種hookタイプ、設定方法
- Skills: SKILL.md形式、frontmatter仕様、invocation制御、agentskills.io標準
- Subagents: カスタム定義方法、managed subagents、agent teamsとの違い
- Agent Teams: アーキテクチャ、有効化方法、制限事項
- Claude Agent SDK: 概要、Python/TypeScript対応、sessions/hooks/subagents/MCP統合
- Claude Managed Agents: 2026-04-08公開ベータ確認
- Advisor Tool: 2026-04-09公開ベータ確認
- Prompt Improver: Consoleツールとして確認
- MCP: 公式仕様・modelcontextprotocol.io確認
- Agent Skills標準: agentskills.io確認、採用企業（Microsoft, OpenAI, Atlassian, Figma等）

#### 公式GitHub（確認済み）
- anthropics/skills: 115k stars、active（2026-04-12更新）
- anthropics/claude-code-action: 7k stars、active
- anthropics/claude-agent-sdk-python: 6.3k stars、active
- anthropics/claude-agent-sdk-typescript: 1.3k stars、active
- anthropics/claude-agent-sdk-demos: 2.2k stars、active
- modelcontextprotocol/registry: 6.7k stars、active
- modelcontextprotocol/servers: 83.5k stars、active

#### OSS / フレームワーク（確認済み）
- musistudio/claude-code-router: 32k stars、概要確認
- BerriAI/litellm: 43k stars、概要確認
- lastmile-ai/mcp-agent: 8.2k stars、概要確認
- lastmile-ai/mcp-eval: 20 stars、活動低迷確認（保留扱い）
- langchain-ai/langgraph: 29k stars、MCP深度・特性確認
- crewAIInc/crewAI: 49k stars、ロールベース特性確認
- microsoft/autogen: 57k stars、会話駆動特性確認
- openai/openai-agents-python: 21k stars、OpenAI版エージェントSDK確認

---

### 今回浅くしか見ていない領域

#### 公式機能（内部仕様まで未確認）
- Claude Managed Agents詳細API仕様（エンドポイント設計・コンテナ設定等）
- Agent SDK: subagents定義の詳細パターン、sessions APIの詳細
- Hooks: HTTPフック・Promptフック・Agentフックの詳細設定方法
- Skills: supporting files（template.md等）の活用パターン詳細
- Agent Teams: トークンコストの詳細、TeammateIdle等の特殊hookイベント
- Advisor Tool: 詳細仕様・pricing（betaのため情報少）
- ant CLI: リリースノート記載確認のみ、ドキュメントURL未確認
- Memory Tool: 詳細設定方法・保存形式

#### GitHub実装（READMEのみ確認、中身未精査）
- anthropics/claude-agent-sdk-demos: デモ一覧・各実装内容
- claude-code-router: 内部ルーティングロジック詳細
- mcp-agent: ワークフローパターン詳細

#### OSS比較（星数・説明のみ確認）
- langgraph/crewAI/autogenの詳細API・Claude Code/Agent SDKとの統合方法
- litellm: Claude特有の設定オプション、Managed Agentsとの統合可能性

---

### 未探索の領域

#### Evaluation / Observability系（ほぼ未確認）
- Langfuse、Braintrust、Weights & Biases（Weave）等のLLM評価基盤
- Claude Agent SDK専用のオブザーバビリティツールの有無
- MCPサーバーのテスト・評価方法（mcp-eval以外の選択肢）

#### AWS/Google Cloud系エージェント基盤
- AWS Strands Agents（AWSが公開したエージェントフレームワーク）
- Google Cloud Agent Builder / Vertex AI Agent Engine

#### MCP Ecosystem詳細
- MCP Registry（api.anthropic.com/mcp-registry/）に登録されているサーバー一覧
- 主要MCPサーバー（Playwright MCP、Stripe MCP、Notion MCP等）の詳細
- MCP Authentication（OAuth等）の実装パターン

#### Claude Code連携パターン
- Slack統合（@Claude to PR機能）の詳細
- Chrome debugging tool
- Remote Control / Channels機能の詳細
- GitLab CI/CD統合詳細
- Dispatch機能の詳細

#### セキュリティ・権限管理
- Claude Code Managed Settingsの詳細
- 組織向け権限管理（Enterprise設定）

---

### 次回優先して探索すべき領域

以下を次回（グループ3以降またはフェーズ2）で優先的に確認することを推奨する。

| 優先順位 | 領域 | 理由 |
|---------|------|------|
| 高 | Evaluation / Observability系OSS | 本プロジェクトの参謀エージェント運用に評価基盤は必須。完全未探索。 |
| 高 | Claude Managed Agents API詳細 | 2026-04-08公開betaで最新機能。本プロジェクトの実行基盤候補として詳細確認が必要。 |
| 高 | MCP Registry 登録済みサーバー一覧 | 接続層の選択肢を網羅するために必要。APIでの取得方法は確認済み。 |
| 中 | AWS Strands Agents | orchestration系の代替候補として確認が必要。 |
| 中 | claude-agent-sdk-demos の実装内容詳細 | 参謀エージェント実装のリファレンスとして価値が高い可能性。 |
| 中 | langgraph × Claude Agent SDK 統合方法 | 最有力OSS候補の具体的統合パターン確認が必要。 |
| 低 | Slack/Chrome/Remote Control統合詳細 | 運用基盤として参考になるが優先度は低い。 |

---

## パート2｜フェーズ2への引き継ぎ内容（グループ3）

> **最終更新**: 2026-04-12（グループ3）

### 比較評価が必要な候補ペア

フェーズ2で「どちらを採用するか」の比較評価が必要な候補の組み合わせ。

| # | 比較ペア / グループ | 候補item_id | 比較軸 |
|---|-------------------|-------------|--------|
| CP-01 | router・gateway選択 | F-020（claude-code-router）vs F-022（litellm） | Claude特化 vs マルチプロバイダー対応・運用コスト・機能カバレッジ |
| CP-02 | orchestration主軸選択 | F-021（LangGraph）vs F-027（CrewAI）vs F-028（AutoGen） | 設計柔軟性 vs ロールベース手軽さ vs 会話駆動精度。Claude Agent SDKとの統合難易度も評価軸 |
| CP-03 | 実行エージェント管理層 | F-003（Subagents）vs F-012（Managed Agents） | 自己ホスト制御性 vs マネージドの運用コスト削減。betaのGA移行後に本格評価 |
| CP-04 | MCPワークフロー層 | F-024（mcp-agent）vs F-021（LangGraph） | MCPファースト設計 vs グラフ制御の豊富さ |
| CP-05 | evaluation・observability基盤 | D-003（Langfuse）vs D-004（Braintrust）vs D-005（W&B Weave） | OSS vs SaaS・コスト・Claude Agent SDKとの統合容易性 |

---

### 評価が必要な未解決論点

フェーズ2に入る前に答えが出ていない重要な技術的・設計的論点。

| # | 論点 | 背景・なぜ重要か | 解決に必要な情報 |
|---|------|----------------|----------------|
| UQ-01 | Claude Agent SDK と orchestrationフレームワーク（LangGraph等）はどう組み合わせるべきか | SDKはエージェントロジックの記述に使い、LangGraphは制御フローに使うという分担が有力だが、実際に相互運用できるかが未確認 | claude-agent-sdk-demosの実装内容確認・LangGraphのMCP/Claude SDK統合例確認 |
| UQ-02 | Skills（SKILL.md）と Subagents（agents/*.md）の役割分担は何か | どちらも「専門エージェントへの委譲」を担えるように見えるが、呼び出し経路・コンテキスト共有・再利用形態が異なる可能性がある | Claude Code Skills Docs（A-012）と Sub-agents Docs（A-010）の詳細比較 |
| UQ-03 | Managed Agentsは本プロジェクトの実行基盤として適切か | 2026-04-08公開betaのため詳細仕様が未確認。コンテナ設定・pricing・スケーリング特性が不明 | A-009の詳細API仕様確認・betaのGA移行後の制限緩和確認 |
| UQ-04 | evaluation・observability基盤をいつ・どの形で導入するか | フェーズ2以降でエージェントの出力品質評価が必須になるが、評価基盤がない状態では参謀エージェントの信頼性を客観的に測定できない | D-003〜D-005の詳細調査。Claude Agent SDKとのトレーシング統合確認 |
| UQ-05 | ant CLIはプロジェクトの運用ワークフローに組み込むべきか | 2026-04-08リリースのClaude API用CLIツール（E-003）だが詳細不明。既存Claude Code CLIとの役割分担が不明 | ant CLIドキュメントURL確認・機能範囲の調査 |

---

### 自作 vs 流用で比較が必要な対象

「既存OSSを使うべきか、Claude Agent SDKを使って自作すべきか」の判断が必要な対象。

| # | 対象領域 | 流用候補 | 自作の根拠 | 判断に必要な情報 |
|---|---------|---------|-----------|---------------|
| BV-01 | エージェントオーケストレーション層 | LangGraph（F-021）/ mcp-agent（F-024） | Claude Agent SDK単体でも制御フローは実装可能。不要な依存を増やしたくない場合 | Claude Agent SDK Docsのworkflow制御機能の詳細確認（A-013）・LangGraph×SDK統合の実績確認 |
| BV-02 | エージェント評価・モニタリング | Langfuse / Braintrust / W&B Weave（D-003〜D-005） | Agent SDKのhooks機能を使えばカスタムトレーシングも実装可能 | 各評価OSSのClaude Agent SDK対応状況・hooks経由の独自実装コスト比較 |
| BV-03 | Skills実装 | anthropics/skills（F-013）から既存スキル流用 | プロジェクト固有のワークフローはゼロから設計する方が適合度が高い | anthropics/skillsのスキル一覧と品質確認（B-001）・プロジェクト要件との適合度評価 |

---

### 先に試験導入を検討すべき候補

比較評価を待たずに早期から試験導入することで学習コストを前倒しできる候補。

| # | 候補 | item_id | 推奨理由 | 試験導入の形態 |
|---|------|---------|---------|--------------|
| TI-01 | Claude Code Hooks | F-002 | 既にGA機能・設定方法確認済み。本プロジェクトのPreToolUse制御に即座に活用できる | `.claude/settings.json`への簡単なhooks設定から開始 |
| TI-02 | Claude Code Subagents | F-003 | GAで最も成熟している自律エージェント機能。YAML定義から学習開始できる | 単一タスク専門のサブエージェントを1つ定義してみる |
| TI-03 | Claude Agent SDK (Python) | F-010 | Anthropic公式SDK。フェーズ3の実装基盤として早期に慣れておく価値がある | claude-agent-sdk-demosのemail assistantから動作確認 |
| TI-04 | MCP（接続層） | F-015 | MCPは接続層の標準。mcpサーバーを1つ動作させるだけで接続層の実感が得られる | Playwright MCP（D-002）を試験接続 |

---

### 将来 RAG 候補になりうる情報資産

フェーズ5（検索・再利用層）でRAG化することで参謀エージェントの知識基盤になりうる情報資産。

| # | 情報資産 | source_id | RAG化の価値 | 備考 |
|---|---------|-----------|-----------|------|
| RA-01 | Claude Platform Release Notes全履歴 | A-003 | 過去の機能変化の経緯・廃止機能・移行パターンが検索可能になる | 2024後半〜現在の全履歴を対象。定期的に増分追加 |
| RA-02 | Claude Code CHANGELOG全履歴 | A-004 | バグ修正・機能追加の経緯が検索可能になる | GitHubから取得可能 |
| RA-03 | 候補カタログ（02_candidate_catalog.md） | — | 「あの技術はなぜ保留にしたか」「当時の評価根拠」が検索可能になる | フェーズ4以降で価値増大。定期的な更新が前提 |
| RA-04 | MCP仕様全文 | A-006 | MCPサーバー実装時の仕様参照が自然言語で可能になる | modelcontextprotocol.io/llms.txtがインデックス役を果たす（A-018） |
| RA-05 | anthropics/claude-agent-sdk-demos実装集 | B-005 | 公式実装パターンを検索可能にすることで実装時の参照コストを削減 | Pythonコードのembedding化が必要 |

---

### 保留候補と保留理由

現時点では積極的に動かさないが、条件が変わった場合に再評価する候補。

| item_id | 候補名 | 保留理由 | 解消条件 | 再評価優先度 |
|---------|--------|---------|---------|------------|
| F-012 | Claude Managed Agents | 2026-04-08公開betaでありAPI詳細・pricing・制限が未確定。安定性の確認が必要 | GA移行、またはbeta利用で十分な情報が得られた時点 | 高（GA後即評価） |
| F-008 | Agent Teams | experimentalフラグが外れていない。本番利用に不安定要素がある | experimental→betaまたはGAへの昇格 | 中（昇格後評価） |
| F-004 | Advisor Tool | 2026-04-09公開betaでpricingが未公表。長期エージェントタスクのコスト試算ができない | pricing公表・GA移行 | 中（pricing公表後評価） |
| F-023 | lastmile-ai/mcp-eval | 20 starsと活動量が極めて低い。MCPサーバー評価ツールとしての実用性が疑わしい | スター数の増加・コントリビューター増加・アクティブメンテナンスの再開 | 低（状況変化があれば） |
| F-030 | openai/openai-agents-python | 比較参照目的のみ。Claude非ネイティブで採用候補とはならない | — | 不要（比較時参照のみ） |
| E-003 | ant CLI | 2026-04-08リリースだがドキュメントURLが未確認。機能範囲が不明 | ドキュメント発見・機能範囲確認 | 中（ドキュメント発見後） |

---

### フェーズ2で最優先で取り組むべき論点

フェーズ2（判断基盤フェーズ）の着手時に最初に取り組むべき論点の優先順位。

| 優先順位 | 論点 | 理由 | 関連item_id |
|---------|------|------|-------------|
| 1 | Evaluation / Observability基盤の選定 | 評価基盤なしには他の採用判断の品質を担保できない。フェーズ2で最初に確立すべき | D-003, D-004, D-005 |
| 2 | Claude Managed Agents詳細仕様の確認 | betaが解禁されている最新機能。実行基盤の主軸になりうるため、詳細確認が比較評価の前提 | F-012, A-009 |
| 3 | LangGraph × Claude Agent SDK 統合方法の実証 | orchestration候補の最有力。実際に組み合わせて動くかを早期に確認することで後続設計の不確実性を除去 | F-021, F-010 |
| 4 | claude-agent-sdk-demos実装内容の精査 | 公式参照実装。フェーズ3の実装方針確定前に参照実装を把握しておく必要がある | B-005, F-025 |
| 5 | Skills vs Subagents 役割分担の明確化（UQ-02） | 実装設計の根幹となる設計判断。曖昧なまま進むと後の混乱につながる | F-005, F-003, UQ-02 |

---

## パート3｜フェーズ1完了宣言（グループ3）

> **最終更新**: 2026-04-12（グループ3）

### 完了確認チェックリスト

- [x] 追跡対象の情報源がカテゴリ別に固定されている（→01）
- [x] 収集対象の分類軸が定義されている（→03 パート1: F1〜F4の全軸定義完了）
- [x] 候補を状態管理できる構造が定義されている（→03 パート2: 9状態の意味・遷移条件定義完了）
- [x] 各候補に対する最低記録項目が定義されている（→03 パート3: 共通必須16項目 + 追加管理8項目 + 公式5項目 + OSS9項目 定義完了）
- [x] 既知の重要候補が初期調査対象として登録されている（→02: F-001〜F-031 全31候補登録済み）
- [x] Claude Code の自律追加調査ルールが明文化されている（→04 パート6: 6ルール定義完了）
- [x] フェーズ2で比較・評価に進めるだけの情報基盤要件が揃っている（→本ファイル パート2: 比較ペア5組・未解決論点5件・試験導入候補4件・優先論点5件 整備完了）
- [x] 「継続的に増やしていく前提」が要件として明記されている（→04 パート6「既知候補依存の禁止」「GitHub再探索の義務」「保留・未確認の積極的解消ルール」に明記）

---

### フェーズ2着手判断

**判断結果: フェーズ2着手可能**

8項目の完了条件は全て充足している。情報基盤として以下が整備された。

**整備済み資産:**
- 情報源32件（A/B/C/D/Eカテゴリ）
- 候補カタログ31件（F-001〜F-031）
- 分類軸4軸（F1:11種別 / F2:8機能層 / F3:5利用段階 / F4:8作業適用先）
- 状態管理スキーマ（9状態 + 遷移条件）
- 記録スキーマ（共通16 + 追加8 + 公式5 + OSS9 = 38フィールド定義）
- 更新追跡ルール（優先度3段階 + 更新履歴テーブル + 自律調査6ルール）
- フェーズ2向け引き継ぎ（比較ペア5 + 未解決論点5 + 試験導入候補4 + 最優先論点5）

**フェーズ2の着手前に解消しておくべき残課題:**

なし。ただし以下は「保留中」として明示的に管理されており、フェーズ2内で解消を試みる。
- E-003（ant CLI詳細）: ドキュメント未発見
- C-005（evaluation/observability系OSS）: 未探索
- E-001（Claude Cowork詳細API）: 製品ページのみ確認
- E-004（MCP Registry API詳細仕様）: エンドポイントのみ確認
