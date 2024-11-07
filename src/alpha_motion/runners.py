#!/usr/bin/env python3
"""
Support functions

Copyright (c) 2024 ROX Automation - Jev Kuznetsov
"""

import asyncio
import logging
import os

import coloredlogs

LOG_FORMAT = "%(asctime)s [%(name)s] %(filename)s:%(lineno)d - %(message)s"
TIME_FORMAT = "%H:%M:%S.%f"


def setup_logging() -> None:
    """Setup logging"""
    loglevel = os.environ.get("LOGLEVEL", "INFO").upper()
    coloredlogs.install(level=loglevel, fmt=LOG_FORMAT, datefmt=TIME_FORMAT)
    logging.info(f"Log level set to {loglevel}")


def get_root_exception(exc: BaseException) -> BaseException:
    """Traverse the exception chain to find the root cause."""
    if isinstance(exc, ExceptionGroup):
        # If it's an ExceptionGroup, recursively check its exceptions
        for e in exc.exceptions:
            return get_root_exception(e)
    while exc.__cause__ is not None:
        exc = exc.__cause__
    return exc


def run_main(func, trace_on_exc=False):  # type: ignore
    """
    Convenience function to run either an async coroutine or a regular callable.

    Args:
        func: Either a coroutine or a regular callable to execute

    Returns:
        None
    """
    setup_logging()

    try:
        if asyncio.iscoroutine(func):
            # If it's a coroutine, run it with asyncio
            asyncio.run(func)
        else:
            # If it's a regular callable, just call it
            func()
    except KeyboardInterrupt:
        logging.info("Process interrupted by user")

    except ExceptionGroup as group:
        root_exc = get_root_exception(group)
        logging.error(f"Root cause: {type(root_exc).__name__}: {str(root_exc)}")
    except Exception as e:
        logging.error(e, exc_info=trace_on_exc)
