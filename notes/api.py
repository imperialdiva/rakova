import logging
import time
from concurrent import futures
from datetime import datetime, timezone

import grpc
from google.protobuf.timestamp_pb2 import Timestamp

from .application import NoteService
from .domain import AlreadyArchived, InvalidNote, NoteNotFound, NoteState
from .infrastructure import InMemoryNoteRepository
from .generated import notes_pb2, notes_pb2_grpc

logger = logging.getLogger(__name__)


def as_proto(note):
    result = notes_pb2.Note(id=note.id, title=note.title, body=note.body,
                            state=int(note.state))
    result.created_at.FromDatetime(note.created_at)
    if note.remind_at:
        result.remind_at.FromDatetime(note.remind_at)
    return result


class LoggingInterceptor(grpc.ServerInterceptor):
    def intercept_service(self, continuation, handler_call_details):
        logger.info("rpc=%s", handler_call_details.method)
        return continuation(handler_call_details)


class NotesApi(notes_pb2_grpc.NotesServiceServicer):
    def __init__(self, service: NoteService):
        self.service = service

    def CreateNote(self, request, context):
        try:
            reminder = request.remind_at.ToDatetime(tzinfo=timezone.utc) if request.HasField("remind_at") else None
            return as_proto(self.service.create(request.title, request.body, reminder))
        except InvalidNote as exc:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, f"INVALID_NOTE: {exc}")

    def GetNote(self, request, context):
        if request.id <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "INVALID_ID: id must be positive")
        try:
            return as_proto(self.service.get(request.id))
        except NoteNotFound as exc:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NOTE_NOT_FOUND: {exc}")

    def ListNotes(self, request, context):
        if request.state not in (0, 1, 2):
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "INVALID_STATE: unknown enum value")
        state = None if request.state == 0 else NoteState(request.state)
        for note in self.service.list(state):
            if not context.is_active():
                return
            yield as_proto(note)
            time.sleep(0.001)

    def ArchiveNote(self, request, context):
        if request.id <= 0:
            context.abort(grpc.StatusCode.INVALID_ARGUMENT, "INVALID_ID: id must be positive")
        try:
            return notes_pb2.ArchiveNoteResponse(note=as_proto(self.service.archive(request.id)))
        except NoteNotFound as exc:
            context.abort(grpc.StatusCode.NOT_FOUND, f"NOTE_NOT_FOUND: {exc}")
        except AlreadyArchived as exc:
            context.abort(grpc.StatusCode.ALREADY_EXISTS, f"ALREADY_ARCHIVED: {exc}")


def build_server(port: int = 50051):
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10),
                         interceptors=(LoggingInterceptor(),))
    notes_pb2_grpc.add_NotesServiceServicer_to_server(
        NotesApi(NoteService(InMemoryNoteRepository())), server)
    actual_port = server.add_insecure_port(f"127.0.0.1:{port}")
    return server, actual_port


def main():
    logging.basicConfig(level=logging.INFO)
    server, port = build_server()
    server.start()
    print(f"Notes gRPC on 127.0.0.1:{port}")
    server.wait_for_termination()


if __name__ == "__main__":
    main()
