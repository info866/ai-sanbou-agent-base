# オーケストラエージェント

AI参謀の統合判断フレームワーク。Phase 1〜6の全基盤を統合した単一パッケージ。依頼に対してモデル選定→能力選定→理由付き提案→実行橋渡しを一貫して実行します。

このフォルダが唯一の正本です。外部に重複コピーはありません。

## 構成

### コアランタイム
- `phase1_information_foundation/` — 候補一覧・分類・状態
- `phase2_decision_foundation/` — 評価基準・採用状態・優先順位
- `phase3_knowledge_foundation/` — 知識活用ルール・再確認ルール・信頼区分
- `phase4_execution_foundation/` — 実行フロー・ツール投入方針・品質保証ルール
- `phase5_ai_advisor/` — 判断原則・分類・能力選定・理由生成・実行橋渡し・更新吸収・最終運用形
- `phase6_model_selection/` — モデルalias選定・公式再確認経路・alias状態永続化

### 検証・証明
- `phase5_operational_verification.py` — 統合検証（110項目）
- `phase4_operational_verification.py` — Phase 4検証（15項目）
- `phase6_model_selection/test_model_selector.py` — モデル選定単体検証（12項目）
- `proof_final.py` — 最終証明（recheck実質化・永続化・クリーン再現・故障注入、18項目）

### 仕様書
- `docs/` — 全フェーズの要件定義書・作業指示書

## 検証

```bash
cd オーケストラエージェント/

# 統合検証（110項目）
python3 phase5_operational_verification.py

# Phase 6 単体検証（12項目）
cd phase6_model_selection && python3 test_model_selector.py && cd ..

# Phase 4 検証（15項目）
python3 phase4_operational_verification.py

# 最終証明（18項目: recheck/永続化/クリーン再現/故障注入）
python3 proof_final.py
```

## 統合フロー

```
依頼受付
  → 分類（RC-1〜RC-6）
  → モデル選定（Phase 6: opus/sonnet/haiku/opusplan）
  → 能力選定（キーワード+基盤マッチング）
  → 選定理由と再確認判断を生成
  → 実行基盤へ5要素+モデル情報で橋渡し
  → 新機能検出時に判断を更新
```

## 使い方

このフォルダを新規プロジェクトにコピーするだけで使えます:

```bash
cp -r オーケストラエージェント/ your-project/オーケストラエージェント/
cd your-project/オーケストラエージェント/
python3 phase5_operational_verification.py  # 動作確認
```
