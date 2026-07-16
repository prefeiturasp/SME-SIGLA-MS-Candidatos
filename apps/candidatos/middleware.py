import json
import logging
import time
import uuid

from sigla_sdk.context import clear_request_context, set_auth_header, set_correlation_id

logger = logging.getLogger("django.request_logger")


def _get_request_header(request, name: str):
    headers = getattr(request, "headers", None)
    if headers is not None:
        return headers.get(name)
    meta = getattr(request, "META", {}) or {}
    return meta.get(f"HTTP_{name.upper().replace('-', '_')}")


class CorrelationIdMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        start_time = time.perf_counter()

        cid = _get_request_header(request, "X-Correlation-ID") or str(uuid.uuid4())
        set_correlation_id(cid)
        set_auth_header(_get_request_header(request, "Authorization"))

        payload = None
        if getattr(request, "method", None) in ["POST", "PUT", "PATCH"]:
            try:
                content_type = getattr(request, "content_type", "") or ""
                body = getattr(request, "body", b"") or b""
                if content_type.startswith("application/json") and body:
                    payload = json.loads(body)
                else:
                    post = getattr(request, "POST", None)
                    payload = (post.dict() if post is not None else None) or body.decode(
                        "utf-8", errors="replace"
                    )
            except Exception:
                payload = "<erro_ao_ler_payload>"

        response = self.get_response(request)

        if getattr(request, "method", None) != "OPTIONS":
            duration_ms = (time.perf_counter() - start_time) * 1000
            extra_data = {
                "method": getattr(request, "method", None),
                "path": getattr(request, "path", None),
                "status_code": getattr(response, "status_code", None),
                "duration_ms": round(duration_ms, 2),
                # "payload": payload,
                "user": str(getattr(request, "user", "Anonymous")),
            }
            logger.info(f"{extra_data['method']} {extra_data['path']}", extra=extra_data)

        try:
            response["X-Correlation-ID"] = cid
        except Exception:
            pass

        clear_request_context()
        return response

