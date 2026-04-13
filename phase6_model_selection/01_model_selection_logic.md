# 【モデル選定ロジック実装仕様 / Phase 6】

## 目的
依頼の重さから最適なモデル alias (`opus`, `sonnet`, `haiku`, `opusplan`) を選定し、fallback と理由を返す。

## 判定基準

### 入力要素
- 推論の重さ (Reasoning Weight)
- 曖昧性 (Ambiguity Level)
- 失敗コスト (Failure Cost)
- 速度要求 (Speed Priority)
- コンテキスト量 (Context Size)
- 計画/実装バランス (Plan vs Execution)

### スコアリング

各要素を 0-1 の float で評価：

```
scoring_dimensions:
  - reasoning_weight: [0.0 (simple) ~ 1.0 (heavy)]
  - ambiguity: [0.0 (clear) ~ 1.0 (high)]
  - failure_cost: [0.0 (low) ~ 1.0 (critical)]
  - speed_priority: [0.0 (normal) ~ 1.0 (urgent)]
  - context_size: [0.0 (small <10K) ~ 1.0 (huge >500K)]
  - plan_weight: [0.0 (exec only) ~ 1.0 (heavy plan)]
```

### 選定ルール

```
# Stage 1: Filter by blocking conditions
if speed_priority >= 0.8 and context_size < 0.3:
  → haiku
if plan_weight >= 0.7 and (reasoning_weight + ambiguity) >= 1.2:
  → opusplan

# Stage 2: Weighted scoring
total_weight = (reasoning_weight * 0.3 + 
                ambiguity * 0.2 + 
                failure_cost * 0.3 + 
                context_size * 0.1 + 
                (1 - speed_priority) * 0.1)

if total_weight >= 0.7:
  → opus
if total_weight >= 0.4 and plan_weight < 0.5:
  → sonnet
if total_weight < 0.4:
  → haiku

# Stage 3: Safety adjustments
if failure_cost >= 0.8:
  bump_up(recommended_model)  # upgrade one tier
if speed_priority >= 0.7:
  bump_down(recommended_model)  # downgrade one tier
```

### Fallback Logic

```
opus → sonnet (cost-aware fallback)
opusplan → sonnet (execution is normal)
sonnet → haiku (if speed needed) or opus (if safety needed)
haiku → sonnet (insufficient for task)
```

## Output Format

```python
{
  "goal": str,  # e.g., "Implement authentication logic"
  "recommended_model": Literal["opus", "sonnet", "haiku", "opusplan"],
  "fallback_model": Literal["opus", "sonnet", "haiku", "opusplan"],
  "reason": str,  # short, max 200 chars
  "recheck_required": bool,
  "handoff_notes": str  # optional, brief execution notes
}
```

## Recheck Triggers

Set `recheck_required=True` if:
- Request has keywords suggesting new alias usage patterns
- Ambiguity is very high (>0.8) → confirm current alias capabilities
- Failure cost is critical (>0.9) → verify alias still suitable
- Context size will exceed current alias limits

## Update Robustness

**Do NOT hardcode**:
- Full model names (e.g., "claude-opus-4-6")
- Version-specific features

**DO use**:
- Alias names as primary routing key
- Role-based descriptions ("complex reasoning", "fast execution")
- Environment variable names for future version mapping

When alias list changes:
- Add new alias to scoring_dimensions
- Add new conditional in Stage 1 Filter
- Update fallback_logic mapping
- No other changes needed in core logic
