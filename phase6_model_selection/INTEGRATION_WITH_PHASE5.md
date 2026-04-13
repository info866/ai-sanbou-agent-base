# Phase 5 と Phase 6 の統合仕様

## 統合の位置づけ

Phase 6（モデル選定）は Phase 5（AI参謀完成）の**前段**として機能します。

```
依頼受け取り
    ↓
[RC-1～RC-6: 依頼分類] (Phase 5)
    ↓
[モデル選定] (Phase 6) ← NEW
    ↓
[能力選定] (Phase 5)
    ↓
[理由生成] (Phase 5)
    ↓
[実行 handoff] (Phase 5, Phase 4)
```

## データフロー

### Phase 5 → Phase 6 入力

Phase 5 の依頼分類後、以下の情報が Phase 6 へ渡されます：

```python
{
  "goal": str,                 # 依頼の目的（例："Implement auth"）
  "request_class": RC-1~RC-6,  # Phase 5 の分類結果
  "reasoning_weight": float,   # 推論の重さ
  "ambiguity": float,          # 曖昧性
  "failure_cost": float,       # 失敗コスト
  "speed_priority": float,     # 速度優先度
  "context_size": float,       # 必要コンテキスト量
  "plan_weight": float         # 計画の重さ
}
```

### Phase 6 → Phase 5 出力

Phase 6 の選定結果が Phase 5 へ戻されます：

```python
{
  "goal": str,
  "recommended_model": "opus" | "sonnet" | "haiku" | "opusplan",
  "fallback_model": "opus" | "sonnet" | "haiku" | "opusplan",
  "reason": str,
  "recheck_required": bool,
  "handoff_notes": str
}
```

## Request Class → 入力パラメータマッピング

Phase 5 の request classification から Phase 6 への入力を自動変換：

| RC | 名称 | reasoning | ambiguity | failure_cost | speed | context | plan |
|-----|------|----------|-----------|-------------|--------|---------|------|
| RC-1 | Simple bug fix | 0.1 | 0.1 | 0.1 | 0.8 | 0.1 | 0.0 |
| RC-2 | Feature impl | 0.5 | 0.3 | 0.3 | 0.2 | 0.4 | 0.2 |
| RC-3 | Architecture design | 0.9 | 0.7 | 0.8 | 0.1 | 0.6 | 0.7 |
| RC-4 | Unclear requirement | 0.6 | 0.9 | 0.6 | 0.1 | 0.5 | 0.5 |
| RC-5 | Critical production | 0.4 | 0.2 | 0.95 | 0.1 | 0.3 | 0.0 |
| RC-6 | Quick support | 0.2 | 0.2 | 0.2 | 0.9 | 0.2 | 0.0 |

### マッピングロジック

```python
def request_class_to_model_selection_input(rc: str, goal: str) -> SelectionInput:
    """Phase 5 の RC 結果 → Phase 6 入力への変換"""
    
    rc_params = {
        "RC-1": (0.1, 0.1, 0.1, 0.8, 0.1, 0.0),
        "RC-2": (0.5, 0.3, 0.3, 0.2, 0.4, 0.2),
        "RC-3": (0.9, 0.7, 0.8, 0.1, 0.6, 0.7),
        "RC-4": (0.6, 0.9, 0.6, 0.1, 0.5, 0.5),
        "RC-5": (0.4, 0.2, 0.95, 0.1, 0.3, 0.0),
        "RC-6": (0.2, 0.2, 0.2, 0.9, 0.2, 0.0),
    }
    
    reasoning, ambiguity, failure_cost, speed, context, plan = rc_params[rc]
    
    return SelectionInput(
        goal=goal,
        reasoning_weight=reasoning,
        ambiguity=ambiguity,
        failure_cost=failure_cost,
        speed_priority=speed,
        context_size=context,
        plan_weight=plan
    )
```

## Phase 5 実装例（モデル選定の組み込み）

```python
# phase5_ai_advisor/03_capability_selection.md に追加

from phase6_model_selection.model_selector import select_model

class Phase5AIAdvisor:
    
    def process_request(self, request):
        # STEP 1: 依頼分類（既存）
        request_class = self.classify_request(request)  # RC-1 ~ RC-6
        
        # STEP 2: モデル選定（NEW）
        model_selection = self.select_model(
            goal=request.goal,
            request_class=request_class
        )
        
        # STEP 3: 能力選定（既存）
        capabilities = self.select_capabilities(
            goal=request.goal,
            request_class=request_class
        )
        
        # STEP 4: 理由生成（既存）
        reasons = self.generate_reasons(
            model_selection=model_selection,
            capabilities=capabilities
        )
        
        # STEP 5: 実行 handoff（既存）
        return self.prepare_handoff(
            model_selection=model_selection,
            capabilities=capabilities,
            reasons=reasons
        )
    
    def select_model(self, goal, request_class):
        """Phase 6: モデル選定"""
        from phase6_model_selection.model_selector import select_model as phase6_select
        
        # RC → 入力パラメータ変換
        params = self.rc_to_params(request_class, goal)
        
        # Phase 6 実行
        return phase6_select(**params)
    
    def rc_to_params(self, rc, goal):
        """RC 分類 → Phase 6 入力パラメータ変換"""
        mapping = {
            "RC-1": {"reasoning": 0.1, "ambiguity": 0.1, "failure_cost": 0.1, 
                     "speed_priority": 0.8, "context_size": 0.1, "plan_weight": 0.0},
            "RC-2": {"reasoning": 0.5, "ambiguity": 0.3, "failure_cost": 0.3,
                     "speed_priority": 0.2, "context_size": 0.4, "plan_weight": 0.2},
            # ... 他の RC-3 ~ RC-6
        }
        params = mapping.get(rc, {})
        params["goal"] = goal
        return params
```

## 実行 Handoff への反映

Phase 6 の出力が Phase 4（実行基盤）への handoff に反映：

```python
handoff = {
    "goal": request.goal,
    "model": model_selection.recommended_model,
    "model_fallback": model_selection.fallback_model,
    "model_reason": model_selection.reason,
    "model_recheck": model_selection.recheck_required,
    "capabilities": [selected_capabilities],
    "tools": [selected_tools],
    "flow": execution_flow,
    # ...
}
```

## Recheck ロジックの連携

`recheck_required=True` の場合の処理：

### Phase 6 での判定
- 曖昧性が非常に高い (> 0.8) → モデルの機能確認
- 失敗コストが致命的 (≥ 0.9) → 選定根拠確認
- コンテキストサイズが制限に近い (≥ 0.8) → 容量確認

### Phase 5 での処理
```python
if model_selection.recheck_required:
    # 公式情報で確認
    verify_model_capabilities(model_selection.recommended_model)
    verify_context_limits(model_selection.recommended_model)
    # 必要に応じて再選定
    if not verified:
        model_selection = select_fallback(model_selection)
```

## Version Update への対応

新しいモデルが Anthropic から公開された場合：

1. **環境変数を更新**（Code 側で自動）
   ```bash
   export ANTHROPIC_DEFAULT_OPUS_MODEL="claude-opus-5-0"
   ```

2. **Phase 6 は変更不要**（alias ベース設計）
   - `opus` → 常に最新版

3. **Phase 5 への影響**
   - 自動的に新モデルへ切り替わる

## テスト戦略

### Phase 6 単体テスト
```bash
cd phase6_model_selection
python3 test_model_selector.py
```

### Phase 5 統合テスト
```python
# phase5_operational_verification.py に追加
def test_model_selection_integration():
    """Phase 5 → 6 → 4 の handoff テスト"""
    request = create_test_request(
        goal="Implement auth",
        request_class="RC-2"
    )
    
    advisor = Phase5AIAdvisor()
    handoff = advisor.process_request(request)
    
    # モデル選定が正しく反映されているか確認
    assert handoff["model"] == "sonnet"
    assert handoff["model_fallback"] == "haiku"
    assert handoff["model_reason"] != ""
```

## 監視・ロギング

選定結果をロギング（オプション）：

```python
import json
from datetime import datetime

def log_model_selection(selection_output):
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "goal": selection_output.goal,
        "recommended_model": selection_output.recommended_model,
        "fallback_model": selection_output.fallback_model,
        "reason": selection_output.reason,
        "recheck_required": selection_output.recheck_required,
    }
    with open("model_selection_log.jsonl", "a") as f:
        f.write(json.dumps(log_entry) + "\n")
```

## パフォーマンス

- **実行時間**: < 10ms
- **メモリ**: < 1MB
- **エラーレート**: 0（deterministic）

## セキュリティ考慮事項

- 入力値の range check（すべて 0.0～1.0）
- 出力は alias のみ（バージョン情報を含まない）
- 環境変数設定は admin only
