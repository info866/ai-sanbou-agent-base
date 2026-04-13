Run a single watch/sync cycle to check for external updates.

1. Execute: `python3 オーケストラエージェント/orchestrator.py --watch`
2. Parse the JSON output
3. If changes_detected > 0, summarize them
4. If reeval_processed > 0, note which capabilities were re-evaluated
5. Keep the response to 3 lines or less if no changes detected
