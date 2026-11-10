import argparse

import grpc

from .generated import notes_pb2, notes_pb2_grpc


def main():
    parser = argparse.ArgumentParser(description="Client for NotesService")
    parser.add_argument("command", choices=["create", "get", "list", "archive", "demo"])
    parser.add_argument("--id", type=int, default=1)
    parser.add_argument("--title", default="Учебная заметка")
    parser.add_argument("--body", default="Проверить gRPC")
    parser.add_argument("--target", default="127.0.0.1:50051")
    args = parser.parse_args()
    try:
        with grpc.insecure_channel(args.target) as channel:
            stub = notes_pb2_grpc.NotesServiceStub(channel)
            if args.command == "create":
                print(stub.CreateNote(notes_pb2.CreateNoteRequest(title=args.title, body=args.body), timeout=3))
            elif args.command == "get":
                print(stub.GetNote(notes_pb2.GetNoteRequest(id=args.id), timeout=3))
            elif args.command == "list":
                for note in stub.ListNotes(notes_pb2.ListNotesRequest(), timeout=5):
                    print(note)
            elif args.command == "archive":
                print(stub.ArchiveNote(notes_pb2.ArchiveNoteRequest(id=args.id), timeout=3))
            else:
                created = stub.CreateNote(notes_pb2.CreateNoteRequest(title=args.title, body=args.body), timeout=3)
                print("created:", created)
                print("get:", stub.GetNote(notes_pb2.GetNoteRequest(id=created.id), timeout=3))
                print("list:", list(stub.ListNotes(notes_pb2.ListNotesRequest(), timeout=5)))
                print("archive:", stub.ArchiveNote(notes_pb2.ArchiveNoteRequest(id=created.id), timeout=3))
    except grpc.RpcError as exc:
        print(f"gRPC error {exc.code().name}: {exc.details()}")
        raise SystemExit(1) from exc


if __name__ == "__main__":
    main()
