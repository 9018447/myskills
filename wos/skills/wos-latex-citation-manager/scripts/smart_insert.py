#!/usr/bin/env python3
"""
智能插入引用到LaTeX文件
"""

import re
import sys
from pathlib import Path

def smart_insert_citations(tex_file: str, bib_keys: list):
    """智能插入引用到LaTeX文件"""
    
    # 读取LaTeX文件
    with open(tex_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 备份原始文件
    backup_file = Path(tex_file).with_suffix('.tex.backup')
    if not backup_file.exists():
        import shutil
        shutil.copy2(tex_file, backup_file)
        print(f"✓ Created backup: {backup_file}")
    
    # 1. 添加natbib包（在\begin{document}后，只添加一次）
    if r'\usepackage{natbib}' not in content:
        # 在\begin{document}后添加
        content = content.replace(
            r'\begin{document}',
            r'\begin{document}' + '\n' + r'\usepackage{natbib}' + '\n' + r'\bibliographystyle{unsrtnat}',
            1
        )
        print("✓ Added natbib package")
    
    # 2. 添加\bibliography命令（在\end{document}前，只添加一次）
    if r'\bibliography{' not in content:
        content = content.replace(
            r'\end{document}',
            r'\bibliography{references}' + '\n' + r'\end{document}',
            1
        )
        print("✓ Added bibliography command")
    
    # 3. 找到introduction部分
    intro_pattern = r'\\section\{Introduction\}(.*?)(?=\\section\{|\\end\{document\})'
    intro_match = re.search(intro_pattern, content, re.DOTALL)
    
    if not intro_match:
        print("✗ No introduction found")
        return False
    
    intro_content = intro_match.group(1)
    
    # 4. 按段落分割introduction
    paragraphs = [p.strip() for p in intro_content.split('\n\n') if p.strip()]
    
    print(f"Found {len(paragraphs)} paragraphs in introduction")
    print(f"Have {len(bib_keys)} BibTeX keys")
    
    # 5. 按段落分组引用键
    keys_per_paragraph = 2
    paragraph_keys = []
    for i in range(0, len(bib_keys), keys_per_paragraph):
        paragraph_keys.append(bib_keys[i:i+keys_per_paragraph])
    
    print(f"Grouped into {len(paragraph_keys)} paragraph groups")
    
    # 6. 为每个段落添加引用
    modified_content = content
    
    for i, para in enumerate(paragraphs[:len(paragraph_keys)]):
        if i < len(paragraph_keys):
            keys = paragraph_keys[i]
            citation = f" \\cite{{{','.join(keys)}}}"
            
            # 在段落末尾添加引用
            para_stripped = para.rstrip()
            if para_stripped in modified_content:
                modified_content = modified_content.replace(
                    para_stripped,
                    para_stripped + citation,
                    1
                )
                print(f"Added citation to paragraph {i+1}: {citation}")
    
    # 7. 保存修改后的文件
    with open(tex_file, 'w', encoding='utf-8') as f:
        f.write(modified_content)
    
    print(f"✓ Updated LaTeX file: {tex_file}")
    return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Smart Insert Citations')
    parser.add_argument('tex_file', help='LaTeX file path')
    parser.add_argument('bib_file', help='BibTeX file path')
    
    args = parser.parse_args()
    
    # 读取BibTeX文件，提取引用键
    with open(args.bib_file, 'r', encoding='utf-8') as f:
        bib_content = f.read()
    
    # 提取引用键
    bib_keys = re.findall(r'@\w+\{([^,]+),', bib_content)
    
    print(f"Found {len(bib_keys)} BibTeX keys: {bib_keys[:5]}...")
    
    # 智能插入引用
    success = smart_insert_citations(args.tex_file, bib_keys)
    
    if success:
        print("\n" + "=" * 80)
        print("✓ Citations inserted successfully!")
        print("=" * 80)
    else:
        print("\n" + "=" * 80)
        print("✗ Failed to insert citations")
        print("=" * 80)
    
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()