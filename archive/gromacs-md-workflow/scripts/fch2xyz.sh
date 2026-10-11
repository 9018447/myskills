#!/bin/bash
icc=0  
nfile=`ls *.fchk|wc -l`  
for inf in *.fchk  
do
((icc++)) 
echo Converting $inf to ${inf//fchk/xyz} ... \($icc of $nfile\) 
Multiwfn $inf << EOF
100 
2   
2
${inf//fchk/xyz} 
0  
q  
EOF
if [ $? -ne 0 ]; then
  echo "Error: Multiwfn failed for $inf"
fi
done