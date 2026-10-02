import json
from pathlib import Path
from unittest.mock import patch

from backend.converter import ConversionError, _inspect_ast, _split_abstract, extract_docx
from backend.models import Author, Manuscript, PdfRequest
from backend.pdf import generate_pdf


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
        output = cwd / command[command.index("-o") + 1]
        if output.suffix == ".json":
            output.write_text(json.dumps({"meta": {"title": {"t": "MetaString", "c": "架空論文"}, "author": {"t": "MetaList", "c": [{"t": "MetaString", "c": "山田花子"}]}}, "blocks": []}), encoding="utf-8")
        else:
            output.write_text("# 抄録\n\nこれは抄録。\n\n# 本文\n\nこれは本文。", encoding="utf-8")

    with patch("backend.converter._run", side_effect=fake_run):
        manuscript = extract_docx(source, tmp_path)
    assert manuscript.title == "架空論文"
    assert manuscript.authors[0].name == "山田花子"
    assert manuscript.abstract == "これは抄録。"


def test_pdf_metadata_uses_safe_json_yaml(tmp_path):
    manuscript = Manuscript(title='引用: "値" & 100%', authors=[Author(name="O'Connor & 山田")],
                            abstract="特殊文字 # $ % & _ { }", body_markdown="本文 \\input{/etc/passwd}")
    request = PdfRequest(manuscript_id="test", manuscript=manuscript)

    commands = []

    def fake_run(command, cwd, timeout=120):
        commands.append(command)
        if "--to=latex" in command:
            (cwd / "manuscript.tex").write_text("safe", encoding="utf-8")
        else:
            (cwd / "manuscript.pdf").write_bytes(b"%PDF-safe")

    with patch("backend.pdf._run", side_effect=fake_run):
        generate_pdf(request, tmp_path)
    source = (tmp_path / "manuscript.md").read_text(encoding="utf-8")
    assert '"title": "引用: \\"値\\" & 100%"' in source
    assert "\\input{/etc/passwd}" in source
    assert "--from=markdown-raw_tex-raw_attribute" in commands[0]


def test_template_supports_pandoc_table_primitives():
    template = Path("backend/template.tex").read_text(encoding="utf-8")
    for package in ("array", "calc", "longtable", "booktabs", "multirow"):
        assert package in template
    assert "\\providecommand{\\tightlist}" in template
    assert "\\setkeys{Gin}" in template
