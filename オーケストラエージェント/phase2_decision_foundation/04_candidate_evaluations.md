# 候補別評価記録（Candidate Evaluations）

> **担当**: グループ3  
> **インプット**: `00`, `01`, `02`, `03` を読み込んでから着手すること  
> **ステップ対応**: フェーズ2作業指示書 ステップ7（候補別評価記録の作成）  
> **最終更新**: 2026-04-12（グループ3）

---

## パート1｜比較グループ別評価

### CG-01｜router / gateway 系

> 比較の問い: Claude Code環境でのモデルルーティング・コスト管理をどう実現するか

#### F-020 | claude-code-router

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | Claude Code特化のrouter。AI参謀基盤でのモデルコスト最適化に直接有用 |
| E2 役割明確性 | 5 | 「Claude CodeのモデルルーティングOSS」と明確。他候補との役割境界が明瞭 |
| E3 導入価値 | 3 | コスト最適化に有用だが、Claude Code標準のモデル切替で一定対応可能 |
| E4 流用可能性 | 4 | Claude Code環境特化の設計でそのまま流用可能 |
| E5 導入難易度 | 3 | Claude Codeとの統合設定が必要だが、公式よりシンプル |
| E6 保守性 | 5 | 32k stars、継続的な活発メンテナンス |
| E7 安全性 | 4 | Claude Code特化のためスコープが限定的。OSSリスクは標準的 |
| E8 拡張性 | 3 | Claude Code環境に最適化されているため他環境への拡張は限定的 |
| E9 代替可能性 | 2 | LiteLLM（F-022）、Portkey（F-036）との競合あり |
| E10 今やる意味 | 3 | マルチモデル環境への移行時に有用。今すぐ必須ではない |

- **compared_with**: F-022, F-036
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B2（部分流用 - Claude Code設定の要カスタマイズ）
- **current_priority**: P3
- **reason_summary**: 32k starsの実績ある Claude Code特化router。今すぐ必須ではないが、複数モデル比較時に小さく試す価値がある。LiteLLMとの使い分けはClaudeに特化するかマルチLLMかで決まる
- **unresolved_points**: Claude Code公式のモデル切替機能と比べた場合の実際のコスト削減効果が未定量
- **next_review_condition**: 複数モデルを並列利用する本番フェーズに移行するとき
- **next_action**: LiteLLMとの比較評価を実施し、どちらを採用するか決定する

---

#### F-022 | LiteLLM

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | 100+ LLM統一管理。AI参謀基盤のコスト管理・マルチモデル比較に有用だが汎用的 |
| E2 役割明確性 | 4 | 「多LLMへの統一OpenAI互換インターフェース」と明確 |
| E3 導入価値 | 4 | pip一発。コスト追跡・フォールバック等が即効果。promptfooとの組み合わせで評価パイプライン構築可能 |
| E4 流用可能性 | 5 | pip install litellm で全面流用可能。依存関係健全（dry-run確認済み） |
| E5 導入難易度 | 5 | pip install のみ。モック動作も可能 |
| E6 保守性 | 5 | 43k stars、日次更新、BerriAI商用サポート |
| E7 安全性 | 3 | 外部APIプロキシのため信頼境界の確認が必要。ローカルモードで緩和可能 |
| E8 拡張性 | 5 | 100+ LLM対応で最高の拡張性 |
| E9 代替可能性 | 2 | claude-code-router、Portkey Gatewayとの競合。汎用性はLiteLLMが最高 |
| E10 今やる意味 | 4 | Phase 2の評価パイプラインにpromptfooと組み合わせで即活用可能 |

- **compared_with**: F-020, F-036
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: 43k starsのLLM統一gateway。フェーズ2ではpromptfooとの組み合わせで評価パイプライン構築に活用できる。フェーズ4のマルチモデルルーティング基盤としても有力
- **unresolved_points**: Anthropic Managed Agentsとの統合可否が未確認
- **next_review_condition**: フェーズ4のマルチモデル本番環境構築時。または評価パイプライン構築を開始するとき
- **next_action**: venv内でインストール確認し、promptfooと組み合わせた基本的な評価テストを実施

---

#### F-036 | Portkey Gateway

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | 200+ LLM対応ゲートウェイ。AI参謀基盤のガードレール要件に有用だがLiteLLMと重複 |
| E2 役割明確性 | 4 | 「ガードレール内蔵AIゲートウェイ」と明確。ガードレール機能がLiteLLMとの差別化 |
| E3 導入価値 | 3 | ガードレール内蔵は差別化だが、現フェーズでは過剰な可能性が高い |
| E4 流用可能性 | 4 | Node.js or Docker で流用可能 |
| E5 導入難易度 | 3 | Dockerが必要なケースもあり、LiteLLMより導入が少し重い |
| E6 保守性 | 5 | 11k stars、2026-04-12更新 |
| E7 安全性 | 5 | 50+ガードレール内蔵で安全性が高い。MCP対応あり |
| E8 拡張性 | 4 | MCP対応で将来的な拡張性高い |
| E9 代替可能性 | 3 | ガードレール機能はLiteLLMで代替困難。ただし現フェーズでは不要 |
| E10 今やる意味 | 2 | ガードレールはフェーズ4〜5で重要。現フェーズでは過剰 |

- **compared_with**: F-020, F-022
- **decision_state**: D5（監視継続）
- **build_vs_buy_state**: B5（判断保留 - LiteLLMとの優劣確定後）
- **current_priority**: P4
- **reason_summary**: ガードレール内蔵という差別化があるが、現フェーズではLiteLLMで十分。フェーズ4〜5の本番セキュリティ要件が明確になった時点で再評価する
- **unresolved_points**: Portkey固有のMCPガードレール機能の詳細仕様が未確認
- **next_review_condition**: フェーズ4〜5でガードレール要件が明確化されたとき
- **next_action**: 監視継続。LiteLLMで不足するガードレール要件が発生した場合に本格評価

---

### CG-02｜orchestration / supervisor / workflow 系

> 比較の問い: 複数エージェントの協調・制御・ワークフロー管理をどう実現するか

#### F-027 | LangGraph

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | グラフベースオーケストレーション。AI参謀基盤の複雑ワークフロー管理に直接有用 |
| E2 役割明確性 | 5 | 「グラフ（DAG）ベースのエージェントオーケストレーション」と明確 |
| E3 導入価値 | 4 | 複雑なステートフルワークフローを実現できる。フェーズ4実行基盤の核心候補 |
| E4 流用可能性 | 3 | Python SDKとして流用可能だが、LangChain依存関係がある |
| E5 導入難易度 | 2 | LangChain依存・グラフ設計の学習コスト高。セットアップに時間がかかる |
| E6 保守性 | 4 | 29k stars、LangChain社がメンテナンス |
| E7 安全性 | 3 | LangChainエコシステム依存が大きく、信頼境界の管理が複雑 |
| E8 拡張性 | 5 | ノードとエッジの拡張が容易。MCP統合深度が高い（ツールのグラフノード化） |
| E9 代替可能性 | 4 | 複雑なステートフルワークフローはAgent SDK単体では実現困難な機能がある |
| E10 今やる意味 | 3 | フェーズ4の実行基盤で必要。今から学習投資する価値はあるが本格利用はフェーズ4 |

- **compared_with**: F-009, F-021, F-028, F-029
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留 - フェーズ4実行基盤設計時に確定）
- **current_priority**: P4
- **reason_summary**: 最も本格的なエージェントオーケストレーションフレームワーク。フェーズ4以降で必要になる可能性が高いが、学習コストと依存関係の重さから現フェーズでの本格採用は保留。Agent SDKで実現困難な複雑ワークフローが出現した時点で本格評価
- **unresolved_points**: Claude Agent SDK単体でどこまで複雑なワークフローを実現できるかが未定量。LangGraph vs Agent SDK+Subagentsの実際の能力差が未検証
- **next_review_condition**: フェーズ4実行基盤設計を開始するとき。または Agent SDK単体では実現できないワークフロー要件が発生したとき
- **next_action**: Agent SDKで実装した後に機能限界を確認し、不足点をLangGraphで補うか評価する

---

#### F-028 | CrewAI

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | ロールベースの協調。AI参謀基盤には有用だがLangGraphよりフレキシビリティが低い |
| E2 役割明確性 | 4 | 「ロールベースのマルチエージェント協調フレームワーク」と明確 |
| E3 導入価値 | 3 | 20行以下でエージェント定義可能だが、5エージェント超で調整オーバーヘッドが増大 |
| E4 流用可能性 | 4 | pip install crewai で流用可能。シンプルなロール設計 |
| E5 導入難易度 | 4 | セットアップが簡単。学習コストが低い |
| E6 保守性 | 4 | 49k stars、活発なメンテナンス |
| E7 安全性 | 3 | 外部サービス連携が多いと信頼境界が複雑化 |
| E8 拡張性 | 3 | ロールベース設計は柔軟性に限界あり |
| E9 代替可能性 | 2 | LangGraph・AutoGen・Agent SDKとの競合が大きい |
| E10 今やる意味 | 2 | 学習コストは低いが、本プロジェクト向けにはLangGraphより機能が限定的 |

- **compared_with**: F-027, F-029, F-009
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P4
- **reason_summary**: 学習コストが最低で即プロトタイプ可能だが、AI参謀基盤の複雑なワークフロー要件に対してLangGraphより機能が限定的。LangGraphを評価した後で補完的な役割があるかを判断する
- **unresolved_points**: CrewAI固有のflow（新機能）がLangGraphの代替になりうるかが未確認
- **next_review_condition**: フェーズ4でロール明確なチーム型エージェントが必要になったとき
- **next_action**: LangGraph評価後に比較検討

---

#### F-029 | AutoGen

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | 会話駆動型の高精度推論。AI参謀基盤のフェーズ5以降での高精度議論に有用 |
| E2 役割明確性 | 4 | 「会話駆動型マルチエージェント協調フレームワーク」と明確 |
| E3 導入価値 | 2 | LLMコール20+/タスクでコストが非常に高い。現フェーズでの実用的利用が困難 |
| E4 流用可能性 | 3 | Python SDKとして流用可能だが、コスト問題で本番利用は限定的 |
| E5 導入難易度 | 3 | セットアップは容易だが、コスト管理設定が必要 |
| E6 保守性 | 5 | 57k stars、Microsoft Researchのバックアップ |
| E7 安全性 | 3 | 多数のLLMコールで外部API依存が高い |
| E8 拡張性 | 3 | 会話駆動設計は拡張性に制約がある |
| E9 代替可能性 | 3 | 会話駆動推論という独自ニッチ。ただしLangGraphでも代替可能なケースが多い |
| E10 今やる意味 | 1 | 高コストで現フェーズでの利用は非効率。フェーズ5の高精度推論が必要になってから |

- **compared_with**: F-027, F-028, F-009
- **decision_state**: D5（監視継続）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P5
- **reason_summary**: 推論精度は最高クラスだが、1タスク20+のLLMコールによるコスト問題がAI参謀基盤の本番利用を阻む。フェーズ5の高精度推論が必要になるまで監視継続
- **unresolved_points**: AutoGen 0.4の新アーキテクチャでコスト問題が改善されたかが未確認
- **next_review_condition**: コスト問題の改善報告があったとき。またはフェーズ5で高精度推論要件が確定したとき
- **next_action**: 監視継続。AutoGen 0.4系の更新情報を追跡する

---

#### F-021 | mcp-agent

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | MCPネイティブのエージェントフレームワーク。AI参謀基盤のMCP統合に有用 |
| E2 役割明確性 | 4 | 「MCPとワークフローパターンを組み合わせたエージェント構築フレームワーク」と明確 |
| E3 導入価値 | 3 | MCPネイティブ統合に特化。シンプルで学習コスト低い |
| E4 流用可能性 | 4 | Python。シンプルな設計で流用しやすい |
| E5 導入難易度 | 4 | シンプルな設計でセットアップが容易 |
| E6 保守性 | 3 | 8k stars。LastMile AI。mcp-eval（F-023）が活動低迷しているため保守継続性に軽度の懸念 |
| E7 安全性 | 4 | MCP標準準拠で信頼境界が明確 |
| E8 拡張性 | 4 | MCP標準準拠で拡張性高い |
| E9 代替可能性 | 3 | LangGraph+MCP統合と競合するが、MCPネイティブという差別化あり |
| E10 今やる意味 | 3 | MCPエコシステム構築に有用。フェーズ3〜4で本格利用 |

- **compared_with**: F-009, F-027, F-028
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留 - LangGraphとの比較後に確定）
- **current_priority**: P4
- **reason_summary**: MCPネイティブという差別化があるが、Agent SDK + MCP Connectorで同等機能が実現できる可能性がある。orchestrationグループ内でLangGraphとAgent SDKの比較評価を先に実施してから判断する
- **unresolved_points**: Agent SDK + MCP ConnectorとMCP-agentの実際の機能差が未検証
- **next_review_condition**: MCPサーバーを複数統合するエージェントを構築するフェーズに移行するとき
- **next_action**: Agent SDKでのMCP統合を先に実装し、不足点を確認してからmcp-agentの採用を評価する

---

#### F-009 | Claude Agent SDK（CG-02での評価）

※ CG-05（実行エージェント管理層）でメイン評価。CG-02では比較参照として記録。

CG-02の観点（orchestration as the comparison baseline）:

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | Anthropic公式SDK。エージェントループ・コンテキスト管理の完全制御が可能 |
| E2 役割明確性 | 5 | 「Anthropicエコシステムでのエージェント構築SDK」と明確。他候補の比較基準点 |
| E4 流用可能性 | 5 | pip install / npm install で全面流用可能 |
| E6 保守性 | 5 | Anthropic公式。継続的なメンテナンスが保証 |
| E8 拡張性 | 5 | subagents・hooks・MCP・sessionsの完全制御が可能 |

- **compared_with**: F-027, F-028, F-021
- **decision_state**: D1（採用候補） ← CG-05でメイン確定
- **reason_summary**: orchestrationグループでの比較基準点として機能する。Agent SDK単体でどこまで複雑なオーケストレーションを実現できるかが、LangGraph/CrewAI/mcp-agent採用を判断する閾値になる

---

#### F-008 | Agent Teams

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | サブエージェント間の直接通信。AI参謀基盤の将来的な協調に有用だが現在は実験的 |
| E2 役割明確性 | 4 | 「複数Claudeインスタンスの直接通信型協調」と明確 |
| E3 導入価値 | 2 | 実験的・制限多数（セッション再開不可等）・コストが Subagentsより大幅高 |
| E4 流用可能性 | 2 | 実験的機能のため流用リスク高 |
| E5 導入難易度 | 2 | 環境変数フラグ制御が必要。制限多数 |
| E6 保守性 | 1 | 実験的機能。GAの見通し不明 |
| E7 安全性 | 3 | 環境変数でのフラグ制御が必要 |
| E8 拡張性 | 3 | サブ間直接通信は成熟後の拡張性が高い可能性 |
| E9 代替可能性 | 4 | Subagentsとの差別化はサブ間直接通信のみ |
| E10 今やる意味 | 1 | 実験的で制限多数。今から使うのは時期尚早 |

- **compared_with**: F-003, F-009
- **decision_state**: D5（監視継続）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P5
- **reason_summary**: サブ間直接通信という独自機能は将来的に有用だが、現時点では実験的・制限多数・高コストで採用できない。GAに移行し安定したタイミングで再評価する
- **unresolved_points**: GA移行のロードマップが未確認。セッション再開問題の解消見込みが不明
- **next_review_condition**: 実験的フラグが外れてGAになったとき
- **next_action**: 監視継続。GA移行のリリースノートを追跡する

---

#### F-030 | OpenAI Agents SDK（比較参照のみ）

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 2 | OpenAI向けSDK。Anthropic環境での採用対象外 |
| E9 代替可能性 | — | 比較参照対象のため評価不要 |

- **compared_with**: F-009
- **decision_state**: D4（不採用）
- **build_vs_buy_state**: B3（参考流用 - 設計パターンの参考として）
- **current_priority**: P5
- **reason_summary**: Anthropicエコシステムでの採用対象外。Claude Agent SDK（F-009）の設計比較・差別化確認のための参照として記録する
- **unresolved_points**: なし（採用対象外のため）
- **next_review_condition**: Anthropic-OpenAI間でのモデル切替が必要になった場合（LiteLLM経由で管理する方が現実的）
- **next_action**: 監視不要。設計比較のメモとして保持

---

### CG-03｜evaluation / observability 系

> 比較の問い: エージェント・LLMの出力品質評価・監視をどう実現するか

#### F-034 | Langfuse

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | LLMオブザーバビリティ・評価・プロンプト管理の統合。AI参謀基盤の品質管理に重要 |
| E2 役割明確性 | 5 | 「LLMエンジニアリングプラットフォーム」と明確。トレーシング・評価・プロンプト管理を統合 |
| E3 導入価値 | 4 | トレーシング・評価・プロンプトバージョン管理が統合。フェーズ3以降で高い効果 |
| E5 導入難易度 | 2 | セルフホストにはDocker+PostgreSQLが必要。クラウド版は軽いが外部送信リスクあり |
| E6 保守性 | 5 | 25k stars、YC W23卒業、LiteLLMとネイティブ統合 |
| E7 安全性 | 4 | セルフホスト可能で機密データを外部送信しなくてもよい |
| E8 拡張性 | 5 | LiteLLM・LangChain・OpenAI SDKとネイティブ統合 |
| E9 代替可能性 | 4 | プロンプト管理+評価+オブザーバビリティの統合は他に少ない |
| E10 今やる意味 | 3 | フェーズ2での本格利用は過剰。フェーズ3以降で重要 |

- **compared_with**: F-032, F-033, F-035
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留 - フェーズ3以降のオブザーバビリティ設計時に確定）
- **current_priority**: P4
- **reason_summary**: 25k stars・YC卒業のLLMエンジニアリングプラットフォームとして非常に優秀だが、Docker+PostgreSQLのセットアップコストがフェーズ2の作業には過剰。フェーズ3のオブザーバビリティ基盤構築時にArize Phoenixと比較して採用を決定する
- **unresolved_points**: セルフホスト版のメンテナンスコストと、クラウド版の無料枠制限が未評価
- **next_review_condition**: フェーズ3でオブザーバビリティ基盤を構築するとき
- **next_action**: フェーズ3でArize Phoenixと比較評価。クラウド版の無料枠で先に試用することも検討

---

#### D-004 | Braintrust（未昇格）

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | LLM eval基盤として有用と推定されるが詳細未調査 |
| E2 役割明確性 | 3 | 「LLM評価基盤（SaaS）」との認識。詳細仕様は未確認 |
| E3 導入価値 | — | 情報不足で評価不能 |
| E4 流用可能性 | — | 情報不足で評価不能 |
| E5 導入難易度 | — | 情報不足で評価不能 |
| E6 保守性 | — | 情報不足で評価不能 |
| E7 安全性 | — | SaaS型のため機密データの外部送信リスクが推定されるが詳細未確認 |
| E8 拡張性 | — | 情報不足で評価不能 |
| E9 代替可能性 | 3 | Langfuse・deepeval・promptfooとの競合 |
| E10 今やる意味 | 2 | 詳細調査前に採用判断不可 |

- **compared_with**: F-032, F-033, F-034, F-035
- **decision_state**: D3（保留 - 詳細未調査）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P5
- **reason_summary**: SaaS型LLM eval基盤として参照情報があるが、GitHub探索でヒットせずサイト訪問が必要。現フェーズではpromptfoo・Langfuse・deepevalで代替可能なため調査の緊急度は低い
- **unresolved_points**: 詳細仕様・価格・ローカル実行可否・OSS版の有無が未確認
- **next_review_condition**: CG-03の他候補（promptfoo, Langfuse, deepeval）では解決できない評価要件が発生したとき
- **next_action**: ブランドラストのウェブサイト（braintrust.dev）で機能・価格を確認してから評価

---

#### D-005 | W&B Weave（未昇格）

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | ML実験管理からLLM評価への拡張版。AI参謀基盤の評価・追跡に有用と推定 |
| E2 役割明確性 | 3 | 「MLops基盤のLLM評価拡張」との認識。詳細仕様は未確認 |
| E3 導入価値 | — | 情報不足 |
| E4 流用可能性 | — | 情報不足 |
| E5 導入難易度 | — | W&B本体との依存関係が懸念されるが未確認 |
| E6 保守性 | — | W&B社（商用企業）がバックアップ |
| E7 安全性 | — | SaaS型のため機密データリスクが推定 |
| E8 拡張性 | — | 情報不足 |
| E9 代替可能性 | 3 | Langfuse・deepeval・promptfooとの競合 |
| E10 今やる意味 | 2 | W&B本体との依存関係の重さが不明。調査先行が必要 |

- **compared_with**: F-032, F-033, F-034, F-035
- **decision_state**: D3（保留 - 詳細未調査）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P5
- **reason_summary**: ML実験管理の老舗W&Bによるエージェント評価拡張。LangGraphやMLワークフローとの統合が強みと推定されるが、W&B本体への依存関係の重さが懸念。他候補で代替可能な可能性が高い
- **unresolved_points**: W&B Weave単体での導入可否（W&B全体が必要か）が未確認
- **next_review_condition**: MLワークフロー全体の管理が必要になったとき（LangGraphと組み合わせて使う場面）
- **next_action**: Braintrust評価後に残課題があれば調査

---

#### F-023 | mcp-eval

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 2 | MCPサーバー評価専用。スコープが限定的でAI参謀基盤への貢献が薄い |
| E2 役割明確性 | 4 | 「MCPサーバー向け軽量評価フレームワーク」と明確 |
| E3 導入価値 | 1 | stars=20、最終更新2026-03-22（活動低迷）。使える状態でない |
| E4 流用可能性 | 1 | mcp-agentへの依存があり、事実上停止プロジェクトへの依存リスク |
| E5 導入難易度 | 1 | 事実上停止プロジェクト |
| E6 保守性 | 1 | 7ヶ月更新なし。メンテナンス停止 |
| E7 安全性 | 3 | 小規模OSSのリスク標準的 |
| E8 拡張性 | 1 | 発展性なし |
| E9 代替可能性 | 2 | promptfoo・MCP Inspectorで代替可能 |
| E10 今やる意味 | 1 | 今使う価値なし |

- **compared_with**: F-032, F-038
- **decision_state**: D4（不採用）
- **build_vs_buy_state**: B5（判断保留 - 採用しないため不要）
- **current_priority**: P5
- **reason_summary**: Stars=20、7ヶ月更新なしの事実上停止プロジェクト。MCPサーバー評価が必要な場合はpromptfoo（F-032）またはMCP Inspector（F-038）で代替可能
- **unresolved_points**: なし（不採用確定）
- **next_review_condition**: mcp-evalがActiveになりstars 500超えたとき
- **next_action**: 不採用。MCPサーバー評価はpromptfooまたはMCP Inspectorで対応する

---

#### F-032 | promptfoo

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | プロンプト/LLM評価。AI参謀基盤の評価品質管理・モデル比較に直接有用 |
| E2 役割明確性 | 5 | 「プロンプト/LLM評価フレームワーク」と明確。YAML宣言的設定が特徴 |
| E3 導入価値 | 5 | Phase 2の評価作業に即活用可能。モデル比較・レッドチーミング・CI/CD統合を包含 |
| E4 流用可能性 | 5 | npx promptfoo@latest で即実行。YAML設定で柔軟なカスタマイズ |
| E5 導入難易度 | 4 | Node.js v22.22+が必要（現環境v22.21.1）。バージョン更新後は即使用可能 |
| E6 保守性 | 5 | 20k stars、日次コミット、OpenAI・Anthropic公式使用 |
| E7 安全性 | 4 | ローカル実行可能。APIキー管理も透明 |
| E8 拡張性 | 4 | CI/CD統合、GitHub Actionsとの連携。評価パイプラインへの組み込みが容易 |
| E9 代替可能性 | 4 | YAML宣言的設定+レッドチーミング統合の組み合わせは他に少ない |
| E10 今やる意味 | 5 | Phase 2に最も直接的な効果がある評価支援部品 |

- **compared_with**: F-033, F-034, F-035
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P2
- **reason_summary**: Anthropic公式使用・20k stars・日次コミットの最有力評価フレームワーク。Node.js更新のみでフェーズ2から即活用可能。deepevalとは相補的（CLI/YAMLvsPython）で共存可能。CI/CD統合でフェーズ3〜5にも繋がる
- **unresolved_points**: Node.js v22.22+への更新後の動作確認が未実施
- **next_review_condition**: Node.js更新後に実際のモデル比較評価を実施する
- **next_action**: Node.js v22.22+に更新し、promptfooでAnthropic vs他モデルの基本比較テストを実施する

---

#### F-033 | deepeval

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | Python-nativeのLLM評価ライブラリ。AI参謀基盤の品質評価に有用 |
| E2 役割明確性 | 5 | 「Python-nativeのLLM評価ライブラリ（pytest風）」と明確 |
| E3 導入価値 | 4 | 14+メトリクスで定量的な品質評価が可能。promptfooとは相補的 |
| E4 流用可能性 | 5 | pip install deepeval で即使用 |
| E5 導入難易度 | 5 | pip一発。pytestエコシステムと統合 |
| E6 保守性 | 5 | 15k stars、日次更新 |
| E7 安全性 | 4 | ローカル実行可能 |
| E8 拡張性 | 4 | pytestエコシステムとの統合で拡張が容易 |
| E9 代替可能性 | 3 | promptfoo（CLI/YAML）とは相補。Python中心メトリクス評価では優位 |
| E10 今やる意味 | 3 | Phase 2ではまずpromptfooで評価基盤を確立。deepevalはPhase 3以降で追加 |

- **compared_with**: F-032, F-034, F-035
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P4
- **reason_summary**: 15k starsの優秀なPython評価ライブラリ。promptfooとは相補的（YAML vs Python）で共存価値あり。現フェーズではpromptfooを先に確立し、Pythonメトリクス評価が必要になった段階で追加導入する
- **unresolved_points**: promptfooとdeepeval両方使う場合の評価パイプライン設計が未定
- **next_review_condition**: promptfoo確立後にPythonメトリクス（faithfulness, hallucination等）の評価が必要になったとき
- **next_action**: promptfoo確立後に評価

---

#### F-035 | Arize Phoenix

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | AIオブザーバビリティ。AI参謀基盤の監視に有用だがフェーズ2では過剰 |
| E2 役割明確性 | 4 | 「AIオブザーバビリティ＆評価プラットフォーム（OpenTelemetry基盤）」と明確 |
| E3 導入価値 | 3 | pip一発でローカル起動可能（Docker不要）。Langfuseより軽いが現フェーズでは過剰 |
| E4 流用可能性 | 4 | pip install arize-phoenix で流用可能 |
| E5 導入難易度 | 4 | Docker不要。Langfuseより導入が軽い |
| E6 保守性 | 4 | 9k stars、2026-04-10更新 |
| E7 安全性 | 4 | ローカル実行可能 |
| E8 拡張性 | 4 | OpenTelemetry基盤で他ツールとの共存が容易 |
| E9 代替可能性 | 3 | Docker不要という差別化でLangfuseと異なるニッチ |
| E10 今やる意味 | 2 | Phase 3のオブザーバビリティ導入時が適切 |

- **compared_with**: F-034, F-032, F-033
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P4
- **reason_summary**: Docker不要でLangfuseより軽量なオブザーバビリティプラットフォーム。現フェーズでは過剰だが、フェーズ3でLangfuseとの比較評価対象として重要。OpenTelemetry基盤は長期的な共存可能性を示す
- **unresolved_points**: LangfuseとArize Phoenixの選択基準（セルフホストコストvsOpenTelemetry基盤）が未定
- **next_review_condition**: フェーズ3でオブザーバビリティ基盤の選定を行うとき
- **next_action**: フェーズ3でLangfuseとの比較評価を実施

---

### CG-04｜知識活用補助候補系

> 比較の問い: 情報の蓄積・検索・再利用をどう実現するか（フェーズ3への接続）

#### F-025 | Memory Tool（API）

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | クロスセッション記憶。AI参謀基盤のコンテキスト継続に直接必須 |
| E2 役割明確性 | 5 | 「会話をまたいで情報を保存・参照するGA済みAPI機能」と明確 |
| E4 流用可能性 | 5 | APIに組み込むだけで全面流用可能。betaヘッダー不要 |
| E8 拡張性 | 4 | API経由で他機能と統合可能。フェーズ3知識活用基盤への接続が容易 |
| E10 今やる意味 | 5 | GA済みで今すぐ使える。CLAUDE.mdのauto memoryとの役割分担を確定させる |

| E5 導入難易度 | 5 | betaヘッダー不要・GA済み。API呼び出しのみ |
| E6 保守性 | 5 | Anthropic公式。継続的なサポート保証 |
| E7 安全性 | 5 | Anthropic管理の安全なストレージ |
| E9 代替可能性 | 5 | クロスセッション記憶の公式APIは他に代替なし |

- **compared_with**: なし（他に代替なし）
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P1
- **reason_summary**: GA済みのクロスセッション記憶API。AI参謀基盤の状態継続に必須機能。CLAUDE.mdのauto memory（project/user スコープ）とは異なるAPIレベルのメモリ管理として補完的に機能する。フェーズ3知識活用基盤への直接接続ポイント
- **unresolved_points**: CLAUDE.mdのauto memoryとMemory Tool APIの役割分担・データの重複管理方針が未定
- **next_review_condition**: フェーズ3知識活用基盤の設計を開始するとき
- **next_action**: auto memoryとMemory Tool APIの役割分担を定義し、フェーズ3でのRAG基盤との接続方針を確立する

---

#### F-002 | MCP（Model Context Protocol）

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | 外部システム接続のオープン標準。AI参謀基盤のあらゆる外部連携の基盤 |
| E2 役割明確性 | 5 | 「AIアプリと外部システムの接続プロトコル（USB-Cアナロジー）」と明確 |
| E4 流用可能性 | 5 | Claude Code組み込み済みで全面流用可能 |
| E5 導入難易度 | 5 | Claude Code設定ファイルで即設定可能 |
| E6 保守性 | 5 | Anthropicリードの公式標準。業界採用拡大中 |
| E7 安全性 | 4 | 権限モデルが明確。MCPサーバーの信頼境界は個別管理が必要 |
| E8 拡張性 | 5 | 新MCPサーバーを追加するだけで無限に機能拡張可能 |
| E9 代替可能性 | 5 | AIと外部システム接続の業界標準。代替なし |
| E10 今やる意味 | 5 | 今すぐ使える。フェーズ3知識活用基盤の中核接続基盤 |

- **compared_with**: なし（プロトコル標準のため他と比較しない）
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P1
- **reason_summary**: Anthropic公式のAI外部連携標準。Claude Codeに組み込み済みで追加コストなし。フェーズ3〜5の全てのフェーズで中核となるプロトコル基盤であり、採用確定
- **unresolved_points**: MCP Apps（第3カテゴリ）の詳細活用方法が未検討
- **next_review_condition**: 特定MCPサーバーの選定・実装を開始するとき
- **next_action**: フェーズ3でRAG・検索系MCPサーバーの選定と実装を開始する

---

#### F-018 | MCP Registry

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | MCPサーバーの発見・管理。利用するMCPサーバー選定に有用 |
| E2 役割明確性 | 5 | 「MCPサーバーのコミュニティ主導レジストリ（公開API）」と明確 |
| E4 流用可能性 | 5 | 公開APIをそのまま活用可能。APIキー不要 |
| E5 導入難易度 | 5 | APIキー不要で即使用可能 |
| E6 保守性 | 5 | modelcontextprotocol公式。6k stars |
| E7 安全性 | 5 | 公式Anthropic管理 |
| E8 拡張性 | 4 | MCPエコシステムの発展とともに価値が増す |
| E9 代替可能性 | 5 | MCPサーバーのレジストリは公式のみ |
| E10 今やる意味 | 3 | フェーズ3のMCP活用時に有用。今は参照程度 |

- **compared_with**: F-019
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: MCPサーバーを探索・選定する際の公式カタログ。APIキー不要で即使用可能。フェーズ3でMCPサーバーを本格的に選定・管理するときに重要な参照ポイントになる
- **unresolved_points**: レジストリのAPIレスポンス品質（説明の詳細度・更新鮮度）が未確認
- **next_review_condition**: フェーズ3でMCPサーバーの選定・比較を開始するとき
- **next_action**: MCPサーバー選定が必要になった時点でAPIを使って候補を探索する

---

#### F-019 | MCP Servers

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | MCPサーバーのリファレンス実装集。外部システム接続実装の参考に直接有用 |
| E2 役割明確性 | 5 | 「MCPサーバーの公式リファレンス実装集」と明確 |
| E4 流用可能性 | 5 | 公式リポジトリからのコード流用が可能 |
| E5 導入難易度 | 4 | 各サーバーの個別セットアップが必要だが標準化されている |
| E6 保守性 | 5 | modelcontextprotocol公式。83k stars。活発 |
| E7 安全性 | 4 | 公式実装。各サーバーの権限は個別確認が必要 |
| E8 拡張性 | 5 | 新MCPサーバーを追加することでいくらでも拡張可能 |
| E9 代替可能性 | 5 | 公式リファレンス実装は他に代替なし |
| E10 今やる意味 | 4 | フェーズ3のMCPサーバー構築時に直接活用。今から把握しておく価値あり |

- **compared_with**: F-018, F-037, F-038
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P2
- **reason_summary**: 83k starsの公式MCPサーバーリファレンス実装集。フェーズ3で外部システム（ファイルシステム・DB・API等）に接続する際の実装基盤として直接活用可能。AI参謀基盤の知識活用層の構築に不可欠
- **unresolved_points**: 本プロジェクトに必要な具体的なMCPサーバーの種類が未定
- **next_review_condition**: フェーズ3の知識活用基盤設計を開始するとき
- **next_action**: フェーズ3でRAG・ファイル・DB系のMCPサーバー実装を選定して導入する

---

#### F-026 | MCP Connector

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | Messages API側からのMCPサーバー接続。プログラマブルなMCP活用に有用 |
| E2 役割明確性 | 4 | 「Messages APIからリモートMCPサーバーに直接接続する機能」と明確 |
| E4 流用可能性 | 5 | GA済みで既存APIに追加するだけ |
| E5 導入難易度 | 5 | betaヘッダー不要。既存API呼び出しに追加するだけ |
| E6 保守性 | 5 | Anthropic公式GA機能 |
| E7 安全性 | 4 | リモートMCPサーバーへの接続のため、サーバー側の信頼管理が必要 |
| E8 拡張性 | 5 | Agent SDKとの組み合わせでプログラマブルなMCP活用が可能 |
| E9 代替可能性 | 4 | API側からのMCPアクセスは他に代替手段が少ない |
| E10 今やる意味 | 4 | GA済み。フェーズ3の知識活用基盤構築時に必要 |

- **compared_with**: F-002（プロトコル標準としての MCP）
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: Messages APIからMCPサーバーへの直接接続機能。GA済みで追加コストなし。Agent SDK + MCP Connector の組み合わせでプログラマブルなRAG・検索基盤が構築可能。フェーズ3で積極的に活用する
- **unresolved_points**: Claude Code settings.jsonのMCP設定方式とAPI側MCP Connectorの役割分担が未定
- **next_review_condition**: フェーズ3でプログラマブルなMCPサーバー統合を設計するとき
- **next_action**: Agent SDKとMCP Connectorを組み合わせたプロトタイプを設計する

---

#### F-038 | MCP Inspector

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | MCPサーバーの開発・デバッグツール。直接的な参謀機能ではないが MCP 開発に不可欠 |
| E2 役割明確性 | 5 | 「MCP公式の視覚的テスト・デバッグツール」と明確 |
| E4 流用可能性 | 5 | MCP公式ツールとして全面流用可能 |
| E5 導入難易度 | 4 | Node.js必要だが、npx経由で即実行可能 |
| E6 保守性 | 5 | modelcontextprotocol公式。9k stars。活発 |
| E7 安全性 | 5 | MCP公式ツール。信頼境界明確 |
| E8 拡張性 | 4 | MCPサーバー開発を加速し、拡張性向上を間接的に支援 |
| E9 代替可能性 | 5 | MCP公式デバッグツールは他に代替なし |
| E10 今やる意味 | 3 | フェーズ3〜4でMCPサーバーを本格開発する際に重要 |

- **compared_with**: F-023（mcp-eval）
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: MCP公式の視覚的テストツール。MCPサーバーの開発・デバッグ・動作確認に必要不可欠。9k stars・公式ツールで信頼性が高い。フェーズ3でMCPサーバーを構築・テストする際に即活用する
- **unresolved_points**: 本プロジェクトで構築するMCPサーバーの設計が未定
- **next_review_condition**: フェーズ3でMCPサーバーを開発・テストするとき
- **next_action**: フェーズ3でMCPサーバー開発を開始した際に即活用する

---

### CG-05｜実行エージェント管理層

> 比較の問い: タスク実行を担うエージェントの管理・制御をどう実現するか

#### F-003 | Subagents

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | Claude Code内でのタスク委譲・並列実行。AI参謀基盤の中核機能として既に活用中 |
| E2 役割明確性 | 5 | 「専門化されたタスクを担うClaude Codeサブエージェント」と明確 |
| E3 導入価値 | 5 | コンテキスト分離・並列実行・専門化が即効で実現。本プロジェクトで既に実証済み |
| E4 流用可能性 | 5 | .claude/agents/*.md 定義で全面流用可能 |
| E5 導入難易度 | 5 | Claude Code標準機能。設定ファイルだけで使用可能 |
| E6 保守性 | 5 | Anthropic公式GA機能 |
| E7 安全性 | 5 | 独立コンテキスト・権限管理が明確 |
| E8 拡張性 | 5 | 16フロントマターフィールドで高い拡張性。worktree分離も可能 |
| E9 代替可能性 | 5 | Claude Code内でのsubagent機能は他に代替なし |
| E10 今やる意味 | 5 | 今すぐ使える。既に活用中。フェーズ2〜5で中核的な役割 |

- **compared_with**: F-006, F-008, F-009
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P1
- **reason_summary**: 既に本プロジェクトで実装・活用済みのAI参謀基盤の中核機能。16フロントマターフィールド・worktree分離・ビルトインエージェントで高い拡張性を持つ。採用確定
- **unresolved_points**: subagentsのネスト禁止制約（subagentはsubagentを起動できない）への対処方法
- **next_review_condition**: Agent Teams（F-008）がGAになった時点で協調設計を見直す
- **next_action**: 本プロジェクトの各フェーズ作業で継続活用。フロントマター16フィールドの全活用を検討する

---

#### F-006 | Claude Managed Agents

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | フルマネージドエージェントHarness。本番運用コスト削減・セキュアサンドボックスに有用 |
| E2 役割明確性 | 4 | 「AnthropicホストのフルマネージドエージェントHarness」と明確 |
| E3 導入価値 | 3 | betaのため即採用はリスクあり。GAになれば本番エージェント運用コストを大幅削減 |
| E4 流用可能性 | 3 | beta APIの変更リスクあり |
| E5 導入難易度 | 3 | betaヘッダー必要。Agent/Environment/Session/Eventsの概念モデルの習得が必要 |
| E6 保守性 | 3 | 2026-04-08公開ベータ。成熟度不明 |
| E7 安全性 | 4 | Anthropicホスト。セキュアサンドボックス内蔵 |
| E8 拡張性 | 4 | SSEストリーミング・セッション管理が内蔵。マルチエージェント機能はresearch preview |
| E9 代替可能性 | 4 | フルマネージドエージェントHarnessは他に代替なし（この特性において） |
| E10 今やる意味 | 3 | betaのため今すぐ採用は時期尚早。GAに移行後に本格検討 |

- **compared_with**: F-003, F-009
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P4
- **reason_summary**: 2026-04-08公開ベータの最新機能。フルマネージドで運用コスト削減の可能性が高いが、beta APIの変更リスクがある。GAに移行したタイミングで本格評価し、Subagents/Agent SDKとの使い分けを確定させる
- **unresolved_points**: GA移行タイムラインが未確認。outcomes/multiagent/memoryのresearch preview機能の詳細が未調査
- **next_review_condition**: managed-agents-2026-04-01 betaヘッダーが不要になってGAになったとき
- **next_action**: リリースノートでGA移行を追跡。GA後に基本的なエージェントタスクで試験導入

---

#### F-005 | Skills

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | 再利用可能なワークフローパッケージ。AI参謀基盤のノウハウ蓄積・共有に直接有用 |
| E2 役割明確性 | 5 | 「SKILL.md形式の再利用可能ワークフローパッケージ」と明確 |
| E3 導入価値 | 5 | チームのノウハウをパッケージ化して共有・再利用できる。本プロジェクトで既に活用中 |
| E4 流用可能性 | 5 | SKILL.md形式で全面流用可能。.claude/skills/に配置するだけ |
| E5 導入難易度 | 5 | .claude/skills/ に配置するだけ |
| E6 保守性 | 5 | Anthropic公式GA。agentskills.ioオープン標準採用済み |
| E7 安全性 | 5 | ローカル実行。権限管理が明確 |
| E8 拡張性 | 5 | 12フロントマターフィールドで高い拡張性。subagent実行も可能 |
| E9 代替可能性 | 5 | SKILL.md形式のスキルパッケージは公式機能として唯一 |
| E10 今やる意味 | 5 | GA済み。本プロジェクトで活用中 |

- **compared_with**: F-013, F-031
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P1
- **reason_summary**: 本プロジェクトで既に活用中の中核機能。動的コンテキスト注入・subagent実行・12フロントマターフィールドで高い拡張性を持つ。採用確定
- **unresolved_points**: supporting files（template.md等）の活用パターンが未検討
- **next_review_condition**: Agent Skills API（betaヘッダー skills-2025-10-02）の詳細が確認されたとき
- **next_action**: 本プロジェクトのフェーズ2以降で継続活用。supporting filesの活用パターンを探索する

---

#### F-015 | claude-agent-sdk-python

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | Python実装のAgent SDK。カスタムエージェント・本番パイプライン構築の中核 |
| E2 役割明確性 | 5 | 「Python実装のClaude Agent SDK」と明確 |
| E3 導入価値 | 5 | pip install で即使用。非同期インターフェース対応。CI/CDパイプライン構築に直結 |
| E4 流用可能性 | 5 | pip install claude-agent-sdk で全面流用 |
| E5 導入難易度 | 5 | pip install のみ |
| E6 保守性 | 5 | Anthropic公式。6k stars。CHANGELOGあり |
| E7 安全性 | 5 | 公式SDK |
| E8 拡張性 | 5 | F-009の完全制御機能をPythonで実装可能 |
| E9 代替可能性 | 5 | 公式Python SDKは唯一 |
| E10 今やる意味 | 5 | 今すぐ使える。フェーズ3〜5で本番エージェント構築に必要 |

- **compared_with**: F-016
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P2
- **reason_summary**: Anthropic公式Python SDK。フェーズ3〜5で本番エージェントを構築する際の中核ライブラリ。pip install で即使用可能。採用確定
- **unresolved_points**: AWS Bedrock / Google Vertex AI経由での利用方法が未詳細確認
- **next_review_condition**: 本番エージェント構築フェーズ（フェーズ3〜4）を開始するとき
- **next_action**: フェーズ3でエージェントパイプラインの構築を開始するときに導入

---

#### F-016 | claude-agent-sdk-typescript

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | TypeScript実装のAgent SDK。Node.js環境でのエージェント開発に有用 |
| E2 役割明確性 | 5 | 「TypeScript実装のClaude Agent SDK」と明確 |
| E3 導入価値 | 4 | npm install で即使用 |
| E4 流用可能性 | 5 | npm install で全面流用 |
| E5 導入難易度 | 5 | npm install のみ |
| E6 保守性 | 4 | Anthropic公式。1k stars（Python版より少ない） |
| E7 安全性 | 5 | 公式SDK |
| E8 拡張性 | 4 | TypeScript環境でのエージェント開発が可能 |
| E9 代替可能性 | 4 | 公式TypeScript SDKは唯一だが、Python版が主流 |
| E10 今やる意味 | 4 | TypeScript環境では必要。promptfooがNode.js環境なので親和性あり |

- **compared_with**: F-015
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: TypeScript環境でのエージェント開発に有用。Python版より小規模だが公式サポートあり。promptfooや他のNode.jsツールとの統合に価値がある
- **unresolved_points**: Python版との機能パリティが未確認
- **next_review_condition**: TypeScript/Node.js環境でのエージェント構築が必要になったとき
- **next_action**: TypeScript環境を使うフェーズで採用検討

---

#### F-013 | anthropics/skills

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | Skills公式リポジトリ・マーケットプレイス。AI参謀基盤のスキル資産として直接活用可能 |
| E2 役割明確性 | 5 | 「Agent Skillsの公式リポジトリ/マーケットプレイス（115k stars）」と明確 |
| E3 導入価値 | 5 | 既製スキルを直接流用可能。独自スキル開発のリファレンスになる |
| E4 流用可能性 | 5 | スキルをコピーするだけで流用可能 |
| E5 導入難易度 | 5 | Claude Codeがあれば即使用可能 |
| E6 保守性 | 5 | Anthropic公式。115k stars。活発 |
| E7 安全性 | 5 | 公式Anthropicリポジトリ |
| E8 拡張性 | 5 | 新しいスキルの追加が容易 |
| E9 代替可能性 | 5 | 公式スキルマーケットプレイスは唯一 |
| E10 今やる意味 | 5 | 今すぐ活用できる最大のスキル資産 |

- **compared_with**: F-005, F-031
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P2
- **reason_summary**: 115k starsのAnthropic公式スキルリポジトリ。AI参謀基盤で必要なスキルの多くをここから流用・学習できる。採用確定
- **unresolved_points**: リポジトリ内の具体的なスキル一覧と本プロジェクトへの適用可能性が未確認
- **next_review_condition**: 新しいワークフローをスキルとして定義するとき
- **next_action**: リポジトリの具体的なスキル一覧を確認し、本プロジェクトに流用できるスキルを探索する

---

### CG-06｜フェーズ2支援部品系

> 比較の問い: 今回のフェーズ2作業そのものの効率・品質を高める部品をどう選定するか

#### F-032 | promptfoo（CG-06での評価）

CG-03でメイン評価済み。CG-06での観点: フェーズ2支援部品としての判定

- **decision_state**: D1（採用候補）- フェーズ2支援部品として最有力
- **build_vs_buy_state**: B1
- **reason_summary**（CG-06観点）: Node.js更新後に候補モデルのA/B比較・プロンプト品質評価をYAML設定で実行できる。フェーズ2の評価作業に最も直接的に貢献する支援部品

---

#### F-022 | LiteLLM（CG-06での評価）

CG-01でメイン評価済み。CG-06での観点: フェーズ2支援部品としての判定

- **decision_state**: D2（試験導入候補）- promptfooと組み合わせで評価パイプライン構築
- **build_vs_buy_state**: B1
- **reason_summary**（CG-06観点）: venv内でインストールし、promptfooと組み合わせてマルチモデル評価パイプラインを構築できる。フェーズ2の候補評価に補完的な価値がある

---

#### F-023 | mcp-eval（CG-06での評価）

CG-03でメイン評価済み。不採用確定（D4）

---

#### F-037 | mcp-use

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | MCPアプリ開発フレームワーク。AI参謀基盤の将来的なMCP構築に有用だがフェーズ2では限定的 |
| E2 役割明確性 | 4 | 「MCPのフルスタックフレームワーク（開発+構築の統合）」と明確 |
| E3 導入価値 | 2 | フェーズ2の評価・比較作業への直接効果が低い |
| E4 流用可能性 | 3 | TypeScript。セットアップ中程度 |
| E5 導入難易度 | 3 | TypeScript環境のセットアップが必要 |
| E6 保守性 | 4 | 10k stars、日次更新 |
| E7 安全性 | 4 | OSSで透明性あり |
| E8 拡張性 | 4 | MCPサーバー+アプリ開発を統合 |
| E9 代替可能性 | 3 | MCP Inspector・mcp-agentとの差別化はフルスタック統合 |
| E10 今やる意味 | 2 | フェーズ3〜4のMCPサーバー開発フェーズで再評価が適切 |

- **compared_with**: F-023, F-038
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P4
- **reason_summary**: 10k starsのMCPフルスタックフレームワーク。フェーズ2では直接的な効果が低いが、フェーズ3〜4でMCPサーバーを本格開発する際にMCP Inspectorと比較評価する価値がある
- **unresolved_points**: MCP Inspector（F-038）とmcp-use（F-037）の役割分担（開発支援vs全スタック管理）が未確認
- **next_review_condition**: フェーズ3〜4でMCPサーバーを本格開発するとき
- **next_action**: フェーズ3でMCP開発を開始する際にMCP Inspectorと比較評価する

---

## パート2｜独立評価候補

> 比較グループに属さない候補の個別評価

### F-001 | Prompt Improver

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | プロンプト品質向上。AI参謀基盤のプロンプトエンジニアリングに有用 |
| E2 役割明確性 | 4 | 「Console上でのプロンプト自動改善ツール」と明確 |
| E3 導入価値 | 3 | プロンプト品質向上に役立つが、手動操作のツール |
| E4 流用可能性 | 4 | Consoleから即使用可能 |
| E5 導入難易度 | 5 | Consoleアカウントがあれば即使用 |
| E6 保守性 | 5 | Anthropic公式GA |
| E7 安全性 | 5 | Anthropic Console内で動作 |
| E8 拡張性 | 2 | Console限定ツール。API統合なし |
| E9 代替可能性 | 4 | Claude自身によるプロンプト改善は他に代替なし |
| E10 今やる意味 | 3 | 今使えるが、フェーズ5のプロンプト最適化で本格活用 |

- **compared_with**: なし（独立評価）
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: Consoleから即使用可能な公式プロンプト改善ツール。AI参謀エージェントのシステムプロンプト最適化に役立つ。API統合がないためフロー自動化には限界があるが、手動でのプロンプト品質向上に有効
- **unresolved_points**: API統合の有無（自動パイプラインへの組み込み可否）が未確認
- **next_review_condition**: AI参謀エージェントのシステムプロンプト改善が必要になったとき
- **next_action**: フェーズ2以降でシステムプロンプト最適化が必要になった際に試用する

---

### F-004 | Hooks

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | Claude Codeライフサイクル制御。AI参謀基盤の安全性・自動化に直接必須 |
| E2 役割明確性 | 5 | 「Claude Codeライフサイクルでの自動実行アクション（24+イベント）」と明確 |
| E3 導入価値 | 5 | 正本保護・危険コマンドブロック・自動化が即実現。本プロジェクトで既に活用中 |
| E4 流用可能性 | 5 | settings.jsonで全面流用可能。本プロジェクトで既に使用中 |
| E5 導入難易度 | 5 | settings.jsonのhooksキーに記述するだけ |
| E6 保守性 | 5 | Anthropic公式GA。24+イベント |
| E7 安全性 | 5 | 正本文書保護等のセキュリティ強化に直結。本プロジェクトで実証済み |
| E8 拡張性 | 5 | 24+イベント・4種類の実装タイプ（command/HTTP/prompt/agent）で高い拡張性 |
| E9 代替可能性 | 5 | Claude Codeライフサイクルフックは公式機能として唯一 |
| E10 今やる意味 | 5 | 今すぐ使える。本プロジェクトで既に活用中 |

- **compared_with**: なし（独立評価）
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P1
- **reason_summary**: 本プロジェクトで既に実装・活用済みの中核機能（protect-canonical.sh）。24+イベント・4種類の実装タイプで高い拡張性を持つ。採用確定。Phase 1記録のイベント数誤記（10→24+）はグループ2で補正済み
- **unresolved_points**: HTTPフック・Promptフック・Agentフックの詳細設定方法が未検討
- **next_review_condition**: 追加の自動化フックが必要になったとき
- **next_action**: 継続活用。HTTPフック・Agentフックの高度な活用パターンを探索する

---

### F-007 | Cowork

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | ナレッジワーカー向けAIアシスタント。AI参謀基盤とは異なる製品カテゴリ |
| E2 役割明確性 | 3 | Research preview。API仕様未確認で役割が不明確 |
| E3 導入価値 | 2 | API仕様未公開のため開発者としての活用方法が不明 |
| E4 流用可能性 | 1 | API仕様未確認のため流用不可 |
| E5 導入難易度 | 1 | アクセス方法不明 |
| E6 保守性 | 2 | Research preview。成熟度低 |
| E7 安全性 | — | 詳細未確認 |
| E8 拡張性 | 1 | API仕様未公開のため拡張方法不明 |
| E9 代替可能性 | 3 | PC上での自律作業という独自カテゴリ |
| E10 今やる意味 | 1 | API仕様未確認のため今は使えない |

- **compared_with**: なし（独立評価）
- **decision_state**: D5（監視継続）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P5
- **reason_summary**: Research previewのナレッジワーカー向け自律AI製品。Claude Desktop appからのみアクセス可能でAPI仕様が未公開。AI参謀基盤構築という本プロジェクトの目的には現時点では合致しない
- **unresolved_points**: 一般開発者向けAPIの有無・アクセス方法が未確認
- **next_review_condition**: API仕様が公開されたとき。またはGAに移行したとき
- **next_action**: 監視継続。APIアクセスが可能になった時点で再評価する

---

### F-010 | GitHub Actions for Claude Code

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | GitHub CI/CDへのClaude Code統合。AI参謀基盤のCI/CD自動化に直結 |
| E2 役割明確性 | 5 | 「GitHub ActionsからClaude Codeを実行する統合機能」と明確 |
| E3 導入価値 | 4 | PRレビュー・issue対応の自動化が実現 |
| E4 流用可能性 | 5 | claude-code-actionを使って全面流用可能 |
| E5 導入難易度 | 4 | GitHub Actions YAMLの設定が必要だが、公式actionで簡素化 |
| E6 保守性 | 5 | Anthropic公式GA |
| E7 安全性 | 4 | GitHub tokenとAPIキーの管理が必要 |
| E8 拡張性 | 4 | GitLab CI/CDへの拡張も可能 |
| E9 代替可能性 | 5 | Anthropic公式GitHub Actions integrationは唯一 |
| E10 今やる意味 | 4 | 今すぐ使える。CI/CD自動化で即効果 |

- **compared_with**: F-014, F-011
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P2
- **reason_summary**: PRレビュー・issue対応・CI自動化に即使える公式機能。anthropics/claude-code-action（F-014）を実装体として利用。AI参謀基盤の開発フローを自動化するうえで重要な統合ポイント
- **unresolved_points**: 本プロジェクトのGitHub ActionsワークフローへのClaude Code統合の具体的な設計が未定
- **next_review_condition**: PRレビューや issue 対応を自動化するとき
- **next_action**: 本プロジェクトのGitHubリポジトリにClaude Code Actionsを設定し、PR自動レビューを試験導入する

---

### F-011 | Cloud Scheduled Tasks

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | 定期タスク自動実行。AI参謀基盤の継続的監視・更新に有用 |
| E2 役割明確性 | 5 | 「Anthropic管理インフラでのcronスケジュール実行」と明確 |
| E3 導入価値 | 4 | ローカルPCなしで定期タスクが動作。PR review・依存関係監査等の継続監視が実現 |
| E4 流用可能性 | 5 | Claudeサブスクリプションで全面流用可能 |
| E5 導入難易度 | 5 | /scheduleコマンドまたはDesktop appから設定 |
| E6 保守性 | 5 | Anthropic公式GA |
| E7 安全性 | 4 | Anthropicインフラで実行。APIキーの管理が必要 |
| E8 拡張性 | 4 | 定期実行と組み合わせて様々な自動化が可能 |
| E9 代替可能性 | 5 | Anthropic公式のクラウドスケジュール実行は唯一 |
| E10 今やる意味 | 4 | 今すぐ使える。継続的な情報更新・監視に有用 |

- **compared_with**: F-010
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P3
- **reason_summary**: ローカルPC不要のクラウドcronスケジュール実行。AI参謀基盤の継続的な情報収集・監視タスクを自動化するうえで有用。/scheduleコマンドで簡単に設定可能
- **unresolved_points**: Desktop版（ローカル実行）とCloud版（Anthropicインフラ）の使い分け基準が未定
- **next_review_condition**: 定期的な監視・更新タスクが必要になったとき
- **next_action**: フェーズ3以降で定期情報更新タスクを設計し、/scheduleコマンドで試験導入する

---

### F-012 | Advisor Tool

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | executor+advisorペアリング。AI参謀基盤のコスト最適化に直接有用 |
| E2 役割明確性 | 4 | 「高速executorと高知能advisorのペアリング機能」と明確 |
| E3 導入価値 | 4 | 長期エージェントタスクのコスト削減効果が期待できる |
| E4 流用可能性 | 3 | betaヘッダー必要。API変更リスクあり |
| E5 導入難易度 | 3 | betaヘッダー必要。ペアリング設定の学習が必要 |
| E6 保守性 | 3 | 2026-04-09公開ベータ。成熟度不明 |
| E7 安全性 | 4 | Anthropic公式betaの信頼境界 |
| E8 拡張性 | 4 | 将来的に参謀エージェントのコスト最適化機能の核になりうる |
| E9 代替可能性 | 5 | executor+advisor ペアリングは他に代替なし |
| E10 今やる意味 | 3 | betaのため今すぐ採用は時期尚早。GAに移行後に本格検討 |

- **compared_with**: なし（独立評価）
- **decision_state**: D3（保留）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P4
- **reason_summary**: 2026-04-09公開ベータの最新機能。AI参謀基盤のコスト最適化に直接寄与する可能性がある（高知能advisor + 高速executorのペアリング）。betaの変更リスクがあるため本格採用はGA移行後
- **unresolved_points**: advisor-executor間のコンテキスト共有方式・pricing詳細が未確認
- **next_review_condition**: advisor-tool-2026-03-01 betaヘッダーが不要になってGAになったとき
- **next_action**: GAになったタイミングで基本的なエージェントタスクで試験導入する

---

### F-014 | anthropics/claude-code-action

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | GitHub Actions実装体。F-010（GitHub Actions機能）の実装実体 |
| E2 役割明確性 | 5 | 「GitHub ActionsでのClaude Code実行action（7k stars）」と明確 |
| E3 導入価値 | 4 | 1 YAMLファイルでClaude CodeをGitHub CI/CDに統合 |
| E4 流用可能性 | 5 | GitHub ActionsのYAMLで全面流用可能 |
| E5 導入難易度 | 4 | GitHub Actions設定のみ |
| E6 保守性 | 5 | Anthropic公式。7k stars |
| E7 安全性 | 4 | GitHub token・APIキー管理が必要 |
| E8 拡張性 | 4 | GitLab CI/CD対応も |
| E9 代替可能性 | 5 | Anthropic公式GitHub action唯一 |
| E10 今やる意味 | 4 | 今すぐ使える |

- **compared_with**: F-010（機能レイヤー）
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P2
- **reason_summary**: F-010の実装実体。7k starsの公式action。GitHub Actions YAMLを設定するだけで本プロジェクトのCI/CDにClaude Codeを統合できる
- **unresolved_points**: なし（F-010と一体で評価）
- **next_review_condition**: F-010のGitHub Actions設定を開始するとき
- **next_action**: F-010の試験導入と同時に設定する

---

### F-017 | claude-agent-sdk-demos

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | 参考実装集。AI参謀基盤の実装パターン学習に有用 |
| E2 役割明確性 | 4 | 「Claude Agent SDKの公式実装例集」と明確 |
| E3 導入価値 | 3 | email assistant, research agent等の参考実装でパターン学習が可能 |
| E4 流用可能性 | 4 | サンプルコードをそのまま流用可能 |
| E5 導入難易度 | 5 | コードを参照するだけ |
| E6 保守性 | 4 | Anthropic公式。2k stars |
| E7 安全性 | 4 | 参考実装であり本番リスクは低い |
| E8 拡張性 | 3 | 参考実装のため拡張は自前で実施 |
| E9 代替可能性 | 4 | 公式SDKデモ実装は他に代替なし |
| E10 今やる意味 | 3 | SDKを実装する際に参考になる。今すぐ必須ではない |

- **compared_with**: なし（独立評価）
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B3（参考流用）
- **current_priority**: P3
- **reason_summary**: Agent SDKの公式デモ集。email assistant・research agentの実装パターンをAI参謀基盤の設計に流用できる。具体的なデモ一覧の確認が必要
- **unresolved_points**: 具体的なデモ一覧と各デモの実装内容が未確認
- **next_review_condition**: Agent SDK（F-015）を使った本番エージェント実装を開始するとき
- **next_action**: リポジトリを確認し、本プロジェクトに流用できる実装パターンをリストアップする

---

### F-024 | ant CLI

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 3 | Claude API用CLI。開発効率化に有用 |
| E2 役割明確性 | 3 | 詳細ドキュメント未確認のため役割が不完全。「Claude API用CLIツール」との認識 |
| E3 導入価値 | 3 | 詳細不明のため効果が不確定 |
| E4 流用可能性 | — | 詳細未確認 |
| E5 導入難易度 | — | 詳細未確認 |
| E6 保守性 | 3 | 2026-04-08リリース。新しすぎる |
| E7 安全性 | — | 詳細未確認 |
| E8 拡張性 | — | YAMLバージョン管理は将来的に有用 |
| E9 代替可能性 | 3 | Claude API用CLIとして有用 |
| E10 今やる意味 | 2 | 詳細調査が必要。公式ドキュメントURLの確認から始める |

- **compared_with**: なし（独立評価）
- **decision_state**: D3（保留 - 詳細未調査）
- **build_vs_buy_state**: B5（判断保留）
- **current_priority**: P5
- **reason_summary**: 2026-04-08リリースの新しいClaude API用CLI。APIリソースのYAMLバージョン管理とClaude Code統合が特徴と推定されるが、詳細ドキュメントURLが未確認。リリースノートの情報のみで評価困難
- **unresolved_points**: 詳細ドキュメントURL・インストール方法・具体的な機能一覧が未確認
- **next_review_condition**: 公式ドキュメントURLが確認できたとき
- **next_action**: platform.claude.com または code.claude.com でant CLIのドキュメントを探索する

---

### F-031 | Agent Skills Open Standard

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 4 | スキルの標準化。AI参謀基盤のスキル相互運用性に貢献 |
| E2 役割明確性 | 5 | 「Agent Skillsのオープン標準仕様（agentskills.io）」と明確 |
| E3 導入価値 | 3 | 標準仕様への準拠が他ツールとのスキル共有を可能にする |
| E4 流用可能性 | 5 | オープン標準として参照するだけで利用可能 |
| E5 導入難易度 | 5 | 仕様を読むだけ。コスト不要 |
| E6 保守性 | 4 | Microsoft, OpenAI, Atlassian, Figmaが採用済みの標準 |
| E7 安全性 | 5 | オープン標準のため信頼境界の問題なし |
| E8 拡張性 | 5 | クロスプラットフォームなスキル相互運用性を提供 |
| E9 代替可能性 | 5 | Agent Skillsのオープン標準は唯一 |
| E10 今やる意味 | 3 | F-005・F-013の利用時に参照するが、標準仕様自体を直接使うものではない |

- **compared_with**: F-005, F-013
- **decision_state**: D2（試験導入候補）
- **build_vs_buy_state**: B3（参考流用）
- **current_priority**: P3
- **reason_summary**: Microsoft・OpenAI・Atlassian・Figmaが採用済みのオープン標準仕様。F-005（Skills機能）の設計根拠として参照し、クロスプラットフォームなスキル設計の指針として活用する
- **unresolved_points**: 本プロジェクトのスキルがagentskills.io準拠になっているかの確認が未実施
- **next_review_condition**: スキルを他のプラットフォームと共有する必要が生じたとき
- **next_action**: 既存スキル定義がagentskills.io標準に準拠しているか確認する

---

### F-009 | Claude Agent SDK（CG-05メイン評価再掲）

| 評価軸 | スコア | 根拠 |
|--------|--------|------|
| E1 目的一致度 | 5 | Anthropic公式SDK。エージェントループ・コンテキスト管理の完全制御 |
| E2 役割明確性 | 5 | 「Claude Codeのツール・エージェントループ・コンテキスト管理SDK」と明確 |
| E3 導入価値 | 5 | 外部orchestratorなしでもCI/CDパイプラインへのエージェント組み込みが実現 |
| E4 流用可能性 | 5 | pip install / npm install で全面流用可能 |
| E5 導入難易度 | 4 | APIキーのみ。ドキュメント充実 |
| E6 保守性 | 5 | Anthropic公式。継続的なメンテナンスが保証 |
| E7 安全性 | 5 | 公式SDK |
| E8 拡張性 | 5 | subagents・hooks・MCP・sessionsの完全制御 |
| E9 代替可能性 | 5 | Anthropic公式SDKは唯一 |
| E10 今やる意味 | 5 | 今すぐ使える。フェーズ2〜5で中核 |

- **compared_with**: F-027, F-028, F-021
- **decision_state**: D1（採用候補）
- **build_vs_buy_state**: B1（全面流用）
- **current_priority**: P1
- **reason_summary**: Anthropic公式のエージェント構築SDK。LangGraph/CrewAI等の外部orchestratorとの比較基準点として機能。本プロジェクトではまずAgent SDKで実装し、単体では実現できないワークフローが発生した場合に外部orchestratorを追加する方針
- **unresolved_points**: sessions APIの詳細・subagents定義の高度なパターンが未検討
- **next_review_condition**: 本番エージェント構築フェーズ（フェーズ3〜4）を開始するとき
- **next_action**: F-015（Python SDK）を使って基本的なエージェントパイプラインを構築する

---

## パート3｜比較グループ別サマリ

| 比較グループ | 要約 | 推奨方向性 |
|-------------|------|-----------|
| CG-01 router/gateway | LiteLLMが最も汎用性が高くpromptfooとの組み合わせで即活用可能。claude-code-routerはClaude Code特化で有用だが緊急度低。Portkey Gatewayはフェーズ4〜5のガードレール要件が明確になってから | LiteLLMを試験導入し、評価パイプラインを構築。claude-code-routerは本番マルチモデル時に再評価 |
| CG-02 orchestration | Claude Agent SDKが全比較の基準点。まずSDKで実装し、複雑ワークフローが不足した時点でLangGraphを評価する。CrewAI・AutoGenはより後のフェーズへ | Agent SDK (D1) を優先。LangGraph (D3) はフェーズ4で評価。CrewAI・AutoGenは監視継続・保留 |
| CG-03 evaluation | promptfooがPhase 2に最も直接的。deepeval・Arize Phoenixは後続フェーズで相補的に追加。Langfuse・Braintrust・W&B Weaveはフェーズ3以降 | promptfooを最優先で導入。mcp-evalは不採用 |
| CG-04 知識活用 | Memory Tool・MCP・MCP Serversは採用確定。MCP Connector・MCP Registryは試験導入。MCP Inspectorはフェーズ3で活用 | Memory Tool・MCP・MCP Servers (D1) を最優先。他はフェーズ3で順次活用 |
| CG-05 実行エージェント | Subagents・Hooks・Skills・Claude Agent SDK・anthropics/skills は採用確定（既に活用中含む）。Managed Agentsは betaでGAまで保留 | 既採用機能を継続深化。Managed AgentsのGA移行を監視 |
| CG-06 支援部品 | promptfoo（CG-03でD1）がフェーズ2の最優先支援部品。LiteLLM（CG-01でD2）が補完。mcp-useは後続フェーズへ。mcp-evalは不採用 | promptfooを即導入。mcp-useはフェーズ3〜4で再評価 |

---

## パート4｜比較漏れチェック

| item_id | 候補名 | 評価済み | 所属 |
|---------|--------|---------|------|
| F-001 | Prompt Improver | ✓ | 独立評価 |
| F-002 | MCP | ✓ | CG-04 |
| F-003 | Subagents | ✓ | CG-05 |
| F-004 | Hooks | ✓ | 独立評価 |
| F-005 | Skills | ✓ | CG-05 |
| F-006 | Claude Managed Agents | ✓ | CG-05 |
| F-007 | Cowork | ✓ | 独立評価 |
| F-008 | Agent Teams | ✓ | CG-02 |
| F-009 | Claude Agent SDK | ✓ | CG-05 (メイン) / CG-02 (参照) |
| F-010 | GitHub Actions for Claude Code | ✓ | 独立評価 |
| F-011 | Cloud Scheduled Tasks | ✓ | 独立評価 |
| F-012 | Advisor Tool | ✓ | 独立評価 |
| F-013 | anthropics/skills | ✓ | CG-05 |
| F-014 | anthropics/claude-code-action | ✓ | 独立評価 |
| F-015 | claude-agent-sdk-python | ✓ | CG-05 |
| F-016 | claude-agent-sdk-typescript | ✓ | CG-05 |
| F-017 | claude-agent-sdk-demos | ✓ | 独立評価 |
| F-018 | MCP Registry | ✓ | CG-04 |
| F-019 | MCP Servers | ✓ | CG-04 |
| F-020 | claude-code-router | ✓ | CG-01 |
| F-021 | mcp-agent | ✓ | CG-02 |
| F-022 | LiteLLM | ✓ | CG-01 (メイン) / CG-06 (参照) |
| F-023 | mcp-eval | ✓ | CG-03 (メイン) / CG-06 (参照) |
| F-024 | ant CLI | ✓ | 独立評価 |
| F-025 | Memory Tool | ✓ | CG-04 |
| F-026 | MCP Connector | ✓ | CG-04 |
| F-027 | LangGraph | ✓ | CG-02 |
| F-028 | CrewAI | ✓ | CG-02 |
| F-029 | AutoGen | ✓ | CG-02 |
| F-030 | OpenAI Agents SDK | ✓ | CG-02 (比較参照のみ) |
| F-031 | Agent Skills Open Standard | ✓ | 独立評価 |
| F-032 | promptfoo | ✓ | CG-03 (メイン) / CG-06 (参照) |
| F-033 | deepeval | ✓ | CG-03 |
| F-034 | Langfuse | ✓ | CG-03 |
| F-035 | Arize Phoenix | ✓ | CG-03 |
| F-036 | Portkey Gateway | ✓ | CG-01 |
| F-037 | mcp-use | ✓ | CG-06 |
| F-038 | MCP Inspector | ✓ | CG-04 |
| D-004 | Braintrust | ✓ | CG-03 (未昇格) |
| D-005 | W&B Weave | ✓ | CG-03 (未昇格) |

**比較漏れ: なし。38 F-xxx候補 + D-004 + D-005 = 40件 全評価完了。**
