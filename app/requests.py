"""Запросы к внешним сервисам."""

__author__ = "aa.blinov"

from enum import StrEnum
from typing import Dict, Any

from httpx import Response, AsyncClient

BASE_TIMEOUT = 5


class HttpMethod(StrEnum):
    """HTTP-методы."""

    GET = "GET"
    POST = "POST"
    PUT = "PUT"
    PATCH = "PATCH"
    DELETE = "DELETE"


async def async_request(
    method: HttpMethod,
    url: str,
    auth: tuple[str, str] | None = None,
    headers: Dict[str, Any] | None = None,
    params: Dict[str, Any] | None = None,
    data: Any = None,
    json: Dict[str, Any] | None = None,
    files: Any = None,
    timeout: int | None = BASE_TIMEOUT,
    client_params: Dict[str, Any] | None = None,
) -> Response:
    """Асинхронно запросить данные."""
    async with AsyncClient(**(client_params or {})) as client:
        return await client.request(
            method=str(method.value),
            url=url,
            auth=auth,
            headers=headers,
            params=params,
            data=data,
            json=json,
            files=files,
            timeout=timeout,
        )
