import httpx
from tenacity import retry_if_exception, stop_after_attempt, wait_exponential
from tenacity.asyncio import AsyncRetrying


def _is_transient_http_error(exc: BaseException) -> bool:
    if isinstance(
        exc,
        (
            httpx.TimeoutException,
            httpx.ConnectError,
            httpx.ReadError,
            httpx.RemoteProtocolError,
        ),
    ):
        return True
    if isinstance(exc, httpx.HTTPStatusError):
        code = exc.response.status_code
        return code >= 500 or code == 429
    return False


_http_retry = AsyncRetrying(
    stop=stop_after_attempt(3),
    wait=wait_exponential(multiplier=0.3, min=0.3, max=2.0),
    reraise=True,
    retry=retry_if_exception(_is_transient_http_error),
)


async def request_with_retry(
    client: httpx.AsyncClient,
    method: str,
    url: str,
    **kwargs,
) -> httpx.Response:
    m = method.lower()
    if m not in ("get", "post", "put", "patch", "delete"):
        raise ValueError(f"Unsupported HTTP method: {method}")

    async def do_request() -> httpx.Response:
        http_call = getattr(client, m)
        response = await http_call(url, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as exc:
            if _is_transient_http_error(exc):
                raise
        return response

    return await _http_retry(do_request)
