import json
from pathlib import Path
from unittest.mock import patch

from backend.converter import _inspect_ast, _split_abstract, extract_docx


def test_abstract_is_extracted_from_markdown():
    abstract, body = _split_abstract("# 抄録\n\n概要です。\n\n# 1. 本文\n\n内容")
    assert abstract == "概要です。"
    assert body == "# 1. 本文\n\n内容"


def test_ast_reports_table_review_warning(tmp_path):
    assert "表のレイアウトはPDF生成後に確認してください。" in _inspect_ast({"blocks": [{"t": "Table"}]}, tmp_path / "media")


def test_docx_extraction_uses_pandoc_ast(tmp_path):
    source = tmp_path / "架空論文.docx"
    source.write_bytes(b"docx")

    def fake_run(command, cwd, timeout=120):
        output = Path(command[command.index("-o") + 1])
        if output.suffix == ".json":
            output.write_text(json.dumps({"meta": {"title": {"t": "MetaString", "c": "架空論文"}, "author": {"t": "MetaList", "c": [{"t": "MetaString", "c": "山田花子"}]}}, "blocks": []}), encoding="utf-8")
        else:
            output.write_text("# 抄録\n\nこれは抄録。\n\n# 本文\n\nこれは本文。", encoding="utf-8")

    with patch("backend.converter._run", side_effect=fake_run):
        manuscript = extract_docx(source, tmp_path)
    assert manuscript.title == "架空論文"
    assert manuscript.authors[0].name == "山田花子"
    assert manuscript.abstract == "これは抄録。"
