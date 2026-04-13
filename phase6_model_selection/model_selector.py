#!/usr/bin/env python3
"""
Model Selection Engine for AI Orchestration
Selects optimal model alias based on request characteristics
"""

from dataclasses import dataclass
from typing import Literal
from enum import Enum


ModelAlias = Literal["opus", "sonnet", "haiku", "opusplan"]


@dataclass
class SelectionInput:
    """Input characteristics for model selection"""
    goal: str
    reasoning_weight: float  # 0.0 (simple) ~ 1.0 (heavy)
    ambiguity: float  # 0.0 (clear) ~ 1.0 (high)
    failure_cost: float  # 0.0 (low) ~ 1.0 (critical)
    speed_priority: float  # 0.0 (normal) ~ 1.0 (urgent)
    context_size: float  # 0.0 (small <10K) ~ 1.0 (huge >500K)
    plan_weight: float  # 0.0 (exec only) ~ 1.0 (heavy plan)


@dataclass
class SelectionOutput:
    """Model selection decision"""
    goal: str
    recommended_model: ModelAlias
    fallback_model: ModelAlias
    reason: str
    recheck_required: bool
    handoff_notes: str = ""


class ModelSelector:
    """Alias-based model selection engine"""

    TIER_ORDER = ["haiku", "sonnet", "opusplan", "opus"]

    FALLBACK_MAP = {
        "opus": "sonnet",
        "opusplan": "sonnet",
        "sonnet": "haiku",  # default for sonnet
        "haiku": "sonnet",
    }

    def select(self, input_: SelectionInput) -> SelectionOutput:
        """Select optimal model alias for the request"""

        # Stage 1: Filter by blocking conditions
        if (input_.speed_priority >= 0.8 and
            input_.context_size < 0.3):
            recommended = "haiku"
            reason = "Speed priority + small context → Haiku"

        elif (input_.plan_weight >= 0.7 and
              (input_.reasoning_weight + input_.ambiguity) >= 1.2):
            recommended = "opusplan"
            reason = "Heavy planning + complex reasoning → OpusPlan"

        else:
            # Stage 2: Weighted scoring
            total_weight = (
                input_.reasoning_weight * 0.3 +
                input_.ambiguity * 0.2 +
                input_.failure_cost * 0.3 +
                input_.context_size * 0.1 +
                (1 - input_.speed_priority) * 0.1
            )

            if total_weight >= 0.7:
                recommended = "opus"
                reason = f"High complexity (score={total_weight:.2f}) → Opus"
            elif total_weight >= 0.4 and input_.plan_weight < 0.5:
                recommended = "sonnet"
                reason = f"Balanced complexity (score={total_weight:.2f}) → Sonnet"
            else:
                recommended = "haiku"
                reason = f"Low complexity (score={total_weight:.2f}) → Haiku"

        # Stage 3: Safety adjustments
        if input_.failure_cost >= 0.8:
            recommended = self._bump_up(recommended)
            reason += " [upgraded for safety]"

        if input_.speed_priority >= 0.7:
            recommended = self._bump_down(recommended)
            reason += " [downgraded for speed]"

        # Determine fallback
        fallback = self._select_fallback(recommended, input_)

        # Determine if recheck is needed
        recheck = self._should_recheck(input_, recommended)

        # Generate execution notes
        notes = self._generate_notes(input_, recommended)

        return SelectionOutput(
            goal=input_.goal,
            recommended_model=recommended,
            fallback_model=fallback,
            reason=reason,
            recheck_required=recheck,
            handoff_notes=notes
        )

    def _bump_up(self, model: ModelAlias) -> ModelAlias:
        """Upgrade model one tier (safety-driven)"""
        idx = self.TIER_ORDER.index(model)
        if idx < len(self.TIER_ORDER) - 1:
            return self.TIER_ORDER[idx + 1]
        return model

    def _bump_down(self, model: ModelAlias) -> ModelAlias:
        """Downgrade model one tier (speed-driven)"""
        idx = self.TIER_ORDER.index(model)
        if idx > 0:
            return self.TIER_ORDER[idx - 1]
        return model

    def _select_fallback(self, recommended: ModelAlias,
                        input_: SelectionInput) -> ModelAlias:
        """Select appropriate fallback model"""
        base_fallback = self.FALLBACK_MAP.get(recommended, "sonnet")

        # If recommended was bumped up due to failure cost,
        # fallback should be the original
        if input_.failure_cost >= 0.8 and recommended == "opus":
            return "sonnet"

        # If recommended was bumped down for speed,
        # fallback should be the original
        if input_.speed_priority >= 0.7 and recommended == "haiku":
            return "sonnet"

        return base_fallback

    def _should_recheck(self, input_: SelectionInput,
                       recommended: ModelAlias) -> bool:
        """Determine if recheck is needed"""
        reasons = []

        # Very high ambiguity
        if input_.ambiguity > 0.8:
            reasons.append("very_high_ambiguity")

        # Critical failure cost
        if input_.failure_cost >= 0.9:
            reasons.append("critical_failure_cost")

        # Will exceed normal context (opusplan/haiku may have limits)
        if input_.context_size >= 0.8 and recommended in ["haiku", "sonnet"]:
            reasons.append("context_size_near_limit")

        return len(reasons) > 0

    def _generate_notes(self, input_: SelectionInput,
                       recommended: ModelAlias) -> str:
        """Generate brief execution notes for handoff"""
        notes = []

        if input_.context_size >= 0.8:
            notes.append(f"Large context ({input_.context_size:.1%})")

        if input_.failure_cost >= 0.8:
            notes.append("High safety requirement")

        if input_.ambiguity >= 0.8:
            notes.append("High ambiguity - verify alias supports required features")

        return "; ".join(notes) if notes else ""


# Convenience function
def select_model(goal: str,
                 reasoning_weight: float,
                 ambiguity: float,
                 failure_cost: float,
                 speed_priority: float,
                 context_size: float,
                 plan_weight: float) -> SelectionOutput:
    """Convenience function for model selection"""
    selector = ModelSelector()
    input_ = SelectionInput(
        goal=goal,
        reasoning_weight=reasoning_weight,
        ambiguity=ambiguity,
        failure_cost=failure_cost,
        speed_priority=speed_priority,
        context_size=context_size,
        plan_weight=plan_weight
    )
    return selector.select(input_)
