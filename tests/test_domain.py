from datetime import datetime, timedelta, timezone

import pytest

from notes.domain import AlreadyArchived, InvalidNote, Note, NoteState, validate_reminder, validate_title


def test_title_is_trimmed():
    assert validate_title("  abc  ") == "abc"


def test_empty_title_is_invalid():
    with pytest.raises(InvalidNote):
        validate_title(" \t ")


def test_past_reminder_is_invalid():
    with pytest.raises(InvalidNote):
        validate_reminder(datetime.now(timezone.utc) - timedelta(days=1))


def test_archiving_twice_is_error():
    note = Note(1, "t", "b", NoteState.ACTIVE, datetime.now(timezone.utc))
    with pytest.raises(AlreadyArchived):
        note.archive().archive()
