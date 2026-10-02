import json
import re
import shutil
import subprocess
import tempfile
from pathlib import Path

from .models import Author, Manuscript

MAX_UPLOAD_BYTES = 25 * 1024 * 1024


class ConversionError(RuntimeError):
    """A safe, user-facing conversion failure."""


def require_tools() -> None:
    missing = [name for name in ("pandoc", "lualatex") if shutil.which(name) is None]
    if missing:
        raise ConversionError(f"変換ツールが利用できません: {', '.join(missing)}")


def _run(command: list[str], cwd: Path, timeout: int = 120) -> subprocess.CompletedProcess[str]:
    try:
        result = subprocess.run(command, cwd=cwd, text=True, capture_output=True, timeout=timeout, check=False)
    except subprocess.TimeoutExpired as exc:
        raise ConversionError("組版処理がタイムアウトしました。") from exc
    if result.returncode:
        details = (result.stderr or result.stdout)[-3000:]
        raise ConversionError(f"変換に失敗しました。\n{details}")
    return result


def extract_docx(source: Path, workdir: Path) -> Manuscript:
    """Use Pandoc's DOCX reader and AST; never executes document content."""
    media = workdir / "media"
    ast_path = workdir / "document.json"
    md_path = workdir / "body.md"
    _run(["pandoc", str(source), "-t", "json", f"--extract-media={media}", "-o", str(ast_path)], workdir)
    _run(["pandoc", str(source), "-t", "markdown", f"--extract-media={media}", "-o", str(md_path)], workdir)
    ast = json.loads(ast_path.read_text(encoding="utf-8"))
    meta = ast.get("meta", {})
    title = _meta_text(meta.get("title")) or _first_heading(ast) or source.stem
    authors = [Author(name=name) for name in _meta_authors(meta.get("author"))]
    markdown = md_path.read_text(encoding="utf-8")
    abstract, body = _split_abstract(markdown)
    bibliography = _reference_section(body)
    warnings = _inspect_ast(ast, media)
    return Manuscript(title=title, authors=authors, abstract=abstract, body_markdown=body,
                      bibliography=bibliography, warnings=warnings)


def _inline_text(value) -> str:
    if isinstance(value, str):
        return value
    if isinstance(value, list):
        return "".join(_inline_text(item) for item in value)
    if isinstance(value, dict):
        kind, content = value.get("t"), value.get("c", "")
        if kind in {"Space", "SoftBreak", "LineBreak"}:
            return " "
        return _inline_text(content)
    return ""


def _meta_text(value) -> str:
    return _inline_text(value).strip() if value else ""


def _meta_authors(value) -> list[str]:
    if not value:
        return []
    content = value.get("c", []) if isinstance(value, dict) else value
    items = content if isinstance(content, list) else [content]
    return [text for item in items if (text := _inline_text(item).strip())]


def _first_heading(ast: dict) -> str:
    for block in ast.get("blocks", []):
        if block.get("t") == "Header":
            content = block.get("c", [])
            return _inline_text(content[-1] if content else []).strip()
    return ""


def _split_abstract(markdown: str) -> tuple[str, str]:
    match = re.search(r"(?ims)^#{1,3}\s*(?:抄録|要旨|abstract)\s*$\n(.*?)(?=^#{1,3}\s|\Z)", markdown)
    if not match:
        return "", markdown
    abstract = match.group(1).strip()
    return abstract, (markdown[:match.start()] + markdown[match.end():]).strip()


def _reference_section(markdown: str) -> str:
    match = re.search(r"(?ims)^#{1,3}\s*(?:参考文献|references)\s*$\n(.*)\Z", markdown)
    return match.group(1).strip() if match else ""


def _inspect_ast(ast: dict, media: Path) -> list[str]:
    serialized = json.dumps(ast, ensure_ascii=False)
    warnings = []
    if '"Math"' in serialized and "\\unsupported" in serialized:
        warnings.append("未対応の数式コマンドが含まれている可能性があります。")
    if '"Image"' in serialized and not media.exists():
        warnings.append("図が検出されましたが、画像を抽出できませんでした。")
    if '"Table"' in serialized:
        warnings.append("表のレイアウトはPDF生成後に確認してください。")
    return warnings
