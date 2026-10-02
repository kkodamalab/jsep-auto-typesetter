import shutil

import pytest

from backend.converter import extract_docx
from backend.models import PdfRequest
from backend.pdf import generate_pdf


@pytest.mark.skipif(not all(shutil.which(tool) for tool in ("pandoc", "lualatex")), reason="Pandoc/LuaLaTeXが必要")
def test_fictional_docx_to_real_pdf(tmp_path):
    docx = pytest.importorskip("docx")
    document = docx.Document()
    document.core_properties.title = "架空の教育工学研究"
    document.core_properties.author = "山田 花子"
    document.add_heading("抄録", level=1)
    document.add_paragraph("これは変換試験専用の架空の抄録である。")
    document.add_heading("はじめに", level=1)
    document.add_paragraph("本稿に実在の人物・研究・未公開情報は含まれない。")
    source = tmp_path / "fictional.docx"
    document.save(source)
    manuscript = extract_docx(source, tmp_path)
    output = generate_pdf(PdfRequest(manuscript=manuscript), tmp_path)
    assert output.read_bytes().startswith(b"%PDF-")
    assert output.stat().st_size > 1000
