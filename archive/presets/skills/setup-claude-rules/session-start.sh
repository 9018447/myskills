#!/bin/sh
# SessionStart routing hook. Extracted from the pstack-claude plugin
# (michael-denyer/pstack-claude, MIT) and adapted for the myskills skill chain:
# the injected text routes multi-file / design / unknown-cause-bug work through
# the poteto-mode skill. Installed per-repo by setup-claude-rules' install.sh,
# which symlinks this file and session-start-context.md into .claude/hooks/ and
# registers the SessionStart entry in .claude/settings.json. Disable per-repo by
# removing that entry; there is no separate off-switch file.
cat "$(dirname "$0")/session-start-context.md"
