/**
 * RULES.md Context Injector for pi
 *
 * Injects RULES.md content into the FRONT of the system prompt before every
 * LLM call, optimized for Anthropic's prefix-based prompt cache.
 *
 * Why prepend (not append) for cache optimization:
 *
 *   Anthropic prompt caching is prefix-based — the START of the request is
 *   cached and reused. Stable content should be at the very front.
 *
 *   If RULES.md were appended to the END of Pi's system prompt:
 *     Turn N:  [Pi sys prompt v1] + [RULES.md]
 *     Turn N+1:[Pi sys prompt v2] + [RULES.md]  ← Pi prompt changed (tools,
 *                                                   skills, context files)
 *               ^^^^^^^^^^^^^^^^ changed prefix → entire cache invalidated!
 *
 *   By prepending RULES.md to the FRONT:
 *     Turn N:  [RULES.md] + [Pi sys prompt v1]
 *     Turn N+1:[RULES.md] + [Pi sys prompt v2]  ← prefix [RULES.md] is STABLE
 *               ^^^^^^^^^^ cache hit!           → only Pi prompt part re-cached
 *
 *   RULES.md is user-defined and stable across turns. Pi's system prompt
 *   can change (tool descriptions, skills loaded, context files). Placing
 *   the stable content first maximizes cache hit rate.
 *
 *   Note: before_agent_start fires on EVERY turn including Turn 1, so the
 *   modified system prompt is used from the very first request. There is no
 *   "unmodified first turn" that would break the cache.
 *
 * File resolution (in priority order):
 *   1. .pi/RULES.md          (project-local)
 *   2. ~/.pi/agent/RULES.md  (global)
 *
 * Usage:
 *   1. Copy this file to ~/.pi/agent/extensions/rules-injector.ts
 *   2. Create ~/.pi/agent/RULES.md (or .pi/RULES.md in your project)
 *   3. Restart pi or run `/reload`
 *
 * Commands:
 *   /rules-reload  — Force reload RULES.md from disk
 *   /rules-status  — Show which RULES.md is active and its size
 */

import * as fs from "node:fs";
import * as path from "node:path";
import type { ExtensionAPI } from "@earendil-works/pi-coding-agent";

interface RulesState {
	content: string | null;
	path: string | null;
	mtimeMs: number;
	size: number;
}

const state: RulesState = {
	content: null,
	path: null,
	mtimeMs: 0,
	size: 0,
};

/**
 * Find the RULES.md file to use.
 * Priority: project-local > global
 */
function findRulesFile(cwd: string): string | null {
	const projectPath = path.join(cwd, ".pi", "RULES.md");
	if (fs.existsSync(projectPath)) {
		return projectPath;
	}

	const globalPath = path.join(
		process.env.HOME || process.env.USERPROFILE || "~",
		".pi",
		"agent",
		"RULES.md",
	);
	if (fs.existsSync(globalPath)) {
		return globalPath;
	}

	return null;
}

/**
 * Load RULES.md from disk if it has changed.
 * Returns the content, or null if no file found.
 */
function loadRules(cwd: string): string | null {
	const rulesPath = findRulesFile(cwd);

	if (!rulesPath) {
		// File removed since last load
		if (state.path) {
			state.content = null;
			state.path = null;
			state.mtimeMs = 0;
			state.size = 0;
		}
		return null;
	}

	try {
		const stats = fs.statSync(rulesPath);

		// Already loaded and file hasn't changed
		if (
			state.path === rulesPath &&
			stats.mtimeMs <= state.mtimeMs &&
			state.content !== null
		) {
			return state.content;
		}

		const raw = fs.readFileSync(rulesPath, "utf-8");
		const trimmed = raw.trim();

		state.content = trimmed;
		state.path = rulesPath;
		state.mtimeMs = stats.mtimeMs;
		state.size = Buffer.byteLength(raw, "utf-8");

		return trimmed;
	} catch (err) {
		// Reset on error
		state.content = null;
		state.path = null;
		state.mtimeMs = 0;
		state.size = 0;
		return null;
	}
}

/**
 * Invalidate cached content to force a reload on next access.
 */
function invalidateRules(): void {
	state.mtimeMs = 0;
}

/**
 * Format rules content for injection into the system prompt.
 * The content is wrapped in a clear section to help the model understand
 * that these are persistent rules, not part of the conversation.
 */
function formatRulesForSystemPrompt(content: string): string {
	return `\n\n## Persistent Rules\n\nThe following rules apply to ALL responses. These rules are pre-loaded and cached — follow them consistently without needing to re-read them:\n\n${content}`;
}

export default function rulesInjectorExtension(pi: ExtensionAPI) {
	// Load rules when session starts
	pi.on("session_start", async (event, ctx) => {
		const content = loadRules(ctx.cwd);

		if (content) {
			const scope = state.path?.includes("/.pi/") ? "project" : "global";
			ctx.ui.notify(
				`RULES.md loaded (${state.size} bytes, ${scope})`,
				"info",
			);
		} else {
			// Only warn if we previously had rules (file was deleted)
			if (state.path) {
				ctx.ui.notify("RULES.md no longer found", "warning");
			}
		}
	});

	// Inject rules into the FRONT of the system prompt before each agent turn.
	// This maximizes cache hit rate because RULES.md is stable user-defined
	// content, while Pi's system prompt can vary (tools, skills, context).
	// By placing RULES.md first, it becomes the stable cache prefix.
	pi.on("before_agent_start", async (event, ctx) => {
		const content = loadRules(ctx.cwd);
		if (!content) {
			return;
		}

		// Prepend rules to the existing system prompt.
		// RULES.md comes FIRST, then Pi's built-in system prompt.
		// This ensures RULES.md forms the stable cache prefix.
		return {
			systemPrompt: formatRulesForSystemPrompt(content) + "\n\n" + event.systemPrompt,
		};
	});

	// Command: force reload RULES.md from disk
	pi.registerCommand("rules-reload", {
		description: "Reload RULES.md from disk",
		handler: async (_args, ctx) => {
			invalidateRules();
			const content = loadRules(ctx.cwd);

			if (content) {
				const scope = state.path?.includes("/.pi/") ? "project" : "global";
				ctx.ui.notify(
					`RULES.md reloaded (${state.size} bytes, ${scope})`,
					"success",
				);
			} else {
				ctx.ui.notify(
					"RULES.md not found. Expected: .pi/RULES.md or ~/.pi/agent/RULES.md",
					"error",
				);
			}
		},
	});

	// Command: show current rules status
	pi.registerCommand("rules-status", {
		description: "Show RULES.md loading status",
		handler: async (_args, ctx) => {
			if (state.content && state.path) {
				const scope = state.path.includes("/.pi/") ? "project" : "global";
				const lines = state.content.split("\n").length;
				ctx.ui.notify(
					`Active: ${state.path} (${scope}, ${state.size} bytes, ${lines} lines)`,
					"info",
				);
			} else {
				ctx.ui.notify(
					"No RULES.md loaded. Expected: .pi/RULES.md or ~/.pi/agent/RULES.md",
					"warning",
				);
			}
		},
	});
}
