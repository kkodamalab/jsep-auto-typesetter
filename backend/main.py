import tempfile
from pathlib import Path

from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .converter import MAX_UPLOAD_BYTES, ConversionError, extract_docx, require_tools
from .models import Manuscript, PdfRequest
from .pdf import generate_pdf

app = FastAPI(title="JSEP Auto Typesetter", version="0.2.0")


@app.get("/api/health")
def health():
    try:
        require_tools()
        return {"status": "ok", "conversion": True}
    except ConversionError as exc:
        return {"status": "degraded", "conversion": False, "detail": str(exc)}


@app.post("/api/extract", response_model=Manuscript)
async def extract(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(415, "DOCXファイルを選択してください。")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "ファイルサイズは25MB以下にしてください。")
    try:
        require_tools()
        with tempfile.TemporaryDirectory(prefix="jsep-") as directory:
            path = Path(directory) / "upload.docx"
            path.write_bytes(data)
            return extract_docx(path, Path(directory))
    except ConversionError as exc:
        raise HTTPException(422, str(exc)) from exc


@app.post("/api/pdf")
def pdf(request: PdfRequest):
    try:
        require_tools()
        directory = tempfile.mkdtemp(prefix="jsep-")
        result = generate_pdf(request, Path(directory))
        return FileResponse(result, media_type="application/pdf", filename="jsep-manuscript.pdf",
                            background=_cleanup_task(directory))
    except ConversionError as exc:
        raise HTTPException(422, str(exc)) from exc


def _cleanup_task(directory: str):
    from starlette.background import BackgroundTask
    import shutil
    return BackgroundTask(shutil.rmtree, directory, True)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
