import typing as t
import random

from labyrinth.labyrinth import Labyrinth
from .base_strategy import Strategy
from .common import find_free_place, measured


class DumbStrategy(Strategy):
    NAME = 'DUMB'

    pacman: t.Tuple[int, int]

    def setup(self, labyrinth: Labyrinth) -> t.Dict[str, t.Any]:
        super(DumbStrategy, self).setup(labyrinth)
        self.pacman = find_free_place(self.labyrinth)
        return dict(pacman=self.pacman)

    @measured
    def next_step(self) -> t.Dict[str, t.Any]:
        self.pacman = random.choice(list(self.labyrinth.edges[self.pacman]))
        return dict(pacman=self.pacman)
