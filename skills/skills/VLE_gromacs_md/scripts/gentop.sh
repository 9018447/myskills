#!/bin/bash
set -e # 遇到错误立即退出

# =================配置区域=================
SOBTOP_DIR="${SOBTOP_DIR:-/media/smh/d/sobtop}"
# ==========================================

if [ $# -eq 0 ]; then
    echo "错误：请提供分子文件路径"
    echo "用法：bash $0 <分子文件路径>"
    exit 1
fi

# 检查依赖
if ! command -v realpath &> /dev/null; then
    echo "错误：未找到 realpath 命令，请先安装 (coreutils)"
    exit 1
fi

# 保存当前工作目录
ORIG_DIR="$(pwd)"

# 获取输入文件的绝对路径
MOL2_FILE_ABS="$(realpath "$1")"
DIR_NAME="$(dirname "$MOL2_FILE_ABS")"
BASENAME="$(basename "$MOL2_FILE_ABS" .mol2)"

# 推导关联文件路径 (假设在同一目录)
FCHK_FILE_ABS="${DIR_NAME}/${BASENAME}.fchk"
CHG_FILE_ABS="${DIR_NAME}/${BASENAME}.chg"

# 文件名（sobtop 运行时需要的文件名）
MOL2_NAME="${BASENAME}.mol2"
FCHK_NAME="${BASENAME}.fchk"
CHG_NAME="${BASENAME}.chg"

echo "=== 任务信息 ==="
echo "工作目录: $ORIG_DIR"
echo "分子文件: $MOL2_FILE_ABS"
echo "FCHK文件: $FCHK_FILE_ABS"
echo "Sobtop源目录: $SOBTOP_DIR"
echo "================"

# 检查输入文件
if [ ! -f "$MOL2_FILE_ABS" ]; then
    echo "错误：文件不存在 $MOL2_FILE_ABS"
    exit 1
fi
if [ ! -f "$FCHK_FILE_ABS" ]; then
    echo "错误：文件不存在 $FCHK_FILE_ABS"
    exit 1
fi

# 检查 Sobtop 目录
if [ ! -d "$SOBTOP_DIR" ]; then
    echo "错误：Sobtop 目录不存在 $SOBTOP_DIR"
    exit 1
fi

# ================= 隔离环境构建 =================
# 创建唯一的临时工作目录，用于本次运行
WORK_DIR=$(mktemp -d -t sobtop_run_XXXXXX)
echo "创建隔离环境: $WORK_DIR"

# 定义清理函数（在脚本退出时执行）
cleanup() {
    echo "正在清理临时环境..."
    # 稍微安全一点，确保不删错
    if [[ "$WORK_DIR" == /tmp/sobtop_run_* ]]; then
        rm -rf "$WORK_DIR"
    fi
}
trap cleanup EXIT

# 将 Sobtop 的资源链接到隔离环境
# 使用 find 避免通配符扩展问题，并只链接一级目录/文件
find "$SOBTOP_DIR" -maxdepth 1 -mindepth 1 -exec ln -sf {} "$WORK_DIR/" \;

# 切换到隔离环境
cd "$WORK_DIR"

# 链接输入文件到隔离环境
ln -sf "$MOL2_FILE_ABS" "$MOL2_NAME"
ln -sf "$FCHK_FILE_ABS" "$FCHK_NAME"

if [ -f "$CHG_FILE_ABS" ]; then
    echo "找到并链接 chg 文件..."
    ln -sf "$CHG_FILE_ABS" "$CHG_NAME"
else
    echo "未找到 chg 文件 (跳过链接)"
fi

# 设置环境变量，指向隔离环境
# 这样 Sobtop 会在当前隔离目录寻找 data/param 等（如果它遵循 SOBTOP_HOME）
export SOBTOP_HOME="$WORK_DIR"
export PATH="$WORK_DIR:$PATH"

echo "启动 Sobtop (在隔离环境中)..."

# 启动 sobtop
# 假设 sobtop 可执行文件已通过 ln -sf 链接到了当前目录，且在 PATH 中
# 如果 sobtop 是脚本或二进制，它现在应该能运行
sobtop << EOF
$MOL2_NAME
7
10
$CHG_NAME
0
2

1
2
7
$FCHK_NAME


0
EOF

# 检查生成结果并移动回原目录
echo "将结果复制回原目录..."

# 启用 nullglob，若没有匹配文件则不展开为字面量
shopt -s nullglob

count=0
missing_types=()

for ext in gro top itp; do
    files=( *."$ext" )
    if [ ${#files[@]} -gt 0 ]; then
        echo "发现 .$ext 文件 (${#files[@]} 个):"
        for f in "${files[@]}"; do
            echo "  正在复制 $f -> $ORIG_DIR/ ..."
            if cp "$f" "$ORIG_DIR/"; then
                echo "    复制成功"
                count=$((count + 1))
            else
                echo "    错误: 复制 $f 失败"
            fi
        done
    else
        echo "未找到 .$ext 文件"
        missing_types+=(".$ext")
    fi
done

shopt -u nullglob

if [ $count -gt 0 ]; then
    echo "处理完成！共复制了 $count 个文件至 $ORIG_DIR"
    if [ ${#missing_types[@]} -gt 0 ]; then
        echo "警告: 未生成以下类型的文件: ${missing_types[*]}"
        # 这里不强制退出，因为可能某些情况下并不总是生成所有文件，但在当前工作流中通常需要
    fi
else
    echo "错误：未成功复制任何结果文件 (.gro, .top, .itp)"
    echo "当前临时目录内容:"
    ls -l
    exit 1
fi