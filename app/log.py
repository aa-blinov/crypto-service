"""Логирование."""

__author__ = "aa.blinov"

import logging
import logging.config

LOGGING = {
    "version": 1,
    "disable_existing_loggers": False,
    "formatters": {
        "default": {
            "format": "%(levelname)s:%(asctime)s:%(name)s:%(message)s",
        },
    },
    "handlers": {
        "stdout": {
            "level": "INFO",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stdout",
            "formatter": "default",
        },
        "stderr": {
            "level": "WARNING",
            "class": "logging.StreamHandler",
            "stream": "ext://sys.stderr",
            "formatter": "default",
        },
    },
    "loggers": {
        "root": {
            "handlers": ["stderr"],
            "level": "ERROR",
            "propagate": False,
        },
        "time": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
        "service": {
            "handlers": ["stdout"],
            "level": "INFO",
            "propagate": False,
        },
    },
}


def setup_logger() -> None:
    """Установить логирования."""
    logging.config.dictConfig(LOGGING)
