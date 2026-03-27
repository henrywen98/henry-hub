#!/usr/bin/env python3
"""
概要设计说明书组装脚本：
从各子系统 HLD 分册 + 公共章节模板 → 合并为完整概设文档

用法：
  python3 assemble_hld.py <设计目录>

输入约定：
  - <设计目录>/_common-chapters.md   → 含 YAML frontmatter（元信息）+ 第1-2章、第4-7章骨架
  - <设计目录>/HLD-{子系统名}-*.md    → 第3章各子系统内容

输出：
  - <设计目录>/HLD-{short_name}-v1.0.md → 合并后的完整概设
"""

import sys
import re
from pathlib import Path


COMMON_CHAPTERS_FILE = '_common-chapters.md'


def parse_frontmatter(path: Path) -> dict:
    """从 Markdown 文件的 YAML frontmatter 提取元信息"""
    content = path.read_text(encoding='utf-8')
    meta = {}
    match = re.match(r'^---\s*\n(.*?)\n---', content, re.DOTALL)
    if match:
        for line in match.group(1).split('\n'):
            if ':' in line:
                key, val = line.split(':', 1)
                meta[key.strip()] = val.strip().strip('"').strip("'")
    return meta


def discover_subsystems(design_dir: Path, output_name: str = '') -> list:
    """自动发现子系统 HLD 分册文件，返回 [(子系统名, 文件路径)] 列表"""
    results = []
    for path in sorted(design_dir.glob('HLD-*.md')):
        name = path.name
        # 跳过合并输出文件
        if output_name and name == output_name:
            continue
        # 从文件一级标题提取子系统名
        content = path.read_text(encoding='utf-8')
        # 去掉 frontmatter
        fm_match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
        if fm_match:
            content = content[fm_match.end():]
        # 匹配 # XXX 概要设计说明书
        h1_match = re.match(r'^#\s+(.+?)(?:\s*概要设计说明书)?\s*$', content.strip(), re.MULTILINE)
        if h1_match:
            subsys_name = h1_match.group(1).strip()
        else:
            # 从文件名提取：HLD-{名称}-v*.md
            m = re.match(r'HLD-(.+?)-v[\d.]+\.md$', name)
            subsys_name = m.group(1) if m else name.replace('.md', '')
        results.append((subsys_name, path))
    return results


def read_file(path: Path) -> str:
    """读取文件，去掉 YAML frontmatter"""
    content = path.read_text(encoding='utf-8')
    match = re.match(r'^---\s*\n.*?\n---\s*\n', content, re.DOTALL)
    if match:
        content = content[match.end():]
    return content.strip()


def extract_chapter3_from_subsystem(path: Path, subsystem_name: str, index: int) -> str:
    """从子系统 HLD 分册中提取第3章功能模块内容，重编号为 3.2.{index}"""
    content = read_file(path)

    # 找到第3章开始位置（子系统分册用 ## 作为章级标题）
    ch3_match = re.search(r'^#{1,2} 3\s+功能模块设计', content, re.MULTILINE)
    if not ch3_match:
        print(f"  警告: {path.name} 中未找到第3章，跳过")
        return ''

    # 找到第4章或文件末尾
    ch4_match = re.search(r'^#{1,2} [4-9]\s+', content[ch3_match.start():], re.MULTILINE)
    if ch4_match:
        ch3_content = content[ch3_match.start():ch3_match.start() + ch4_match.start()]
    else:
        ch3_content = content[ch3_match.start():]

    ch3_content = ch3_content.strip()

    # 跳过 "### 3.1 功能结构图" 部分，只保留 "### 3.2" 之后的内容
    sec32_match = re.search(r'^### 3\.2\s+', ch3_content, re.MULTILINE)
    if sec32_match:
        after_32_title = ch3_content[sec32_match.start():]
        first_func = re.search(r'^#### ', after_32_title, re.MULTILINE)
        if first_func:
            ch3_content = after_32_title[first_func.start():]
        else:
            ch3_content = after_32_title
    else:
        first_h4 = re.search(r'^#### ', ch3_content, re.MULTILINE)
        if first_h4:
            ch3_content = ch3_content[first_h4.start():]

    # 重编号：#### 3.2.X → #### 3.2.{index}.X
    lines = ch3_content.split('\n')
    result_lines = [f'### 3.2.{index} {subsystem_name}子系统', '']

    func_counter = 0
    for line in lines:
        m = re.match(r'^####\s+3\.2\.\d+\s+(.*)', line)
        if m:
            func_counter += 1
            result_lines.append(f'#### 3.2.{index}.{func_counter} {m.group(1)}')
            continue
        result_lines.append(line)

    return '\n'.join(result_lines).strip()


def extract_common_chapters(path: Path, meta: dict) -> dict:
    """从公共章节模板提取各章节，替换占位符"""
    content = read_file(path)

    short_name = meta.get('short_name', '')
    if short_name:
        content = content.replace('{子系统名称}', short_name)
        content = content.replace('{项目简称}', short_name)

    chapters = {}
    parts = re.split(r'^(## \d+\s+.+)', content, flags=re.MULTILINE)

    for i in range(1, len(parts), 2):
        heading = parts[i].strip()
        body = parts[i + 1].strip() if i + 1 < len(parts) else ''
        m = re.match(r'## (\d+)\s+(.*)', heading)
        if m:
            ch_num = int(m.group(1))
            promoted_heading = f'# {m.group(1)} {m.group(2)}'
            promoted_body = re.sub(r'^####\s+', '### ', body, flags=re.MULTILINE)
            promoted_body = re.sub(r'^###\s+', '## ', promoted_body, flags=re.MULTILINE)
            chapters[ch_num] = f'{promoted_heading}\n\n{promoted_body}'

    return chapters


def build_function_tree(subsystems: list, short_name: str) -> str:
    """从各子系统 HLD 分册生成功能结构树"""
    tree_lines = ['```', short_name]

    for i, (name, path) in enumerate(subsystems):
        content = read_file(path)
        is_last = (i == len(subsystems) - 1)
        prefix = '└──' if is_last else '├──'

        tree_lines.append(f'{prefix} {i + 1}. {name}子系统')

        # 提取 #### 标题作为子模块
        h4_titles = re.findall(r'^####\s+[\d.]+\s+(.+)', content, re.MULTILINE)
        if not h4_titles:
            modules = set(re.findall(r'\|\s*\d+\s*\|\s*([^|]+?)\s*\|', content))
            h4_titles = sorted(modules)[:8]

        child_prefix = '    ' if is_last else '│   '
        for j, title in enumerate(h4_titles[:10]):
            is_last_child = (j == min(len(h4_titles), 10) - 1)
            child_connector = '└──' if is_last_child else '├──'
            tree_lines.append(f'{child_prefix}{child_connector} {title}')

        if len(h4_titles) > 10:
            tree_lines.append(f'{child_prefix}└── ...（共{len(h4_titles)}个模块）')

    tree_lines.append('```')
    return '\n'.join(tree_lines)


def assemble(design_dir: Path):
    """组装完整概设文档"""
    # 1. 读取元信息
    common_path = design_dir / COMMON_CHAPTERS_FILE
    if not common_path.exists():
        print(f'错误: 公共章节文件不存在: {common_path}')
        sys.exit(1)

    meta = parse_frontmatter(common_path)
    short_name = meta.get('short_name', '项目')
    title = meta.get('title', short_name)
    subtitle = meta.get('subtitle', '概要设计说明书')
    company = meta.get('company', '')
    date_str = meta.get('date', '')

    print(f'组装概要设计说明书')
    print(f'项目: {title}')

    # 2. 确定输出文件名并发现子系统
    output_name = f'HLD-{short_name}-v1.0.md'
    output_path = design_dir / output_name
    subsystems = discover_subsystems(design_dir, output_name)

    if not subsystems:
        print(f'错误: 在 {design_dir} 中未找到 HLD-*.md 分册文件')
        sys.exit(1)

    print(f'  发现 {len(subsystems)} 个子系统: {", ".join(n for n, _ in subsystems)}')

    # 3. 读取公共章节
    chapters = extract_common_chapters(common_path, meta)
    print(f'  公共章节: {sorted(chapters.keys())}')

    # 4. 构建 frontmatter
    frontmatter = f"""---
title: {title}
subtitle: {subtitle}
company: {company}
date: {date_str}
---"""

    # 5. 构建第3章
    print('  组装第3章功能模块设计...')

    ch3_parts = []
    ch3_parts.append('# 3 功能模块设计')
    ch3_parts.append('')
    ch3_parts.append('## 3.1 功能结构图')
    ch3_parts.append('')
    ch3_parts.append(build_function_tree(subsystems, short_name))
    ch3_parts.append('')
    ch3_parts.append('## 3.2 功能模块具体功能定义')
    ch3_parts.append('')

    missing = []
    for i, (name, path) in enumerate(subsystems, 1):
        subsys_content = extract_chapter3_from_subsystem(path, name, i)
        if subsys_content:
            ch3_parts.append(subsys_content)
            ch3_parts.append('')
            table_rows = len(re.findall(r'^\|\s*\d+\s*\|', subsys_content, re.MULTILINE))
            print(f'    ✓ 3.2.{i} {name}: {table_rows} 个功能点')
        else:
            missing.append(path.name)
            print(f'    ✗ {name}: 未提取到第3章内容')

    if missing:
        print(f'\n  警告: {len(missing)} 个子系统分册内容缺失: {missing}')

    ch3_text = '\n'.join(ch3_parts)

    # 6. 组装完整文档
    sections = [frontmatter, '']

    # 第1章（修正双重替换）
    if 1 in chapters:
        ch1 = chapters[1]
        if short_name:
            ch1 = ch1.replace(f'{short_name}——{short_name}', short_name)
            ch1 = ch1.replace(f'{short_name}中的{short_name}部分', short_name)
        sections.append(ch1)
    else:
        print('  警告: 第1章缺失')

    # 第2章
    if 2 in chapters:
        sections.append(chapters[2])
    else:
        print('  警告: 第2章缺失')

    # 第3章
    sections.append(ch3_text)

    # 第4-7章
    for ch_num in [4, 5, 6, 7]:
        if ch_num in chapters:
            sections.append(chapters[ch_num])
        else:
            print(f'  警告: 第{ch_num}章缺失')

    # 7. 写入文件
    full_doc = '\n\n'.join(sections)

    lines = full_doc.count('\n') + 1
    chars = len(full_doc)
    table_rows = len(re.findall(r'^\|\s*\d+\s*\|', full_doc, re.MULTILINE))

    output_path.write_text(full_doc, encoding='utf-8')

    print(f'\n═══ 组装完成 ═══')
    print(f'  输出: {output_path}')
    print(f'  总行数: {lines}')
    print(f'  总字符: {chars}')
    print(f'  功能点: {table_rows}')
    print(f'  预估页数: ~{lines // 40}')


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print('用法: assemble_hld.py <设计目录>')
        print('示例: assemble_hld.py docs/03-系统设计/')
        sys.exit(1)
    design_dir = Path(sys.argv[1])
    if not design_dir.is_dir():
        print(f'错误: {design_dir} 不是有效目录')
        sys.exit(1)
    assemble(design_dir)
