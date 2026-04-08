#!/usr/bin/env python3
"""Tests for split_doc.py"""
import json
import os
import pytest
from split_doc import split_document, normalize


# ---------- existing tests (updated for heading_text rename) ----------

@pytest.fixture
def sample_doc(tmp_path):
    """Create a sample markdown document with multiple modules."""
    content = """# 投资管理系统

## 公共说明

文本框最大50字。金额精度6位小数。

## 1.1 本级管理

### 基金列表

本级管理的基金列表页面...

### 新增基金

新增基金的表单...

## 1.2 载体管理

### 载体列表

载体管理的列表页面...

### 新增载体

新增载体的表单...

## 1.3 子基金投资

### 子基金列表

子基金投资的列表页面...
"""
    doc_path = tmp_path / "test_doc.md"
    doc_path.write_text(content, encoding="utf-8")
    return str(doc_path)


@pytest.fixture
def sample_analysis(tmp_path):
    """Create a sample analysis.json."""
    analysis = {
        "source_doc": "test_doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级管理", "module_code": "BJGL", "heading_text": "## 1.1 本级管理"},
            {"id": "grp_2", "name": "载体管理", "module_code": "ZTGL", "heading_text": "## 1.2 载体管理"},
            {"id": "grp_3", "name": "子基金投资", "module_code": "ZJTZ", "heading_text": "## 1.3 子基金投资"},
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")
    return str(analysis_path)


def test_split_creates_common_and_group_files(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_common.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_2.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_3.md"))


def test_common_contains_public_section(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    common = open(os.path.join(output_dir, "doc_common.md"), encoding="utf-8").read()
    assert "公共说明" in common
    assert "文本框最大50字" in common
    assert "本级管理的基金列表" not in common


def test_group_file_contains_common_prefix(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    # Group file should contain common section + its own content
    assert "公共说明" in grp1
    assert "本级管理的基金列表" in grp1
    assert "载体管理的列表页面" not in grp1


def test_last_group_captures_remaining(sample_doc, sample_analysis, tmp_path):
    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(sample_analysis, sample_doc, output_dir)

    grp3 = open(os.path.join(output_dir, "doc_grp_3.md"), encoding="utf-8").read()
    assert "子基金投资的列表页面" in grp3


def test_single_group(tmp_path):
    """Single module_group should still produce common + group file."""
    doc = "# 系统\n\n## 公共\n\n说明\n\n## 1.1 资源池\n\n内容\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "资源池", "module_code": "ZYC", "heading_text": "## 1.1 资源池"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)
    split_document(str(analysis_path), str(doc_path), output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_common.md"))
    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    assert "说明" in grp1
    assert "内容" in grp1


# ---------- new tests (v3.1.0 bug fixes) ----------

def test_normalize_strips_bom_crlf_nbsp_fullwidth():
    """normalize() should handle all the Unicode/encoding edge cases we care about."""
    assert normalize("\ufeff# 1 标题") == "# 1 标题"
    assert normalize("# 1 标题\r") == "# 1 标题"
    assert normalize("## 1.1\xa0本级管理") == "## 1.1 本级管理"
    assert normalize("## 1.1\u3000本级管理") == "## 1.1 本级管理"
    assert normalize("# 1  标题") == "# 1 标题"  # multi-space collapse
    assert normalize("  # 1 标题  ") == "# 1 标题"  # both-ends strip


def test_heading_with_nbsp(tmp_path):
    """Chinese Word-exported docs often have \\xa0 in headings."""
    doc = "# 系统\n\n## 公共\n\n说明\n\n## 1.1\xa0本级管理\n\n内容\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级", "module_code": "BJ", "heading_text": "## 1.1\xa0本级管理"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    split_document(str(analysis_path), str(doc_path), output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    assert "内容" in grp1


def test_heading_with_fullwidth_space(tmp_path):
    """Fullwidth space \\u3000 is common in typeset Chinese text."""
    doc = "# 系统\n\n## 公共\n\n说明\n\n## 1.1\u3000本级管理\n\n内容\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    # heading_text may or may not contain the exact fullwidth char;
    # normalize should handle both forms.
    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级", "module_code": "BJ", "heading_text": "## 1.1 本级管理"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    split_document(str(analysis_path), str(doc_path), output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))


def test_bom_and_crlf(tmp_path):
    """Windows + pandoc often produces UTF-8 BOM and CRLF line endings."""
    # \ufeff BOM at the start, \r\n line endings throughout
    doc = "\ufeff# 系统\r\n\r\n## 公共\r\n\r\n说明\r\n\r\n## 1.1 本级管理\r\n\r\n内容\r\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级", "module_code": "BJ", "heading_text": "## 1.1 本级管理"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    split_document(str(analysis_path), str(doc_path), output_dir)

    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    assert "内容" in grp1


def test_numbered_collision(tmp_path):
    """# 1 must not substring-match # 11; literal equality only."""
    doc = (
        "# 系统\n\n"
        "## 公共\n\n说明\n\n"
        "## 1 本级\n\n本级内容\n\n"
        "## 11 资产盘点\n\n盘点内容\n"
    )
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级", "module_code": "BJ", "heading_text": "## 1 本级"},
            {"id": "grp_2", "name": "资产盘点", "module_code": "ZCPD", "heading_text": "## 11 资产盘点"},
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    split_document(str(analysis_path), str(doc_path), output_dir)

    grp1 = open(os.path.join(output_dir, "doc_grp_1.md"), encoding="utf-8").read()
    grp2 = open(os.path.join(output_dir, "doc_grp_2.md"), encoding="utf-8").read()

    # grp_1 must contain ONLY 本级 content, not 盘点 content
    assert "本级内容" in grp1
    assert "盘点内容" not in grp1
    # grp_2 must contain 盘点 content
    assert "盘点内容" in grp2


def test_regex_heading_fails_loudly(tmp_path):
    """When heading_text contains regex metachars, we should raise with a useful diagnostic
    rather than silently producing wrong output."""
    doc = "# 系统\n\n## 公共\n\n说明\n\n## 1.1 本级管理\n\n内容\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    # User mistakenly writes a regex instead of literal text
    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级", "module_code": "BJ", "heading_text": "^## 1.1\\s+本级管理"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    os.makedirs(output_dir)

    with pytest.raises(ValueError) as exc_info:
        split_document(str(analysis_path), str(doc_path), output_dir)

    # Error message must include the offending heading and hint about fix
    err_msg = str(exc_info.value)
    assert "Cannot find heading_text" in err_msg
    assert "closest lines" in err_msg
    # The diagnostic should surface the real heading as a candidate
    assert "本级管理" in err_msg


def test_deprecation_warning_on_old_field(tmp_path, capsys):
    """Old analysis.json with heading_pattern should still work but emit a warning."""
    doc = "# 系统\n\n## 公共\n\n说明\n\n## 1.1 本级管理\n\n内容\n"
    doc_path = tmp_path / "doc.md"
    doc_path.write_text(doc, encoding="utf-8")

    # Legacy field name
    analysis = {
        "source_doc": "doc.md",
        "common_rules": {},
        "module_groups": [
            {"id": "grp_1", "name": "本级", "module_code": "BJ", "heading_pattern": "## 1.1 本级管理"}
        ],
    }
    analysis_path = tmp_path / "analysis.json"
    analysis_path.write_text(json.dumps(analysis, ensure_ascii=False), encoding="utf-8")

    output_dir = str(tmp_path / "output")
    split_document(str(analysis_path), str(doc_path), output_dir)

    # Split should succeed
    assert os.path.exists(os.path.join(output_dir, "doc_grp_1.md"))
    # And a deprecation warning should have been printed to stderr
    captured = capsys.readouterr()
    assert "deprecated" in captured.err.lower()
    assert "heading_pattern" in captured.err
