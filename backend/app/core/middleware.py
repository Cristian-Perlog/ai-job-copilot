import uuid

from starlette.types import ASGIApp, Message, Receive, Scope, Send

from app.core.logging import request_id_var

REQUEST_ID_HEADER = "x-request-id"


class RequestIDMiddleware:
    """Attach a correlation id to every request/response.

    Reads ``X-Request-ID`` from the incoming request (or generates a uuid4),
    stores it in a ContextVar so log records can include it, and echoes it
    back on the response ``X-Request-ID`` header.
    """

    def __init__(self, app: ASGIApp) -> None:
        self.app = app

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] != "http":
            await self.app(scope, receive, send)
            return

        headers = dict(scope["headers"])
        incoming = headers.get(REQUEST_ID_HEADER.encode())
        request_id = incoming.decode() if incoming else str(uuid.uuid4())

        # Set without resetting: each request enters with a fresh value, and
        # the var must stay populated for exception handlers, which run in
        # Starlette's ServerErrorMiddleware *outside* this middleware after the
        # call stack unwinds. ContextVars are task-local, so there is no leak
        # across concurrent requests.
        request_id_var.set(request_id)

        async def send_with_request_id(message: Message) -> None:
            if message["type"] == "http.response.start":
                raw_headers = [
                    (k, v)
                    for k, v in message.get("headers", [])
                    if k.lower() != REQUEST_ID_HEADER.encode()
                ]
                raw_headers.append((REQUEST_ID_HEADER.encode(), request_id.encode()))
                message["headers"] = raw_headers
            await send(message)

        await self.app(scope, receive, send_with_request_id)
