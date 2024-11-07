#!/usr/bin/env python3
import logging
import time
from typing import Any, Callable


class Timer:
    """Timer class, including timeout"""

    def __init__(self, timeout: float) -> None:
        self.timeout = timeout
        self.start_time = time.time()

    def is_timeout(self) -> bool:
        """Check if timeout has expired"""
        return time.time() - self.start_time > self.timeout

    def reset(self) -> None:
        """Reset timer"""
        self.start_time = time.time()

    def elapsed(self) -> float:
        """Return elapsed time since timer was started"""
        return time.time() - self.start_time


def log_call(log_params: bool = False) -> Callable[[Any], Any]:
    """log class function call"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            class_name = (
                args[0].__class__.__name__
                if args and hasattr(args[0], "__class__")
                else ""
            )
            if log_params:
                # Exclude the first argument if it is 'self'
                parameters = list(args[1:]) + [f"{k}={v}" for k, v in kwargs.items()]
                parameter_str = ", ".join([str(param) for param in parameters])
                logging.debug(
                    f"calling {class_name}.{func.__name__} with parameters: {parameter_str}"
                )
            else:
                logging.debug(f"calling {class_name}.{func.__name__}")
            return func(*args, **kwargs)

        return wrapper

    return decorator
