from datetime import datetime, timezone
from typing import Protocol

from .domain import Note, NoteNotFound, NoteState, validate_reminder, validate_title


class NoteRepository(Protocol):
    def add(self, title: str, body: str, remind_at: datetime | None) -> Note: ...
    def get(self, note_id: int) -> Note | None: ...
    def list(self) -> list[Note]: ...
    def save(self, note: Note) -> None: ...


class NoteService:
    def __init__(self, repository: NoteRepository):
        self.repository = repository

    def create(self, title: str, body: str, remind_at: datetime | None = None) -> Note:
        return self.repository.add(validate_title(title), body, validate_reminder(remind_at))

    def get(self, note_id: int) -> Note:
        note = self.repository.get(note_id)
        if note is None:
            raise NoteNotFound(f"note {note_id} does not exist")
        return note

    def list(self, state: NoteState | None = None) -> list[Note]:
        return [note for note in self.repository.list() if state is None or note.state == state]

    def archive(self, note_id: int) -> Note:
        note = self.get(note_id).archive()
        self.repository.save(note)
        return note
