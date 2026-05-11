# Claude Code — Build Instruction: Orchestra “Zero-Slash” Full Auto

Paste this block into Claude Code as the task prompt.

---

## Objective

Make **AI統合オーケストラ** usable so the user **never needs slash commands or memorized triggers**. Normal chat input should drive **`orchestrator.py` full pipeline** (classify → model → plan → gates → connections → execute → record → improve) unless skipped for safety.

## Non-Goals

- Teaching the user `/orchestrate` (keep slash as optional fallback only).
- Perfect automation of human-only steps (e.g. `gh auth login`, MCP server bring-up).

## Required Behavior

1. **UserPromptSubmit hook**  
   - On **every** user prompt (no `▶`, no `!orchestrate`, no `.orchestra_hook_all` file).  
   - Invoke: `python3 <ABS_PATH>/claude_cc_hook/<hook>.py` (stdin = hook JSON).  
   - Hook runs: `orchestrator.py` with the **full user text** as the single argument (after minimal trim).  
   - Return Claude hook JSON with `hookSpecificOutput.additionalContext` containing the orchestrator JSON stdout (truncate if needed; document cap).

2. **Guards (minimal)**  
   - If prompt is empty / whitespace only → return `{}` or empty additionalContext (no orchestrator run).  
   - Optional: ignore very short noise (e.g. `< 2` chars) — document if added.  
   - On subprocess failure / timeout: inject **short** error context, do not block the user’s prompt unless product decision is to block (default: **do not** block; fail open for UX).

3. **Paths**  
   - Hook `command` in `.claude/settings.json` must use **absolute path** to the hook script (CWD varies when Claude launches).  
   - Inside the hook, resolve `orchestrator.py` by walking from `cwd` in stdin (same logic as existing hooks).

4. **setup.py**  
   - Default install: merge **UserPromptSubmit** full-auto hook + keep **SessionStart** optional or lightweight (status/runtime only).  
   - Flags: `--no-hook` disables all; `--slash-only` if you need a mode without prompt hook (optional).  
   - Idempotent merges; no duplicate hook entries.

5. **Docs**  
   - README: one short section — “Type normally; orchestrator runs each message; slash is optional.”

## Files to Touch (expected)

- `オーケストラエージェント/claude_cc_hook/user_prompt_orchestrate_hook.py` (or new `full_auto_prompt_hook.py`)  
- `オーケストラエージェント/setup.py` (merge hooks, defaults)  
- `README.md` (short UX section)  
- Project `.claude/settings.json` (example / template with **absolute** command — or generate via setup only)

## Acceptance Criteria

- [ ] Opening Claude Code in project root: user sends plain Japanese/English request → orchestrator runs without `/` or `▶`.  
- [ ] Hook works when Claude is launched from non-root CWD (absolute command path).  
- [ ] `setup.py` produces working config on a fresh machine (Python 3.10+).  
- [ ] No mandatory slash command in user-facing flow.

## Tests (manual)

- Send one-line request → JSON outcome appears in context.  
- Send empty message → no crash.  
- Disconnect `gh` / MCP → orchestrator returns `blocked_by_connections`; context still useful.

---

**End of instruction block**
