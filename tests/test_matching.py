import pytest

import pandas as pd
import numpy as np

import config
import matching


class TestMatching:

    def setup(self):
        t = {"x": [1, 2, 3, 4, 4, 4, 5, 5, 5, 5, 5, 6],
             "y": [0, 20, 19, 0, 1, 1, 0, 0, 1, 1, 2, 1],
             }
        self.df = pd.DataFrame.from_dict(t, dtype=int)


    def test_choose_most_occuring(self):

        result = matching.choose_most_occuring(self.df)
        d = {1: 0, 2: 20, 3: 19, 4: 1, 5: 0, 6: 1}
        goal = pd.Series(data=d, index=[1, 2, 3, 4, 5, 6])
        goal.rename_axis(index="x")
        assert result.equals(goal)
