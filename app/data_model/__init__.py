import typing
from dataclasses import dataclass


@dataclass
class Security:
    ticker: str
    exchange: str
    name: str = ''


# todo
class Quote(typing.NamedTuple):
    ticker: str
    exchange: str

