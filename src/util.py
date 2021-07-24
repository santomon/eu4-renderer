import os
import re
import typing as t

import PIL.Image as Image
import pandas as pd

from src import config


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

def get_available_tags(gamestate: str):
    """
    also checks, if they have a history attached to them;
    :param palette_img:
    :return:
    """

    countries_pos_query = r"(?<!_countries=)(?<=countries=){"
    tags_query = r"(?<=\n\t)\S\S\S(?=={)"

    start_pos = re.search(countries_pos_query, gamestate).span()[0]
    end_pos = start_pos + find_closing_bracket(gamestate[start_pos:])
    return [tag for tag in re.findall(tags_query, gamestate[start_pos:end_pos]) if tag not in config.ineligible_tags]


def get_n_tags(tags: t.List[str], n, desired_tags):

    assert n <= len(tags), "number of tags needed has to be lower than total number of available tags!"
    priority_tags = [tag for i, tag in enumerate(tags) if tag in desired_tags and i < n]
    return priority_tags + [tag for tag in tags if tag not in priority_tags][:n-len(priority_tags)]


def combine_tags_colours(tags: t.List[str], colours: t.List) -> t.Dict[str, str]:
    assert len(tags) >= len(colours), "There need to be more tags than colours"
    result = {colour: tag for tag, colour in zip(tags, colours)}
    return result

def get_colours_from_palette(palette_img: Image.Image):

    if palette_img.mode == "P":
        palette_img = palette_img.convert("RGB")
    try:
        c = [str((r, g, b)) for (encoding, (r, g, b)) in palette_img.getcolors()]
    except TypeError:
        c = [str((r, g, b)) for (r, g, b) in palette_img.getcolors()]
    b = str((0, 0, 0))
    if not b in c:
        c.insert(0, b)
    return c


def insert_mapcolours_into_gamestate(gamestate: str, start_date: str, colour_matching: t.Dict[str, str]) -> str:
    # oke

    countries_pos_query = r"(?<!_countries=)(?<=countries=){"
    tags_query = r"(?<=\n\t){tag}(?=={{)"
    history_query = r"(?<=history=){"

    start_pos = re.search(countries_pos_query, gamestate).span()[0]
    end_pos = start_pos + find_closing_bracket(gamestate[start_pos:])

    countries_txt = gamestate[start_pos: end_pos]

    for colour, tag in colour_matching.items():
        tag_start = re.search(tags_query.format(tag=tag), countries_txt).span()[0]
        history_start = tag_start + re.search(history_query, countries_txt[tag_start:]).span()[0]
        history_end = history_start + find_closing_bracket(countries_txt[history_start:])
        insert = config.mapcolour_fragment.format(
            date=start_date,
            colour=" ".join(re.findall(r"\d+", colour))
        )

        countries_txt = countries_txt[:history_end] + insert + countries_txt[history_end:]

    return gamestate[:start_pos] + countries_txt + gamestate[end_pos:]


if __name__ == '__main__':
    c_matching = {(0, 0, 0): "SWE"}

    gamestatef = open(os.path.join(r"C:\Grand Archives\shitty projects\eu4-renderer\resources\tmp\save", "gamestate"), "r", encoding=config.encoding)
    gamestatet = gamestatef.read()
    gamestatef.close()
    u = get_available_tags(gamestatet)
    # v = get_n_tags(u, config.ncolours, config.desired_tags)
