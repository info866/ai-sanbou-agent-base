Show the current orchestrator system status.

1. Execute: `python3 オーケストラエージェント/orchestrator.py --status`
2. Format the JSON output as a concise status report showing:
   - Runtime capabilities (claude CLI version, dispatch capability)
   - Watch state (targets, known hashes, pending events)
   - Improvement state (version, applied count)
   - Evaluation records count
