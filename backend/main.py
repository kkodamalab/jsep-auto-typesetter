from fastapi import FastAPI, File, HTTPException, UploadFile
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

from .converter import MAX_UPLOAD_BYTES, ConversionError, extract_docx, require_tools
from .models import ExtractionResponse, PdfRequest
from .pdf import generate_pdf
from .storage import store

app = FastAPI(title="JSEP Auto Typesetter", version="0.2.0")


@app.get("/api/health")
def health():
    try:
        require_tools()
        return {"status": "ok", "conversion": True}
    except ConversionError as exc:
        return {"status": "degraded", "conversion": False, "detail": str(exc)}


@app.post("/api/extract", response_model=ExtractionResponse)
async def extract(file: UploadFile = File(...)):
    if not file.filename or not file.filename.lower().endswith(".docx"):
        raise HTTPException(415, "DOCXファイルを選択してください。")
    data = await file.read(MAX_UPLOAD_BYTES + 1)
    if len(data) > MAX_UPLOAD_BYTES:
        raise HTTPException(413, "ファイルサイズは25MB以下にしてください。")
    manuscript_id, directory = store.create()
    try:
        require_tools()
        path = directory / "upload.docx"
        path.write_bytes(data)
        manuscript = extract_docx(path, directory)
        return ExtractionResponse(**manuscript.model_dump(), manuscript_id=manuscript_id)
    except ConversionError as exc:
        store.delete(manuscript_id)
        raise HTTPException(422, str(exc)) from exc
    except Exception:
        store.delete(manuscript_id)
        raise


@app.post("/api/pdf")
def pdf(request: PdfRequest):
    directory = store.get(request.manuscript_id)
    if directory is None:
        raise HTTPException(404, "原稿の一時データが見つからないか、有効期限が切れています。再アップロードしてください。")
    try:
        require_tools()
        result = generate_pdf(request, directory)
        return FileResponse(result, media_type="application/pdf", filename="jsep-manuscript.pdf",
                            background=_cleanup_task(request.manuscript_id))
    except ConversionError as exc:
        store.delete(request.manuscript_id)
        raise HTTPException(422, str(exc)) from exc
    except Exception:
        store.delete(request.manuscript_id)
        raise


def _cleanup_task(manuscript_id: str):
    from starlette.background import BackgroundTask
    return BackgroundTask(store.delete, manuscript_id)


app.mount("/", StaticFiles(directory="frontend", html=True), name="frontend")
