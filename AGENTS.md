# AGENTS.md — info866/ai-sanbou-agent-base

Bootstrapped by `info866/brain` scripts/brain_bootstrap.sh.

## Before non-trivial work, call Brain Router once

Non-trivial = new feature, refactor across 2+ files, bug fix, anything in
`scripts/calendar_secretary/` (if present), API / MCP / RAG changes.

Exempt = README typo, 1-line fix the user pinpointed, format-only changes.

For non-trivial work, **make ONE call** to the Brain Router:

```
GET https://brain.color2021.com/issue-rag/briefing/info866/ai-sanbou-agent-base
  Header: X-API-Key: $BRAIN_API_KEY

# or via MCP:
issue_rag_briefing(owner="info866", repo="ai-sanbou-agent-base")
```

Returned bundle: `project_context` + `recent_lessons` + `active_failures`
+ `acceptance_summary`. Read once, factor into your plan, then start work.

If `active_failures` is non-empty, address those constraints first.
Before finalizing any completion report, also call
`POST /issue-rag/audit-report` with the draft.

## 4-piece protocol (mandatory for any bug discovered + fixed)

1. Create GitHub Issue (`gh issue create --repo info866/ai-sanbou-agent-base --label bug`)
2. Record in `reports/issue_rag_incidents.md` (or this repo's incident log)
3. Commit + push the fix + the record
4. Close the Issue with a comment referencing the fix commit

## Token / secret hygiene before every commit

Abort if the staged diff matches:
```
gho_[A-Za-z0-9]{30,}  ghp_[A-Za-z0-9]{30,}  cfut_[A-Za-z0-9]{30,}
sk-[A-Za-z0-9_-]{20,}  x-api-key:\s*[A-Za-z0-9_-]{20,}
```
