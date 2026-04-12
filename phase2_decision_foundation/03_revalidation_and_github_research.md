# 公式再確認・GitHub追加探索・支援部品評価（Revalidation & GitHub Research）

> **担当**: グループ2  
> **インプット**: `00`, `01`, `02` を読み込んでから着手  
> **ステップ対応**: フェーズ2作業指示書 ステップ4（公式一次情報再確認）＋ ステ���プ5（GitHub追加探索）＋ ステップ6（フェーズ2支��部品評価）  
> **最終更新**: 2026-04-12（グループ2）

---

## パート1｜公式一次情報の再確認

### 1-1 Anthropic公式機能の再確認

#### Prompt Improver（F-001）

- **正式名称**: Prompt improver（Console Workbench内の「Prompting tools」の一部）
- **現在の位置づけ**: GA。Prompt generator、Prompt templates and variablesと並ぶConsoleツール
- **主用途**: 既存プロンプトの自動分析・改善。4ステップ（例識別→初稿→CoT追加→例拡充）
- **制約**: 複雑な推論タスクに最適化。生成結果は長い応答を出す傾向があり、レイテンシ重視の用途には不向き
- **フェーズ3以降接続性**: プロンプト最適化ツールとしてフェーズ5で参謀エージェントのプロンプト改善に利用可能
- **フェーズ1記録の補正要否**: 不要。Phase 1記録は正確。URLがdocs.anthropic.comからplatform.claude.comへリダイレクトされる点のみ補足

#### MCP（F-002）

- **正式名称**: Model Context Protocol (MCP)
- **現在の位置づけ**: GA。オープンソース標準
- **主用途**: AIアプリケーションと外部システムの接続（USB-Cアナロジー確認）
- **制約**: 特になし。幅広いクライアント対応済み（ChatGPT, VS Code, Cursor, MCPJam等）
- **新情報**: MCP Appsが第3のカテゴリとして追加された（servers/clientsに加え、AIクライアント内で動作するインタラクティブアプリ）
- **フェーズ1記録の補正要否**: 軽微。MCP Appsカテゴリの存在を補足として追記推奨

#### Subagents（F-003）

- **正式名称**: Custom subagents（Claude Code機能）
- **現在の位置づけ**: GA
- **主用途**: 専門化されたタスク委譲。独立コンテキスト・ツール・権限で作業
- **制約**: subagentsは他のsubagentsを起動できない（ネスト禁止）
- **重要な補正事項（Phase 1の記録が大幅に不足）**:
  - **フロントマター16フィールド**: name, description, tools, disallowedTools, model, permissionMode, maxTurns, skills, mcpServers, hooks, memory, background, effort, isolation, color, initialPrompt
  - **ビルトインsubagents**: Explore（Haiku, 読取専用）、Plan（継承モデル, 読取専用）、general-purpose（全ツール）、statusline-setup、Claude Code Guide
  - **定義方法3種**: ファイル（.claude/agents/*.md）、CLI（--agents JSONフラグ）、マネージド（組織設定）
  - **パーミッションモード**: default, acceptEdits, auto, dontAsk, bypassPermissions, plan
  - **Git worktree分離**: `isolation: worktree`でリポジトリの独立コピーで作業可能
  - **永続メモリ**: user/project/localスコープ
- **フェーズ1記録の補正要否**: **要補正（重要）**。Phase 1は最小限の記載のみ。16フロントマターフィールド、ビルトインエージェント、3つの定義方法、権限モード、worktree分離を補足すべき

#### Hooks（F-004）

- **正��名称**: Hooks
- **現在の位置づけ**: GA
- **主用途**: Claude Codeライフサイクル上の特定ポイントで自動実行されるアクション
- **重大補正事項（Phase 1の記録に重大な誤り）**:
  - **イベント数**: Phase 1は「10種類」と記録 → **実際は24種類以上**
  - **確認済みイベント**: SessionStart, SessionEnd, UserPromptSubmit, Stop, StopFailure, PreToolUse, PermissionRequest, PermissionDenied, PostToolUse, PostToolUseFailure, SubagentStart, SubagentStop, TaskCreated, TaskCompleted, TeammateIdle, Notification, InstructionsLoaded, ConfigChange, CwdChanged, FileChanged, PreCompact, PostCompact, Elicitation, ElicitationResult, WorktreeCreate, WorktreeRemove
  - **実装タイプ4種**: 正確（command, HTTP, prompt, agent）
  - **設定スコープ5つ**: user settings, project settings, project local, plugin hooks.json, skill/agent frontmatter
  - **制約**: JSON出力10,000文字上限、デフォルトタイムアウト（command 600s / prompt 30s / agent 60s）、マルチ判定優先順位（deny > defer > ask > allow）
- **フェーズ1記録の補正要否**: **要補正（重大）**。イベント数を10→24+に修正必須

#### Skills（F-005）

- **正式名称**: Skills（Claude Code機能）/ Agent Skills Open Standard
- **現在の位置づけ**: GA
- **主用途**: SKILL.md形式の再利用可能ワークフローパッケージ
- **制約**: 自動コンパクション対応（スキルあたり5,000トークン、合計25,000トークン予算）
- **新情報**:
  - **フロントマター12フィールド**: name, description, argument-hint, disable-model-invocation, user-invocable, allowed-tools, model, effort, context, agent, hooks, paths, shell
  - **動的コンテキスト注入**: `!`コマンドで外部データを動的に取り込み可能
  - **subagent実行**: `context: fork`でsubagentとして独立コンテキストで実行可能
  - **スコープ4つ**: enterprise, personal, project, plugin
  - `.claude/commands/`は後方互換性維持だが、skillsが推奨パス
- **企業採用について**: Phase 1は「Microsoft, OpenAI, Atlassian, Figma採用済み」と記載したが、**現時点の公式ドキュメントからはこの記載を直接確認できなかった**。「works across multiple AI tools」との表現のみ。agentskills.ioサイト側では確認できる可能性があるが、公式docs上では未確認
- **フ���ーズ1記録の補正要否**: 要補足。12フロントマターフィールド、動的コンテキスト注入、企業採用の記述について根拠URLの確認が必要

#### Claude Managed Agents（F-006）

- **正式名称**: Claude Managed Agents
- **現在の位置づけ**: Public beta（betaヘッダー `managed-agents-2026-04-01` 必要）
- **主用途**: AnthropicホストのフルマネージドエージェントHarness。セキュアサンドボックス・SSEストリーミング
- **制約**: レート制限（create 60 req/min, read 600 req/min）。一部機能（outcomes, multiagent, memory）はresearch previewで別途アクセスリクエスト必要
- **補正事項**: Phase 1は「/v1/agents, /v1/sessionsエンドポイント」と記載 → **実際はAgent/Environment/Session/Eventsの4概念で構成**。エンドポイントはセッションベース（`/docs/en/api/beta/sessions`で参照）
- **同日リリース**: `ant` CLI（Claude API用CLIツール）
- **フェーズ1記録の補正要否**: 要補正。APIの概念モデル（Agent/Environment/Session/Events）とエンドポイント構造を修正

#### Cowork（F-007）

- **正式名称**: Claude Cowork
- **現在の位置づけ**: **Research preview**（Phase 1では状態不明と記録）
- **主用途**: ナレッジワーカー向けAIアシスタント。自律的にPC上で作業を実行
- **制約**: Claude Desktop appからのみアクセス可能。API仕様は未公開
- **フェーズ1記録の補正要否**: 要補正。状態を「Research preview」に明記

#### Claude Code Release Notes

- **確認範囲**: 2026年2月〜4月の主要更新
- **注目すべき更新**:
  - 2026-04-09: Advisor Tool公開ベータ
  - 2026-04-08: Managed Agents公開ベータ + ant CLI
  - 2026-04-07: Claude Mythos Preview（防御的サイバーセキュリティ向け、gated research preview）
  - 2026-03-30: Batches API max_tokens 300Kに引き上げ
  - 2026-03-13: 1Mコンテキストウィンドウ GA（Opus 4.6 / Sonnet 4.6）
  - 2026-02-17: Sonnet 4.6リリース、Web検索ツール・Programmatic tool calling GA
  - 2026-02-05: Opus 4.6リリース、Compaction API beta、Effortパラメータ GA
  - 2025-10-16: Agent Skills API beta（skills-2025-10-02）
- **フェーズ1記録の補正要否**: 不要（Phase 1は2026-04-12時点で確認済み）

#### Claude Apps / Cowork Release Notes

- **確認結果**: A-005（support.claude.com/en/articles/12138966-release-notes）はClaude.ai一般向けリリースノート。Cowork固有の技術的リリースノートは別途確認できず
- **フェーズ1記録の補正要否**: 不要

---

### 1-2 公式実装資産の再確認

#### anthropics/skills（B-001 / F-013）

- **Stars**: 115,429（Phase 1記録: 115,361 → 微増、正確）
- **状態**: active、2026-04-12更新
- **topics**: agent-skills
- **archived**: false
- **フェーズ1記録の補正要否**: 不要

#### anthropics/claude-code-action（B-002 / F-014）

- **Stars**: 7,012（Phase 1記録: 7,010 → 微増、正確）
- **状態**: active、2026-04-12更新
- **フェーズ1��録の補正要否**: 不要

#### modelcontextprotocol/registry（B-006 / F-018）

- **Stars**: 6,667（Phase 1記録と一致）
- **状態**: active、2026-04-12更新
- **topics**: mcp, mcp-servers
- **フェーズ1記録の補正要��**: 不要

#### modelcontextprotocol/servers（B-007 / F-019）

- **Stars**: 83,531（Phase 1記録: 83,525 → 微増、正確）
- **状態**: active、2026-04-12更新
- **フェーズ1記録の補正要否**: 不���

---

### 1-3 再確認結果の差分サマリ

| 対象 | 差分内容 | 重要度 | フェーズ1記録の補正要否 |
|------|---------|--------|---------------------|
| Hooks（F-004） | イベント数10→24+。重大な過少記載 | **重大** | **必須修正** |
| Subagents（F-003） | 16フロントマターフィールド、ビルトインエージェント、worktree分離等が未記載 | **重要** | 補足推奨 |
| Managed Agents（F-006） | APIの概念モデルがAgent/Environment/Session/Events構造 | 重要 | 要修正 |
| Cowork（F-007） | 状態が「Research preview」であることを確認 | 中 | 要明記 |
| Skills（F-005） | 12フロントマターフィールド、動的コンテキスト注入 | 中 | 補足推奨 |
| MCP（F-002） | MCP Appsが第3カテゴリとして追加 | 低 | 補足推奨 |
| Prompt Improver（F-001） | 変更なし | — | 不要 |
| Advisor Tool（F-012） | 変更なし。Phase 1記録正確 | — | 不要 |
| 公式GitHubリポジトリ4件 | Star数微増のみ。全てactive | — | 不要 |

---

## パート2｜GitHub追加探索

### 2-1 役割類似探索

#### router / gateway 系の追加候補

| リポジトリ | Stars | 最終更新 | 概要 | 比較グループ |
|-----------|-------|---------|------|------------|
| **portkey-ai/gateway** | 11,280 | 2026-04-12 | 200+ LLMへのAIゲートウェイ。50+のAIガードレール内蔵。MCP対応。 | CG-01 |

- portkey-ai/gatewayはLiteLLM（F-022）の最有力代替候補。ガードレール内蔵とMCPネイティブ対応が差別化ポイント
- その他のrouter候補は既知候補（claude-code-router, LiteLLM）を超える特筆点がなく、追加登録対象外

#### orchestration / supervisor / workflow 系の追加候補

| リポジトリ | Stars | 最終更新 | 概要 | 比較グループ |
|-----------|-------|---------|------|------------|
| kyegomez/swarms | 6,217 | 2026-04-12 | エンタープライズ向けマルチエージェントオーケストレーション。多様なswarmトポロジ対応 | CG-02 |

- kyegomez/swarmsはD-006として既に追跡中。Star数6,217を確認し、activeを確認
- VRSEN/agency-swarm（4,208 stars）、dsifry/metaswarm（202 stars、Claude Code特化）は監視候補として記録するが、カタログ登録はしない
- ibbybuilds/aegra（775 stars）はLangGraph Platformの自己ホスト代替。LangGraph採用時に検討

#### MCP agent framework 系の追加候補

- lastmile-ai/mcp-agent（F-021）以外の有力MCP-nativeフレームワークは発見されなかった
- mcp-use/mcp-use（後述）はフレームワーク的側面もあるが、主用途はMCPアプリ開発

---

### 2-2 フェーズ2支援部品探索

#### evaluation / observability 系の候補（最優先探索）

| リポジトリ | Stars | 最終更新 | 概要 | 比較グループ |
|-----------|-------|---------|------|------------|
| **promptfoo/promptfoo** | 19,964 | 2026-04-12 | プロンプト/LLM評価フレームワーク。レッドチーミング・CI/CD統合。OpenAI/Anthropic公式使用 | CG-03/CG-06 |
| **confident-ai/deepeval** | 14,716 | 2026-04-12 | Python-nativeのLLM評価ライブラリ。14+の評価メトリクス。pytest風インターフェース | CG-03 |
| **langfuse/langfuse** | 24,760 | 2026-04-10 | LLMエンジニアリングプラットフォーム。オブザーバビリティ・評価・プロンプト管理。セルフホスト可能。YC W23 | CG-03 |
| **Arize-ai/phoenix** | 9,247 | 2026-04-10 | AIオブザーバビリティ＆評価。ローカル実行可能（pip一発）。OpenTelemetry基盤 | CG-03 |
| traceloop/openllmetry | 6,995 | 2026-04-12 | OpenTelemetry-nativeのLLM計測ライブラリ。LangChain/Anthropic/OpenAI自動計測 | CG-03（監視） |
| helicone/helicone | 5,475 | 2026-04-12 | プロキシ型LLMオブザーバビリティ。コード変更ゼロ（base URL変更のみ）。YC W23 | CG-03（監視） |
| AgentOps-AI/agentops | 5,452 | 2026-04-12 | エージェント専用モニタリングSDK。CrewAI/AutoGen/LangChainネイティブ統合 | CG-03（監視） |

**所見**: evaluation/observability領域はPhase 1時点で「ほぼ未探索」だったが、実際には非常に成熟したエコシステムが存在する。promptfoo（20K stars）、Langfuse（25K stars）、deepeval（15K stars）が三大候補。

#### prompt evaluation 系の候補

- promptfoo/promptfooが圧倒的な存在感（上記に記載済み）
- promptfoo/promptfoo-action（60 stars）: promptfooのGitHub Action。CI/CD評価パイプラインに使用可能。promptfoo採用時に自動的に利用可能

#### MCP testing / inspection 系の候補

| リポジトリ | Stars | 最終更新 | 概要 | 比較グループ |
|-----------|-------|---------|------|------------|
| **modelcontextprotocol/inspector** | 9,403 | 2026-04-12 | **MCP公式**の視覚的テストツール。Web UIでMCPサーバーに接続し、ツール/リソース/プロンプトを検査・テスト | CG-04 |

- modelcontextprotocol/inspectorはMCP公式の開発・デバッグツール。Phase 1では未発見だった重要候補
- steviec/mcp-server-tester（34 stars）、gleanwork/mcp-server-tester（5 stars）はCI/CD向けテスターだが規模が小さく監視のみ

---

### 2-3 公開エージェント探索

| リポジトリ | Stars | 概要 | 備考 |
|-----------|-------|------|------|
| BeehiveInnovations/pal-mcp-server | 11,409 | Claude Code/Gemini CLI/Codex CLIを複数モデルプロバイダーと統合するMCPサーバー | マルチプロバイダーMCPエージェントの参考実装 |
| OneRedOak/claude-code-workflows | 3,776 | Claude Code利用の実践的ワークフロー集 | パターンライブラリとして参考価値あり |
| catlog22/Claude-Code-Workflow | 1,784 | JSON駆動マルチエージェント開発フレームワーク | マルチエージェントパターンの参考 |
| CloudAI-X/claude-workflow-v2 | 1,324 | Claude Codeユニバーサルワークフロープラグイン | プラグイン型拡張の参考 |

**所見**: 公開エージェント・ワークフロー実装は増加傾向。ただしカタログ登録に値する独自性・規模を持つものは少数。パターン参考として03に記録するに留める。

---

### 2-4 未探索領域の抽出

| 領域 | 理由 | 優先度 |
|------|------|--------|
| Braintrust（D-004）詳細 | 今回GitHub探索でヒットせず。SaaS型のため詳細確認にはサイト訪問が必要 | 中 |
| W&B Weave（D-005）詳細 | ML実験管理からLLM評価への拡張状況が未確認 | 中 |
| LangSmith詳細 | LangGraph採用時に不可避のevalプラットフォーム。有料のためPhase 2では深入りしない | 低（LangGraph採用時に再確認） |
| Claude Mythos Preview | 2026-04-07にgated research previewとしてリリース。防御的サイバーセキュリティ向け | 低（本プロジェクトのスコープ外の可能性） |
| Agent Skills API（beta） | 2025-10-16にskills-2025-10-02ヘッダーでAPI beta開始。Claude Code Skills（F-005）とは別のAPI側skills機能 | 中（API側のskills機能を別候補として評価すべきか検討） |
| Managed Agents research preview機能 | outcomes, multiagent, memoryは別途アクセスリクエスト必要。現時点では未調査 | 中（GA移行後に再確認） |

---

## パート3｜フェーズ2支援部品の評価

### 評価対象と判定結果

| 候補名 | Stars | Phase 2への直接効果 | セットアップコスト | 判定 |
|--------|-------|-------------------|-----------------|------|
| **promptfoo** | 19,964 | **高**: プロンプト/モデル比較、レッドチーミング、CI/CD統合 | 軽微（Node.js 22.22+必要） | **小さく試す** |
| **LiteLLM** | 42,996 | **高**: マルチモデル統一API、コスト追跡 | 軽微（pip install） | **小さく試す** |
| **mcp-use** | 9,762 | 中: MCPアプリ開発フレームワーク | 中（TypeScript） | **後続で扱う** |
| **Langfuse** | 24,760 | 中: オブザーバビリティ・評価 | 中〜重（Docker/PostgreSQL） | **監視継続** |
| **Arize Phoenix** | 9,247 | 中: オブザーバビリティ（pip一発で起動可能） | 中（依存多） | **後続で扱う** |
| **deepeval** | 14,716 | 中: Python-native LLM評価 | 軽微（pip install） | **後続で扱う** |
| **mcp-eval** | 20 | 低: MCPサーバー評価だが活動停止 | 不明 | **見送り** |

### 各候補の詳細評価

#### promptfoo（promptfoo/promptfoo）

- **機能**: プロンプト/LLM評価フレームワーク。YAML宣言的設定で複数モデルの出力を並べて比較。レッドチーミング・ペネトレーションテスト機能。CI/CD統合。**OpenAIとAnthropicが公式利用**
- **Phase 2での活用**: 候補モデルの比較評価、プロンプト品質のA/Bテスト、評価結果のJSON/CSV出力
- **セットアップ**: `npx promptfoo@latest` で即実行可能。Node.js 22.22.0以上が必要
- **APIキー**: ローカルのmockテストは不要。LLM呼び出し比較にはAPIキーが必要
- **最終ゴール接続**: フェーズ5のAI参謀評価パイプラインの基盤になりうる
- **判定**: **小さく試す**
- **理由**: Phase 2のモデル比較・評価に最も直接的に役立つツール。20K stars、MIT、日次コミット。Anthropic公式使用。Node.js更新後にYAML設定でのモック比較テストから開始すべき

#### LiteLLM（BerriAI/litellm）- 既存F-022

- **機能**: 100+ LLM APIへの統一OpenAI互換インターフェース。コスト追跡・ガードレール・ロードバランシング・ロギング
- **Phase 2での活用**: 複数モデルのA/B比較、コスト分析、promptfooとの組み合わせでの評価パイプライン
- **セットアップ**: `pip install litellm` で完了。dry-run確認済み（依存: aiohttp, openai, tiktoken, pydantic等、妥当）
- **APIキー**: 実際のLLM呼び出しにはAPIキーが必要。mockモードあり
- **最終ゴール接続**: フェーズ4のマルチモデルルーティング基盤
- **判定**: **小さく試す**
- **理由**: 43K stars、日次更新。promptfooと組み合わせればPhase 2の評価パイプラインが構築可能。venv内でのmockテストから開始推奨

#### mcp-use（mcp-use/mcp-use）

- **機能**: MCPのフルスタックフレームワーク。MCP Appsの開発（ChatGPT/Claude向け）とMCPサーバー構築を統合的に提供
- **Phase 2での活用**: MCPサーバーのテスト・開発には有用だが、Phase 2の核心（候補評価・比較）には間接的
- **セットアップ**: TypeScript、npm依存。中程度
- **判定**: **後続で扱う**
- **理由**: 10K starsで活発だが、Phase 2の評価・比較タスクには直接関係しない。Phase 3〜4のMCPサーバー開発フェーズで再評価

#### Langfuse（langfuse/langfuse）

- **機能**: LLMエンジニアリングプラットフォーム。オブザーバビリティ、メトリクス、評価、プロンプト管理。LiteLLMとネイティブ統合。セルフホスト可能
- **Phase 2での活用**: 評価・メトリクス収集に有用だが、Phase 2の核心は「候補発掘・比較」であり本格オブザーバビリティは過剰
- **セットアップ**: Docker + PostgreSQL必要（セルフホスト）またはクラウド版（無料枠あり）
- **判定**: **監視継続**
- **理由**: 25K stars、YC卒業、エコシステム統合充実。ただしPhase 2にはpromptfoo+LiteLLMの方が軽量で直接的。Phase 3の本格運用・監視で導入検討

#### Arize Phoenix（Arize-ai/phoenix）

- **機能**: AIオブザーバビリティ＆評価。トレース、評価、実験管理。OpenTelemetry基盤。ローカル実行可能
- **Phase 2での活用**: Langfuseと同カテゴリだがpip一発で動く手軽さが利点
- **セットアップ**: `pip install arize-phoenix` でローカル起動（Docker不要）。依存は多い
- **判定**: **後続で扱う**
- **理由**: Phase 3のオブザーバビリティ導入時にLangfuseと比較検討。Phase 2では過剰

#### deepeval（confident-ai/deepeval）

- **機能**: Python-nativeのLLM評価ライブラリ。14+の評価メトリクス（faithfulness, relevancy, hallucination, toxicity等）。pytest風テストランナー
- **Phase 2での活用**: LLM出力品質の定量評価が可能。promptfoo（YAML/CLI中心）とは相補的（Python中心）
- **セットアップ**: `pip install deepeval` で完了。軽微
- **判定**: **後続で扱う**
- **理由**: 15K starsで優秀だが、Phase 2ではまずpromptfooで評価基盤を確立し、必要に応じてdeepevalを追加する方が効率的。Phase 3以降でのメトリクス評価に最適

#### mcp-eval（lastmile-ai/mcp-eval）

- **機能**: MCPサーバー向け軽量評価フレームワーク
- **Phase 2での活用**: MCPサーバー評価はPhase 2の主要スコープ外
- **現状**: 20 stars、最終更新2025-09-10（約7ヶ月前）。事実上メンテナンス停止
- **判定**: **見送り**
- **理由**: Stars 20、7ヶ月更新なし。MCPサーバー評価が必要な場合、promptfooやmodelcontextprotocol/inspectorの方が成熟

### 小さな試用の記録

#### promptfoo試用

- **実施内容**: `npx promptfoo@latest --version` の実行を試行
- **結果**: Node.js v22.22.0以上が必要（現環境v22.21.1）で実行不可。npmキャッシュ権限問題（EACCES）も検出
- **分かったこと**: Node.jsを1マイナーバージョン上げれば動作する見込み。MIT、CLI中心の設計で本プロジェクトに親和性が高い
- **判定変更なし**: **小さく試す**（Node.js更新後に再試行推奨）

#### LiteLLM試用

- **実施内容**: `pip install litellm --dry-run` の実行
- **結果**: 依存関係は健全（aiohttp, openai, tiktoken, tokenizers, pydantic等）。インストール自体は問題なし
- **分かったこと**: pip一発でインストール可能。依存関係の競合なし
- **判定変更なし**: **小さく試す**（venv内でのインストールと基本動作確認を推奨）

---

## パート4｜候補カタログへの追加記録

以下の候補を `phase1_information_foundation/02_candidate_catalog.md` に追加した。

| 追加item_id | 候補名 | 発見経路 | 所属比較グループ |
|------------|--------|---------|---------------|
| F-032 | promptfoo | GitHub追加探索（evaluation系） | CG-03 / CG-06 |
| F-033 | deepeval | GitHub追加探索（evaluation系） | CG-03 |
| F-034 | Langfuse | GitHub追加探索（observability系）。D-003から昇格 | CG-03 |
| F-035 | Arize Phoenix | GitHub追加探索（observability系） | CG-03 |
| F-036 | Portkey Gateway | GitHub追加探索（router/gateway系） | CG-01 |
| F-037 | mcp-use | GitHub追加探索（MCPフレームワーク） | CG-06 |
| F-038 | MCP Inspector | GitHub追加探索（MCP testing） | CG-04 |

### 追加しなかった候補と理由

| 候補 | Stars | 理由 |
|------|-------|------|
| helicone/helicone | 5,475 | CG-03に既に十分な候補がある。プロキシ型で独自だが、Langfuse/Phoenixでカバー可能 |
| traceloop/openllmetry | 6,995 | 計測ライブラリであり評価フレームワークではない。OTel基盤が必要になった段階で再検討 |
| AgentOps-AI/agentops | 5,452 | エージェント専用モニタリング。Phase 3以降で再検討。現時点ではevaluation基盤の確立が先 |
| kyegomez/swarms | 6,217 | D-006として既に追跡中。F-xxx昇格はPhase 2評価後に判断 |
| VRSEN/agency-swarm | 4,208 | 規模・独自性が既存CG-02候補を超えない |
| BeehiveInnovations/pal-mcp-server | 11,409 | 参考実装として価値はあるが評価対象としての独自カテゴリが不明確 |
| 各種Claude Code workflow集 | 1K〜4K | パターン参考であり、評価対象の候補ではない |
