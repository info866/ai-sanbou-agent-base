Run the autonomous orchestrator for the given request. The external orchestrator (orchestrator.py) is the single brain — do not duplicate its classification, model selection, or capability logic here.

Steps:
1. Execute: `python3 オーケストラエージェント/orchestrator.py "$ARGUMENTS"`
2. Parse the JSON output
3. Report the classification, model selection, and execution results to the user
4. For any deferred actions with `deferred_reason` containing "harness-only", execute them natively:
   - If action_type is "slash_command" and target starts with "/skill": use the Skill tool
   - If action_type is "slash_command" and target starts with "/schedule": use the Skill tool with skill name "schedule"
   - If action_type is "hook": skip (hooks fire automatically via settings.json)
5. If improvements were applied, mention the count
6. Keep the response concise
