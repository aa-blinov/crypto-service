"""Главная точка входа сервиса."""

__author__ = "aa.blinov"

import asyncio
import logging
from enum import StrEnum
from http import HTTPStatus
from typing import Any

from fastapi import FastAPI, HTTPException
from httpx import HTTPStatusError, TimeoutException

from app.config import settings
from app.log import setup_logger
from app.middleware import log_requests
from app.requests import HttpMethod, async_request

setup_logger()
logger = logging.getLogger("service")

app = FastAPI(
    title=settings.API_TITLE,
    description=settings.API_DESCRIPTION,
    version=settings.API_VERSION,
    debug=settings.DEBUG,
    root_path="/api",
)
app.middleware("http")(log_requests)


class CryptoSource(StrEnum):
    """Источники данных."""

    BINANCE = "binance"
    BYBIT = "bybit"

    @staticmethod
    def get_url(source: str) -> str:
        """Получить URL источника данных."""
        return {
            CryptoSource.BINANCE: "https://api.binance.com/api/v3/ticker/price",
            CryptoSource.BYBIT: "https://api.bybit.com/v2/public/tickers",
        }[source]

    @staticmethod
    def get_result_key(source: str) -> str | None:
        """Получить ключ результата из источника данных."""
        return {
            CryptoSource.BINANCE: None,
            CryptoSource.BYBIT: "result",
        }[source]

    @staticmethod
    def get_symbol_key(source: str) -> str:
        """Получить ключ символа из источника данных."""
        return {
            CryptoSource.BINANCE: "symbol",
            CryptoSource.BYBIT: "symbol",
        }[source]

    @staticmethod
    def get_price_key(source: str) -> str:
        """Получить ключ цены из источника данных."""
        return {CryptoSource.BINANCE: "price", CryptoSource.BYBIT: "last_price"}[source]

    @staticmethod
    def get_code_key(source: str) -> str:
        """Получить ключ кода ответа."""
        return {
            CryptoSource.BINANCE: "code",
            CryptoSource.BYBIT: "ret_code",
        }[source]

    @staticmethod
    def get_not_found_codes(source: str) -> tuple[int]:
        """Получить код ответа при отсутствии данных."""
        return {
            CryptoSource.BINANCE: (-1100, -1121),
            CryptoSource.BYBIT: (10001,),
        }[source]


def round_numeric_value(value: float | str) -> int:
    """Округлить значение."""
    return round(float(value))


async def get_coin_prices(source: CryptoSource, symbol: str = None) -> dict[str, float] | None:
    """Получить цены монет из указанного источника данных."""
    source_url = CryptoSource.get_url(source.value)

    params = None
    if symbol:
        params = {"symbol": symbol}

    response = await async_request(
        method=HttpMethod.GET,
        url=source_url,
        params=params,
    )
    if response.status_code not in (HTTPStatus.OK.value, HTTPStatus.BAD_REQUEST.value):
        response.raise_for_status()

    response_json = response.json()

    result_key = CryptoSource.get_result_key(source.value)
    price_key = CryptoSource.get_price_key(source.value)
    if not symbol:
        if result_key:
            response_json = response_json[result_key]

        symbol_key = CryptoSource.get_symbol_key(source.value)

        return {item[symbol_key]: round_numeric_value(item[price_key]) for item in response_json}

    code_key = CryptoSource.get_code_key(source.value)
    not_found_codes = CryptoSource.get_not_found_codes(source.value)

    if response_json.get(code_key) in not_found_codes:
        return {source.value: None}

    if result_key:
        response_json = response_json[result_key]
        if isinstance(response_json, list):
            response_json = response_json[0]

    return {source.value: round_numeric_value(response_json[price_key])}


def check_service_availability(*replies: Any) -> None:
    """Проверить доступность источника данных."""
    for reply in replies:
        if isinstance(reply, (HTTPStatusError, TimeoutException)):
            raise HTTPException(
                status_code=HTTPStatus.SERVICE_UNAVAILABLE.value,
                detail="Не удалось получить цены от всех криптовалютных бирж. Попробуйте позже.",
            )


@app.get("/prices")
async def get_prices() -> list[dict[str, Any]]:
    """Получить цены монет на биржах на данный момент времени."""
    binance_coins, bybit_coins = await asyncio.gather(
        get_coin_prices(CryptoSource.BINANCE), get_coin_prices(CryptoSource.BYBIT), return_exceptions=True
    )

    check_service_availability(binance_coins, bybit_coins)

    common_coins = set(binance_coins.keys()) & set(bybit_coins.keys())
    prices = []
    for coin in common_coins:
        binance_price = binance_coins.get(coin)
        bybit_price = bybit_coins.get(coin)

        if binance_price is not None and bybit_price is not None:
            prices.append(
                {
                    "name": coin,
                    "prices": {
                        "binance": binance_price,
                        "bybit": bybit_price,
                    },
                }
            )

    return prices


@app.get("/prices/{coin_name}")
async def get_coin_price(coin_name: str) -> dict[str, Any]:
    binance_coin, bybit_coin = await asyncio.gather(
        get_coin_prices(CryptoSource.BINANCE, symbol=coin_name),
        get_coin_prices(CryptoSource.BYBIT, coin_name),
        return_exceptions=True,
    )

    check_service_availability(binance_coin, bybit_coin)

    return {
        "name": coin_name,
        "prices": {
            **binance_coin,
            **bybit_coin,
        },
    }
