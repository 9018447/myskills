#!/bin/bash

# DFT 团簇构象搜索助手 - 自动化工作流（非交互模式）
# 功能：从任意目录运行，自动处理团簇构象搜索全流程
#
# 用法：
#   ./cluster_search_step1.sh <分子种类数> "<分子1_xyz:数量>" "<分子2_xyz:数量>" ... <总电荷> <输出文件名>
#
# 示例：
#   ./cluster_search_step1.sh 2 "water.xyz:3" "methane.xyz:2" 0 cluster_opt
#   ./cluster_search_step1.sh 1 "benzene.xyz:5" -1 benzene_cluster

#==========================================
# 环境配置部分 - 用户可修改
#==========================================

# 目标工作目录路径（请修改为您的工作目录）
# 如果为空，将使用脚本所在目录下的 cluster_search_workspace
TARGET_WORK_DIR="/media/smh/d/moclus"

# 如果 TARGET_WORK_DIR 为空，使用默认路径
if [ -z "$TARGET_WORK_DIR" ]; then
    SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
    TARGET_WORK_DIR="${SCRIPT_DIR}/cluster_search_workspace"
fi

#==========================================
# 参数解析与验证
#==========================================

# 显示用法信息
show_usage() {
    echo "用法："
    echo "  $0 <分子种类数> \"<分子1_xyz:数量>\" \"<分子2_xyz:数量>\" ... <总电荷> <输出文件名>"
    echo ""
    echo "参数说明："
    echo "  分子种类数   : 正整数，表示有多少种不同的分子（1-10）"
    echo "  分子xyz:数量 : 格式为 \"文件名:数量\"，例如 \"water.xyz:3\""
    echo "  总电荷       : 整数，例如 0, 1, -1, 2, -2"
    echo "  输出文件名   : Gaussian 输入文件名（不含扩展名），例如 cluster_opt"
    echo ""
    echo "示例："
    echo "  $0 2 \"water.xyz:3\" \"methane.xyz:2\" 0 cluster_opt"
    echo "  $0 1 \"benzene.xyz:5\" -1 benzene_cluster"
    echo ""
    exit 1
}

# 检查参数数量
if [ $# -lt 4 ]; then
    echo "错误：参数不足"
    echo ""
    show_usage
fi

# 解析分子种类数
NUM_TYPES=$1
if ! [[ "$NUM_TYPES" =~ ^[0-9]+$ ]] || [ "$NUM_TYPES" -lt 1 ] || [ "$NUM_TYPES" -gt 10 ]; then
    echo "错误：分子种类数必须是 1-10 之间的正整数"
    echo ""
    show_usage
fi

# 预期参数数量：1(种类数) + NUM_TYPES(分子参数) + 1(电荷) + 1(输出文件名)
EXPECTED_ARGS=$((1 + NUM_TYPES + 2))
if [ $# -ne $EXPECTED_ARGS ]; then
    echo "错误：参数数量不匹配"
    echo "预期 $EXPECTED_ARGS 个参数，实际得到 $# 个"
    echo ""
    show_usage
fi

# 解析分子参数
declare -a XYZ_FILES
declare -a QUANTITIES

for ((i=1; i<=NUM_TYPES; i++)); do
    param_index=$((i + 1))
    molecule_param="${!param_index}"

    # 解析 "xyz:数量" 格式
    if [[ ! "$molecule_param" =~ ^([^:]+):([0-9]+)$ ]]; then
        echo "错误：分子参数格式错误，应为 \"xyz文件:数量\""
        echo "得到：$molecule_param"
        echo ""
        show_usage
    fi

    xyz_file="${BASH_REMATCH[1]}"
    quantity="${BASH_REMATCH[2]}"

    # 验证数量范围
    if [ "$quantity" -lt 1 ] || [ "$quantity" -gt 100 ]; then
        echo "错误：分子数量必须在 1-100 之间"
        echo "得到：$quantity"
        echo ""
        show_usage
    fi

    XYZ_FILES+=("$xyz_file")
    QUANTITIES+=("$quantity")
done

# 解析总电荷（倒数第2个参数）
CHARGE_INDEX=$(($# - 1))
CHARGE="${!CHARGE_INDEX}"
if ! [[ "$CHARGE" =~ ^-?[0-9]+$ ]]; then
    echo "错误：电荷必须是整数"
    echo "得到：$CHARGE"
    echo ""
    show_usage
fi

# 解析输出文件名（最后一个参数）
OUTPUT_NAME="${!#}"
if [ -z "$OUTPUT_NAME" ]; then
    echo "错误：输出文件名不能为空"
    echo ""
    show_usage
fi

# 去除可能的扩展名
OUTPUT_NAME="${OUTPUT_NAME%.gjf}"
OUTPUT_NAME="${OUTPUT_NAME%.xyz}"

#==========================================
# 初始化设置
#==========================================

# 保存原始工作目录
ORIGINAL_PWD=$(pwd)

# 错误处理函数
error_exit() {
    echo ""
    echo "错误：$1"
    echo "脚本执行失败。"
    # 恢复原始目录
    cd "$ORIGINAL_PWD" 2>/dev/null
    exit 1
}

# 清理函数（用于 trap）
cleanup() {
    echo ""
    echo "正在清理并恢复原始目录..."
    cd "$ORIGINAL_PWD" 2>/dev/null
}

# 设置 trap 以确保在脚本退出时恢复目录
trap cleanup EXIT

#==========================================
# 创建目标目录结构
#==========================================

echo "=========================================="
echo "  DFT 团簇构象搜索助手 - 自动化工作流"
echo "=========================================="
echo ""
echo "目标工作目录：$TARGET_WORK_DIR"
echo ""

# 检查目标目录路径是否有效
if [ -z "$TARGET_WORK_DIR" ]; then
    error_exit "目标工作目录路径为空。"
fi

# 创建目标工作目录
if [ ! -d "$TARGET_WORK_DIR" ]; then
    echo "创建目标工作目录：$TARGET_WORK_DIR"
    if ! mkdir -p "$TARGET_WORK_DIR"; then
        error_exit "无法创建目标工作目录：$TARGET_WORK_DIR"
    fi
else
    echo "目标工作目录已存在：$TARGET_WORK_DIR"
fi

# 创建 results 子目录
RESULTS_DIR="$TARGET_WORK_DIR/results"
if [ ! -d "$RESULTS_DIR" ]; then
    echo "创建结果目录：$RESULTS_DIR"
    if ! mkdir -p "$RESULTS_DIR"; then
        error_exit "无法创建结果目录：$RESULTS_DIR"
    fi
else
    echo "结果目录已存在：$RESULTS_DIR"
fi

echo ""

#==========================================
# 复制必要文件到目标目录
#==========================================

echo "正在复制文件到目标工作目录..."
echo ""

# 复制 .fchk 文件
fchk_count=0
for file in *.fchk; do
    if [ -f "$file" ]; then
        if cp "$file" "$TARGET_WORK_DIR/"; then
            echo "  已复制：$file"
            ((fchk_count++))
        else
            echo "  警告：无法复制 $file"
        fi
    fi
done
echo "共复制 $fchk_count 个 .fchk 文件"

# 复制 .xyz 文件
xyz_count=0
for file in *.xyz; do
    if [ -f "$file" ]; then
        if cp "$file" "$TARGET_WORK_DIR/"; then
            echo "  已复制：$file"
            ((xyz_count++))
        else
            echo "  警告：无法复制 $file"
        fi
    fi
done
echo "共复制 $xyz_count 个 .xyz 文件"

# 复制可执行文件
executables=("genmer" "molclus" "isostat")
for exe in "${executables[@]}"; do
    if [ -f "$exe" ]; then
        if cp "$exe" "$TARGET_WORK_DIR/"; then
            chmod +x "$TARGET_WORK_DIR/$exe"
            echo "  已复制并设置可执行权限：$exe"
        else
            echo "  警告：无法复制 $exe"
        fi
    else
        echo "  警告：找不到可执行文件 $exe"
    fi
done

# 复制配置文件
config_files=("genmer.ini" "genmer.ini.bak" "settings.ini")
for cfg in "${config_files[@]}"; do
    if [ -f "$cfg" ]; then
        if cp "$cfg" "$TARGET_WORK_DIR/"; then
            echo "  已复制：$cfg"
        else
            echo "  警告：无法复制 $cfg"
        fi
    else
        echo "  警告：找不到配置文件 $cfg"
    fi
done

# 复制模板文件
template_files=("template.inp" "template.gjf")
for tpl in "${template_files[@]}"; do
    if [ -f "$tpl" ]; then
        if cp "$tpl" "$TARGET_WORK_DIR/"; then
            echo "  已复制：$tpl"
        else
            echo "  警告：无法复制 $tpl"
        fi
    fi
done

echo ""

#==========================================
# 切换到目标工作目录
#==========================================

echo "切换到目标工作目录：$TARGET_WORK_DIR"
if ! cd "$TARGET_WORK_DIR"; then
    error_exit "无法切换到目标工作目录：$TARGET_WORK_DIR"
fi
echo "当前工作目录：$(pwd)"
echo ""

#==========================================
# 第一步：检查并转换 .fchk 文件为 .xyz
#==========================================

echo "=========================================="
echo "  步骤 1：转换 FCHK 为 XYZ"
echo "=========================================="
echo ""

echo "正在扫描当前目录下的 .fchk 文件..."
echo ""

# 查找所有 .fchk 文件
shopt -s nullglob
fchk_files=(*.fchk)
shopt -u nullglob

if [ ${#fchk_files[@]} -gt 0 ]; then
    echo "找到 ${#fchk_files[@]} 个 .fchk 文件："
    echo "------------------------------------------"
    
    index=1
    for file in "${fchk_files[@]}"; do
        size=$(du -h "$file" | cut -f1)
        printf "%3d. %-30s (%s)\n" "$index" "$file" "$size"
        ((index++))
    done
    
    echo "------------------------------------------"
    echo ""
    echo "开始转换 .fchk 文件为 .xyz 格式..."
    echo ""
    
    # 检查 Multiwfn 命令是否存在
    if ! command -v Multiwfn &> /dev/null; then
        error_exit "找不到 Multiwfn 命令。请确保已安装 Multiwfn 并添加到 PATH。"
    fi
    
    # 转换每个 .fchk 文件
    converted_count=0
    for file in "${fchk_files[@]}"; do
        base_name="${file%.fchk}"
        xyz_file="${base_name}.xyz"
        
        # 检查是否已存在对应的 .xyz 文件
        if [ -f "$xyz_file" ]; then
            echo "跳过 $file (对应的 $xyz_file 已存在)"
            continue
        fi
        
        echo "正在转换: $file → $xyz_file"
        
        # 执行 Multiwfn 转换（使用管道符直接传入命令）
        if printf "100\n2\n2\n\n0\nq\n" | Multiwfn "$file" > /dev/null 2>&1; then
            echo "  ✓ 转换成功: $xyz_file"
            ((converted_count++))
        else
            echo "  ✗ 转换失败: $file"
        fi
    done
    
    echo ""
    echo "转换完成: 成功转换 $converted_count 个文件"
    echo ""
else
    echo "未找到 .fchk 文件。"
    echo ""
fi

echo "验证命令行参数中指定的 xyz 文件..."
echo ""

# 验证所有参数中指定的 xyz 文件是否存在
missing_files=()
for ((i=0; i<NUM_TYPES; i++)); do
    xyz_file="${XYZ_FILES[$i]}"
    if [ ! -f "$xyz_file" ]; then
        missing_files+=("$xyz_file")
    fi
done

if [ ${#missing_files[@]} -gt 0 ]; then
    echo "错误：以下 xyz 文件不存在："
    for file in "${missing_files[@]}"; do
        echo "  - $file"
    done
    error_exit "请确保所有指定的 xyz 文件都存在。"
fi

echo "所有指定的 xyz 文件都已找到："
echo "------------------------------------------"
for ((i=0; i<NUM_TYPES; i++)); do
    xyz_file="${XYZ_FILES[$i]}"
    quantity="${QUANTITIES[$i]}"
    size=$(du -h "$xyz_file" | cut -f1)
    printf "%3d. %-30s 数量:%3d (%s)\n" "$((i+1))" "$xyz_file" "$quantity" "$size"
done
echo "------------------------------------------"
echo ""

#==========================================
# 第二步：配置 genmer.ini 并运行 genmer
#==========================================

echo "=========================================="
echo "  步骤 2：配置团簇生成参数"
echo "=========================================="
echo ""

# 检查 genmer 可执行文件是否存在
if [ ! -f "./genmer" ]; then
    error_exit "找不到 genmer 可执行文件。"
fi

# 检查 genmer.ini 是否存在
if [ ! -f "genmer.ini" ]; then
    error_exit "找不到 genmer.ini 配置文件。"
fi

# 使用命令行参数配置
echo "使用命令行参数配置："
echo "分子种类数：$NUM_TYPES"
echo ""

config_lines=""

for ((type=0; type<NUM_TYPES; type++)); do
    xyz_file="${XYZ_FILES[$type]}"
    quantity="${QUANTITIES[$type]}"

    echo "--- 第 $((type + 1)) 种分子 ---"
    echo "文件：$xyz_file"
    echo "数量：$quantity"

    # 检查xyz文件是否存在
    if [ ! -f "$xyz_file" ]; then
        error_exit "找不到 xyz 文件：$xyz_file"
    fi

    # 添加到配置
    config_lines+="$quantity"$'\n'
    config_lines+="$xyz_file"$'\n'

    echo ""
done

echo "配置完成。正在更新 genmer.ini..."
echo ""

# 备份原来的 genmer.ini
if [ -f "genmer.ini" ]; then
    cp genmer.ini genmer.ini.bak
    echo "已备份原配置文件为 genmer.ini.bak"
fi

# 读取 genmer.ini 的前10行（参数设置部分）
head_lines=$(head -n 10 genmer.ini)

# 写入新的 genmer.ini
if echo "$head_lines" > genmer.ini && echo "$config_lines" >> genmer.ini; then
    echo "genmer.ini 更新成功。"
else
    echo "错误：无法写入 genmer.ini。"
    # 恢复备份
    if [ -f "genmer.ini.bak" ]; then
        mv genmer.ini.bak genmer.ini
        echo "已恢复原配置文件。"
    fi
    error_exit "genmer.ini 更新失败。"
fi

echo "genmer.ini 已更新，配置如下："
echo "------------------------------------------"
cat genmer.ini
echo "------------------------------------------"
echo ""

# 直接运行 genmer（自动输入回车）
echo "正在运行 ./genmer ..."
echo ""

if echo "" | ./genmer; then
    echo ""
    echo "genmer 执行完成。"
else
    echo ""
    error_exit "genmer 执行失败。"
fi

echo ""

#==========================================
# 第三步：配置电荷并运行 molclus
#==========================================

echo "=========================================="
echo "  步骤 3：配置电荷并运行 molclus"
echo "=========================================="
echo ""

# 检查 settings.ini 是否存在
if [ ! -f "settings.ini" ]; then
    error_exit "找不到 settings.ini 配置文件。"
fi

# 检查 molclus 可执行文件是否存在
if [ ! -f "./molclus" ]; then
    error_exit "找不到 molclus 可执行文件。"
fi

# 使用命令行参数中的电荷
echo "使用命令行参数配置电荷：$CHARGE"
echo ""

# 修改 settings.ini 的 xtb_arg 行
xtb_arg_line="  xtb_arg= \"--gfn 1 --ohess --chrg $CHARGE --uhf 0\""

if sed -i "s|^[[:space:]]*xtb_arg=.*|$xtb_arg_line|" settings.ini; then
    echo "settings.ini 已更新："
    echo "------------------------------------------"
    grep "xtb_arg=" settings.ini
    echo "------------------------------------------"
else
    error_exit "无法更新 settings.ini。"
fi

echo ""

# 运行 molclus
echo "正在运行 ./molclus ..."
echo ""

if ./molclus; then
    echo ""
    echo "molclus 执行完成。"
else
    echo ""
    error_exit "molclus 执行失败。"
fi

echo ""

#==========================================
# 第四步：运行 isostat 进行异构体统计分析
#==========================================

echo "=========================================="
echo "  步骤 4：运行 isostat 进行异构体统计分析"
echo "=========================================="
echo ""

if [ ! -f "./isostat" ]; then
    error_exit "找不到 isostat 可执行文件。"
fi

echo "正在运行 ./isostat ..."
echo ""

if printf "\n\n\n\n" | ./isostat; then
    echo ""
    echo "isostat 执行完成。"
else
    echo ""
    error_exit "isostat 执行失败。"
fi

echo ""

#==========================================
# 第五步：使用 Multiwfn 将 cluster.xyz 转换为 Gaussian 输入文件
#==========================================

echo "=========================================="
echo "  步骤 5：使用 Multiwfn 转换 XYZ 为 GJF"
echo "=========================================="
echo ""

# 检查 cluster.xyz 是否存在
if [ ! -f "cluster.xyz" ]; then
    error_exit "找不到 cluster.xyz 文件。"
fi

# 检查 Multiwfn 命令是否存在
if ! command -v Multiwfn &> /dev/null; then
    error_exit "找不到 Multiwfn 命令。请确保已安装 Multiwfn 并添加到 PATH。"
fi

# 使用命令行参数中的输出文件名
echo "使用输出文件名：$OUTPUT_NAME"

# 将 cluster.xyz 重命名为指定的文件名
echo "正在重命名 cluster.xyz → ${OUTPUT_NAME}.xyz ..."
if mv "cluster.xyz" "${OUTPUT_NAME}.xyz"; then
    echo "  ✓ 重命名完成。"
else
    error_exit "重命名失败。"
fi

echo ""
echo "正在使用 Multiwfn 转换 ${OUTPUT_NAME}.xyz → ${OUTPUT_NAME}.gjf ..."
echo ""

# 使用 Multiwfn 转换 XYZ 为 GJF
# 菜单序列: 100 (文件转换) → 2 (输出为高斯输入文件) → 10 (.gjf格式) → 回车(确认) → 0 (返回) → q (退出)
if printf "100\n2\n10\n\n0\nq\n" | Multiwfn "${OUTPUT_NAME}.xyz" > /dev/null 2>&1; then
    echo "  Multiwfn 转换执行完成。"

    if [ -f "${OUTPUT_NAME}.gjf" ]; then
        echo "  ✓ 生成文件: ${OUTPUT_NAME}.gjf"
    else
        echo "  警告：未找到 ${OUTPUT_NAME}.gjf，可能需要手动检查。"
    fi
else
    echo ""
    error_exit "Multiwfn 转换失败。"
fi

# 将生成的 .gjf 文件移动回原目录
if [ -f "${OUTPUT_NAME}.gjf" ]; then
    echo ""
    echo "正在将 ${OUTPUT_NAME}.gjf 移动回原目录..."

    if cp "${OUTPUT_NAME}.gjf" "$ORIGINAL_PWD/"; then
        echo "  ✓ 已复制: ${OUTPUT_NAME}.gjf → $ORIGINAL_PWD/${OUTPUT_NAME}.gjf"
    else
        echo "  警告：无法复制文件到原目录。"
    fi
fi

echo ""

echo ""

#==========================================
# 保存最终结果到 results 目录
#==========================================

echo "=========================================="
echo "  保存最终结果"
echo "=========================================="
echo ""

# 检查结果目录是否存在
if [ ! -d "results" ]; then
    mkdir -p results
    echo "创建结果目录：results"
fi

# 复制最终产出文件到 results 目录
final_files=("cluster.xyz" "isomers.xyz")
saved_count=0

for file in "${final_files[@]}"; do
    if [ -f "$file" ]; then
        if cp "$file" "results/"; then
            echo "  已保存：$file → results/$file"
            ((saved_count++))
        else
            echo "  警告：无法保存 $file"
        fi
    else
        echo "  警告：找不到文件 $file"
    fi
done

echo ""
echo "共保存 $saved_count 个最终结果文件到 results 目录。"
echo ""

#==========================================
# 清理中间文件
#==========================================

echo "=========================================="
echo "  清理中间文件"
echo "=========================================="
echo ""

# 定义要删除的中间文件模式
intermediate_patterns=("traj.xyz" "xtblast.xyz" "mol2_xyz")

# 定义要删除的输入文件（复制过来的）
input_patterns=("*.fchk" "*.xyz")

# 保留的文件（不删除）
preserved_files=("genmer" "molclus" "isostat" "genmer.ini" "genmer.ini.bak" "settings.ini" "template.inp" "template.gjf")

# 删除中间文件
echo "删除中间文件..."
deleted_count=0

for pattern in "${intermediate_patterns[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            # 检查是否在保留列表中
            preserve=false
            for preserved in "${preserved_files[@]}"; do
                if [ "$file" = "$preserved" ]; then
                    preserve=true
                    break
                fi
            done
            
            if [ "$preserve" = false ]; then
                if rm -f "$file"; then
                    echo "  已删除：$file"
                    ((deleted_count++))
                else
                    echo "  警告：无法删除 $file"
                fi
            fi
        fi
    done
done

# 删除复制过来的输入文件
echo ""
echo "删除复制过来的输入文件..."

for pattern in "${input_patterns[@]}"; do
    for file in $pattern; do
        if [ -f "$file" ]; then
            if rm -f "$file"; then
                echo "  已删除：$file"
                ((deleted_count++))
            else
                echo "  警告：无法删除 $file"
            fi
        fi
    done
done

echo ""
echo "共删除 $deleted_count 个文件。"
echo ""

# 显示保留的文件
echo "保留的文件："
echo "------------------------------------------"

for file in "${preserved_files[@]}"; do
    if [ -f "$file" ]; then
        size=$(du -h "$file" | cut -f1)
        printf "  %-20s (%s)\n" "$file" "$size"
    fi
done

# 显示 results 目录内容
echo ""
echo "结果目录内容："
echo "------------------------------------------"

if [ -d "results" ]; then
    ls -lh results/
else
    echo "  results 目录不存在"
fi

echo ""

#==========================================
# 完成并恢复原始目录
#==========================================

echo "=========================================="
echo "  执行完成"
echo "=========================================="
echo ""
echo "目标工作目录：$TARGET_WORK_DIR"
echo "结果保存位置：$TARGET_WORK_DIR/results/"
echo ""
echo "保留的文件："
echo "  - 可执行文件：genmer, molclus, isostat"
echo "  - 配置文件：genmer.ini, genmer.ini.bak, settings.ini"
echo "  - 模板文件：template.inp, template.gjf"
echo "  - 结果文件：results/cluster.xyz, results/isomers.xyz"
echo "  - 转换结果：已在原目录生成 .gjf 文件"
echo ""
echo "脚本执行完毕。"

# trap 会自动恢复原始目录
