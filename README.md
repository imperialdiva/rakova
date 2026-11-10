# gRPC сервис заметок

## Установка и генерация

```bash
uv sync --extra dev
uv run python -m grpc_tools.protoc -Iproto --python_out=notes/generated --grpc_python_out=notes/generated proto/notes.proto
```

Сгенерированные файлы включены в репозиторий. После регенерации нужно убедиться, что импорт `notes_pb2` в `notes_pb2_grpc.py` относительный (`from . import notes_pb2`).

## Запуск

Терминал 1: `uv run python -m notes.api` (insecure `127.0.0.1:50051`, пул 10 потоков). Терминал 2: `uv run python -m notes.client demo`; команды `create`, `get --id 1`, `list`, `archive --id 1` выполняются отдельно. Тесты: `uv run pytest -q`.

## Методы и ошибки

| Метод | Тип | Назначение |
|---|---|---|
| CreateNote | unary | Создание |
| GetNote | unary | Чтение по ID |
| ListNotes | server streaming | Поток снимка заметок с фильтром состояния |
| ArchiveNote | unary | Архивация |

`INVALID_ARGUMENT` — пустой/длинный заголовок, плохая дата, ID или enum; `NOT_FOUND` — отсутствующая заметка; `ALREADY_EXISTS` — повторная архивация. Детали каждой ошибки содержат машинный префикс и пояснение. Клиент задаёт дедлайн каждому вызову и показывает `code/details`. Интерцептор `LoggingInterceptor` записывает имя метода для диагностики; содержимое заметок не логируется. Insecure канал служит только для учебного локального запуска.

Контракт использует `int64` ID, `Timestamp` и enum. Номер и имя удалённого поля зарезервированы. Архитектура описана в [docs/architecture.md](docs/architecture.md). История содержит не менее пяти осмысленных коммитов. Репозиторий опубликован на [GitHub](https://github.com/imperialdiva/rakova). В тексте задания указан GitLab; для буквального соответствия потребуется зеркало на GitLab.

Документация: [gRPC Python basics](https://grpc.io/docs/languages/python/basics/), [Protobuf proto3](https://protobuf.dev/programming-guides/proto3/).
