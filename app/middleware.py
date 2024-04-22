"""Связующее программное обеспечение."""

__author__ = "aa.blinov"

import logging
import random
import string
import time
from typing import Any, Callable

from fastapi import Request

logger = logging.getLogger("time")

MILLISECONDS_PER_SECOND = 1000


def get_unique_id(size: int = 8) -> str:
    """Получить уникальный идентификатор."""
    return "".join(random.choices(string.ascii_uppercase + string.digits, k=size))


async def log_requests(request: Request, func: Callable) -> Any:  # type: ignore
    """Промежуточный слой для логирование запроса."""
    uid = get_unique_id()
    logger.info(f"START:path={request.url.path};rid={uid}")
    start_time = time.time()
    try:
        response = await func(request)
    except Exception:
        logger.exception("ERROR:")
        raise
    finally:
        process_time = (time.time() - start_time) * MILLISECONDS_PER_SECOND
        logger.info(f"END REQUEST rid={uid};completed_in={process_time:.2f}ms")

    return response
