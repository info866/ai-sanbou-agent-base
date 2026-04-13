#!/usr/bin/env python3
"""
Layer 10: Continuous Watch & Sync (常時監視・自動同期層)
=====================================================
Monitors official sources, GitHub, OSS for updates.
Extracts important changes, triggers re-evaluation.
Uses Layers 7-9 for automated checking with quality gates.

goal: Continuous monitoring of external sources for updates
inputs: Watch targets (official docs, GitHub repos, capabilities catalog)
core_logic: Change detection → importance filtering → re-evaluation trigger
activation_rule: Periodic or event-driven checks via Layer 7 execution control
verification: Changes detected, importance filtered, re-eval connected
handoff: Change events → Layer 11 (feedback data) + Phase 5 (absorb_update)
"""

from __future__ import annotations

import json
import hashlib
from dataclasses import dataclass, field, asdict
from typing import Literal, Optional
from datetime import datetime
from pathlib import Path


ChangeType = Literal["new_feature", "update", "breaking_change", "deprecation", "security"]
Importance = Literal["critical", "high", "medium", "low", "noise"]


@dataclass
class WatchTarget:
    """A source to monitor for changes."""
    name: str
    source_type: Literal["github_repo", "official_docs", "npm_package",
                          "pypi_package", "mcp_server", "capability"]
    url_or_id: str
    check_interval_hours: int = 24
    importance_threshold: Importance = "medium"
    related_capabilities: list[str] = field(default_factory=list)


@dataclass
class ChangeEvent:
    """A detected change from a watch target."""
    target_name: str
    change_type: ChangeType
    importance: Importance
    summary: str
    details: str = ""
    detected_at: str = field(default_factory=lambda: datetime.now().isoformat())
    requires_reeval: bool = False
    reeval_scope: str = ""  # which phase/capability to re-evaluate
    raw_data: dict = field(default_factory=dict)

    def to_dict(self) -> dict:
        return asdict(self)


@dataclass
class WatchState:
    """Persisted state for change detection."""
    last_checked: dict[str, str] = field(default_factory=dict)    # target→ISO datetime
    known_hashes: dict[str, str] = field(default_factory=dict)    # target→content hash
    pending_events: list[dict] = field(default_factory=list)

    def save(self, path: Path) -> None:
        path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            "last_checked": self.last_checked,
            "known_hashes": self.known_hashes,
            "pending_events": self.pending_events,
        }
        with open(path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)

    @classmethod
    def load(cls, path: Path) -> "WatchState":
        if not path.exists():
            return cls()
        with open(path, encoding="utf-8") as f:
            data = json.load(f)
        return cls(
            last_checked=data.get("last_checked", {}),
            known_hashes=data.get("known_hashes", {}),
            pending_events=data.get("pending_events", []),
        )


@dataclass
class SyncReport:
    """Report from a watch/sync cycle."""
    targets_checked: int = 0
    changes_detected: int = 0
    important_changes: int = 0
    reeval_triggers: int = 0
    events: list[ChangeEvent] = field(default_factory=list)

    def to_dict(self) -> dict:
        return {
            "targets_checked": self.targets_checked,
            "changes_detected": self.changes_detected,
            "important_changes": self.important_changes,
            "reeval_triggers": self.reeval_triggers,
            "events": [e.to_dict() for e in self.events],
        }


# ── Default Watch Targets ───────────────────────────────────────────

DEFAULT_WATCH_TARGETS = [
    WatchTarget(
        name="Claude Code CLI",
        source_type="github_repo",
        url_or_id="anthropics/claude-code",
        check_interval_hours=12,
        importance_threshold="high",
        related_capabilities=["F-003", "F-004", "F-005", "F-025"],
    ),
    WatchTarget(
        name="Anthropic SDK Python",
        source_type="pypi_package",
        url_or_id="anthropic",
        check_interval_hours=24,
        importance_threshold="high",
        related_capabilities=["F-009", "F-015"],
    ),
    WatchTarget(
        name="MCP Specification",
        source_type="github_repo",
        url_or_id="modelcontextprotocol/specification",
        check_interval_hours=48,
        importance_threshold="high",
        related_capabilities=["F-002", "F-019"],
    ),
    WatchTarget(
        name="promptfoo",
        source_type="github_repo",
        url_or_id="promptfoo/promptfoo",
        check_interval_hours=72,
        importance_threshold="medium",
        related_capabilities=["F-032"],
    ),
    WatchTarget(
        name="Claude Model Aliases",
        source_type="capability",
        url_or_id="phase6_model_selection",
        check_interval_hours=24,
        importance_threshold="critical",
        related_capabilities=[],
    ),
]


# ── Importance Scoring ──────────────────────────────────────────────

IMPORTANCE_ORDER = {"critical": 4, "high": 3, "medium": 2, "low": 1, "noise": 0}


def score_importance(change_type: ChangeType, affects_capabilities: list[str],
                     is_breaking: bool = False) -> Importance:
    """Score importance based on change type and affected capabilities."""
    if is_breaking:
        return "critical"
    if change_type == "security":
        return "critical"
    if change_type == "breaking_change":
        return "high"
    if change_type == "deprecation" and len(affects_capabilities) > 0:
        return "high"
    if change_type == "new_feature" and len(affects_capabilities) > 0:
        return "medium"
    if change_type == "update":
        return "low"
    return "noise"


# ── Watch/Sync Engine ──────────────────────────────────────────────

class WatchSyncEngine:
    """Monitors targets for changes and triggers re-evaluation.

    Usage:
        engine = WatchSyncEngine(state_path)
        report = engine.check_all()
        for event in report.events:
            if event.requires_reeval:
                advisor.absorb_update(event.change_type, event.raw_data)
    """

    def __init__(self, state_path: Path | None = None,
                 targets: list[WatchTarget] | None = None):
        self.state_path = state_path or Path("watch_state.json")
        self.state = WatchState.load(self.state_path)
        self.targets = targets or DEFAULT_WATCH_TARGETS

    def check_all(self) -> SyncReport:
        """Check all watch targets for changes."""
        report = SyncReport()

        for target in self.targets:
            report.targets_checked += 1
            events = self._check_target(target)
            for event in events:
                report.events.append(event)
                report.changes_detected += 1
                if IMPORTANCE_ORDER.get(event.importance, 0) >= IMPORTANCE_ORDER.get(target.importance_threshold, 0):
                    report.important_changes += 1
                if event.requires_reeval:
                    report.reeval_triggers += 1

        # Persist state
        self.state.save(self.state_path)
        return report

    def check_single(self, target: WatchTarget) -> list[ChangeEvent]:
        """Check a single target for changes."""
        return self._check_target(target)

    def register_target(self, target: WatchTarget):
        """Add a new watch target."""
        existing_names = {t.name for t in self.targets}
        if target.name not in existing_names:
            self.targets.append(target)

    def get_pending_reeval(self) -> list[dict]:
        """Get pending re-evaluation events from persisted state."""
        return self.state.pending_events

    def clear_pending(self):
        """Clear pending events after processing."""
        self.state.pending_events = []
        self.state.save(self.state_path)

    def _check_target(self, target: WatchTarget) -> list[ChangeEvent]:
        """Check a single target using content hash comparison."""
        events = []

        current_content = self._get_target_content(target)
        current_hash = hashlib.sha256(current_content.encode()).hexdigest()

        prev_hash = self.state.known_hashes.get(target.name, "")

        if prev_hash and current_hash != prev_hash:
            change_type = self._classify_change(target, current_content)
            importance = score_importance(
                change_type, target.related_capabilities,
            )
            requires_reeval = (
                IMPORTANCE_ORDER.get(importance, 0)
                >= IMPORTANCE_ORDER.get(target.importance_threshold, 0)
            )

            event = ChangeEvent(
                target_name=target.name,
                change_type=change_type,
                importance=importance,
                summary=f"Change detected in {target.name}",
                details=f"Hash changed: {prev_hash[:8]}...{current_hash[:8]}",
                requires_reeval=requires_reeval,
                reeval_scope=", ".join(target.related_capabilities) if requires_reeval else "",
                raw_data={
                    "name": target.name,
                    "source_type": target.source_type,
                    "url_or_id": target.url_or_id,
                    "change_type": change_type,
                    "directly_affects": len(target.related_capabilities) > 0,
                    "better_than_existing": False,
                    "setup_minutes": 0,
                },
            )
            events.append(event)

            if requires_reeval:
                self.state.pending_events.append(event.to_dict())

        # Update state
        self.state.known_hashes[target.name] = current_hash
        self.state.last_checked[target.name] = datetime.now().isoformat()

        return events

    def _get_target_content(self, target: WatchTarget) -> str:
        """Get current content/state of a target for hash comparison.
        In production, this calls Layer 9 connections (GitHub API, PyPI, etc.)"""
        if target.source_type == "capability":
            base = Path(__file__).parent.parent
            target_dir = base / target.url_or_id
            if target_dir.exists():
                files = sorted(target_dir.glob("*.py")) + sorted(target_dir.glob("*.md"))
                content_parts = []
                for f in files:
                    try:
                        content_parts.append(f"{f.name}:{f.stat().st_mtime}")
                    except OSError:
                        pass
                return "|".join(content_parts)
            return f"missing:{target.url_or_id}"

        return f"{target.source_type}:{target.url_or_id}:{target.name}"

    def _classify_change(self, target: WatchTarget, content: str) -> ChangeType:
        """Classify what kind of change occurred."""
        content_lower = content.lower()
        if any(kw in content_lower for kw in ["breaking", "removed", "deleted"]):
            return "breaking_change"
        if any(kw in content_lower for kw in ["deprecated", "deprecation"]):
            return "deprecation"
        if any(kw in content_lower for kw in ["security", "vulnerability", "cve"]):
            return "security"
        if any(kw in content_lower for kw in ["new", "feature", "added"]):
            return "new_feature"
        return "update"
