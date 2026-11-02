---
name: ypm-playbook-session-pickup
description: "从现有记录继续推进，避免重复劳动；YPM 改编自 pstack session-pickup Playbook。"
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

### Session pickup

**You own the resume point. Read the prior trail, don't redo it.**

1. Locate the prior trail. A local transcript in the active workspace's session directory (in Cursor, the `agent-transcripts/` directory the system prompt names. Other harnesses: see the shared policy’s Harness section. Do not glob across every project's directory, that crosses workspace boundaries and reads private chats from unrelated projects), a cloud-agent URL, or a pushed branch. Read the metadata overview and last messages first, then scan back for the decision points. Have the Minister dispatch long-transcript parsing to an appointed civil servant; an assigned civil servant parses it directly and keep the reduced timeline in the main thread (the **principle-guard-the-context-window** skill). Use the appointed Agent configuration; follow the YPM dispatch rules in the shared policy.
2. Reconstruct operational state. The branch and worktree, what already landed (`git log`, `git diff` against the base), the open todos, the decisions made. The prior trail is authoritative input. Resist the bias to re-derive it.
3. Diff done vs pending. Compare what shipped against what was planned, name the resume point, do not re-run the prior repro or redo completed work. A "let me verify from scratch" pass means you're treating the trail as untrustworthy when it's authoritative.
4. Route the remaining work to the matching playbook and pick the verdict: continue the execution, ship a finished recommendation, ratify or override a prior conclusion, or postmortem a failed run. The pickup playbook ends here. The routed playbook owns the rest.
5. Verify the inherited claims against the original goal on the real artifact (the **principle-prove-it-works** skill). A passing prior self-report is not the proof.

**Reply:** where the prior agent stopped, what you inherited vs redid (ideally nothing redone), the resume point, and the outcome.
