from pathlib import Path
from unittest.mock import patch

from backend.storage import ManuscriptStore


def test_store_keeps_assets_until_deleted(tmp_path):
    store = ManuscriptStore(tmp_path)
    manuscript_id, directory = store.create()
    asset = directory / "media" / "image.png"
    asset.parent.mkdir()
    asset.write_bytes(b"image")
    assert store.get(manuscript_id) == directory
    assert asset.read_bytes() == b"image"
    store.delete(manuscript_id)
    assert not directory.exists()


def test_store_purges_expired_sessions(tmp_path):
    store = ManuscriptStore(tmp_path, ttl=1)
    manuscript_id, directory = store.create()
    with patch("backend.storage.time.monotonic", return_value=10**9):
        assert store.get(manuscript_id) is None
    assert not directory.exists()
