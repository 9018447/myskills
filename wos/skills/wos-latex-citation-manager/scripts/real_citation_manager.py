#!/usr/bin/env python3
"""
真实的LaTeX Citation Manager
使用Web of Science API搜索文献，生成BibTeX引用
"""

import re
import sys
import json
import os
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass
from pathlib import Path

@dataclass
class KeyPoint:
    """关键要点"""
    id: int
    text: str
    keywords: List[str]
    paragraph_index: int

@dataclass
class Reference:
    """文献引用"""
    key: str
    title: str
    authors: str
    journal: str
    year: int
    volume: str
    issue: str
    pages: str
    doi: str
    citations: int
    wos_id: str

class RealCitationManager:
    def __init__(self, tex_file: str, points: int = 10, refs_per_point: int = 5):
        self.tex_file = Path(tex_file)
        self.points_count = points
        self.refs_per_point = refs_per_point
        self.introduction = ""
        self.key_points: List[KeyPoint] = []
        self.references: List[Reference] = []
        self.bib_content = ""
        
    def read_tex_file(self) -> bool:
        """读取LaTeX文件"""
        try:
            with open(self.tex_file, 'r', encoding='utf-8') as f:
                self.content = f.read()
            return True
        except Exception as e:
            print(f"Error reading file: {e}")
            return False
    
    def extract_introduction(self) -> bool:
        """提取introduction部分"""
        # 匹配\section{Introduction}到下一个\section{或\end{document}
        pattern = r'\\section\{Introduction\}(.*?)(?=\\section\{|\\end\{document\})'
        match = re.search(pattern, self.content, re.DOTALL)
        
        if match:
            self.introduction = match.group(1)
            print(f"✓ Found introduction section ({len(self.introduction)} characters)")
            return True
        else:
            print("✗ No introduction section found")
            return False
    
    def extract_key_points(self) -> bool:
        """提取关键要点"""
        # 按段落分割
        paragraphs = [p.strip() for p in self.introduction.split('\n\n') if p.strip()]
        
        if not paragraphs:
            print("✗ No paragraphs found in introduction")
            return False
        
        # 为每个段落创建关键要点
        self.key_points = []
        for i, para in enumerate(paragraphs[:self.points_count]):
            # 提取关键词
            keywords = self.extract_keywords_from_text(para)
            
            key_point = KeyPoint(
                id=i+1,
                text=para[:200] + "..." if len(para) > 200 else para,
                keywords=keywords,
                paragraph_index=i
            )
            self.key_points.append(key_point)
        
        print(f"✓ Extracted {len(self.key_points)} key points")
        return True
    
    def extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        
        # 查找常见的学术术语
        patterns = [
            r'carbon dioxide capture',
            r'deep eutectic solvents',
            r'ionic liquids',
            r'thermodynamic models',
            r'molecular dynamics',
            r'CO₂ capture',
            r'hydrogen bonding',
            r'solubility',
            r'viscosity',
            r'phase equilibrium',
            r'COSMO-RS',
            r'Pitzer-Debye-Hückel',
            r'activity coefficient'
        ]
        
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                keywords.append(pattern)
        
        # 如果没有找到预定义的关键词，提取一些通用词
        if not keywords:
            words = re.findall(r'\b[A-Za-z]{4,}\b', text)
            # 简单过滤
            stop_words = {'the', 'and', 'for', 'that', 'with', 'this', 'from', 'are', 'were', 'been', 'have', 'has'}
            keywords = [word for word in words if word.lower() not in stop_words][:5]
        
        return keywords
    
    def generate_bibtex_key(self, ref: Dict) -> str:
        """生成BibTeX引用键"""
        # 简单的键生成：作者姓氏+年份
        first_author = ref["authors"].split(",")[0].split()[-1] if ref["authors"] else "Unknown"
        year = ref["year"]
        # 添加关键词的第一个词
        keyword_part = ref["title"].split()[0].lower() if ref["title"] else "ref"
        
        # 清理键名
        key = f"{first_author}{year}{keyword_part}"
        key = re.sub(r'[^a-zA-Z0-9]', '', key)
        return key
    
    def create_bibtex_entry(self, ref: Dict, key: str) -> str:
        """创建BibTeX条目"""
        entry = f"""@article{{{key},
  title = {{{ref['title']}}},
  author = {{{ref['authors']}}},
  journal = {{{ref['journal']}}},
  year = {{{ref['year']}}},
  volume = {{{ref['volume']}}},
  number = {{{ref['issue']}}},
  pages = {{{ref['pages']}}},
  doi = {{{ref['doi']}}},
  note = {{Citations: {ref['citations']}, WoS ID: {ref['wos_id']}}}
}}"""
        return entry
    
    def generate_bibtex_file(self):
        """生成BibTeX文件"""
        bib_entries = []
        
        for point in self.key_points:
            # 这里应该调用Web of Science API搜索文献
            # 但我们需要通过chrome_devtools调用
            # 所以这个函数需要修改
            pass
        
        self.bib_content = "\n\n".join(bib_entries)
        print(f"✓ Generated {len(bib_entries)} BibTeX entries")
    
    def insert_citations_into_latex(self):
        """将引用插入到LaTeX中"""
        # 这是一个简化版本，实际应该更智能地插入引用
        
        # 1. 添加必要的包
        preamble_additions = r"""
\usepackage{natbib}
\bibliographystyle{unsrtnat}
"""
        
        # 2. 在文档末尾添加\bibliography命令
        bibliography_command = r"""
\bibliography{references}
"""
        
        # 修改内容
        modified_content = self.content
        
        # 在\begin{document}后添加包
        modified_content = modified_content.replace(
            r'\begin{document}',
            f'\\begin{{document}}{preamble_additions}'
        )
        
        # 在\end{document}前添加\bibliography
        modified_content = modified_content.replace(
            r'\end{document}',
            f'{bibliography_command}\n\\end{{document}}'
        )
        
        # 3. 在introduction的每个段落末尾添加引用
        # 简化：在每个段落末尾添加所有相关引用
        paragraphs = modified_content.split('\n\n')
        new_paragraphs = []
        
        for i, para in enumerate(paragraphs):
            new_paragraphs.append(para)
            
            # 如果是introduction段落，添加引用
            if i < len(self.key_points) and i < len(self.references):
                # 找到这个段落对应的引用
                point_refs = [ref for ref in self.references 
                             if ref.key in [r.key for r in self.references[i*self.refs_per_point:(i+1)*self.refs_per_point]]]
                
                if point_refs:
                    citation_keys = ','.join([ref.key for ref in point_refs])
                    citation = f" \\cite{{{citation_keys}}}"
                    new_paragraphs[-1] = para.rstrip() + citation
        
        modified_content = '\n\n'.join(new_paragraphs)
        
        # 保存修改后的文件
        backup_file = self.tex_file.with_suffix('.tex.backup')
        if not backup_file.exists():
            import shutil
            shutil.copy2(self.tex_file, backup_file)
            print(f"✓ Created backup: {backup_file}")
        
        with open(self.tex_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✓ Updated LaTeX file: {self.tex_file}")
    
    def save_bib_file(self):
        """保存BibTeX文件"""
        bib_file = self.tex_file.with_suffix('.bib')
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(self.bib_content)
        print(f"✓ Saved BibTeX file: {bib_file}")
    
    def compile_pdf(self) -> bool:
        """编译PDF"""
        print("Compiling PDF...")
        
        # 获取文件名（不含扩展名）
        base_name = self.tex_file.stem
        
        try:
            import subprocess
            
            # 运行pdflatex
            subprocess.run(['pdflatex', '-interaction=nonstopmode', base_name + '.tex'], 
                          capture_output=True, text=True, check=True)
            
            # 运行bibtex
            subprocess.run(['bibtex', base_name], 
                          capture_output=True, text=True, check=True)
            
            # 再次运行pdflatex两次
            subprocess.run(['pdflatex', '-interaction=nonstopmode', base_name + '.tex'], 
                          capture_output=True, text=True, check=True)
            subprocess.run(['pdflatex', '-interaction=nonstopmode', base_name + '.tex'], 
                          capture_output=True, text=True, check=True)
            
            print(f"✓ PDF compiled successfully: {base_name}.pdf")
            return True
            
        except subprocess.CalledProcessError as e:
            print(f"✗ Compilation error: {e}")
            print("Error output:", e.stderr)
            return False
        except FileNotFoundError:
            print("✗ pdflatex not found. Please install LaTeX distribution.")
            return False
    
    def run(self, compile_pdf: bool = False):
        """运行完整的工作流程"""
        print("=" * 80)
        print("Real LaTeX Citation Manager")
        print("=" * 80)
        
        # 1. 读取文件
        if not self.read_tex_file():
            return False
        
        # 2. 提取introduction
        if not self.extract_introduction():
            return False
        
        # 3. 提取关键要点
        if not self.extract_key_points():
            return False
        
        # 4. 这里应该调用Web of Science API搜索文献
        # 但需要通过chrome_devtools调用
        print("⚠️  需要通过chrome_devtools调用Web of Science API")
        print("请使用chrome_devtools_evaluate调用Web of Science API")
        
        # 5. 生成BibTeX（目前是空的）
        self.generate_bibtex_file()
        
        # 6. 插入引用到LaTeX
        self.insert_citations_into_latex()
        
        # 7. 保存BibTeX文件
        self.save_bib_file()
        
        # 8. 编译PDF（可选）
        if compile_pdf:
            self.compile_pdf()
        
        print("=" * 80)
        print("✓ Process completed (partial - needs Web of Science API)")
        print(f"Updated file: {self.tex_file}")
        print(f"BibTeX file: {self.tex_file.with_suffix('.bib')}")
        if compile_pdf:
            print(f"PDF file: {self.tex_file.with_suffix('.pdf')}")
        print("=" * 80)
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Real LaTeX Citation Manager')
    parser.add_argument('tex_file', help='LaTeX file path')
    parser.add_argument('--points', type=int, default=10, help='Number of key points to extract')
    parser.add_argument('--refs-per-point', type=int, default=5, help='References per key point')
    parser.add_argument('--compile', action='store_true', help='Compile PDF after processing')
    
    args = parser.parse_args()
    
    manager = RealCitationManager(
        tex_file=args.tex_file,
        points=args.points,
        refs_per_point=args.refs_per_point
    )
    
    success = manager.run(compile_pdf=args.compile)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()