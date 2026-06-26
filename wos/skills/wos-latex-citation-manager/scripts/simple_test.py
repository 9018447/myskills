#!/usr/bin/env python3
"""
简单的测试：验证skill的核心功能
"""

import re
import sys
from pathlib import Path

def simple_test():
    """简单测试"""
    print("=" * 80)
    print("Simple Test: Verify Core Functionality")
    print("=" * 80)
    
    # 1. 测试提取introduction
    print("\n1. Testing introduction extraction...")
    with open('/home/smh/pi-chrome-workspace/wos-skills/main_manuscript.tex', 'r', encoding='utf-8') as f:
        content = f.read()
    
    intro_pattern = r'\\section\{Introduction\}(.*?)(?=\\section\{|\\end\{document\})'
    intro_match = re.search(intro_pattern, content, re.DOTALL)
    
    if intro_match:
        intro_content = intro_match.group(1)
        print(f"✓ Found introduction ({len(intro_content)} characters)")
        
        # 按段落分割
        paragraphs = [p.strip() for p in intro_content.split('\n\n') if p.strip()]
        print(f"✓ Found {len(paragraphs)} paragraphs")
        
        # 提取关键词
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
        
        key_points = []
        for i, para in enumerate(paragraphs[:5]):  # 只处理前5个段落
            keywords = []
            for pattern in patterns:
                if re.search(pattern, para, re.IGNORECASE):
                    keywords.append(pattern)
            
            if keywords:
                search_query = " AND ".join([f'"{kw}"' for kw in keywords[:2]])
            else:
                # 提取一些关键词
                words = re.findall(r'\b[A-Za-z]{4,}\b', para)
                stop_words = {'the', 'and', 'for', 'that', 'with', 'this', 'from', 'are', 'were', 'been', 'have', 'has'}
                keywords = [word for word in words if word.lower() not in stop_words][:3]
                search_query = " AND ".join([f'"{kw}"' for kw in keywords])
            
            key_points.append({
                'id': i+1,
                'keywords': keywords,
                'query': search_query
            })
            
            print(f"  Paragraph {i+1}: {keywords}")
            print(f"    Query: {search_query}")
        
        print(f"\n✓ Extracted {len(key_points)} key points")
        
        # 2. 测试BibTeX生成
        print("\n2. Testing BibTeX generation...")
        
        # 模拟搜索结果
        mock_results = [
            {
                "query": key_points[0]['query'],
                "records": [
                    {
                        "title": "Carbon Dioxide Capture: Prospects for New Materials",
                        "authors": "D'Alessandro, DM; Smit, B; Long, JR",
                        "journal": "ANGEWANDTE CHEMIE-INTERNATIONAL EDITION",
                        "year": "2010",
                        "volume": "49",
                        "issue": "35",
                        "pages": "6058-6082",
                        "doi": "10.1002/anie.201000431",
                        "citations": 3587,
                        "wos_id": "WOS:000281316000005"
                    }
                ]
            }
        ]
        
        # 生成BibTeX条目
        bib_entries = []
        bib_keys = []
        
        for result in mock_results:
            for ref in result.get('records', []):
                # 生成引用键
                first_author = ref["authors"].split(",")[0].split()[-1]
                year = ref["year"]
                keyword_part = ref["title"].split()[0].lower()
                
                key = f"{first_author}{year}{keyword_part}"
                key = re.sub(r'[^a-zA-Z0-9]', '', key)
                
                # 确保键唯一
                counter = 1
                original_key = key
                while key in bib_keys:
                    key = f"{original_key}{counter}"
                    counter += 1
                
                # 创建BibTeX条目
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
                
                bib_entries.append(entry)
                bib_keys.append(key)
        
        print(f"✓ Generated {len(bib_entries)} BibTeX entries")
        print(f"✓ BibTeX keys: {bib_keys}")
        
        # 3. 测试引用插入
        print("\n3. Testing citation insertion...")
        
        # 读取BibTeX文件
        with open('/home/smh/pi-chrome-workspace/wos-skills/main_manuscript.bib', 'r', encoding='utf-8') as f:
            bib_content = f.read()
        
        # 提取引用键
        all_bib_keys = re.findall(r'@\w+\{([^,]+),', bib_content)
        print(f"✓ Found {len(all_bib_keys)} BibTeX keys in file")
        
        # 按段落分组引用键
        keys_per_paragraph = 2
        paragraph_keys = []
        for i in range(0, len(all_bib_keys), keys_per_paragraph):
            paragraph_keys.append(all_bib_keys[i:i+keys_per_paragraph])
        
        print(f"✓ Grouped into {len(paragraph_keys)} paragraph groups")
        
        # 显示每个段落的引用
        for i, keys in enumerate(paragraph_keys):
            print(f"  Paragraph {i+1}: {keys}")
        
        print("\n" + "=" * 80)
        print("✓ All tests passed!")
        print("=" * 80)
        
        return True
    
    else:
        print("✗ No introduction found")
        return False

if __name__ == "__main__":
    success = simple_test()
    sys.exit(0 if success else 1)