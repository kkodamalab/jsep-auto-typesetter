from unittest.mock import patch

import pytest

from backend.converter import ConversionError
from backend.main import pdf
from backend.models import Manuscript, PdfRequest
from backend.storage import ManuscriptStore


def test_pdf_conversion_error_removes_session(tmp_path):
    temporary_store = ManuscriptStore(tmp_path)
    manuscript_id, directory = temporary_store.create()
    (directory / "media").mkdir()
    request = PdfRequest(manuscript_id=manuscript_id, manuscript=Manuscript(title="架空原稿"))

    with patch("backend.main.store", temporary_store), \
         patch("backend.main.require_tools"), \
         patch("backend.main.generate_pdf", side_effect=ConversionError("test failure")):
        with pytest.raises(Exception) as raised:
            pdf(request)
    assert getattr(raised.value, "status_code", None) == 422
    assert not directory.exists()
