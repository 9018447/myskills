#!/usr/bin/env python3
"""
完整的工作流程：从LaTeX提取要点，搜索Web of Science，生成BibTeX，插入引用
"""

import re
import sys
import json
from typing import List, Dict, Tuple
from pathlib import Path

class CompleteWorkflow:
    def __init__(self, tex_file: str, points: int = 5, refs_per_point: int = 2):
        self.tex_file = Path(tex_file)
        self.points_count = points
        self.refs_per_point = refs_per_point
        self.introduction = ""
        self.key_points = []
        self.search_results = []
        self.bib_entries = []
        self.bib_keys = []
        
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
        paragraphs = [p.strip() for p in self.introduction.split('\n\n') if p.strip()]
        
        if not paragraphs:
            print("✗ No paragraphs found in introduction")
            return False
        
        self.key_points = []
        for i, para in enumerate(paragraphs[:self.points_count]):
            keywords = self.extract_keywords_from_text(para)
            self.key_points.append({
                'id': i+1,
                'text': para[:200] + "..." if len(para) > 200 else para,
                'keywords': keywords,
                'paragraph_index': i
            })
        
        print(f"✓ Extracted {len(self.key_points)} key points")
        return True
    
    def extract_keywords_from_text(self, text: str) -> List[str]:
        """从文本中提取关键词"""
        keywords = []
        
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
        
        if not keywords:
            words = re.findall(r'\b[A-Za-z]{4,}\b', text)
            stop_words = {'the', 'and', 'for', 'that', 'with', 'this', 'from', 'are', 'were', 'been', 'have', 'has'}
            keywords = [word for word in words if word.lower() not in stop_words][:5]
        
        return keywords
    
    def generate_bibtex_key(self, ref: Dict) -> str:
        """生成BibTeX引用键"""
        first_author = ref["authors"].split(",")[0].split()[-1] if ref["authors"] else "Unknown"
        year = ref["year"]
        keyword_part = ref["title"].split()[0].lower() if ref["title"] else "ref"
        
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
    
    def save_search_results(self, results: List[Dict]):
        """保存搜索结果"""
        self.search_results = results
        
        # 生成BibTeX条目
        self.bib_entries = []
        self.bib_keys = []
        
        for result in results:
            for ref in result.get('records', []):
                key = self.generate_bibtex_key(ref)
                # 确保键唯一
                counter = 1
                original_key = key
                while key in self.bib_keys:
                    key = f"{original_key}{counter}"
                    counter += 1
                
                entry = self.create_bibtex_entry(ref, key)
                self.bib_entries.append(entry)
                self.bib_keys.append(key)
        
        print(f"✓ Generated {len(self.bib_entries)} BibTeX entries")
    
    def save_bib_file(self):
        """保存BibTeX文件"""
        bib_content = "\n\n".join(self.bib_entries)
        bib_file = self.tex_file.with_suffix('.bib')
        with open(bib_file, 'w', encoding='utf-8') as f:
            f.write(bib_content)
        print(f"✓ Saved BibTeX file: {bib_file}")
    
    def insert_citations_into_latex(self):
        """将引用插入到LaTeX中"""
        # 备份原始文件
        backup_file = self.tex_file.with_suffix('.tex.backup')
        if not backup_file.exists():
            import shutil
            shutil.copy2(self.tex_file, backup_file)
            print(f"✓ Created backup: {backup_file}")
        
        # 读取原始内容
        with open(self.tex_file, 'r', encoding='utf-8') as f:
            content = f.read()
        
        # 1. 添加必要的包（在\begin{document}后）
        preamble_additions = r"""
\usepackage{natbib}
\bibliographystyle{unsrtnat}
"""
        
        # 2. 在\end{document}前添加\bibliography
        bibliography_command = r"""
\bibliography{references}
"""
        
        # 修改内容
        modified_content = content
        
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
        # 找到introduction部分
        intro_pattern = r'\\section\{Introduction\}(.*?)(?=\\section\{|\\end\{document\})'
        intro_match = re.search(intro_pattern, modified_content, re.DOTALL)
        
        if intro_match:
            intro_content = intro_match.group(1)
            
            # 按段落分割
            paragraphs = [p.strip() for p in intro_content.split('\n\n') if p.strip()]
            
            # 按段落分组引用键
            keys_per_paragraph = 2
            paragraph_keys = []
            for i in range(0, len(self.bib_keys), keys_per_paragraph):
                paragraph_keys.append(self.bib_keys[i:i+keys_per_paragraph])
            
            # 为每个段落添加引用
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
        
        # 保存修改后的文件
        with open(self.tex_file, 'w', encoding='utf-8') as f:
            f.write(modified_content)
        
        print(f"✓ Updated LaTeX file")
    
    def compile_pdf(self) -> bool:
        """编译PDF"""
        print("Compiling PDF...")
        
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
        print("Complete LaTeX Citation Workflow")
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
        
        print("=" * 80)
        print("Ready to search Web of Science")
        print("Please provide search results from Web of Science API")
        print("=" * 80)
        
        return True

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Complete LaTeX Citation Workflow')
    parser.add_argument('tex_file', help='LaTeX file path')
    parser.add_argument('--points', type=int, default=5, help='Number of key points to extract')
    parser.add_argument('--refs-per-point', type=int, default=2, help='References per key point')
    parser.add_argument('--compile', action='store_true', help='Compile PDF after processing')
    
    args = parser.parse_args()
    
    workflow = CompleteWorkflow(
        tex_file=args.tex_file,
        points=args.points,
        refs_per_point=args.refs_per_point
    )
    
    success = workflow.run(compile_pdf=args.compile)
    sys.exit(0 if success else 1)

if __name__ == "__main__":
    main()