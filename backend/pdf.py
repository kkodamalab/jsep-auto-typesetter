import json
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
    # JSON flow mappings are valid YAML and safely encode quotes, colons and newlines.
    metadata = json.dumps({"title": request.manuscript.title, "author": authors,
                           "fontsize": f"{request.font_size}pt", "margin": f"{request.margin_mm}mm"},
                          ensure_ascii=False)
    markdown.write_text(f"---\n{metadata}\n---\n\n# 抄録\n\n{request.manuscript.abstract}\n\n"
                        f"{request.manuscript.body_markdown}", encoding="utf-8")
    # Disable Pandoc's smart typography: author names and titles must retain
    # their source apostrophes/quotation marks exactly through PDF generation.
    _run(["pandoc", str(markdown), "--from=markdown-smart-raw_tex-raw_attribute", "--to=latex", "--template", str(template),
          "--standalone", "--number-sections", "--resource-path", str(workdir), "-o", str(tex)], workdir)
    # Defense in depth: no shell escape, isolated temp cwd, and a hard timeout.
    _run(["lualatex", "--no-shell-escape", "--interaction=nonstopmode", "--halt-on-error", tex.name], workdir)
    if not pdf.is_file():
        raise ConversionError("PDFファイルが生成されませんでした。")
    output = workdir / "jsep-manuscript.pdf"
    shutil.copyfile(pdf, output)
    return output
