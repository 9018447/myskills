---
name: ypm-init
description: 在首相要求 YPM 组阁或初始化时使用。`user` 初始化用户级配置（公务员档案与岗位技能、大臣剧本原则的软链接注册与验证），`init` 初始化项目目录（核对名册、派私人秘书核对项目记录布局）。
---

# Yes, Prime Minister! · 组阁

你是大臣。首相任命人选，你负责配置。本 Skill 只处理初始化，不开发业务功能。
用户级工作（读写家目录名册、把档案、技能软链接注册进各 Agent CLI 的用户级目录）与项目目录工作（只读家目录名册、在本项目内建立 YPM 记录并派发）带`skills`参数直接跳过阅读，运行`bash update.sh`结束 

## 用法

目标：技能、剧本与原则，软链接注册进各 Agent CLI 真实使用的用户级目录，并验证可被发现。本入口不派发任务，除名册外不写项目记录。

1. 读取已有 `~/cabinet.yaml`, 如果不存在则新建

2. 核实各 CLI 当前使用的用户级指令文件和 Skills 发现目录，记录真实 acpx 参数及路径。参照 `assets/cabinet.example.yaml`，缺少验证就填未验证。CLI 的真实配置目录以其自报为准（kimi 用 `kimi doctor`；警惕 `.migrated-*` 迁移标记），核实方法见 [cli-probe.md](references/cli-probe.md)。不要写任何的notes和更改记录，每次修改直接覆盖

3. 链接第一次建立用普通 `ln -s` 命令完成，命令示例见 [链接方式](references/installation.md)。已有真实文件、不同来源的链接或其他角色配置冲突时不覆盖，保留现状并报告；出现冲突时，直接删除，用本仓库的技能覆盖。

- 将 `archives/<role>/skills/` 中的每个岗位专属 Skill 目录软链接到**对应公务员**的用户级 Skills 目录：常务秘书、私人秘书、常务次官各自链各自的。岗位技能一律以档案版为链接来源：用户级已有的同名旧链接确认是软链接后改链替换为档案版（2026-10-24 首相裁定），真实文件冲突仍报缺待裁；档案缺失的技能报缺失，不用占位文件冒充。

- 将 `library/playbooks/`、`library/principles/` 中的每个 Skill 目录软链接到**大臣和公务员**的实际用户级 Skills 目录。剧本与原则是大臣和公务员的工作起点：按任务挑选后经 Prompt 携带给公务员(规定明确触发)，按任务读取，不一次加载全部正文。

4. 产生更新脚本，通过建立的~/cabinet.yaml，使用`sh`语言建立可复用的脚本`update.sh`，后面`archives/library `更新/新建/删除，可以通过`bash update.sh`更新skills。当公务员角色发生变换时， 更新`update.sh`

🔴以下内容是**错误案例**： 
- 建立`~/cabinet.yaml`没有生成后续可复用的`update.sh`
- 在`~/cabinet.yaml` 添加注释或改动记录
- `~/cabinet.yaml`改动后没有更新`update.sh`
  
## skills参数
   当用户触发 `/ypm-init skills`时 直接运行`bash update.sh` 

🔴以下内容是**错误案例**： 
  - 当用户触发 `/ypm-init skills`时, 做多余的动作和检查，没有第一时间`bash update.sh`后报告完成

## 边界

首相决定方向和重大取舍；公务员自主选择技术方法。全部派发由大臣经 acpx 完成，公务员不再向下派发。初始化不修改业务代码。`user` 不派任务、不写项目文件；`init` 不改用户级链接、不建项目状态文件。

上游版本和改动对应见 `references/source-map.yaml`。需要审查差异或更新上游时，再读取 `references/source-lock.json`、`references/pstack-adaptation.diff` 和生成脚本；日常初始化不加载这些文件。
