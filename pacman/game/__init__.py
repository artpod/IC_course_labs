import typing as t
from game.game import Game
from labyrinth.labyrinth import Labyrinth

game: t.Optional[Game] = None


def init(**kwargs):
    global game
    game = Game(**kwargs)


def start():
    game.mainloop()
