from dataclasses import dataclass
import dataclasses
from typing import Dict


@dataclass
class DataClassMixin:
    def as_dict(self) -> Dict:
        return dataclasses.asdict(self)