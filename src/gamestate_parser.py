import src.config as config

import pandas as pd
import numpy as np
import collections
import os

import typing as t


class GameStateParser():
    def __init__(self):
        pass

    def load_gamestate(self, gamestate: str) -> t.NoReturn:

        if os.path.isfile(gamestate):
            with open(gamestate, "r", encoding=config.encoding) as f:
                gamestate = f.read()

        self.gamestate = gamestate

    def save_gamestate(self, out: str)-> t.NoReturn:
        pass

    def parse_gamestate(self) -> t.NoReturn:

        assert self.gamestate is not None, "Error, gamestate was not loaded yet"