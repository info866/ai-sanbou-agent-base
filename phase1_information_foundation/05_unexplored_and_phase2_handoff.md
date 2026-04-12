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

## パート2｜フェーズ2への引き継ぎ内容（グループ3が完成させる）

### 比較評価が必要な候補ペア

<!-- グループ3が記入 -->

### 評価が必要な未解決論点

<!-- グループ3が記入 -->

### 自作 vs 流用で比較が必要な対象

<!-- グループ3が記入 -->

### 先に試験導入を検討すべき候補

<!-- グループ3が記入 -->

### 将来 RAG 候補になりうる情報資産

<!-- グループ3が記入 -->

### 保留候補と保留理由

<!-- グループ3が記入 -->

### フェーズ2で最優先で取り組むべき論点

<!-- グループ3が記入 -->

---

## パート3｜フェーズ1完了宣言（グループ3が記入）

### 完了確認チェックリスト

- [x] 追跡対象の情報源がカテゴリ別に固定されている（→01）
- [ ] 収集対象の分類軸が定義されている（→03）
- [ ] 候補を状態管理できる構造が定義されている（→03）
- [ ] 各候補に対する最低記録項目が定義されている（→03）
- [x] 既知の重要候補が初期調査対象として登録されている（→02）
- [ ] Claude Code の自律追加調査ルールが明文化されている（→04）
- [ ] フェーズ2で比較・評価に進めるだけの情報基盤要件が揃っている（→本ファイル）
- [ ] 「継続的に増やしていく前提」が要件として明記されている（→04）

### フェーズ2着手判断

<!-- グループ3が記入 -->
