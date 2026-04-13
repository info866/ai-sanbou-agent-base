# オーケストラエージェント

AI参謀の統合判断・自動実行フレームワーク。Phase 1〜6の判断基盤 + 追加5層の自動実行基盤を統合した単一パッケージ。依頼→分類→モデル選定→能力選定→実行計画→品質ゲート→接続確認→監視→評価改善まで一貫して自動実行します。

このフォルダが唯一の正本です。外部に重複コピーはありません。

## 構成

### 頭脳（Phase 1〜6）
- `phase1_information_foundation/` — 候補一覧・分類・状態
- `phase2_decision_foundation/` — 評価基準・採用状態・優先順位
- `phase3_knowledge_foundation/` — 知識活用ルール・再確認ルール・信頼区分
- `phase4_execution_foundation/` — 実行フロー・ツール投入方針・品質保証ルール
- `phase5_ai_advisor/` — 判断原則・分類・能力選定・理由生成・実行橋渡し・更新吸収
- `phase6_model_selection/` — モデルalias選定・公式再確認経路・alias状態永続化

### 手足（追加5層）
- `layer7_execution_control/` — Phase 5橋渡し→自動実行計画変換・能力→アクション対応
- `layer8_quality_gates/` — リスク検知・品質ゲート自動挿入・危険操作ブロック
- `layer9_connection_bootstrap/` — MCP/API/GitHub/CLI接続の自動確認・不足検知
- `layer10_watch_sync/` — 外部ソース監視・変更検知・重要度フィルタ・再評価トリガー
- `layer11_continuous_eval/` — 実行結果計測・選定精度評価・改善提案フィードバック

### 検証・証明
- `phase5_operational_verification.py` — 統合検証（110項目）
- `phase4_operational_verification.py` — Phase 4検証（15項目）
- `phase6_model_selection/test_model_selector.py` — モデル選定単体検証（12項目）
- `proof_final.py` — 最終証明（recheck/永続化/クリーン再現/故障注入、18項目）
- `proof_5layers.py` — 追加5層証明（全層+統合パイプライン、48項目）

## 検証

```bash
cd オーケストラエージェント/

# 頭脳: 統合検証（110項目）
python3 phase5_operational_verification.py

# 頭脳: Phase 6 単体検証（12項目）
cd phase6_model_selection && python3 test_model_selector.py && cd ..

# 頭脳: Phase 4 検証（15項目）
python3 phase4_operational_verification.py

# 頭脳: 最終証明（18項目）
python3 proof_final.py

# 手足: 追加5層証明（48項目）
python3 proof_5layers.py
```

## 統合フロー

```
依頼受付
  → 分類（RC-1〜RC-6）                    [Phase 5]
  → モデル選定（opus/sonnet/haiku/opusplan）  [Phase 6]
  → 能力選定（キーワード+基盤マッチング）      [Phase 5]
  → 実行計画変換（能力→アクション自動対応）    [Layer 7]
  → 品質ゲート挿入（リスク検知・自動検証）     [Layer 8]
  → 接続確認（MCP/API/GitHub自動チェック）    [Layer 9]
  → 監視登録（外部ソース変更検知）            [Layer 10]
  → 実行結果評価（精度計測・改善提案）         [Layer 11]
```

## 使い方

このフォルダを新規プロジェクトにコピーするだけで使えます:

```bash
cp -r オーケストラエージェント/ your-project/オーケストラエージェント/
cd your-project/オーケストラエージェント/
python3 proof_5layers.py          # 追加5層動作確認
python3 proof_final.py            # 頭脳動作確認
```
