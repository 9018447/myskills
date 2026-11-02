---
name: principle-encode-lessons-in-structure
description: "Apply when you notice yourself writing the same instruction or correction a second time, or the same mistake keeps coming back. Signals: repeating guidance in prompts or docs, \"I keep telling it to...\", recurring review comments."
---

> YPM 执行约定见 [共享规则](../../../references/ypm-policy.md)。保留 pstack 工程步骤，仅适配角色、工具和引用。

# Encode Lessons in Structure

When the same instruction or correction shows up a second time, stop adding text and change the structure so the rule cannot be broken. Prose only steers readers who remember to read it; a lint, metadata flag, runtime check, or script enforces the rule whether or not anyone is looking.

**Why:** Each repetition of an instruction is evidence that text is not holding. Adding a third reminder raises the noise budget without raising the guarantee. Encode the lesson once in a mechanism that fails loudly when violated.

**Pattern:**
- Catch the repetition: the same review comment, the same prompt line, the same "don't do X" is your trigger.
- Ask what structure would make X impossible or obvious: a lint rule, a type, a metadata flag, a runtime assertion, a check script, a scaffold that only builds the correct shape.
- Build the guard once and let it carry the rule from then on.

If the lesson needs judgment and cannot be encoded, make the instruction more prominent and add an example of the failure mode.

**Corollary:** If the fix is structural, only use the structural fix. The instruction is the symptom.
