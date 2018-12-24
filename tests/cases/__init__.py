from dataclasses import dataclass
from typing import Tuple, Iterable, List


@dataclass
class Region:
    a: int = 0
    b: int = 0


Symbols = Iterable[Tuple[Region, str]]


class Selection(Region):
    """
    Represents the Region a mouse has clicked on the View
    """

    def __init__(self, x: int) -> None:
        self.a = self.b = x


class View():
    def __init__(self, sel_region: Region, symbols: Symbols, syntax_path: str = '') -> None:
        self._symbols = symbols
        self._sel_region = sel_region
        self._syntax_path = syntax_path
        self.ignored_packages: List = []

    def sel(self):
        return [self._sel_region]

    def settings(self):
        return {
            'syntax': self._syntax_path,
            'ignored_packages': self.ignored_packages,
        }

    def symbols(self):
        return self._symbols
