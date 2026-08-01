# AGENTS.md outline for ULW

Use this outline as a checklist, not a rigid template. Keep sections that are supported by repository evidence and skip empty filler.

## Recommended section order

1. `# AGENTS.md`
2. `## Project Overview`
3. `## Repository Structure`
4. `## Setup Commands`
5. `## Development Workflow`
6. `## Testing Instructions`
7. `## Code Style / Conventions`
8. `## Build / Release / Deployment`
9. `## Troubleshooting / Gotchas`
10. `## PR / Change Expectations`

## Evidence rules

- Prefer commands copied from repo scripts, task files, docs, or CI.
- If a section cannot be supported by evidence, omit it or label it as an inference.
- If the repository is a monorepo, explain both root-level rules and package-specific differences.
- Mention generated directories, vendored code, or artifacts that agents should avoid editing directly.

## Good section examples

### Project Overview
- What the project does
- Main languages/frameworks
- Whether it is a library, app, monorepo, template, or automation repo

### Repository Structure
- Meaning of each top-level directory
- Entry points, package boundaries, docs, and script locations

### Testing Instructions
- Exact commands for all tests
- Targeted test patterns if discoverable
- Expectations before commit or PR if CI makes them clear

### Troubleshooting / Gotchas
- Environment quirks
- Generated files
- Required services or external dependencies
- Commands that must be run from a specific directory

## What to avoid

- Generic text that could fit any repository
- Commands not supported by files in the repo
- Repeating README prose without adding agent-relevant context
- Excessive detail for lockfiles, caches, or binary assets
