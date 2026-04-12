# Runtime 基盤 最終証跡

> **作成日**: 2026-04-12

---

## 目的

Claude Code 公式機能によるプロジェクト runtime 基盤が「実際に動く」ことの最終証跡を残す。

---

## 最終構成

```
.claude/
  settings.json              # hooks + permissions
  hooks/
    protect-canonical.sh     # 正本文書保護（PreToolUse）
  agents/
    catalog-checker.md       # 候補カタログ整合性検査
    scope-guard.md           # 作業範囲逸脱監査
    phase-reporter.md        # 完了報告書生成
  settings.local.json        # 既存（未変更）
```

---

## 正式な呼び出し方法

| 機能 | 方法 | 補足 |
|------|------|------|
| 正本保護 | 自動 | Edit/Write で正本に触ると hook が自動発動 |
| catalog-checker | Agent tool | prompt に「候補カタログの整合性を検査してください」+ 検査項目を書く |
| scope-guard | Agent tool | prompt に「スコープ監査を実行してください」+ 作業説明を書く |
| phase-reporter | Agent tool | prompt に「完了報告を生成してください」+ git情報 + 作業概要を書く |

subagent の model は haiku。ツールは Read/Grep/Glob（読取専用）。

---

## 実行証跡

### Hook

```
=== BLOCK TEST ===
正本文書の直接編集をブロックしました: ５.フェーズ２ 要件定義書.md
正本文書は変更禁止です。内容を参照し、成果物ファイルに反映してください。
exit=2

=== ALLOW TEST ===
exit=0
```

### catalog-checker

Agent tool (haiku) で実行。結果:

```
1. item_id 連番確認（F-001〜F-038）: PASS
2. 参照整合性（05引き継ぎ文書 → 02カタログ）: PASS
3. 比較グループ所属マップ整合（パート4）: PASS
4. current_status 正規値チェック: PASS
5. 必須フィールド欠落チェック: PASS

5/5 PASS。38候補完全整合。
```

### scope-guard

Agent tool (haiku) で実行。結果:

```
- 成果物ファイル一覧: 想定外なし
- 禁止キーワード混入: なし
- タスク範囲判定: 逸脱なし
- 正本文書補助確認: 6ファイルをReadで直接確認。全件Read成功
```

### phase-reporter

Agent tool (haiku) で実行。git情報と作業概要を渡し、報告書を生成。結果:

```
テンプレート6セクション（実施概要/ファイル一覧/成果物要点/逸脱確認/GitHub情報/引き継ぎ）
を正常生成。作業契約書（00）を Read で参照し、完了条件・停止線を把握した上で報告を構成。
```

---

## 未解決ゼロの根拠

| 確認事項 | 状態 |
|---------|------|
| hook が動くか | PASS（ブロック/許可ともに正常） |
| catalog-checker が動くか | PASS（5/5 PASS） |
| scope-guard が動くか | PASS（逸脱なし。正本文書6件Read確認成功） |
| phase-reporter が動くか | PASS（報告書正常生成） |
| F-032〜F-038 所属マップ | 解消済み（パート4に全件記載） |
| scope-guard Glob制約 | 解消済み（Read確認方式に変更） |
| D-003 残存 | 解消済み（c42943e: 2箇所〔phase2×1+phase1×1〕、08e28c4: phase1×4箇所、本コミット: phase2×1箇所; 合計7箇所） |
| 07/09/10 に古い説明が残っているか | なし（最終状態のみ記載） |

**core runtime 未解決課題: ゼロ**

---

## 設計判断の記録

### 正本文書の保護体制

- **主防御**: PreToolUse hook（.claude/hooks/protect-canonical.sh）。Edit/Write を直接ブロック
- **補助検査**: scope-guard の Read 確認。6正本ファイルを明示パスで Read し、全件成功を確認

---

## コミット分類

runtime 基盤コミットと phase1 後処理コミットを明確に区別する。

### Runtime 基盤コミット群

以下は `.claude/` 配下の hooks・agents・settings、または runtime 証跡文書（07/09/10）を直接変更したコミット。

- `922058d` fix(phase2): runtime activation 補正・全機能実動作確認
- `d381410` fix(phase2): runtime基盤の残課題3件解消
- `8f6b7d2` fix(phase2): phase-report を subagent へ置き換え
- `ddb7acb` feat(phase2): runtime基盤を完成状態に仕上げ、最終証跡を作成
- `c42943e` fix(runtime): scope-guard Glob制約解消・runtime基盤を完全完成状態へ
- `f459e57` docs(runtime): 07/09/10 を最終状態のみの文書に書き直し
- `5626ce9` fix(hooks): PreToolUse schema を正式形式に修正（Settings Error解消）
- `e068897` docs(runtime): 10証跡にコミット分類を追加しD-003修正箇所数を実態に修正

### Phase1 カタログ後処理コミット

catalog-checker 実行中に発見された phase1 文書の参照ミスを修正したコミット。  
runtime 基盤自体（.claude/ 配下・runtime証跡文書）への変更はない。

- `08e28c4` fix(catalog): 05引き継ぎ文書の D-003 残置を F-034 に修正・候補数 31→38 更新
  - 変更対象: `phase1_information_foundation/05_unexplored_and_phase2_handoff.md` のみ
  - 内容: D-003（廃止ID）→ F-034（Langfuse正規ID）4箇所、候補数31→38 2箇所

> **注意**: 本コミット分類リストはリスト末尾のコミット時点までを対象とする（自己参照回避）。HEAD commit は `git log --oneline -1` で確認すること。
