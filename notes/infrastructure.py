from datetime import datetime, timezone
from threading import RLock

from .domain import Note, NoteState


class InMemoryNoteRepository:
    def __init__(self):
        self._notes: dict[int, Note] = {}
        self._next_id = 1
        self._lock = RLock()

    def add(self, title: str, body: str, remind_at: datetime | None) -> Note:
        with self._lock:
            note = Note(self._next_id, title, body, NoteState.ACTIVE,
                        datetime.now(timezone.utc), remind_at)
            self._notes[note.id] = note
            self._next_id += 1
            return note

    def get(self, note_id: int) -> Note | None:
        with self._lock:
            return self._notes.get(note_id)

    def list(self) -> list[Note]:
        with self._lock:
            return list(self._notes.values())

    def save(self, note: Note) -> None:
        with self._lock:
            self._notes[note.id] = note
