import os
import re
import typing as t

import config


def find_closing_bracket(text, bracket="{"):
    """
    given a text; the first time a brackets opens; will return the index of the balancing parenthesis
    :param text: str
    :bracket text: either "[", "{", "("
    :return: index:int
    """
    assert bracket in config.brackets.keys()
    bracket_c = 0
    started_looking = False
    for i, char in enumerate(text):
        if char == bracket:
            started_looking = True
            bracket_c += 1
        elif char == config.brackets[bracket]:
            bracket_c -= 1
        if bracket_c == 0 and started_looking:
            return i
    raise Exception("Could not find a matching closing bracket!")


def next_frame(current_frame):
    cfname, ext = os.path.splitext(current_frame)
    if re.fullmatch(r"[\d\D]*\D\d*", cfname):
        return re.sub(r"(?<=\D)\d*$", increment, cfname) + ext
    else:
        return -1


def increment(fnumber: t.Union[re.Match, str]):
    fnumber = fnumber.group(0) if isinstance(fnumber, re.Match) else fnumber
    return "1" if fnumber == "" else str(int(fnumber) + 1)


def increment_date(date:str):
    assert re.fullmatch(r"\d+\.\d+\.\d+", date), date
    y, m, d = date.split(".")
    if m == "12":
        y = str(int(y) + 1)
        m = "1"
    else:
        m = str(int(m) + 1)
    return ".".join([y, m, d])


def interpolate_colour(colour, available_values: t.Iterable, mode: str="closest"):
    """
    :param colour:
    :param available_values:
    :param mode: "lower", "upper", "closest"
    :return:
    """
    new_colour = []
    for c in colour:
        if mode.lower() == "lower":
            new_colour.append(_lower_neighbour(c, available_values))
        elif mode.lower() == "upper":
            new_colour.append(_upper_neighbour(c, available_values))
        elif mode.lower() == "closest":
            new_colour.append(_closest_neighbour(c, available_values))
        else:
            raise ValueError("mode should be 'lower', 'upper' or 'closest'")

    return tuple(new_colour)


def _lower_neighbour(value, iterable):
    iterable = sorted(iterable, reverse=True)
    for i in iterable:
        if i < value:
            return i
    return iterable[-1]

def _upper_neighbour(value, iterable):
    iterable = sorted(iterable)
    for i in iterable:
        if i > value:
            return i
    return iterable[-1]

def _closest_neighbour(value, iterable):
    iterable = sorted(iterable)  # is a list, after operation

    min_dist = abs(value - iterable[0])
    closest = iterable[0]
    for i in iterable[1:]:
        tmp = abs(value - i)
        if tmp < min_dist:
            min_dist = tmp
            closest = i
        else:
            return closest
    return closest
