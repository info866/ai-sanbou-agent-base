# 採用状態・自作流用判断・優先順位一覧（Adoption, Build vs Buy & Priority）

> **担当**: グループ4  
> **インプット**: `00`, `01`, `02`, `03`, `04` を読み込んでから着手すること  
> **ステップ対応**: フェーズ2作業指示書 ステップ8（自作/流用判断）＋ ステップ9（優先順位確定）＋ ステップ10（未解決論点整理）  
> **最終更新**: 2026-04-12（グループ4）

---

## この文書の役割

本文書は、`04_candidate_evaluations.md`の評価結果に基づき、全候補の採用状態・自作流用判断・優先順位を確定し、未解決論点を整理する。

---

## パート1｜採用状態一覧

### D1｜採用候補

> 今後の基盤に組み込む方向で優先的に検討・試験すべき（10件）

| item_id | 候補名 | 採用理由（要約） |
|---------|--------|----------------|
| F-002 | MCP | 業界標準の接続プロトコル。Claude Code組み込み済み。フェーズ3〜5の全接続の基盤 |
| F-003 | Subagents | 既に本プロジェクトで活用中。16フロントマターフィールドで高い拡張性。AI参謀基盤の中核機能 |
| F-004 | Hooks | 既に本プロジェクトで活用中（protect-canonical.sh）。24+イベント・4実装タイプで拡張性最高 |
| F-005 | Skills | 既に本プロジェクトで活用中。SKILL.md形式でノウハウをパッケージ化。オープン標準準拠 |
| F-009 | Claude Agent SDK | Anthropic公式SDK。本番エージェント構築の中核。外部orchestratorの比較基準点 |
| F-013 | anthropics/skills | 115k starsの公式スキルマーケットプレイス。流用可能なスキル資産の宝庫 |
| F-015 | claude-agent-sdk-python | 公式Python SDK。フェーズ3〜5の本番エージェント構築の実装基盤 |
| F-019 | MCP Servers | 83k starsの公式MCPサーバーリファレンス実装集。フェーズ3の知識活用基盤構築に直結 |
| F-025 | Memory Tool | GA済みのクロスセッション記憶API。AI参謀基盤の状態継続に必須 |
| F-032 | promptfoo | 20k stars・Anthropic公式使用のLLM評価フレームワーク。フェーズ2支援部品の最有力 |

---

### D2｜試験導入候補

> 本採用前に小さく試す価値が高い（12件）

| item_id | 候補名 | 試験導入の理由・形態 |
|---------|--------|-------------------|
| F-001 | Prompt Improver | Consoleから即使用可能。AI参謀エージェントのシステムプロンプト改善で小さく試す |
| F-010 | GitHub Actions for Claude Code | PRレビュー・issue対応自動化。GitHub Actions YAMLで設定し本プロジェクトCI/CDで試験 |
| F-011 | Cloud Scheduled Tasks | 定期タスク自動実行。/scheduleコマンドで1タスクだけ試験導入する |
| F-014 | anthropics/claude-code-action | F-010の実装体。GitHub Actions設定と同時に試験 |
| F-016 | claude-agent-sdk-typescript | TypeScript/Node.js環境用。promptfooとの統合時に試験導入 |
| F-017 | claude-agent-sdk-demos | 公式デモ集。Agent SDK実装開始前に参照して実装パターンを学習 |
| F-018 | MCP Registry | MCPサーバー選定時に公開APIを活用。APIキー不要で即試用 |
| F-020 | claude-code-router | Claude Code特化モデルルーティング。複数モデル比較時に小さく試す |
| F-022 | LiteLLM | マルチモデル統一API。venv内でインストールしpromptfooと組み合わせて評価パイプライン構築 |
| F-026 | MCP Connector | Messages API経由のMCPサーバー接続。Agent SDKとの組み合わせでフェーズ3に先行試験 |
| F-031 | Agent Skills Open Standard | 既存スキルのagentskills.io準拠確認。スキル設計の指針として参照 |
| F-038 | MCP Inspector | MCPサーバー開発・デバッグ。フェーズ3でMCPサーバーを構築するときに即活用 |

---

### D3｜保留

> 価値はありそうだが時期尚早・情報不足・比較不足で決めない（12件）

| item_id | 候補名 | 保留理由 | 解消条件 |
|---------|--------|---------|---------|
| D-004 | Braintrust | SaaS型LLM evalだが詳細未調査。promptfoo等で代替可能の可能性 | braintrust.devで詳細調査を実施してからCG-03他候補と比較 |
| D-005 | W&B Weave | ML実験管理からLLM評価への拡張だが詳細未調査。W&B依存関係の重さが不明 | W&B Weave単体での導入可否を確認。LangGraph採用時に再評価 |
| F-006 | Claude Managed Agents | 2026-04-08公開ベータ。beta API変更リスクあり | betaヘッダーが不要になりGAになったとき |
| F-012 | Advisor Tool | 2026-04-09公開ベータ。pricing詳細・advisor-executor間の仕様が未確認 | betaヘッダーが不要になりGAになったとき |
| F-021 | mcp-agent | orchestration比較が未完了。Agent SDK+MCP Connectorで代替可能の可能性あり | Agent SDK単体でのMCP統合実装後に不足点を確認してから評価 |
| F-024 | ant CLI | 詳細ドキュメントURLが未確認。リリースノートの情報のみ | 公式ドキュメントでant CLIの詳細機能を確認 |
| F-027 | LangGraph | フェーズ4向け。学習コストと依存関係の重さが現フェーズには過剰 | フェーズ4実行基盤設計時、またはAgent SDK単体では実現困難な複雑ワークフローが発生したとき |
| F-028 | CrewAI | フェーズ4向け。LangGraphの評価後に補完的な役割があるか判断 | フェーズ4でロール明確なチーム型エージェントが必要になったとき |
| F-033 | deepeval | promptfoo確立後に追加。Python-nativeメトリクス評価はフェーズ3以降 | promptfooを確立してPythonメトリクス評価が必要になったとき |
| F-034 | Langfuse | フェーズ3向け。Docker+PostgreSQLのセットアップコストが現フェーズに過剰 | フェーズ3でオブザーバビリティ基盤を構築するとき |
| F-035 | Arize Phoenix | フェーズ3向け。Langfuseとの比較後に採否決定 | フェーズ3でLangfuseと比較評価するとき |
| F-037 | mcp-use | フェーズ3〜4向け。MCP InspectorとMCP Serverで代替可能な可能性 | フェーズ3〜4でMCPサーバーを本格開発するとき |

---

### D4｜不採用

> 現時点では使わない（理由と再検討条件を記録）（2件）

| item_id | 候補名 | 不採用理由 | 再検討条件 |
|---------|--------|----------|-----------|
| F-023 | mcp-eval | Stars=20、7ヶ月更新なし。事実上メンテナンス停止。promptfoo・MCP Inspectorで代替可能 | mcp-evalがActiveになりstars 500超え・定期更新が確認されたとき |
| F-030 | OpenAI Agents SDK | Anthropicエコシステムの採用対象外。設計比較・差別化確認のための参照として記録するのみ | Anthropic-OpenAI間のモデル切替が必要になった場合（LiteLLM経由で管理する方が現実的） |

---

### D5｜監視継続

> 今は使わないが、更新や成熟度の変化を追う（4件）

| item_id | 候補名 | 監視理由 | 再評価トリガー |
|---------|--------|---------|--------------|
| F-007 | Cowork | Research preview。API仕様未公開。一般開発者向けAPIの有無が不明 | API仕様が公開されたとき、またはGAに移行したとき |
| F-008 | Agent Teams | 実験的機能。セッション再開不可等の制限多数。コストがSubagentsより大幅に高い | 実験的フラグが外れてGAになったとき |
| F-029 | AutoGen | LLMコール20+/タスクのコスト問題。フェーズ5の高精度推論で検討価値あり | コスト問題の改善報告、またはフェーズ5で高精度推論要件が確定したとき |
| F-036 | Portkey Gateway | 現フェーズではLiteLLMで十分。ガードレール機能はフェーズ4〜5以降で必要 | フェーズ4〜5でガードレール要件が明確化されたとき |

---

## パート2｜自作 / 流用判断一覧

### B1｜全面流用

> 既存資産をそのまま基盤として採用する価値が高い（15件）

| item_id | 候補名 | 全面流用の理由 |
|---------|--------|--------------|
| F-001 | Prompt Improver | Consoleから即使用可能 |
| F-002 | MCP | Claude Code組み込み済みの標準プロトコル |
| F-003 | Subagents | .claude/agents/*.md 定義で全面流用可能 |
| F-004 | Hooks | settings.jsonのhooksキーに記述するだけ |
| F-005 | Skills | .claude/skills/に配置するだけ |
| F-009 | Claude Agent SDK | pip install / npm install で全面流用可能 |
| F-010 | GitHub Actions | anthropics/claude-code-actionのYAMLで全面流用 |
| F-011 | Cloud Scheduled Tasks | /scheduleコマンドで全面流用 |
| F-013 | anthropics/skills | スキルをコピーするだけで流用可能 |
| F-014 | anthropics/claude-code-action | GitHub Actions YAMLで全面流用可能 |
| F-015 | claude-agent-sdk-python | pip install claude-agent-sdk で全面流用 |
| F-019 | MCP Servers | 公式リポジトリからのコード流用が可能 |
| F-025 | Memory Tool | APIに組み込むだけで全面流用可能 |
| F-026 | MCP Connector | 既存API呼び出しに追加するだけ |
| F-032 | promptfoo | npx promptfoo@latest で全面流用可能 |

---

### B2｜部分流用

> 一部機能・一部設計のみ流用し、自作補完する（5件）

| item_id | 候補名 | 流用する部分 | 自作補完する部分 |
|---------|--------|------------|----------------|
| F-016 | claude-agent-sdk-typescript | npm install で SDK部分を全面流用 | TypeScript固有のエージェント設計・統合パターンを自作 |
| F-018 | MCP Registry | 公開APIをそのまま活用 | MCPサーバー選定基準・管理ルールを自作 |
| F-020 | claude-code-router | OSSをそのまま流用 | Claude Code設定との統合部分を調整 |
| F-022 | LiteLLM | pip install で SDK部分を全面流用 | マルチモデル比較設定・コスト管理ポリシーを自作 |
| F-038 | MCP Inspector | npxで全面流用 | MCPサーバーのテストケース設計を自作 |

---

### B3｜参考流用

> 設計思想や構成だけ参考にし、実装は自作する（3件）

| item_id | 候補名 | 参考にする設計思想 |
|---------|--------|-----------------|
| F-017 | claude-agent-sdk-demos | email assistant・research agentの実装パターンをAI参謀基盤の設計に参照 |
| F-030 | OpenAI Agents SDK | handoffs・guardrails・tracingの設計パターンをClaude Agent SDKとの比較に参照 |
| F-031 | Agent Skills Open Standard | SKILL.md形式のオープン標準仕様をスキル設計の指針として参照 |

---

### B4｜自作優先

> 既存候補では要件に合わず、自作した方がよい（0件）

現フェーズでは自作優先の判断に達した候補なし。候補はB5（判断保留）で扱っている。

---

### B5｜判断保留

> 追加比較・追加調査が必要でまだ決めない（17件）

| item_id | 候補名 | 保留理由 | 必要な追加情報 |
|---------|--------|---------|-------------|
| D-004 | Braintrust | 詳細未調査 | 機能・価格・OSS版の有無 |
| D-005 | W&B Weave | 詳細未調査 | W&B本体との依存関係の重さ |
| F-006 | Claude Managed Agents | beta API変更リスク | GA移行タイムライン |
| F-007 | Cowork | API仕様未確認 | 一般開発者向けAPIの有無 |
| F-008 | Agent Teams | 実験的機能 | GA移行のロードマップ |
| F-012 | Advisor Tool | beta API変更リスク | GA移行タイムライン・pricing |
| F-021 | mcp-agent | orchestration比較未完了 | Agent SDK単体との機能差 |
| F-023 | mcp-eval | D4（不採用）のため実質不要 | — |
| F-024 | ant CLI | 詳細ドキュメント未確認 | 公式ドキュメントURL・機能一覧 |
| F-027 | LangGraph | フェーズ4向け | Agent SDK単体での限界値の確認 |
| F-028 | CrewAI | フェーズ4向け | LangGraph評価後の比較結果 |
| F-029 | AutoGen | コスト問題 | コスト改善報告 |
| F-033 | deepeval | promptfoo確立後に判断 | promptfooとの役割分担設計 |
| F-034 | Langfuse | フェーズ3向け | セルフホストコスト・クラウド版評価 |
| F-035 | Arize Phoenix | フェーズ3向け | Langfuseとの比較評価 |
| F-036 | Portkey Gateway | LiteLLMで十分 | フェーズ4〜5のガードレール要件明確化 |
| F-037 | mcp-use | フェーズ3〜4向け | MCP Inspectorとの役割分担 |

---

## パート3｜優先順位一覧

### P1｜最優先（次フェーズで必ず深掘り・再利用・試験導入判断に進む）

| item_id | 候補名 | 最優先の理由 |
|---------|--------|------------|
| F-002 | MCP | 全フェーズの接続基盤。今すぐ深掘り必要 |
| F-003 | Subagents | 既採用・中核機能。高度な活用パターンを深掘りする |
| F-004 | Hooks | 既採用・中核機能。HTTPフック・Agentフックの高度活用を探索 |
| F-005 | Skills | 既採用・中核機能。supporting filesの活用パターンを深掘り |
| F-009 | Claude Agent SDK | 本番エージェント構築の核。フェーズ3で必ず使う |
| F-025 | Memory Tool | GA済み・クロスセッション記憶の唯一の公式実装。即活用 |

---

### P2｜高優先（最優先の直後に扱う）

| item_id | 候補名 | 高優先の理由 |
|---------|--------|------------|
| F-010 | GitHub Actions for Claude Code | CI/CD自動化で開発フロー全体の品質が向上 |
| F-013 | anthropics/skills | 115k starsのスキル資産。流用可能なスキルの把握が先行投資になる |
| F-014 | anthropics/claude-code-action | F-010の実装体。同時に設定する |
| F-015 | claude-agent-sdk-python | フェーズ3〜5の本番エージェント構築基盤 |
| F-019 | MCP Servers | フェーズ3の知識活用基盤構築に直結するリファレンス実装集 |
| F-032 | promptfoo | フェーズ2の評価作業に最も直接的な効果がある支援部品 |

---

### P3｜中優先（今すぐではないが価値あり）

| item_id | 候補名 |
|---------|--------|
| F-001 | Prompt Improver |
| F-011 | Cloud Scheduled Tasks |
| F-016 | claude-agent-sdk-typescript |
| F-017 | claude-agent-sdk-demos |
| F-018 | MCP Registry |
| F-020 | claude-code-router |
| F-022 | LiteLLM |
| F-026 | MCP Connector |
| F-031 | Agent Skills Open Standard |
| F-038 | MCP Inspector |

---

### P4｜低優先（監視継続で足りる）

| item_id | 候補名 |
|---------|--------|
| D-004 | Braintrust |
| D-005 | W&B Weave |
| F-006 | Claude Managed Agents |
| F-012 | Advisor Tool |
| F-021 | mcp-agent |
| F-027 | LangGraph |
| F-028 | CrewAI |
| F-033 | deepeval |
| F-034 | Langfuse |
| F-035 | Arize Phoenix |
| F-036 | Portkey Gateway |
| F-037 | mcp-use |

---

### P5｜凍結（再評価条件成立まで積極的に扱わない）

| item_id | 候補名 | 凍結理由 | 再評価条件 |
|---------|--------|---------|-----------|
| F-007 | Cowork | API仕様未公開のため開発者向けの活用方法が確立できない | API仕様公開またはGA移行 |
| F-008 | Agent Teams | 実験的機能・制限多数・コスト高 | GA移行 |
| F-023 | mcp-eval | 事実上停止プロジェクト | stars 500超え・定期更新再開 |
| F-024 | ant CLI | 詳細ドキュメント未確認 | 公式ドキュメントURLの確認と機能理解 |
| F-029 | AutoGen | コスト20+LLMコール/タスクで本番利用困難 | コスト問題の改善、またはフェーズ5高精度推論要件 |
| F-030 | OpenAI Agents SDK | Anthropicエコシステムでの採用対象外 | Anthropic-OpenAI間のモデル切替が必要になった場合 |

---

## パート4｜フェーズ2支援部品の採用可否

> CG-06の候補について、フェーズ2内での利用判断を記録する。

| 候補名 | 判定 | 理由 | 利用開始時期 |
|--------|------|------|------------|
| promptfoo (F-032) | **今すぐ試す** | 20k stars・Anthropic公式使用・YAML宣言的設定でモデル比較が容易。Node.js更新（v22.22+）後に即活用 | Node.js更新後すぐ |
| LiteLLM (F-022) | **小さく試す** | 43k stars・pip一発・promptfooと組み合わせで評価パイプライン構築可能 | promptfoo設定後にvenv内で試験 |
| mcp-use (F-037) | **後続フェーズで扱う** | フェーズ2の評価・比較作業への直接効果が低い。フェーズ3〜4のMCP開発で再評価 | フェーズ3〜4 |
| mcp-eval (F-023) | **見送り（不採用）** | stars=20・7ヶ月更新なし。promptfoo・MCP Inspectorで代替可能 | — |
| deepeval (F-033) | **後続フェーズで扱う** | promptfoo確立後に追加。Python-nativeメトリクス評価はフェーズ3以降 | promptfoo確立後（フェーズ3） |

---

## パート5｜未解決論点と再調査条件

### 追加比較が必要な論点

| # | 論点 | 理由 | 必要な情報 |
|---|------|------|-----------|
| 1 | Claude Agent SDK単体 vs LangGraph の能力境界 | orchestration判断の最重要論点。SDKで実現できないワークフローが発生したらLangGraph採用の根拠になる | Agent SDK単体での複雑ワークフロー実装とその限界値の確認 |
| 2 | LiteLLM vs Portkey Gateway の選択基準 | フェーズ4〜5でガードレール要件が明確になったときに再浮上する | ガードレール要件の定義。LiteLLMのガードレール機能の有無確認 |
| 3 | Langfuse vs Arize Phoenix の選択 | フェーズ3でオブザーバビリティ基盤を構築するときに必要 | セルフホストのメンテナンスコスト比較、クラウド版の無料枠評価 |
| 4 | Memory Tool API vs CLAUDE.mdのauto memoryの役割分担 | 両方とも使っている本プロジェクトで重複管理のリスク | 各機能の保存スコープ・検索方法・データ形式の詳細比較 |

---

### 追加調査が必要な候補

| item_id | 候補名 | 調査内容 | 期限目安 |
|---------|--------|---------|---------|
| F-024 | ant CLI | 公式ドキュメントURLの確認、機能一覧、インストール方法 | フェーズ3開始前 |
| D-004 | Braintrust | braintrust.devで機能・価格・OSS版の有無を確認 | フェーズ3のeval基盤選定時 |
| D-005 | W&B Weave | W&B Weave単体での導入可否、W&B本体との依存関係 | LangGraph採用が決まったとき |
| F-017 | claude-agent-sdk-demos | 具体的なデモ一覧と本プロジェクトへの適用可能性 | Agent SDK実装開始前 |

---

### 公式更新待ちの対象

| item_id | 候補名 | 待っている更新 | 確認方法 |
|---------|--------|-------------|---------|
| F-006 | Claude Managed Agents | betaヘッダー(managed-agents-2026-04-01)不要になるGA移行 | Anthropicリリースノート追跡 |
| F-008 | Agent Teams | CLAUDE_CODE_EXPERIMENTAL_AGENT_TEAMS フラグのGA化 | Claude Code リリースノート追跡 |
| F-012 | Advisor Tool | betaヘッダー(advisor-tool-2026-03-01)不要になるGA移行 | Anthropicリリースノート追跡 |
| F-029 | AutoGen | LLMコール数削減・コスト最適化の改善報告 | AutoGen GitHubリリースノート追跡 |

---

### 活性度・保守性の継続監視対象

| item_id | 候補名 | 監視理由 | 確認頻度 |
|---------|--------|---------|---------|
| F-021 | mcp-agent | LastMile AIの保守継続性。mcp-eval停止が先例 | 月1回のGitHub確認 |
| F-023 | mcp-eval | 不採用候補。再活性化の確認 | 3ヶ月に1回 |
| F-028 | CrewAI | 5エージェント超のオーバーヘッド問題の改善状況 | 月1回のリリースノート確認 |
| F-036 | Portkey Gateway | MCPガードレール機能の成熟度 | 3ヶ月に1回 |
