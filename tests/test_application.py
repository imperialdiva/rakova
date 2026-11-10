import pytest

from notes.application import NoteService
from notes.domain import NoteNotFound, NoteState
from notes.infrastructure import InMemoryNoteRepository


def test_create_and_filter_with_fake_repository():
    service = NoteService(InMemoryNoteRepository())
    note = service.create(" New ", "body")
    assert service.list(NoteState.ACTIVE) == [note]
    assert service.list(NoteState.ARCHIVED) == []


def test_archive_and_missing_with_fake_repository():
    service = NoteService(InMemoryNoteRepository())
    note = service.create("New", "body")
    assert service.archive(note.id).state == NoteState.ARCHIVED
    with pytest.raises(NoteNotFound):
        service.get(999)
