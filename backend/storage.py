import shutil
import tempfile
import threading
import time
import uuid
from pathlib import Path

SESSION_TTL_SECONDS = 60 * 60


class ManuscriptStore:
    """Process-local registry for short-lived manuscript assets."""

    def __init__(self, root: Path | None = None, ttl: int = SESSION_TTL_SECONDS):
        self.root = root or Path(tempfile.gettempdir()) / "jsep-manuscripts"
        self.root.mkdir(mode=0o700, parents=True, exist_ok=True)
        self.ttl = ttl
        self._sessions: dict[str, tuple[Path, float]] = {}
        self._lock = threading.Lock()

    def create(self) -> tuple[str, Path]:
        self.purge_expired()
        manuscript_id = uuid.uuid4().hex
        path = self.root / manuscript_id
        path.mkdir(mode=0o700)
        with self._lock:
            self._sessions[manuscript_id] = (path, time.monotonic())
        return manuscript_id, path

    def get(self, manuscript_id: str) -> Path | None:
        if not manuscript_id or not manuscript_id.isascii() or not manuscript_id.isalnum():
            return None
        with self._lock:
            entry = self._sessions.get(manuscript_id)
        if not entry:
            return None
        path, created = entry
        if time.monotonic() - created > self.ttl:
            self.delete(manuscript_id)
            return None
        return path

    def delete(self, manuscript_id: str) -> None:
        with self._lock:
            entry = self._sessions.pop(manuscript_id, None)
        if entry:
            shutil.rmtree(entry[0], ignore_errors=True)

    def purge_expired(self) -> None:
        now = time.monotonic()
        with self._lock:
            expired = [key for key, (_, created) in self._sessions.items() if now - created > self.ttl]
        for key in expired:
            self.delete(key)


store = ManuscriptStore()
