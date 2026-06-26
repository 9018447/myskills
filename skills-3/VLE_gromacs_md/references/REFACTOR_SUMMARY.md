# GROMACS MD Workflow 重构总结

## 重构目标
移除所有 Zellij 依赖，使用 pueue 任务队列管理 MD 模拟工作流。

## 主要改动

### 1. 后台运行机制
**之前**: 使用 Zellij 会话管理，需要额外安装依赖
**现在**: 使用 pueue 任务队列，专业任务管理

### 2. 文件变更

#### 修改的文件
- `scripts/run_workflow.sh` - 核心重构
  - 移除 `USE_ZELLIJ` 变量和 `--no-zellij` 参数
  - 重写 `run_md_background()` 函数
  - 使用 `pueue add` 提交后台任务

- `scripts/check_progress.sh` - 监控逻辑更新
  - 移除 Zellij 会话检查
  - 使用 `pueue list` 查看任务队列状态

- `SKILL.md` - 文档更新
  - 移除所有 Zellij 相关说明
  - 更新为 pueue 任务管理文档
  - 更新监控方法说明

#### 删除的文件
- `task.kdl` - Zellij 布局模板
- `references/gromacs-md.kdl` - Zellij 布局参考

### 3. 工作流保持不变
- **前台执行**: 能量最小化 + 默认 NVT（`--run-nvt` 现在只是显式声明）
- **后台执行**: 三阶段 NPT 平衡 + Production MD

### 4. 新的后台运行方式

```bash
# 启动（pueue 自动管理任务）
pueue add -- bash local_stage_runner.sh

# 监控
pueue list
pueue status
pueue log [task_id]

# 管理任务
pueue pause [task_id]
pueue resume [task_id]
pueue remove [task_id]
```

### 5. 生成的文件
- `.gromacs_local.env` - 环境变量配置
- `gromacs_md.log` - 后台任务日志

## 优势
- ✅ 专业任务队列管理
- ✅ 支持暂停/恢复/取消任务
- ✅ 便于查看任务状态和日志
- ✅ 支持任务依赖关系（未来扩展）
