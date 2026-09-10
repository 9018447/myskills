#!/bin/bash

# 检查是否提供了参数
if [ $# -eq 0 ]; then
  echo "Usage: $0 <input.fchk> [more.fchk ...]"
  echo "Converts fchk files to resp format using Multiwfn"
  exit 1
fi

icc=0
nfile=$#

# 处理每个输入文件
for inf in "$@"
do
  # 检查文件是否存在
  if [ ! -f "$inf" ]; then
    echo "Error: File '$inf' not found"
    continue
  fi
  
  ((icc++)) 
  echo Converting $inf to ${inf//fchk/resp} ...
Multiwfn $inf << EOF
7
18
1
y
0
0
q
EOF
echo "resp for '$inf' is caculated"
if [ $? -ne 0 ]; then
  echo "Error: Multiwfn failed for $inf"
fi
done
