#!/usr/bin/env python3
"""Tests for split_doc.py"""
import json
import os
import pytest
from split_doc import split_document


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
            {"id": "grp_1", "name": "本级管理", "module_code": "BJGL", "heading_pattern": "## 1.1 本级管理"},
            {"id": "grp_2", "name": "载体管理", "module_code": "ZTGL", "heading_pattern": "## 1.2 载体管理"},
            {"id": "grp_3", "name": "子基金投资", "module_code": "ZJTZ", "heading_pattern": "## 1.3 子基金投资"},
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
            {"id": "grp_1", "name": "资源池", "module_code": "ZYC", "heading_pattern": "## 1.1 资源池"}
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
