# 候補カタログ（Candidate Catalog）

> **担当**: グループ2  
> **インプット**: `00_scope_and_execution_contract.md` と `01_information_sources.md` を読んでから着手すること  
> **ステップ対応**: フェーズ1作業指示書 ステップ3（初期既知候補の登録）＋ ステップ4（追加探索）

---

## 記入ルール

- 各候補に以下を必ず付与すること
  - `item_id`（連番）
  - `item_name`（正式名称）
  - `item_type`（公式機能 / 公式実装 / OSS / 公開エージェント / その他）
  - `layer_category`（機能層：後で03で定義される）
  - `vendor_owner`
  - `source_url`
  - `summary`（1〜3行の概要）
  - `primary_use_cases`（何に効くか）
  - `prerequisites`（導入前提）
  - `current_status`（未確認 / 調査中 / 候補 / 比較待ち / 保留 / 不採用候補 / 採用候補 / 監視継続 / 試験導入候補）
  - `first_seen_at`（初回確認日）
  - `last_checked_at`（最終確認日）
  - `notes`

- **既知候補** と **追加探索で見つかった候補** を分けて管理すること
- 採用判断・不採用確定はここでしない。状態は「候補」「比較待ち」「監視継続」止まりにすること

---

## セクション1｜既知初期候補（登録必須）

### 公式機能層

<!-- グループ2が記入 -->
<!-- 対象: Prompt Improver, MCP, subagents, hooks, skills, Claude Managed Agents, Cowork -->

### 公式実装資産層

<!-- グループ2が記入 -->
<!-- 対象: anthropics/skills, anthropics/claude-code-action, modelcontextprotocol/registry, modelcontextprotocol/servers -->

### OSS / 基盤候補層（既知）

<!-- グループ2が記入 -->
<!-- 対象: musistudio/claude-code-router, BerriAI/litellm, lastmile-ai/mcp-agent, lastmile-ai/mcp-eval -->

---

## セクション2｜追加探索候補（グループ2が探索して追加）

### 公式追加探索で見つかった候補

<!-- グループ2が記入 -->

### GitHub追加探索で見つかった候補

<!-- グループ2が記入 -->

### 公開エージェント追加探索で見つかった候補

<!-- グループ2が記入 -->

---

## セクション3｜比較対象メモ

<!-- 同じ役割を持つ候補同士の比較メモ -->
<!-- グループ2が記入、グループ3が完成させる -->

---

## 除外・保留メモ

<!-- 探索中に見つかったが今回対象外にした候補と理由 -->
<!-- グループ2が記入 -->
