#!/usr/bin/env python3
"""
Catalog Auto-Updater: Fetches release notes → extracts features → updates catalog + dynamic capabilities.

This closes the gap between "detecting changes" and "actually learning new features."

Flow:
  1. Fetch latest GitHub releases for Claude Code (anthropics/claude-code)
  2. Parse release notes to extract new features/capabilities
  3. Generate catalog entries in 02_candidate_catalog.md format
  4. Write dynamic_capabilities.json for orchestrator to load at runtime
  5. Orchestrator merges dynamic capabilities into hardcoded pools

Usage:
  updater = CatalogUpdater(state_dir, catalog_path)
  result = updater.update_from_releases()
  # result = {"new_capabilities": [...], "catalog_entries_added": N}
"""

from __future__ import annotations

import json
import os
import re
import tempfile
import urllib.request
from dataclasses import dataclass, field, asdict
from datetime import datetime
from pathlib import Path


# Lines matching these prefixes are FEATURES (not bug fixes)
FEATURE_LINE_PREFIXES = [
    "added ", "- added ",
    "new ", "- new ",
    "claude ", "- claude ",
    # Specific patterns for new capabilities/modes
]

# Lines matching these are excluded (bug fixes, polish)
EXCLUDE_PREFIXES = [
    "fixed ", "- fixed ",
    "reverted ", "- reverted ",
    "suppressed ", "- suppressed ",
    "hardened ", "- hardened ",
]

# Feature classification rules: (regex on cleaned line, name_extractor, layer, rcs)
FEATURE_CLASSIFIERS = [
    # Slash commands: /command — the most concrete new features
    (r"[`/](\w[\w-]+)[`]?\s+(?:command|skill|for|—|to\s)",
     "command", "実行層", ["RC-1", "RC-3", "RC-6"]),
    # New model/effort levels
    (r"(\w+\s+\d+\.\d+\s*\w*)\s+is\s+now\s+available",
     "model", "推論層", ["RC-1", "RC-3", "RC-5"]),
    (r"[`](\w+)[`]\s+effort\s+level",
     "effort", "推論層", ["RC-1", "RC-3"]),
    # New tools
    (r"(?:push\s+notification|notification)\s+tool",
     "tool", "接続層", ["RC-3", "RC-6"]),
    (r"(\w+)\s+tool\s+(?:is|—|for)",
     "tool", "実行層", ["RC-1", "RC-3"]),
    # New modes
    (r"(auto\s+mode)\s+(?:is|no\s+longer)",
     "mode", "実行層", ["RC-1", "RC-3", "RC-6"]),
    # Config/settings
    (r"[`](\w+)[`]\s+(?:config|setting)",
     "config", "実行層", ["RC-6"]),
    # Hook/permission system changes
    (r"(hook|hooks?|permission)\s+(?:support|system|model)",
     "system", "自動化層", ["RC-3", "RC-4", "RC-6"]),
    # MCP-related
    (r"(MCP|mcp)\s+(?:server|tool|connector)",
     "mcp", "接続層", ["RC-1", "RC-3", "RC-5"]),
    # IDE/platform
    (r"(PowerShell|IDE|VS\s+Code|JetBrains)\s+(?:tool|extension|integration)",
     "platform", "接続層", ["RC-3", "RC-6"]),
    # SDK/headless
    (r"(SDK|headless|Remote\s+Control)\s+(?:session|support|client)",
     "sdk", "接続層", ["RC-3", "RC-5"]),
]

# Keywords for generating CAPABILITY_KEYWORDS entries
KEYWORD_GENERATORS = {
    "接続層": ["接続", "connect", "server", "api", "mcp"],
    "実行層": ["実行", "execute", "run", "dispatch"],
    "自動化層": ["自動", "hook", "trigger", "event"],
    "品質保証層": ["品質", "検証", "security", "permission"],
    "知識層": ["知識", "memory", "context", "session"],
    "推論層": ["推論", "model", "reasoning"],
}

# Action type mapping by layer
LAYER_ACTION_MAP = {
    "接続層": {"type": "tool", "target": "mcp_call"},
    "実行層": {"type": "bash", "target": "python3"},
    "自動化層": {"type": "hook", "target": "PreToolUse"},
    "品質保証層": {"type": "bash", "target": "python3"},
    "知識層": {"type": "tool", "target": "memory"},
    "推論層": {"type": "subagent", "target": "general-purpose"},
}


@dataclass
class DiscoveredCapability:
    """A newly discovered capability from release notes."""
    item_id: str
    item_name: str
    item_type: str
    layer_category: str
    summary: str
    source_version: str
    source_url: str
    applicable_rcs: list[str]
    keywords: list[str]
    action_type: str
    action_target: str
    discovered_at: str = field(default_factory=lambda: datetime.now().isoformat())

    def to_catalog_entry(self) -> str:
        """Generate markdown catalog entry."""
        today = datetime.now().strftime("%Y-%m-%d")
        return f"""
---

#### {self.item_id} | {self.item_name}

- **item_id**: {self.item_id}
- **item_name**: {self.item_name}
- **item_type**: {self.item_type}
- **layer_category**: {self.layer_category}
- **vendor_owner**: Anthropic
- **source_url**: {self.source_url}
- **summary**: {self.summary}
- **primary_use_cases**: Claude Code の新機能として自動検出。詳細はリリースノート参照。
- **prerequisites**: Claude Code CLI {self.source_version}+
- **current_status**: 候補
- **first_seen_at**: {today}
- **last_checked_at**: {today}
- **notes**: Layer 10 自動検出。リリース {self.source_version} で追加。"""

    def to_pool_entry(self) -> dict:
        """Generate dynamic capability pool entry."""
        return {
            "item_id": self.item_id,
            "name": self.item_name,
            "applicable_rcs": self.applicable_rcs,
            "keywords": self.keywords,
            "action": {
                "type": self.action_type,
                "target": self.action_target,
                "desc": self.summary[:80],
            },
            "step_affinity": self._infer_step_affinity(),
        }

    def _infer_step_affinity(self) -> list[str]:
        """Infer which work steps this capability belongs to."""
        affinity_map = {
            "接続層": ["調査", "実装"],
            "実行層": ["実装", "検証"],
            "自動化層": ["実装", "検証"],
            "品質保証層": ["検証"],
            "知識層": ["調査", "記録"],
            "推論層": ["調査", "設計"],
        }
        return affinity_map.get(self.layer_category, ["調査"])


def _atomic_save(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, tmp = tempfile.mkstemp(dir=path.parent, suffix=".tmp")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        os.replace(tmp, path)
    except BaseException:
        try:
            os.unlink(tmp)
        except OSError:
            pass
        raise


def _safe_load(path: Path) -> dict | None:
    if not path.exists():
        return None
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (json.JSONDecodeError, OSError):
        return None


class CatalogUpdater:
    """Fetches releases → extracts features → updates catalog + dynamic capabilities."""

    def __init__(self, state_dir: Path, catalog_path: Path):
        self.state_dir = state_dir
        self.catalog_path = catalog_path
        self.dynamic_path = state_dir / "dynamic_capabilities.json"
        self.releases_cache_path = state_dir / "releases_cache.json"
        self._load_state()

    def _load_state(self):
        """Load existing dynamic capabilities and release cache."""
        self.dynamic = _safe_load(self.dynamic_path) or {
            "capabilities": [],
            "known_item_ids": [],
            "last_updated": "",
            "last_release_tag": "",
        }
        self.releases_cache = _safe_load(self.releases_cache_path) or {
            "releases": [],
            "last_fetched": "",
        }

    def update_from_releases(self, repo: str = "anthropics/claude-code",
                              max_releases: int = 5) -> dict:
        """Full update cycle: fetch → parse → discover → write."""
        result = {"new_capabilities": [], "catalog_entries_added": 0,
                  "releases_checked": 0, "errors": []}

        # Step 1: Fetch releases from GitHub API
        releases = self._fetch_releases(repo, max_releases)
        result["releases_checked"] = len(releases)

        if not releases:
            result["errors"].append("No releases fetched")
            return result

        # Step 2: Filter to only new releases
        last_tag = self.dynamic.get("last_release_tag", "")
        new_releases = []
        for r in releases:
            if r["tag_name"] == last_tag:
                break
            new_releases.append(r)

        if not new_releases:
            return result  # All up to date

        # Step 3: Extract features from release notes
        known_ids = set(self.dynamic.get("known_item_ids", []))
        next_id = self._get_next_item_id()

        discovered = []
        for release in new_releases:
            body = release.get("body", "") or ""
            tag = release.get("tag_name", "")
            url = release.get("html_url", "")

            features = self._extract_features(body, tag, url)
            for feat in features:
                # Deduplicate by name similarity
                if not self._is_duplicate(feat["name"], known_ids):
                    cap = DiscoveredCapability(
                        item_id=f"F-{next_id:03d}",
                        item_name=feat["name"],
                        item_type=feat["type"],
                        layer_category=feat["layer"],
                        summary=feat["summary"],
                        source_version=tag,
                        source_url=url,
                        applicable_rcs=feat["rcs"],
                        keywords=feat["keywords"],
                        action_type=feat["action"]["type"],
                        action_target=feat["action"]["target"],
                    )
                    discovered.append(cap)
                    known_ids.add(cap.item_id)
                    next_id += 1

        # Step 4: Write to catalog and dynamic capabilities
        if discovered:
            self._append_to_catalog(discovered)
            self._update_dynamic(discovered, new_releases[0]["tag_name"])
            result["new_capabilities"] = [
                {"id": c.item_id, "name": c.item_name, "rcs": c.applicable_rcs}
                for c in discovered
            ]
            result["catalog_entries_added"] = len(discovered)

        # Even if no new capabilities, update the release tag
        if new_releases:
            self.dynamic["last_release_tag"] = new_releases[0]["tag_name"]
            self.dynamic["last_updated"] = datetime.now().isoformat()
            _atomic_save(self.dynamic_path, self.dynamic)

        # Cache releases
        self.releases_cache["releases"] = [
            {"tag": r["tag_name"], "date": r.get("published_at", ""),
             "body_preview": (r.get("body") or "")[:200]}
            for r in releases
        ]
        self.releases_cache["last_fetched"] = datetime.now().isoformat()
        _atomic_save(self.releases_cache_path, self.releases_cache)

        return result

    def get_dynamic_capabilities(self) -> dict:
        """Return current dynamic capabilities for orchestrator consumption."""
        return _safe_load(self.dynamic_path) or {"capabilities": []}

    # ── Private ──────────────────────────────────────────────────────

    def _fetch_releases(self, repo: str, max_releases: int) -> list[dict]:
        """Fetch releases: prefer gh CLI (authenticated, 5000 req/hr) → fallback to urllib."""
        import shutil
        import subprocess

        # Strategy 1: gh CLI (authenticated — avoids rate limits)
        gh_path = shutil.which("gh")
        if gh_path:
            try:
                r = subprocess.run(
                    [gh_path, "api", f"repos/{repo}/releases",
                     "-q", f".[0:{max_releases}]"],
                    capture_output=True, text=True, timeout=15,
                )
                if r.returncode == 0 and r.stdout.strip():
                    return json.loads(r.stdout)
            except Exception:
                pass

        # Strategy 2: Direct API (unauthenticated — 60 req/hr limit)
        url = f"https://api.github.com/repos/{repo}/releases?per_page={max_releases}"
        try:
            req = urllib.request.Request(url, headers={
                "User-Agent": "OrchestraAgent/2.0",
                "Accept": "application/vnd.github.v3+json",
            })
            with urllib.request.urlopen(req, timeout=15) as resp:
                return json.loads(resp.read().decode())
        except Exception:
            return []

    def _extract_features(self, body: str, tag: str, url: str) -> list[dict]:
        """Extract NEW FEATURES only from a release note body. Excludes bug fixes."""
        features = []
        if not body:
            return features

        for line in body.split("\n"):
            line_stripped = line.strip()
            if not line_stripped or line_stripped.startswith("#"):
                continue

            # Remove leading bullet
            cleaned = re.sub(r"^[-•*]\s*", "", line_stripped)
            cleaned_lower = cleaned.lower()

            # EXCLUDE bug fixes, reverts, polish
            if any(cleaned_lower.startswith(p) for p in EXCLUDE_PREFIXES):
                continue

            # Only process lines that look like new features
            is_feature = (
                any(cleaned_lower.startswith(p) for p in FEATURE_LINE_PREFIXES)
                or re.match(r"^[`/]\w", cleaned)  # starts with `/command` or `setting`
                or "is now available" in cleaned_lower
                or "no longer requires" in cleaned_lower
            )
            if not is_feature:
                continue

            # Classify the feature
            for pattern, feat_type, layer, rcs in FEATURE_CLASSIFIERS:
                match = re.search(pattern, cleaned, re.IGNORECASE)
                if match:
                    # Extract feature name
                    if feat_type == "command":
                        name_raw = match.group(1) if match.lastindex else ""
                        name = f"/{name_raw}" if name_raw and not name_raw.startswith("/") else name_raw
                    elif feat_type == "model":
                        name_raw = match.group(1) if match.lastindex else ""
                        name = name_raw.strip()
                    else:
                        name_raw = match.group(1) if match.lastindex and match.group(1) else ""
                        name = name_raw.strip() if name_raw else self._extract_name_from_line(cleaned)

                    if not name or len(name) < 2:
                        name = self._extract_name_from_line(cleaned)
                    if not name or len(name) < 2:
                        continue

                    action = LAYER_ACTION_MAP.get(layer, {"type": "bash", "target": "python3"})
                    keywords = self._generate_keywords(name, layer)

                    features.append({
                        "name": name,
                        "type": "公式機能",
                        "layer": layer,
                        "summary": self._build_summary(cleaned, tag),
                        "rcs": rcs,
                        "keywords": keywords,
                        "action": action,
                    })
                    break

        return features

    def _extract_name_from_line(self, line: str) -> str:
        """Extract a short feature name from a line when regex didn't capture one."""
        # Look for backtick-quoted names
        bt = re.search(r"`(/?\w[\w-]*)`", line)
        if bt:
            return bt.group(1)
        # Take first meaningful phrase (before dash or comma)
        parts = re.split(r"\s+(?:—|–|-|,|\.)\s+", line, maxsplit=1)
        name = parts[0].strip()
        # Remove "Added" prefix
        name = re.sub(r"^(?:Added|New|Changed)\s+", "", name, flags=re.I)
        if len(name) > 50:
            name = name[:50].rsplit(" ", 1)[0]
        return name

    def _clean_feature_name(self, line: str) -> str:
        """Extract a usable feature name from a line."""
        # Remove markdown formatting
        cleaned = re.sub(r"[*_`#\[\]\(\)]", "", line)
        # Remove common prefixes
        cleaned = re.sub(r"^[-•]\s*", "", cleaned)
        cleaned = re.sub(r"^(?:feat|fix|chore|docs|refactor)\s*[:(]\s*", "", cleaned, flags=re.I)
        # Take first meaningful phrase
        parts = re.split(r"[.!?—–:;]", cleaned)
        return parts[0].strip()[:60] if parts else ""

    def _normalize_feature_name(self, raw: str) -> str:
        """Create a clean, titlecase feature name."""
        # Remove leading/trailing whitespace and common noise
        name = raw.strip()
        name = re.sub(r"\s+", " ", name)
        if len(name) > 50:
            name = name[:50].rsplit(" ", 1)[0]
        return name

    def _build_summary(self, line: str, tag: str) -> str:
        """Build a concise summary from the release note line."""
        cleaned = re.sub(r"[*_`#]", "", line).strip()
        cleaned = re.sub(r"^[-•]\s*", "", cleaned)
        if len(cleaned) > 150:
            cleaned = cleaned[:150].rsplit(" ", 1)[0] + "..."
        return f"Claude Code {tag}: {cleaned}"

    def _generate_keywords(self, name: str, layer: str) -> list[str]:
        """Generate search keywords for capability matching."""
        keywords = []
        # Add layer-based keywords
        keywords.extend(KEYWORD_GENERATORS.get(layer, [])[:2])
        # Add name-derived keywords
        words = re.findall(r"\w+", name.lower())
        keywords.extend(w for w in words if len(w) > 2 and w not in ("the", "and", "for", "with"))
        return list(dict.fromkeys(keywords))[:8]  # Dedupe, max 8

    def _is_duplicate(self, name: str, known_ids: set) -> bool:
        """Check if a feature name is too similar to existing capabilities."""
        name_lower = name.lower()
        for cap in self.dynamic.get("capabilities", []):
            existing = cap.get("name", "").lower()
            # Exact match or very high overlap
            if name_lower == existing or name_lower in existing or existing in name_lower:
                return True
        return False

    def _get_next_item_id(self) -> int:
        """Get the next available F-XXX ID by scanning catalog and dynamic state."""
        max_id = 38  # Known max from static catalog

        # Check dynamic capabilities
        for cap in self.dynamic.get("capabilities", []):
            fid = cap.get("item_id", "")
            m = re.match(r"F-(\d+)", fid)
            if m:
                max_id = max(max_id, int(m.group(1)))

        # Check catalog file for any higher IDs
        if self.catalog_path.exists():
            content = self.catalog_path.read_text(encoding="utf-8")
            for m in re.finditer(r"F-(\d+)", content):
                max_id = max(max_id, int(m.group(1)))

        return max_id + 1

    def _append_to_catalog(self, capabilities: list[DiscoveredCapability]) -> None:
        """Append new entries to 02_candidate_catalog.md."""
        if not capabilities:
            return

        header = f"\n\n## セクション3｜自動検出候補（Layer 10 自動更新: {datetime.now().strftime('%Y-%m-%d')}）\n"

        entries = []
        for cap in capabilities:
            entries.append(cap.to_catalog_entry())

        new_content = header + "\n".join(entries) + "\n"

        # Read existing content
        if self.catalog_path.exists():
            existing = self.catalog_path.read_text(encoding="utf-8")
            # Check if auto-detect section already exists
            if "セクション3｜自動検出候補" in existing:
                # Append to existing section
                new_content = "\n".join(entries) + "\n"
        else:
            existing = ""

        # Atomic append
        full_content = existing + new_content
        fd, tmp = tempfile.mkstemp(dir=self.catalog_path.parent, suffix=".tmp")
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as f:
                f.write(full_content)
            os.replace(tmp, self.catalog_path)
        except BaseException:
            try:
                os.unlink(tmp)
            except OSError:
                pass
            raise

    def _update_dynamic(self, capabilities: list[DiscoveredCapability],
                         latest_tag: str) -> None:
        """Update dynamic_capabilities.json with new entries."""
        existing_caps = self.dynamic.get("capabilities", [])
        existing_ids = set(self.dynamic.get("known_item_ids", []))

        for cap in capabilities:
            existing_caps.append(cap.to_pool_entry())
            existing_ids.add(cap.item_id)

        self.dynamic["capabilities"] = existing_caps
        self.dynamic["known_item_ids"] = sorted(existing_ids)
        self.dynamic["last_release_tag"] = latest_tag
        self.dynamic["last_updated"] = datetime.now().isoformat()

        _atomic_save(self.dynamic_path, self.dynamic)
