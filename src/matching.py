"""
this file contains different variants for matching.
Expected is a 2 column pandas Frame
with
with pairs of values (duplicates possible, multi-entries possible);

goal: for every unique entry of the first column, choose 1 from the second
for which a pairing exists, based on some criteria.

"""
import pandas as pd


def choose_first(df: pd.DataFrame) -> pd.Series:
    c1, c2 = df.columns
    df = df.groupby([c1]).apply(lambda x: x.iloc[0])
    result = pd.Series(df[c2])
    result.index = df[c1]
    return result


def choose_last(df: pd.DataFrame) -> pd.Series:
    c1, c2 = df.columns
    df = df.groupby([c1]).apply(lambda x: x.iloc[-1])
    result = pd.Series(df[c2])
    result.index = df[c1]
    return result


def choose_random(df: pd.DataFrame, unweighted=False) -> pd.Series:
    c1, c2 = df.columns

    if unweighted:
        df = df.drop_duplicates()

    df = df.groupby([c1]).apply(pd.DataFrame.sample, n=1)
    result = pd.Series(df[c2])
    result.index = df[c1]
    return result

def choose_most_occuring(df: pd.DataFrame) -> pd.Series:
    """
    for every value of the first column, the value of the right is chosen, which has the most pairs with the former;
    if there are multiple contenders the first is chosen
    :return: a series where index the value of c1 and the entry the value of c2
    """
    c1, c2 = df.columns
    df["n"] = 0
    df = df.groupby([c1, c2]).count()
    df = df.groupby([c1]).apply(lambda f: f["n"].idxmax()[1])
    df.name = c2
    return df


choices = {
    "most": choose_most_occuring,
    "last": choose_last,
    "first": choose_first,
    "random": choose_random,
}

if __name__ == '__main__':
    t = {"x": [1, 2, 3, 4, 4, 4, 5, 5, 5, 5, 5, 6],
         "y": [0, 20, 19, 0, 1, 1, 0, 0, 1, 1, 2, 1],
         }
    t = pd.DataFrame.from_dict(t, dtype=int)
    t = choose_last(t)
    print(t)
