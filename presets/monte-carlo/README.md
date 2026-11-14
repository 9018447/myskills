# monte-carlo 预设集

气体吸附与孔隙结构分析的蒙特卡洛技能集，5 个成员技能，全部基于 RASPA3。

## 成员

| 技能 | 用途 |
|---|---|
| `gas-adsorption` | 气体吸附模拟 |
| `adsorption-isotherm` | 吸附等温线 |
| `gas-separation` | 混合气体分离 |
| `gcmc-simulation` | 巨正则蒙特卡洛模拟 |
| `pore-analysis` | 孔隙结构分析 |

## 来源

上游 MatClaw 的容器计算技能库 `container/skills/monte-carlo/`。该目录不在公开 git 仓库中
（各分支与标签均无），只烘焙进容器镜像，因此从镜像层提取：

- 镜像：`ghcr.io/dingyanglyu/matclaw-agent:latest`（amd64）
- manifest：`sha256:465052af6a782a93fbea5421069f3c20ec1d5d768047c842c64db480f996cbcd`
- 层：`COPY skills/ /home/node/.claude/skills/`，`sha256:9e657287dd5ee0ff67c94f32fc774db58569698a8018f3bb66a162b62a00a663`（2.48 MB）
- 提取日期：2026-11-14
- 上游仓库：https://github.com/DingyangLyu/MatClaw （Apache-2.0）

5 个 `SKILL.md` 正文与上游逐字一致，仅在头部补了本仓库分发所需的 YAML frontmatter
（`name` / `description` / `license` / `metadata`）。上游子技能原本没有 frontmatter。

## 运行依赖

技能正文假定容器内环境：`raspa3` 二进制、示例库 `/usr/share/raspa3/examples/`、ASE、pymatgen。
本机 `/RASPA/simulations` 装的是 **RASPA 2.0.41**（`simulate`，文本输入），与技能要求的
RASPA3（`raspa3`，JSON 输入 `simulation.json`）**不是同一代**，直接照搬命令会失败。

---

# Monte Carlo Simulations

Grand Canonical Monte Carlo (GCMC) and related ensemble simulations for gas adsorption, mixture separation, and thermodynamic property estimation in porous materials (MOFs, zeolites, covalent organic frameworks).

## Sub-Skills

| Sub-Skill | Directory | Description |
|---|---|---|
| Gas Adsorption | `gas-adsorption/` | GCMC adsorption isotherms, Henry coefficients, mixture selectivity, and heat of adsorption using RASPA3 |

## Method Decision Guide

```
What Monte Carlo property do you need?

Single-component adsorption isotherm (loading vs pressure)?
  --> gas-adsorption/  (GCMC at multiple pressures)

Henry coefficient / heat of adsorption at infinite dilution?
  --> gas-adsorption/  (Widom insertion method)

Mixture selectivity (e.g., CO2/N2)?
  --> gas-adsorption/  (multi-component GCMC)

Diffusion in pores?
  --> Consider MD instead (molecular-dynamics/ in thermal-properties/)
  --> Or use RASPA3 with MSD tracking in NVT/NVE ensemble

Framework: need charges for polar molecules (CO2, H2O)?
  --> gas-adsorption/ covers charge assignment strategies
```

## Tool

All Monte Carlo simulations use **RASPA3** (`raspa3` binary). RASPA3 uses JSON-based input files (`simulation.json`) rather than the legacy RASPA2 text format. Official examples are at `/usr/share/raspa3/examples/`.
