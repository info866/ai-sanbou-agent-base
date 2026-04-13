# オーケストラエージェント

AI参謀の統合判断フレームワーク。Phase 1〜5の全基盤を統合して、依頼に対して能力選定→理由付き提案→実行橋渡しを一貫して実行します。

## 構成

- `phase1_information_foundation/` — 候補一覧・分類・状態
- `phase2_decision_foundation/` — 評価基準・採用状態・優先順位
- `phase3_knowledge_foundation/` — 知識活用ルール・再確認ルール・信頼区分
- `phase4_execution_foundation/` — 実行フロー・ツール投入方針・品質保証ルール
- `phase5_ai_advisor/` — 判断原則・分類ルール・能力選定ルール・理由生成ルール・実行橋渡しルール・更新吸収ルール・最終運用形

## 検証

```bash
# Phase 5の統合判断エンジン検証（54項目）
python3 phase5_operational_verification.py

# Phase 4の実行基盤検証（15項目）
python3 phase4_operational_verification.py
```

## 使用例

Phase 5 AIアドバイザーのコア動作：
- 依頼を受け取る → 分類（RC-1〜RC-6）
- 必要能力を選定（キーワード+基盤マッチング）
- 選定理由と再確認判断を生成
- 実行基盤へ5要素で橋渡し
- 新機能検出時に判断を更新

## デプロイ

このフォルダ全体を新規プロジェクトにコピーし、phase5_operational_verification.py で統合動作を検証してください。
