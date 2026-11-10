import grpc
import pytest

from notes.api import build_server
from notes.generated import notes_pb2, notes_pb2_grpc


def test_full_grpc_scenario():
    server, port = build_server(0)
    server.start()
    try:
        with grpc.insecure_channel(f"127.0.0.1:{port}") as channel:
            stub = notes_pb2_grpc.NotesServiceStub(channel)
            created = stub.CreateNote(notes_pb2.CreateNoteRequest(title="test", body="body"), timeout=3)
            assert stub.GetNote(notes_pb2.GetNoteRequest(id=created.id), timeout=3).title == "test"
            assert [n.id for n in stub.ListNotes(notes_pb2.ListNotesRequest(), timeout=3)] == [created.id]
            assert stub.ArchiveNote(notes_pb2.ArchiveNoteRequest(id=created.id), timeout=3).note.state == 2
            with pytest.raises(grpc.RpcError) as exc:
                stub.ArchiveNote(notes_pb2.ArchiveNoteRequest(id=created.id), timeout=3)
            assert exc.value.code() == grpc.StatusCode.ALREADY_EXISTS
            with pytest.raises(grpc.RpcError) as exc:
                stub.GetNote(notes_pb2.GetNoteRequest(id=999), timeout=3)
            assert exc.value.code() == grpc.StatusCode.NOT_FOUND
            with pytest.raises(grpc.RpcError) as exc:
                stub.CreateNote(notes_pb2.CreateNoteRequest(title=" "), timeout=3)
            assert exc.value.code() == grpc.StatusCode.INVALID_ARGUMENT
    finally:
        server.stop(0).wait()
