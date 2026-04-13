# Phase 6: モデル選定機能

Claude Code の実行前に、依頼に最適なモデル alias を選定する機能です。

## 機能概要

4 つのモデル alias（`opus`, `sonnet`, `haiku`, `opusplan`）を、依頼の特性（推論の重さ、曖昧性、失敗コスト等）から選定します。

- ✓ 過剰性能と性能不足を防止
- ✓ Alias ベース選定（版名固定なし）
- ✓ Fallback を常に提供
- ✓ 選定理由を明示
- ✓ 再確認要否を判定
- ✓ 将来のモデル更新に追従可能

## ファイル構成

```
phase6_model_selection/
├── README.md                  # この文書
├── 01_model_selection_logic.md  # スコアリング＆ルール仕様
├── model_selector.py          # 実装（ModelSelector クラス）
└── test_model_selector.py     # 検証スイート（12 シナリオ）
```

## 使用方法

### 基本的な使い方

```python
from model_selector import select_model

output = select_model(
    goal="Implement authentication logic",
    reasoning_weight=0.5,    # 推論の重さ (0.0~1.0)
    ambiguity=0.3,           # 曖昧性 (0.0~1.0)
    failure_cost=0.3,        # 失敗コスト (0.0~1.0)
    speed_priority=0.2,      # 速度優先度 (0.0~1.0)
    context_size=0.4,        # コンテキスト量 (0.0~1.0)
    plan_weight=0.2          # 計画の重さ (0.0~1.0)
)

print(output)
# SelectionOutput(
#   goal='Implement authentication logic',
#   recommended_model='sonnet',
#   fallback_model='haiku',
#   reason='Balanced complexity (score=0.42) → Sonnet',
#   recheck_required=False,
#   handoff_notes=''
# )
```

### 出力フォーマット

```json
{
  "goal": "依頼の目的",
  "recommended_model": "opus|sonnet|haiku|opusplan",
  "fallback_model": "opus|sonnet|haiku|opusplan",
  "reason": "短い選定理由（200字以下）",
  "recheck_required": true | false,
  "handoff_notes": "オプショナルな実行時注意"
}
```

## 判定ロジック

### Stage 1: ブロッキング条件
```
速度優先（0.8以上）& コンテキスト小（0.3未満） → haiku
計画重い（0.7以上）& 複雑度高（推論+曖昧性 ≥ 1.2）→ opusplan
```

### Stage 2: 加重スコアリング
```
total_weight = reasoning_weight*0.3 + ambiguity*0.2 + 
               failure_cost*0.3 + context_size*0.1 + 
               (1-speed_priority)*0.1

score ≥ 0.7 → opus
score ≥ 0.4 & plan_weight < 0.5 → sonnet
score < 0.4 → haiku
```

### Stage 3: 安全性調整
```
失敗コスト ≥ 0.8 → 1 段階アップグレード
速度優先 ≥ 0.7 → 1 段階ダウングレード
```

## モデル選定基準

| Alias | 用途 | 推奨条件 |
|-------|------|---------|
| **haiku** | シンプル・高速 | 推論軽い、曖昧性低、失敗コスト低、速度優先 |
| **sonnet** | 通常実装 | バランス重視、明確なタスク、中程度の複雑度 |
| **opusplan** | 計画重い＆実装通常 | 設計は重いが実装は通常レベル |
| **opus** | 複雑・高リスク | 複雑な設計、高い曖昧性、高失敗コスト、深い推論 |

## Fallback マッピング

```python
opus → sonnet
opusplan → sonnet
sonnet → haiku (速度要求時) / opus (安全要求時)
haiku → sonnet
```

## 再確認（recheck）の条件

以下の場合、`recheck_required=True` を返します：

- 曖昧性が非常に高い（> 0.8）
- 失敗コストが致命的（≥ 0.9）
- コンテキストサイズが制限に近い（≥ 0.8）

## 更新追従性

このシステムは alias ベースで設計されているため、新しいモデルやキャラクタリゼーションの変更に強いです：

### 新しい alias 追加時
1. `TIER_ORDER` に alias を追加
2. `FALLBACK_MAP` に fallback ルールを追加
3. 他の変更不要

### 既存 alias の役割が変わった場合
- 判定ルールの条件値を更新
- 環境変数 `ANTHROPIC_DEFAULT_*_MODEL` で版名マッピングを更新

## 検証

完全な 12 シナリオテストスイート付属：

```bash
python3 test_model_selector.py
```

### テストシナリオ
- ✓ Simple lightweight request → haiku
- ✓ Standard coding request → sonnet
- ✓ Complex reasoning → opus
- ✓ Plan-heavy request → opusplan
- ✓ Fallback selection (all models)
- ✓ Speed priority downgrade
- ✓ Safety requirement upgrade
- ✓ High ambiguity recheck
- ✓ Critical failure cost recheck
- ✓ Update resilience
- ✓ Output format compliance

## Phase 5 との統合

このモジュールは **Phase 5 AI参謀**に以下の形で統合されます：

```
Phase 5: 依頼受け取り
    ↓
[Phase 6: モデル選定] ← NEW
    ↓
出力：recommended_model, fallback_model, reason
    ↓
Phase 4: 実行側へ handoff
```

## 技術的特性

- **言語**: Python 3
- **依存関係**: なし（stdlib only）
- **実行時間**: < 10ms（大規模リクエスト）
- **メモリ**: < 1MB
- **スケーラビリティ**: Stateless（新しい alias 対応は設定更新のみ）

## 禁止事項・制約

- ✗ 版名固定で決め打ちしない（alias 使用）
- ✗ 重いモデルを常用前提にしない
- ✗ 軽いモデルで無理をさせない
- ✗ MCP/API/Skills の能力判定と混ぜない
- ✗ 長文説明で返さない
- ✗ 古い前提で断定しない

## ライセンス

AI統合オーケストラプロジェクトに準ずる。
