"""Shared logging configuration and helpers.

Usage:
    from card_scraper.logging_utils import setup_logging, log_call

    setup_logging(level="DEBUG", log_file="scraper.log")

    @log_call()
    def fetch(url): ...
"""

from __future__ import annotations

import functools
import logging
import logging.handlers
from pathlib import Path
from typing import Callable, Optional, Union

DEFAULT_FORMAT = "%(asctime)s [%(levelname)s] %(name)s: %(message)s"
DEFAULT_DATEFMT = "%Y-%m-%d %H:%M:%S"

_configured = False


def setup_logging(
    level: Union[int, str] = logging.INFO,
    log_file: Optional[Union[str, Path]] = None,
    fmt: str = DEFAULT_FORMAT,
    datefmt: str = DEFAULT_DATEFMT,
    console: bool = True,
    max_bytes: int = 1_000_000,
    backup_count: int = 3,
    force: bool = False,
) -> logging.Logger:
    """Configure the root logger.

    Call this once at program start (e.g. in ``main.py``). Subsequent calls
    are no-ops unless ``force=True``.

    Args:
        level: Logging level (e.g. ``logging.DEBUG`` or ``"DEBUG"``).
        log_file: Optional path for a rotating file handler.
        fmt: Log message format string.
        datefmt: Date format string.
        console: If True, attach a stream handler to stderr.
        max_bytes: Rotation size for the file handler.
        backup_count: Number of rotated files to keep.
        force: Re-configure even if already configured.

    Returns:
        The configured root logger.
    """
    global _configured
    root = logging.getLogger()

    if _configured and not force:
        return root

    # Clear any pre-existing handlers so repeated configuration is predictable.
    for h in list(root.handlers):
        root.removeHandler(h)

    if isinstance(level, str):
        level = level.upper()
    root.setLevel(level)

    formatter = logging.Formatter(fmt=fmt, datefmt=datefmt)

    if console:
        stream = logging.StreamHandler()
        stream.setFormatter(formatter)
        root.addHandler(stream)

    if log_file is not None:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.handlers.RotatingFileHandler(
            log_path, maxBytes=max_bytes, backupCount=backup_count, encoding="utf-8"
        )
        file_handler.setFormatter(formatter)
        root.addHandler(file_handler)

    _configured = True
    return root


def log_call(
    level: int = logging.DEBUG,
    log_args: bool = True,
    log_return: bool = True,
    logger: Optional[logging.Logger] = None,
) -> Callable:
    """Decorator that logs function calls, arguments, and return values.

    Exceptions are logged with a traceback at ERROR level and re-raised.

    Args:
        level: Level used for call/return messages.
        log_args: Include positional and keyword arguments in the call log.
        log_return: Include the return value in the return log.
        logger: Logger to use. Defaults to one named after the wrapped
            function's module.
    """

    def decorator(func: Callable) -> Callable:
        log = logger or logging.getLogger(func.__module__)
        qualname = func.__qualname__

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if log_args:
                log.log(level, "CALL %s args=%r kwargs=%r", qualname, args, kwargs)
            else:
                log.log(level, "CALL %s", qualname)
            try:
                result = func(*args, **kwargs)
            except Exception:
                log.exception("RAISE %s", qualname)
                raise
            if log_return:
                log.log(level, "RETURN %s -> %r", qualname, result)
            else:
                log.log(level, "RETURN %s", qualname)
            return result

        return wrapper

    return decorator
