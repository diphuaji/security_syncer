import logging
import sys
import typing
import more_itertools
import os


DEFAULT_FORMAT = '%(asctime)s %(name)-12s %(levelname)-8s %(message)s'


def add_file_handler(logger: logging.Logger, level: int, path: str, format = DEFAULT_FORMAT):
    handler = logging.FileHandler(path)
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt=format))
    path = os.path.abspath(path)
    if not more_itertools.first_true(logger.handlers, pred=lambda h: type(h)==logging.FileHandler and h.baseFilename==path):
        logger.addHandler(handler)
    return logger


def add_stdout_handler(logger: logging.Logger, level: int, format = DEFAULT_FORMAT) -> logging.Logger:
    handler = logging.StreamHandler()
    handler.setLevel(level)
    handler.setFormatter(logging.Formatter(fmt=format))
    if not more_itertools.first_true(logger.handlers, pred=lambda h: type(h)==logging.StreamHandler):
        logger.addHandler(handler)
    return logger


def set_format_for_handlers(handlers: typing.Iterable[logging.Handler], format: str):
    for handler in handlers:
        handler.setFormatter(logging.Formatter(fmt=format))
