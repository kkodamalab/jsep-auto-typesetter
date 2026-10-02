import shutil
from pathlib import Path

from .converter import ConversionError, _run
from .models import PdfRequest


def generate_pdf(request: PdfRequest, workdir: Path) -> Path:
    template = Path(__file__).with_name("template.tex")
    markdown = workdir / "manuscript.md"
    tex = workdir / "manuscript.tex"
    pdf = workdir / "manuscript.pdf"
    authors = "; ".join(a.name + (f"（{a.affiliation}）" if a.affiliation else "") for a in request.manuscript.authors)
    markdown.write_text(
        f"---\ntitle: {request.manuscript.title!r}\nauthor: {authors!r}\n"
        f"fontsize: {request.font_size}pt\nmargin: {request.margin_mm}mm\n---\n\n"
        f"# 抄録\n\n{request.manuscript.abstract}\n\n{request.manuscript.body_markdown}", encoding="utf-8")
    _run(["pandoc", str(markdown), "--from=markdown-raw_tex-raw_attribute", "--to=latex", "--template", str(template),
          "--standalone", "--number-sections", "-o", str(tex)], workdir)
    # Defense in depth: no shell escape, isolated temp cwd, and a hard timeout.
    _run(["lualatex", "--no-shell-escape", "--interaction=nonstopmode", "--halt-on-error", tex.name], workdir)
    if not pdf.is_file():
        raise ConversionError("PDFファイルが生成されませんでした。")
    output = workdir / "jsep-manuscript.pdf"
    shutil.copyfile(pdf, output)
    return output
