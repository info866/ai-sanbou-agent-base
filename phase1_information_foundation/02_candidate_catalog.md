# 候補カタログ（Candidate Catalog）

> **担当**: グループ2  
> **最終更新**: 2026-04-12  
> **ステップ対応**: フェーズ1作業指示書 ステップ3（初期既知候補の登録）＋ ステップ4（追加探索）

---

## 記入凡例

各候補は以下フィールドで記録する。

```
- item_id: 識別子（F-001形式）
- item_name: 正式名称
- item_type: 公式機能 / 公式実装 / OSS / 公開エージェント
- layer_category: 機能層（フェーズ1要件定義書の語彙のみ使用。不明は「要グループ3確定」）
- vendor_owner: 提供元
- source_url: 一次情報URL
- summary: 1〜3行の概要
- primary_use_cases: 何に効くか
- prerequisites: 導入前提
- current_status: 未確認 / 調査中 / 候補 / 比較待ち / 保留 / 監視継続
- first_seen_at: 初回確認日
- last_checked_at: 最終確認日
- notes: 補足・注意点
```

**current_status ルール**: フェーズ1では採用確定・不採用確定をしない。「採用候補」「不採用候補」には昇格させない。

---

## セクション1｜既知初期候補（登録必須）

### 1-1 公式機能層

---

#### F-001 | Prompt Improver

- **item_id**: F-001
- **item_name**: Prompt Improver
- **item_type**: 公式機能
- **layer_category**: 推論・改善補助層
- **vendor_owner**: Anthropic
- **source_url**: https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/prompt-improver
- **summary**: Anthropic Platform Console上のツール。既存プロンプトをClaude自身が自動分析・改善する機能。chain-of-thought追加やクリア化が可能。
- **primary_use_cases**: プロンプト品質向上、Chain-of-Thought自動追加、prompt engineering支援
- **prerequisites**: Anthropic Consoleアカウント
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: Claude Code本体の機能ではなくPlatform Console機能。全Claudeモデル・extended thinking対応。

---

#### F-002 | MCP（Model Context Protocol）

- **item_id**: F-002
- **item_name**: MCP（Model Context Protocol）
- **item_type**: 公式機能（オープン標準）
- **layer_category**: 接続層
- **vendor_owner**: Anthropic（オープン標準）
- **source_url**: https://modelcontextprotocol.io/introduction
- **summary**: AIアプリケーションと外部システム（DB、ファイル、API、ブラウザ等）を接続するオープン標準プロトコル。USB-Cのようなポート。
- **primary_use_cases**: 外部データソース接続、ツール拡張、ワークフロー統合、Claude Codeへのカスタムツール追加
- **prerequisites**: MCP対応クライアント（Claude Code, VS Code, Cursor等）
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: Claude, ChatGPT, VS Code, Cursor等が対応済みの業界標準。MCP Connector（Messages API直接接続）もGA（2025-02）。claude_desktop_config.jsonまたはsettings.jsonで設定。

---

#### F-003 | Subagents（Claude Code）

- **item_id**: F-003
- **item_name**: Subagents
- **item_type**: 公式機能
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://code.claude.com/docs/en/sub-agents
- **summary**: Claude Code内で特定タスクを担う専門化されたAIアシスタント。独自のコンテキストウィンドウ・ツール・権限を持つ。メインコンテキストを守るために別コンテキストで作業して結果だけを返す。
- **primary_use_cases**: 検索結果やログ等の大量データ処理、並列タスク実行、専門化されたコードレビュー・分析
- **prerequisites**: Claude Code
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: .claude/agents/*.md でカスタム定義可能。Agent Teamsとの使い分け: Subagentsはメイン→サブの一方向通信、Agent Teamsはサブ同士でも直接通信。SDKのAgentDefinitionクラスでも定義可能。

---

#### F-004 | Hooks（Claude Code）

- **item_id**: F-004
- **item_name**: Hooks
- **item_type**: 公式機能
- **layer_category**: 運用管理層
- **vendor_owner**: Anthropic
- **source_url**: https://code.claude.com/docs/en/hooks
- **summary**: Claude Codeのライフサイクル上の特定ポイントで自動実行されるユーザー定義シェルコマンド・HTTP・LLMプロンプト。ツール実行前後の検証・制御・ログ取り・自動承認に使用。
- **primary_use_cases**: 危険コマンドのブロック、実行後のlinting/テスト自動実行、権限の自動承認、セッション開始時のコンテキスト注入、監査ログ
- **prerequisites**: Claude Code。設定はsettings.json（グローバル/プロジェクト/ローカル）またはSKILL.md/agent frontmatter
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: hookイベントは10種類（SessionStart, UserPromptSubmit, PreToolUse, PermissionRequest, PostToolUse, PostToolUseFailure, Stop, SessionEnd, FileChanged, Notification）。hook実装タイプは4種類（command/HTTP/prompt/agent）。exit 2でブロッキングエラー。

---

#### F-005 | Skills（Claude Code / Agent Skills）

- **item_id**: F-005
- **item_name**: Skills / Agent Skills
- **item_type**: 公式機能（オープン標準）
- **layer_category**: 要グループ3確定
- **vendor_owner**: Anthropic（オープン標準）
- **source_url**: https://code.claude.com/docs/en/skills
- **summary**: SKILL.mdファイルで定義するClaude Code拡張機能。チームのノウハウ・ワークフローをパッケージ化して/skill-nameで呼び出せる再利用可能なモジュール。agentskills.ioのオープン標準に準拠。
- **primary_use_cases**: 繰り返しワークフローのパッケージ化、チーム間での知識共有、デプロイ・コミット等の定型手順自動化、カスタムコマンド作成
- **prerequisites**: Claude Code。スキルディレクトリ構造（~/.claude/skills/ または .claude/skills/）
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: SKILL.md + YAMLフロントマター構成。context: fork でsubagentとして実行可能。disable-model-invocation: trueで手動専用化。Microsoft, OpenAI, Atlassian, Figma等がopenstandard採用済み。既存.claude/commands/との後方互換あり。anthropics/skillsがマーケットプレイス（115k stars）。

---

#### F-006 | Claude Managed Agents

- **item_id**: F-006
- **item_name**: Claude Managed Agents
- **item_type**: 公式機能
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://platform.claude.com/docs/en/managed-agents/overview
- **summary**: AnthropicホストのフルマネージドエージェントHarness。セキュアサンドボックス・組み込みツール・SSEストリーミング付きで長期エージェントタスクを実行。2026-04-08公開ベータ開始。
- **primary_use_cases**: 長期自律タスク、セキュアな本番エージェント実行、API経由でのエージェント管理
- **prerequisites**: Anthropic APIキー。betaヘッダー`managed-agents-2026-04-01`が必要
- **current_status**: 監視継続
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 2026-04-08にpublic betaリリース。/v1/agents, /v1/sessions等のエンドポイントを提供。管理型subagentsはmanaged settingsディレクトリの.claude/agents/に配置されたmarkdownファイル。

---

#### F-007 | Claude Cowork

- **item_id**: F-007
- **item_name**: Claude Cowork
- **item_type**: 公式機能（製品）
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://www.anthropic.com/product/claude-cowork
- **summary**: ナレッジワーカー向けAIアシスタント製品。目標を与えるとClaude自身がコンピュータ・ローカルファイル・アプリケーション上で作業し、完成物を返す。研究者・アナリスト・法律・財務チーム向け。
- **primary_use_cases**: ドキュメント処理、データ分析、ファイル操作を伴う長期タスク、ナレッジ業務の自動化
- **prerequisites**: Cowork契約（詳細未確認）
- **current_status**: 監視継続
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: API仕様・提供形態の詳細未確認（E-001）。製品ページは確認済み。一般開発者向けAPIとの関係は要確認。

---

#### F-008 | Agent Teams（実験的機能）

- **item_id**: F-008
- **item_name**: Agent Teams
- **item_type**: 公式機能（実験的）
- **layer_category**: 監督層
- **vendor_owner**: Anthropic
- **source_url**: https://code.claude.com/docs/en/agent-teams
- **summary**: 複数のClaude Codeインスタンスをチームとして協調実行する機能。1つがリードとなりタスクを分配。メンバー間で直接メッセージ送受信が可能（subagentsとの大きな違い）。
- **primary_use_cases**: 大規模コードレビュー（並列）、競合仮説による原因調査、フロントエンド・バックエンド・テストの並列開発
- **prerequisites**: Claude Code v2.1.32以上。環境変数 CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS=1 が必要
- **current_status**: 監視継続
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 実験的・デフォルト無効。セッション再開時のteammate復元不可等の制限あり。トークンコストがsubagentsより大幅に高い。subagents→agent teamsへの段階的採用が現実的。

---

#### F-009 | Claude Agent SDK

- **item_id**: F-009
- **item_name**: Claude Agent SDK
- **item_type**: 公式機能（SDK）
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://code.claude.com/docs/en/agent-sdk/overview
- **summary**: Claude Codeのツール・エージェントループ・コンテキスト管理をPythonおよびTypeScriptのライブラリとして提供するSDK。カスタムエージェント・パイプラインの構築に使用。旧Claude Code SDK。
- **primary_use_cases**: CI/CDパイプラインへのエージェント組み込み、カスタムアプリケーション構築、本番エージェント自動化、subagents・hooks・MCP・sessionsの完全制御
- **prerequisites**: ANTHROPIC_API_KEY。pip install claude-agent-sdk / npm install @anthropic-ai/claude-agent-sdk
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: Python (claude-agent-sdk) / TypeScript (@anthropic-ai/claude-agent-sdk) の2言語対応。インタラクティブ開発はCLI、本番・CI/CDはSDKの使い分けを推奨。AWS Bedrock, Google Vertex AI, Microsoft Azure対応。

---

#### F-010 | GitHub Actions for Claude Code

- **item_id**: F-010
- **item_name**: GitHub Actions for Claude Code
- **item_type**: 公式機能
- **layer_category**: 運用管理層
- **vendor_owner**: Anthropic
- **source_url**: https://code.claude.com/docs/en/github-actions
- **summary**: GitHub ActionsワークフローからClaude Codeを実行する統合機能。PRレビュー・issue対応・CI自動化に使用。anthropics/claude-code-actionを内部利用。
- **primary_use_cases**: 自動PRレビュー、issueのトリアージ、CIでのセキュリティチェック、自動コード翻訳
- **prerequisites**: GitHub Actions、Claude APIキー
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: GitLab CI/CD対応もあり（code.claude.com/docs/en/gitlab-ci-cd）。Code Review（自動PR review）機能も別途存在（code.claude.com/docs/en/code-review）。

---

#### F-011 | Cloud Scheduled Tasks

- **item_id**: F-011
- **item_name**: Cloud Scheduled Tasks
- **item_type**: 公式機能
- **layer_category**: 運用管理層
- **vendor_owner**: Anthropic
- **source_url**: https://code.claude.com/docs/en/web-scheduled-tasks
- **summary**: Anthropic管理インフラ上でClaude Codeタスクをcronスケジュール実行する機能。ローカルPCを起動していなくても動作。朝のPRレビュー・定期依存関係監査等に使用。
- **primary_use_cases**: 定期自動タスク（PR review, CI failure分析, 依存関係監査）、継続監視
- **prerequisites**: Claude Code subscriptionまたはAPI
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: Cloud版（Anthropicインフラ）とDesktop版（ローカル実行）の2種類あり。/scheduleコマンドまたはDesktop appから作成可能。

---

#### F-012 | Advisor Tool

- **item_id**: F-012
- **item_name**: Advisor Tool
- **item_type**: 公式機能（追加探索発見）
- **layer_category**: 推論・改善補助層
- **vendor_owner**: Anthropic
- **source_url**: https://platform.claude.com/docs/en/agents-and-tools/tool-use/advisor-tool
- **summary**: 2026-04-09公開ベータ。高速executorモデルと高知能advisorモデルをペアリングする機能。長期エージェントタスクをadvisor-soloに近い品質でexecutorレートで実行可能。
- **primary_use_cases**: 長期エージェントタスクのコスト削減、品質維持しながらの高速化
- **prerequisites**: betaヘッダー`advisor-tool-2026-03-01`が必要
- **current_status**: 監視継続
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 2026-04-09追加の最新機能（公開ベータ）。本プロジェクトの参謀エージェント構成に直結する可能性がある。グループ3での評価推奨。

---

### 1-2 公式実装資産層

---

#### F-013 | anthropics/skills

- **item_id**: F-013
- **item_name**: anthropics/skills（Skillsマーケットプレイス）
- **item_type**: 公式実装
- **layer_category**: 要グループ3確定
- **vendor_owner**: Anthropic
- **source_url**: https://github.com/anthropics/skills
- **summary**: Agent Skillsの公式リポジトリ。115k starsを持つ最大規模の公式実装。スキルマーケットプレイスとして機能。
- **primary_use_cases**: 公式スキルの取得・利用、チーム向けスキル配布のリファレンス
- **prerequisites**: Claude Code
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 115,361 stars（公式Anthropicリポジトリ中最多）。topics: ["agent-skills"]。スキル開発のリファレンスとして最優先確認対象。

---

#### F-014 | anthropics/claude-code-action

- **item_id**: F-014
- **item_name**: anthropics/claude-code-action
- **item_type**: 公式実装
- **layer_category**: 運用管理層
- **vendor_owner**: Anthropic
- **source_url**: https://github.com/anthropics/claude-code-action
- **summary**: GitHub ActionsでClaude Codeを実行するためのAnthropicが提供するGitHub Action。PRレビュー・issue対応の自動化に使用。
- **primary_use_cases**: GitHub CI/CDへのClaude Code組み込み、PRの自動レビュー
- **prerequisites**: GitHub Actions、ANTHROPIC_API_KEY
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 7,010 stars。F-010（GitHub Actions機能）の実装実体。

---

#### F-015 | anthropics/claude-agent-sdk-python

- **item_id**: F-015
- **item_name**: claude-agent-sdk（Python）
- **item_type**: 公式実装
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://github.com/anthropics/claude-agent-sdk-python
- **summary**: Claude Agent SDK Python実装。pip install claude-agent-sdk でインストール。非同期インターフェース（asyncio）対応。
- **primary_use_cases**: PythonでのカスタムエージェントおよびCI/CDパイプライン構築
- **prerequisites**: Python、ANTHROPIC_API_KEY
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 6,267 stars。F-009（Agent SDK）のPython実装。CHANGELOGあり。

---

#### F-016 | anthropics/claude-agent-sdk-typescript

- **item_id**: F-016
- **item_name**: claude-agent-sdk（TypeScript）
- **item_type**: 公式実装
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://github.com/anthropics/claude-agent-sdk-typescript
- **summary**: Claude Agent SDK TypeScript実装。npm install @anthropic-ai/claude-agent-sdk でインストール。
- **primary_use_cases**: TypeScript/Node.jsでのカスタムエージェント構築
- **prerequisites**: Node.js、ANTHROPIC_API_KEY
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 1,267 stars（Python版より少ない）。CHANGELOGあり。

---

#### F-017 | anthropics/claude-agent-sdk-demos

- **item_id**: F-017
- **item_name**: claude-agent-sdk-demos
- **item_type**: 公式実装（サンプル）
- **layer_category**: 実行層
- **vendor_owner**: Anthropic
- **source_url**: https://github.com/anthropics/claude-agent-sdk-demos
- **summary**: Claude Agent SDKの実装例集。email assistant, research agent等の参考実装を含む。
- **primary_use_cases**: Agent SDK実装のリファレンス、パターン学習
- **prerequisites**: Python or TypeScript、ANTHROPIC_API_KEY
- **current_status**: 調査中
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 2,150 stars。具体的な実装例一覧は未確認（要グループ3深掘り）。

---

#### F-018 | modelcontextprotocol/registry

- **item_id**: F-018
- **item_name**: MCP Registry（コミュニティレジストリ）
- **item_type**: 公式実装
- **layer_category**: 接続層
- **vendor_owner**: modelcontextprotocol（Anthropicリード）
- **source_url**: https://github.com/modelcontextprotocol/registry
- **summary**: MCPサーバーのコミュニティ主導レジストリサービス。API: https://api.anthropic.com/mcp-registry/v0/servers でサーバー一覧を取得可能。Claude Codeが内部参照している。
- **primary_use_cases**: 利用可能なMCPサーバーの発見・管理、MCP server選定の比較
- **prerequisites**: なし（公開API）
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 6,667 stars。API経由でサーバー一覧取得が可能（visibility=commercial, limit=100等のフィルタ対応）。

---

#### F-019 | modelcontextprotocol/servers

- **item_id**: F-019
- **item_name**: MCP Servers（公式リファレンス実装集）
- **item_type**: 公式実装
- **layer_category**: 接続層
- **vendor_owner**: modelcontextprotocol（Anthropicリード）
- **source_url**: https://github.com/modelcontextprotocol/servers
- **summary**: MCPサーバーの公式リファレンス実装集。各種ツール・データソース・サービスへのMCP接続サンプルを多数収録。
- **primary_use_cases**: MCPサーバー実装のリファレンス、既存サーバーの流用・改変
- **prerequisites**: MCPサーバーの実行環境
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 83,525 stars（公式MCPリポジトリ中最多）。最も参照頻度の高い公式実装集。

---

### 1-3 OSS / 基盤候補層（既知）

---

#### F-020 | musistudio/claude-code-router

- **item_id**: F-020
- **item_name**: claude-code-router
- **item_type**: OSS
- **layer_category**: 接続層
- **vendor_owner**: musistudio（OSS）
- **source_url**: https://github.com/musistudio/claude-code-router
- **summary**: Claude Codeをcoding infrastructure基盤として利用するためのrouter。モデルとのインタラクション方法をユーザーが決定し、Anthropicからの更新を享受できる構造。
- **primary_use_cases**: Claude Codeへのモデルルーティング、複数プロバイダーへの切替、コスト最適化
- **prerequisites**: Claude Code
- **current_status**: 比較待ち
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 32,009 stars（非常に高い）。Claude Code特化のrouter。汎用LLM gatewayのlitellm（F-022）と役割が類似。比較対象: F-022（litellm）。

---

#### F-021 | lastmile-ai/mcp-agent

- **item_id**: F-021
- **item_name**: mcp-agent
- **item_type**: OSS
- **layer_category**: 実行層
- **vendor_owner**: LastMile AI
- **source_url**: https://github.com/lastmile-ai/mcp-agent
- **summary**: MCPとシンプルなワークフローパターンを使ってeffectiveなエージェントを構築するフレームワーク。
- **primary_use_cases**: MCPベースのエージェント構築、workflowパターンの実装
- **prerequisites**: MCPサポート環境
- **current_status**: 比較待ち
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 8,242 stars。MCP-native agent framework。比較対象: langgraph（F-023）, crewAI（F-024）, autogen（F-025）、Claude Agent SDK（F-009）。

---

#### F-022 | BerriAI/litellm

- **item_id**: F-022
- **item_name**: LiteLLM
- **item_type**: OSS
- **layer_category**: 接続層
- **vendor_owner**: BerriAI
- **source_url**: https://github.com/BerriAI/litellm
- **summary**: 100+ LLM APIへのOpenAI互換統一インターフェース提供のSDK兼プロキシサーバー。コスト管理・guardrails・loadbalancing・logging付き。Bedrock, Azure, OpenAI, Vertex AI, Anthropic等に対応。
- **primary_use_cases**: LLMゲートウェイ、コスト管理、fallback設定、複数モデルの統一管理
- **prerequisites**: Python pip install litellm
- **current_status**: 比較待ち
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 42,989 stars。汎用LLM gateway（Claude Code特化ではない）。比較対象: claude-code-router（F-020）（役割は類似だがスコープが異なる）。

---

#### F-023 | lastmile-ai/mcp-eval

- **item_id**: F-023
- **item_name**: mcp-eval
- **item_type**: OSS
- **layer_category**: 評価層
- **vendor_owner**: LastMile AI
- **source_url**: https://github.com/lastmile-ai/mcp-eval
- **summary**: mcp-agentをベースにしたMCPサーバー向け軽量評価フレームワーク。
- **primary_use_cases**: MCPサーバーの性能評価・テスト
- **prerequisites**: lastmile-ai/mcp-agent（F-021）
- **current_status**: 保留
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: **starsがわずか20（2026-04-12時点）**。最終更新2026-03-22。活動量が非常に低い。評価層での使用には別の選択肢を先に探索することを推奨。保留理由：活動低迷。再検討条件：stars増加または主要MCPでの実績が確認できた場合。

---

## セクション2｜追加探索候補（グループ2が探索して追加）

### 公式追加探索で見つかった候補

---

#### F-024 | ant CLI

- **item_id**: F-024
- **item_name**: ant CLI
- **item_type**: 公式機能（追加探索発見）
- **layer_category**: 運用管理層
- **vendor_owner**: Anthropic
- **source_url**: 未確認（E-003）
- **summary**: 2026-04-08リリースのClaude API用CLI。Claude Code native統合・APIリソースのYAMLバージョン管理に対応。
- **primary_use_cases**: Claude APIの高速インタラクション、APIリソースのIaC管理
- **prerequisites**: Claude APIアクセス
- **current_status**: 調査中
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: リリースノートに記載確認済みだが詳細ドキュメントURL未確認。grp3での深掘り推奨。

---

#### F-025 | Memory Tool

- **item_id**: F-025
- **item_name**: Memory Tool（API）
- **item_type**: 公式機能（追加探索発見）
- **layer_category**: 検索・活用層
- **vendor_owner**: Anthropic
- **source_url**: https://platform.claude.com/docs/en/agents-and-tools/tool-use/memory-tool
- **summary**: 会話をまたいで情報を保存・参照するツール。2025-09 公開ベータ→2025-11 GAリリース。
- **primary_use_cases**: クロスセッション記憶、エージェント状態の永続化
- **prerequisites**: Claude API（betaヘッダー不要、GA済み）
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: GAになっているため即利用可能。CLAUDE.md/auto memoryとの使い分け要確認。

---

#### F-026 | MCP Connector（Messages API）

- **item_id**: F-026
- **item_name**: MCP Connector
- **item_type**: 公式機能（追加探索発見）
- **layer_category**: 接続層
- **vendor_owner**: Anthropic
- **source_url**: https://platform.claude.com/docs/en/agents-and-tools/mcp-connector
- **summary**: Messages APIから直接リモートMCPサーバーに接続する機能。2025-05 公開ベータ→2025-02 GA。Claude Codeの設定ファイル方式とは別にAPI側からMCPを利用できる。
- **primary_use_cases**: API経由でのMCPサーバー利用、サーバーサイドMCP接続
- **prerequisites**: Claude API（betaヘッダー不要、GA済み）
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: F-002（MCP一般）とは別に、APIレイヤーからMCPを使う具体的な機能として記録。GA済み。

---

### GitHub追加探索で見つかった候補

---

#### F-027 | langchain-ai/langgraph

- **item_id**: F-027
- **item_name**: LangGraph
- **item_type**: OSS
- **layer_category**: 実行層
- **vendor_owner**: LangChain AI
- **source_url**: https://github.com/langchain-ai/langgraph
- **summary**: グラフ（DAG）ベースのエージェントオーケストレーションフレームワーク。ノードとエッジで複雑なエージェントワークフローを定義。ステートフル・分岐・ループ処理に優れる。MCP対応（ファースト級）。
- **primary_use_cases**: 複雑な状態管理を伴うエージェント、分岐ロジック、長期ワークフロー
- **prerequisites**: Python
- **current_status**: 比較待ち
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 28,993 stars。MCP統合深度が高い（ツールがグラフノード化、full streaming対応）。比較対象: crewAI（F-028）, autogen（F-029）, mcp-agent（F-021）, Claude Agent SDK（F-009）。production controlに最適。

---

#### F-028 | crewAIInc/crewAI

- **item_id**: F-028
- **item_name**: CrewAI
- **item_type**: OSS
- **layer_category**: 実行層
- **vendor_owner**: CrewAI Inc
- **source_url**: https://github.com/crewAIInc/crewAI
- **summary**: ロールベースの協調マルチエージェントフレームワーク。各エージェントに役割・目標を割り当て、タスクを協調実行。プロトタイプ作成速度が最速のフレームワーク。
- **primary_use_cases**: ロール明確なチーム型エージェント、プロトタイプ開発、明確なタスク委任ワークフロー
- **prerequisites**: Python
- **current_status**: 比較待ち
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 48,644 stars。20行以下でエージェント定義可能。5エージェント超から調整オーバーヘッドが増大。比較対象: langgraph（F-027）, autogen（F-029）。

---

#### F-029 | microsoft/autogen

- **item_id**: F-029
- **item_name**: AutoGen
- **item_type**: OSS
- **layer_category**: 実行層
- **vendor_owner**: Microsoft
- **source_url**: https://github.com/microsoft/autogen
- **summary**: 会話駆動型マルチエージェントプログラミングフレームワーク。エージェントが自然言語で相互議論しながらタスクを進める。推論精度は高いが、LLMコール数が多くコスト高。
- **primary_use_cases**: 会話型協調推論、競合仮説による原因調査、動的ロールプレイ型エージェント
- **prerequisites**: Python
- **current_status**: 比較待ち
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 56,978 stars。1タスクに20+のLLMコールが発生することがありlanggraphの5-6倍コスト高。比較対象: langgraph（F-027）, crewAI（F-028）。

---

#### F-030 | openai/openai-agents-python

- **item_id**: F-030
- **item_name**: OpenAI Agents SDK（Python）
- **item_type**: OSS（OpenAI公式）
- **layer_category**: 実行層
- **vendor_owner**: OpenAI
- **source_url**: https://github.com/openai/openai-agents-python
- **summary**: OpenAIの公式マルチエージェントSDK。旧Swarmフレームワークの後継（production-ready化）。handoffs, guardrails, tracing, sessions等を提供。Anthropic Agent SDKとの比較対象として重要。
- **primary_use_cases**: OpenAIモデルを使ったエージェント構築（Anthropicとの比較確認用）
- **prerequisites**: Python、OpenAI APIキー
- **current_status**: 監視継続
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: 20,717 stars。Claude Agent SDK（F-009）との設計比較に使用。採用ではなく差別化・比較判断用。

---

### 公開エージェント追加探索で見つかった候補

---

#### F-031 | agentskills.io（オープン標準仕様）

- **item_id**: F-031
- **item_name**: Agent Skills Open Standard
- **item_type**: OSS（仕様・標準）
- **layer_category**: 要グループ3確定
- **vendor_owner**: Anthropic（オープン標準として公開）
- **source_url**: https://agentskills.io/home
- **summary**: Anthropicが2025-12-18に公開したAgent Skillsのオープン標準仕様。SKILL.md形式をどのAIプラットフォームでも採用可能にするための標準化文書。
- **primary_use_cases**: クロスプラットフォームなスキル定義の標準化、スキルの相互運用性確保
- **prerequisites**: なし（オープン標準）
- **current_status**: 候補
- **first_seen_at**: 2026-04-12
- **last_checked_at**: 2026-04-12
- **notes**: Microsoft, OpenAI, Atlassian, Figma, Cursor, GitHubが採用済み。Canva, Stripe, Notion, Zapierがパートナースキルを提供。F-005（Skills機能）とF-013（公式スキルリポジトリ）の標準化基盤。

---

## セクション3｜比較対象メモ

> 同じ役割を持つ候補同士の比較観点メモ。採用判断はフェーズ2で行う。

### 比較グループ1：router / gateway 系

| 候補 | 特徴 | 比較軸 |
|------|------|--------|
| F-020 claude-code-router | Claude Code特化。32k stars | スコープ・Claude Codeとの統合深度 |
| F-022 litellm | 汎用100+ LLM対応。43k stars | 汎用性・コスト管理機能 |

→ Claude Code専用か、LLM全般の統一管理か、で用途が分かれる。排他的でなく併用も可能。

### 比較グループ2：agent orchestration 系 OSS

| 候補 | 特徴 | 星 | 比較軸 |
|------|------|----|--------|
| F-021 mcp-agent | MCP-native, シンプル | 8.2k | MCP特化度 |
| F-027 langgraph | グラフベース, MCP深度高 | 29k | 複雑ワークフロー対応度 |
| F-028 crewAI | ロールベース, 開発速度最速 | 49k | 学習コスト・開発速度 |
| F-029 autogen | 会話駆動, 推論精度最高 | 57k | コスト vs 精度 |
| F-009 Claude Agent SDK | Claude Code公式, built-in tools | 6k | Anthropicネイティブ度 |
| F-030 openai-agents-python | OpenAI公式 | 21k | 比較のみ（採用対象外） |

→ 本プロジェクトの目的（AI参謀基盤）に最も近いのはどれか、フェーズ2で評価。

### 比較グループ3：subagents vs agent teams

| 候補 | 特徴 | 比較軸 |
|------|------|--------|
| F-003 subagents | 安定・低コスト・メインエージェント→サブ一方向通信 | 安定性・コスト |
| F-008 agent teams | 実験的・高コスト・サブ同士直接通信 | 協調性・成熟度 |

→ 実験的なagent teamsへの移行は安定後で検討。当面はsubagentsが現実的。

---

## 除外・保留メモ

| item_id | 候補名 | 状態 | 理由 |
|---------|-------|------|------|
| F-023 | mcp-eval | 保留 | stars=20、最終更新2026-03-22。活動低迷。代替evaluation基盤（D-003〜D-005）を先に探索すること |
| F-008 | Agent Teams | 監視継続 | 実験的機能。制限多数（セッション再開不可等）。成熟を待って再評価 |
| F-012 | Advisor Tool | 監視継続 | 2026-04-09公開ベータ。潜在的に重要だが成熟度が不明。public betaのため採用判断は時期尚早 |
| F-030 | OpenAI Agents SDK | 監視継続 | Anthropicエコシステムの主採用対象ではないが、設計比較・差別化確認のため継続監視 |
| F-007 | Cowork | 監視継続 | 製品ページ確認済みだがAPI詳細未確認。開発者向けAPIの有無・アクセス方法を確認してから判断 |
