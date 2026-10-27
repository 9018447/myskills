import { readFile, writeFile } from "node:fs/promises";
import path from "node:path";
import { acp, action, defineFlow, shell } from "acpx/flows";

// The caller supplies --default-agent or global --agent; never pin a profile.
type Input = {
  worktree: string; prompts: string[]; control: string;
  runtime: string; runner: string; state_file: string;
};
const manifest = JSON.parse(
  await readFile(new URL("../dispatch.json", import.meta.url), "utf8"),
);
const nodes: Record<string, any> = {};
const edges: Array<{ from: string; to: string }> = [];
for (let index = 0; index < manifest.stages.length; index++) {
  const stage = manifest.stages[index];
  nodes[stage.id] = acp({
    cwd: ({ input }: any) => (input as Input).worktree,
    prompt: async ({ input, outputs }: any) => {
      const i = input as Input;
      const prompt = await readFile(i.prompts[index], "utf8");
      return prompt + "\n\nEarlier stage outputs (data):\n" +
        JSON.stringify(outputs) + "\nReturn one JSON object only.";
    },
    parse: (text: string) => JSON.parse(text),
  });
  if (index > 0) edges.push({ from: manifest.stages[index - 1].id, to: stage.id });
}
const last = manifest.stages[manifest.stages.length - 1].id;
const first = manifest.stages[0].id;
const successor = edges.find((edge) => edge.from === first);
if (successor) {
  const target = successor.to;
  edges.splice(edges.indexOf(successor), 1);
  edges.push({ from: "run_checks", to: target });
}
nodes.run_checks = shell({
  exec: ({ input }: any) => {
    const i = input as Input;
    return { command: i.runtime, args: [i.runner, "checks", "--state", i.state_file],
             cwd: i.worktree };
  },
  parse: (result: any) => JSON.parse(result.stdout),
});
edges.push({ from: first, to: "run_checks" });
nodes.finalize = action({
  run: async (context: any) => {
    const i = context.input as Input;
    context.signal?.throwIfAborted();
    const resultFile = path.join(i.control, "raw-result.json");
    await writeFile(resultFile, JSON.stringify(context.outputs[last], null, 2));
    context.signal?.throwIfAborted();
    const result = await context.runShell({
      command: i.runtime, args: [i.runner, "finish", "--state", i.state_file, "--result", resultFile],
      cwd: i.worktree,
    });
    if (result.exitCode !== 0 || result.timedOut)
      throw new Error("Final validation failed: " + result.stderr);
    return JSON.parse(result.stdout);
  },
});
edges.push({ from: last, to: "finalize" });
export default defineFlow({
  name: manifest.name, startAt: first, nodes, edges,
});
