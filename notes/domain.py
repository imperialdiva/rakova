from dataclasses import dataclass, replace
from datetime import datetime, timezone
from enum import IntEnum


class NoteState(IntEnum):
    ACTIVE = 1
    ARCHIVED = 2


@dataclass(frozen=True)
class Note:
    id: int
    title: str
    body: str
    state: NoteState
    created_at: datetime
    remind_at: datetime | None = None

    def archive(self) -> "Note":
        if self.state == NoteState.ARCHIVED:
            raise AlreadyArchived("note is already archived")
        return replace(self, state=NoteState.ARCHIVED)


class InvalidNote(ValueError):
    pass


class NoteNotFound(LookupError):
    pass


class AlreadyArchived(ValueError):
    pass


def validate_title(title: str) -> str:
    clean = title.strip()
    if not clean or len(clean) > 120:
        raise InvalidNote("title must contain 1..120 characters")
    return clean


def validate_reminder(remind_at: datetime | None) -> datetime | None:
    if remind_at is None:
        return None
    if remind_at.tzinfo is None:
        raise InvalidNote("remind_at must contain a timezone")
    value = remind_at.astimezone(timezone.utc)
    if value <= datetime.now(timezone.utc):
        raise InvalidNote("remind_at must be in the future")
    return value
