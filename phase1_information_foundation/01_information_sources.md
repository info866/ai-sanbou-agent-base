# 情報源一覧（Information Sources）

> **担当**: グループ2  
> **最終更新**: 2026-04-12  
> **ステップ対応**: フェーズ1作業指示書 ステップ2

---

## 記入凡例

| フィールド | 説明 |
|-----------|------|
| source_id | 識別子（A-001, B-001... 形式） |
| source_type | 公式docs / 公式GitHub / OSS / その他 |
| authority_level | 一次情報 / 二次情報 |
| update_pattern | 随時 / 定期 / 不定期 / 不明 |

---

## カテゴリA｜公式一次情報

### A-1 Anthropic 公式

| source_id | source_name | source_url | authority_level | update_pattern | notes |
|-----------|-------------|-----------|----------------|----------------|-------|
| A-001 | Claude Code Docs | https://code.claude.com/docs/en/ | 一次情報 | 随時 | 旧 docs.anthropic.com から移行済み（301リダイレクト）。hooks, skills, subagents, agent teams, SDK等を網羅 |
| A-002 | Claude Platform Docs（API）| https://platform.claude.com/docs/en/ | 一次情報 | 随時 | API全般（Messages API, Tool Use, Models等）。旧 console.anthropic.com から2026-01-12移行 |
| A-003 | Claude Platform Release Notes | https://platform.claude.com/docs/en/release-notes/overview | 一次情報 | 随時 | API更新の正本。Claude 4.6モデル、Managed Agents、Advisor Tool等の最新追加が記録されている |
| A-004 | Claude Code CHANGELOG | https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md | 一次情報 | 随時 | Claude Code CLI/アプリの詳細更新履歴。Platform Release Notesに記載なしの細かい更新もある |
| A-005 | Claude Apps Release Notes | https://support.claude.com/en/articles/12138966-release-notes | 一次情報 | 随時 | Claude.ai（一般ユーザー向け）のリリースノート |
| A-006 | MCP 公式ドキュメント | https://modelcontextprotocol.io/introduction | 一次情報 | 随時 | MCPの仕様・設計・実装ガイドの正本。Anthropic主導のオープン標準 |
| A-007 | Agent Skills 公式仕様 | https://agentskills.io/home | 一次情報 | 随時 | Anthropic公開のAgent Skills オープン標準。SKILL.md形式の仕様正本。Microsoft, OpenAI, Atlassian, Figma等が採用済み |
| A-008 | Prompt Improver Docs | https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver | 一次情報 | 随時 | Claude Platform ConsoleのPrompt Improver機能のドキュメント |
| A-009 | Claude Managed Agents Docs | https://platform.claude.com/docs/en/managed-agents/overview | 一次情報 | 随時 | Managed Agents（ホスト型エージェント実行基盤）のAPIドキュメント。2026-04-08 公開ベータ |
| A-010 | Claude Code Sub-agents Docs | https://code.claude.com/docs/en/sub-agents | 一次情報 | 随時 | Claude Codeにおけるsubagentsの設定・運用ガイド |
| A-011 | Claude Code Hooks Docs | https://code.claude.com/docs/en/hooks | 一次情報 | 随時 | Hooksのタイプ（PreToolUse等10種類）、設定方法（command/HTTP/prompt/agent 4種類）の完全リファレンス |
| A-012 | Claude Code Skills Docs | https://code.claude.com/docs/en/skills | 一次情報 | 随時 | Skills（SKILL.md形式）の作成・設定・共有方法の完全ガイド |
| A-013 | Claude Agent SDK Docs | https://code.claude.com/docs/en/agent-sdk/overview | 一次情報 | 随時 | Python/TypeScriptでカスタムエージェントを構築するSDKのドキュメント |
| A-014 | Agent Teams Docs | https://code.claude.com/docs/en/agent-teams | 一次情報 | 随時 | 複数Claude Codeインスタンスの協調実行（実験的機能）のドキュメント |
| A-015 | Advisor Tool Docs | https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool | 一次情報 | 随時 | 2026-04-09追加。executor＋advisorモデルのペアリングによる長期エージェントタスク向け機能（public beta）|

---

### A-2 OpenAI 公式（比較対象、必要範囲に限定）

| source_id | source_name | source_url | authority_level | update_pattern | notes |
|-----------|-------------|-----------|----------------|----------------|-------|
| A-016 | OpenAI Agents SDK Docs | https://openai.github.io/openai-agents-python/ | 一次情報 | 随時 | OpenAI版のエージェントSDK公式ドキュメント。Swarmの後継。比較・差別化判断に必要な範囲で参照 |
| A-017 | OpenAI Platform Docs（Agents） | https://platform.openai.com/docs/agents | 一次情報 | 随時 | OpenAI Agents機能全般。MCP対応有無・tool use形式・比較確認に使用 |

---

### A-3 MCP仕様・その他一次情報

| source_id | source_name | source_url | authority_level | update_pattern | notes |
|-----------|-------------|-----------|----------------|----------------|-------|
| A-018 | MCP仕様 llms.txt | https://modelcontextprotocol.io/llms.txt | 一次情報 | 随時 | MCP全ドキュメントのインデックス。AI向けナビゲーション用 |
| A-019 | Claude Code llms.txt | https://code.claude.com/docs/llms.txt | 一次情報 | 随時 | Claude Code全ドキュメントのインデックス |

---

## カテゴリB｜公式GitHub

### B-1 Anthropic 公式リポジトリ

| source_id | repo | html_url | stars | updated_at | notes |
|-----------|------|---------|-------|-----------|-------|
| B-001 | anthropics/skills | https://github.com/anthropics/skills | 115,361 | 2026-04-12 | Agent Skills公式リポジトリ。公式スキル定義・スキルマーケットプレイス |
| B-002 | anthropics/claude-code-action | https://github.com/anthropics/claude-code-action | 7,010 | 2026-04-12 | GitHub ActionsでClaude Codeを実行するための公式アクション |
| B-003 | anthropics/claude-agent-sdk-python | https://github.com/anthropics/claude-agent-sdk-python | 6,267 | 2026-04-12 | Claude Agent SDK Python実装。旧Claude Code SDK |
| B-004 | anthropics/claude-agent-sdk-typescript | https://github.com/anthropics/claude-agent-sdk-typescript | 1,267 | 2026-04-12 | Claude Agent SDK TypeScript実装 |
| B-005 | anthropics/claude-agent-sdk-demos | https://github.com/anthropics/claude-agent-sdk-demos | 2,150 | 2026-04-12 | Agent SDK実装例（email assistant, research agent等） |

---

### B-2 MCP 公式リポジトリ

| source_id | repo | html_url | stars | updated_at | notes |
|-----------|------|---------|-------|-----------|-------|
| B-006 | modelcontextprotocol/registry | https://github.com/modelcontextprotocol/registry | 6,667 | 2026-04-12 | MCPサーバーのコミュニティ主導レジストリサービス |
| B-007 | modelcontextprotocol/servers | https://github.com/modelcontextprotocol/servers | 83,525 | 2026-04-12 | MCPサーバーの公式実装集（最多スター）。リファレンス実装多数 |

---

### B-3 公式action / sample / skills / registry

| source_id | repo | html_url | notes |
|-----------|------|---------|-------|
| B-008 | MCP Registry API | https://api.anthropic.com/mcp-registry/v0/servers | MCP registryのAPI。Claude Codeが内部で使用するサーバー一覧取得エンドポイント |

---

## カテゴリC｜公開OSS

### C-1 router / gateway 系

| source_id | repo | html_url | stars | updated_at | notes |
|-----------|------|---------|-------|-----------|-------|
| C-001 | musistudio/claude-code-router | https://github.com/musistudio/claude-code-router | 32,009 | 2026-04-12 | Claude Code専用router。異なるモデル・プロバイダーへの振り分けを管理 |
| C-002 | BerriAI/litellm | https://github.com/BerriAI/litellm | 42,989 | 2026-04-12 | 100+ LLM APIへの統一ゲートウェイ。コスト管理・guardrails・loadbalancing付き |

### C-2 MCP agent / MCP library 系

| source_id | repo | html_url | stars | updated_at | notes |
|-----------|------|---------|-------|-----------|-------|
| C-003 | lastmile-ai/mcp-agent | https://github.com/lastmile-ai/mcp-agent | 8,242 | 2026-04-12 | MCPとシンプルなworkflowパターンを使ったエージェント構築フレームワーク |
| C-004 | lastmile-ai/mcp-eval | https://github.com/lastmile-ai/mcp-eval | 20 | 2026-03-22 | MCPサーバー向け評価フレームワーク。活動量が少ない点に注意 |

### C-3 evaluation / observability 系

| source_id | repo / URL | notes |
|-----------|-----------|-------|
| C-005 | 未確認（要追加探索） | 主要OSSのevaluation・observability系はグループ2の追加探索では未発見。Langfuse, Weights&Biases, Braintrust等が候補として存在する可能性あり |

### C-4 orchestration / workflow 系

| source_id | repo | html_url | stars | updated_at | notes |
|-----------|------|---------|-------|-----------|-------|
| C-006 | langchain-ai/langgraph | https://github.com/langchain-ai/langgraph | 28,993 | 2026-04-12 | グラフベースの柔軟なエージェントオーケストレーション。MCP対応（ファースト級サポート）|
| C-007 | crewAIInc/crewAI | https://github.com/crewAIInc/crewAI | 48,644 | 2026-04-12 | ロールベースの協調マルチエージェント。プロトタイプ作成が最速 |
| C-008 | microsoft/autogen | https://github.com/microsoft/autogen | 56,978 | 2026-04-12 | 会話駆動型マルチエージェントフレームワーク。高精度だが高コスト |
| C-009 | openai/openai-agents-python | https://github.com/openai/openai-agents-python | 20,717 | 2026-04-12 | OpenAI版エージェントSDK。旧Swarmの後継。比較・差別化確認に使用 |

### C-5 公開エージェント / 運用例

| source_id | repo | html_url | notes |
|-----------|------|---------|-------|
| C-010 | anthropics/claude-agent-sdk-demos | https://github.com/anthropics/claude-agent-sdk-demos | 公式デモ実装。email assistant, research agent等の参考実装 |

---

## カテゴリD｜将来拡張・追跡候補

> 今回は深掘りしていないが、追跡候補として登録する領域

| source_id | 候補名 | 種別 | 補足 |
|-----------|-------|------|------|
| D-001 | AWS Strands Agents | OSS orchestration | AWSが公開したエージェントフレームワーク。2026時点での活動状況は未確認 |
| D-002 | Microsoft Playwright MCP | MCP server | ブラウザ自動化MCP。Agent SDKドキュメントに事例として登場 |
| D-003 | Langfuse | evaluation/observability | LLMオブザーバビリティOSS。評価系の追加探索で要確認 |
| D-004 | Braintrust | evaluation | LLM eval基盤。要確認 |
| D-005 | Weights & Biases（Weave） | observability | ML実験管理。エージェント評価への応用事例あり。要確認 |
| D-006 | kyegomez/swarms | orchestration | Enterprise-grade multi-agent。Claude Code系との接続性未確認 |

---

## 未確認・保留の情報源

| source_id | 候補名 | 理由 |
|-----------|-------|------|
| E-001 | Claude Cowork詳細API/仕様 | 製品ページ（anthropic.com/product/claude-cowork）は確認済みだが、APIドキュメントの有無・アクセス方法が未確認 |
| E-002 | Managed Agents詳細設定（コンテナ設定等） | APIリファレンスのURL取得済み（A-009）だが内部仕様は未確認 |
| E-003 | ant CLI詳細 | 2026-04-08にリリースされたClaude API用CLIツール。ドキュメントURL未確認 |
| E-004 | MCP Registry API詳細仕様 | エンドポイントは確認（B-008）。認証方法・フィルタリング方法等は未確認 |
