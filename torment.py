import os
import re
import typing as t

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm
import zipfile
import shutil

import config

class HistoryMaker:

    def __init__(self):
        self.definitions = None
        self.province_map = None
        self.histories = None
        self.frames = None
        self.mp4 = None
        self.frame = None
        self.size = None

    def load_mp4(self):
        pass

    def mp4_to_frames(self):
        pass

    def load_frames(self, frame_folder, first_frame_name, *args, **kwargs):

        files = os.listdir(frame_folder)
        current_frame = first_frame_name
        self.frames = []
        self.frame_args = args
        self.frame_kwargs = kwargs

        while True:
            if current_frame in files:
                full_frame_name = os.path.join(frame_folder, current_frame)
                self.frames.append(full_frame_name)
                next_frame = _next_frame(current_frame)
                if next_frame == -1:
                    print("finished with frame: {}".format(current_frame))
                    break
                else:
                    current_frame = next_frame
                    continue
            else:
                print("could not load frame: {}.".format(current_frame))
                break

    def load_frame(self, full_frame_name, resize=None):
        im = Image.open(full_frame_name)
        if resize is not None:
            im = im.resize(resize)
            self.size = None
        self.frame = np.asarray(im)
        return self.frame

    def match_frame_to_map(self, frame: np.ndarray, matching=config.bw_match):
        """
        whatever the case; should produce entries for self.histories
        should add a tag in the appropriate province entries;
        --
        this version simply resizes the frame to the map; uses Image.NEAREST for resizing;
        exact colour => tag
        --
        for every province, simply count which pixelcolour is most prevalent and choose that colour

        :param frame:
        :param matching: a dict that matches a colour to a tag
        :return:
        """
        frame = np.asarray(Image.fromarray(frame).resize(self.size, Image.NEAREST))

        province_map = self.province_map.reshape((self.size[0]*self.size[1], 3))
        frame = frame.reshape((self.size[0]*self.size[1], 3))

        self.pairs = pd.DataFrame({"pcolour":[tuple(x) for x in province_map], "frame": [tuple(x) for x in frame]})
        self.pairs["pcolour"] = self.pairs["pcolour"].astype(str)
        self.pairs = self.pairs.merge(self.definitions, how="inner", on="pcolour")[["province", "frame"]]
        self.pairs["province"] = self.pairs["province"].astype(int)
        self.pairs["n"] = 0
        self.pairs = self.pairs.groupby(["province", "frame"]).count()
        self.pairs = self.pairs.groupby(["province"]).apply(lambda f: f["n"].idxmax()[1]) # get the strongest color for each province
        self.pairs = self.pairs.map(lambda x: (0, 0, 0) if x[0] < 200 else (255, 255, 255))
        self.pairs = self.pairs.astype(str)
        self.pairs = self.pairs.replace(matching)

        if self.histories is None:
            self.histories = [self.pairs]
        else:
            self.histories.append(self.pairs)

    def create_histories(self):
        for full_frame_name in tqdm(self.frames):
            self.match_frame_to_map(self.load_frame(full_frame_name, *self.frame_args, **self.frame_kwargs))
        self.histories = pd.DataFrame(self.histories)

    def export_histories(self, output_file):
        self.histories.to_csv(output_file, **config.export_definitions_kwargs)

    def load_histories(self, histories_file):
        self.histories = pd.read_csv(histories_file, **config.load_definitions_kwargs)


    def apply_histories(self, eusave: str, output_file: str, tmp_dir=config.tmp_dir):
        """
        loads a save file, that is at the start of the game;
        appends province histories of self.histories to all provinces
        in 1 month intervals;

        then sets the actual date 1 month after the last frame

        :param eusave:
        :param output_file: has to end with .eu4
        :param tmp_dir: where to unzip and edit files
        :return:
        """
        if not output_file[-4:] == ".eu4":
            raise Exception("output_file should end with '.eu4'")

        eu = zipfile.ZipFile(eusave)
        eu.extractall(tmp_dir)
        eu.close()

        metaf = open(os.path.join(tmp_dir, "meta"), "r", encoding=config.encoding)
        metat = metaf.read()
        metaf.close()
        gamestatef = open(os.path.join(tmp_dir, "gamestate"), "r", encoding=config.encoding)
        gamestatet = gamestatef.read()
        gamestatef.close()

        start_date = re.search(r"(?<=date=)\d+\.\d+\.\d+", metat).group()
        start_date = ".".join([*start_date.split(".")[:2], "28"])
        end_date = start_date
        for _ in range(self.histories.shape[0]):
            end_date = _increment_date(end_date)

        provinces = [int(p) for p in self.histories.columns]
        self.histories.columns = [int(p) for p in self.histories.columns]
        provinces.sort(reverse=True)

        for p in tqdm(provinces):
            history = self._generate_single_history(self.histories[p], start_date)
            gamestatet = self._insert_history(p, history, gamestatet)
        metat = re.sub(r"(?<=date=)\d+\.\d+\.\d+",end_date, metat)

        self.metat = metat
        self.gamestatet = gamestatet
        with open(os.path.join(tmp_dir, "meta"), "w", config.encoding) as metaf:
            metaf.write(metat)
        with open(os.path.join(tmp_dir, "gamestate"), "w", encoding=config.encoding) as gamestatef:
            gamestatef.write(gamestatet)
        shutil.make_archive(output_file, "zip", tmp_dir)
        os.rename(output_file + ".zip", output_file)

    def load_definitions(self, fname, *args, **kwargs):

        self.definitions = pd.read_csv(fname, *args, **kwargs)
        self.definitions["pcolour"] = self.definitions[["red", "green", "blue"]].apply(lambda x: str((x["red"], x["green"], x["blue"])), axis=1)
        self.definitions = self.definitions[["province", "pcolour"]]

    def load_province_map(self, fname, resize=None):
        im = Image.open(fname)
        if resize is not None:
            im = im.resize(resize, Image.NEAREST)
            self.size = resize
        self.province_map = np.asarray(im)

    def redefine(self, output_file, reload_def=True):
        assert self.definitions is not None and self.province_map is not None
        # province_in_crop = pd.DataFrame(self.definitions["province"])
        # province_in_crop["n"] = [0 for _ in range(len(province_in_crop))]

        existing_provinces = set()

        for x in tqdm(self.province_map):
            for colour in x:
                t = self.definitions[(self.definitions["red"] == colour[0]) &
                                     (self.definitions["green"] == colour[1]) &
                                     (self.definitions["blue"] == colour[2])]
                if len(t) == 1:
                    existing_provinces.add(t.iloc[0]["province"])

        self.existing_provinces = existing_provinces
        new_def: pd.DataFrame = self.definitions[self.definitions["province"].isin(existing_provinces)]
        if output_file is not None:
            new_def.to_csv(output_file, **config.export_definitions_kwargs)
        if reload_def:
            self.load_definitions(output_file, **config.load_definitions_kwargs)

    def _generate_single_history(self, ownership_history, start_date) -> str:

        date = start_date
        history = ""
        for tag in ownership_history:
            history = history + config.history_insert.format(date=date, tag=tag)
            date = _increment_date(date)
        return history

    def _insert_history(self, p:int, history:str, gamestate:str)-> str:
        query = r"(?<=-{}=){{".format(p)
        start_pos = re.search(query, gamestate).span()[0]
        end_pos = start_pos + _find_closing_bracket(gamestate[start_pos:])
        return gamestate[:end_pos] + history + gamestate[end_pos:]

def _next_frame(current_frame):
    cfname, ext = os.path.splitext(current_frame)
    if re.fullmatch(r"[\d\D]*\D\d*", cfname):
        return re.sub(r"(?<=\D)\d*$", _increment, cfname) + ext
    else:
        return -1


def _increment(fnumber: t.Union[re.Match, str]):
    fnumber = fnumber.group(0) if isinstance(fnumber, re.Match) else fnumber
    return "1" if fnumber == "" else str(int(fnumber) + 1)

def _get_hre_members(province_history_path, output_file):

    files = os.listdir(province_history_path)
    current_file = "1.txt"
    hre_provinces = set()

    while True:
        if current_file in files:
            with open(os.path.join(province_history_path, current_file)) as f:
                text = f.read()
            if re.search(r"hre\s*=\s*yes", text):
                print("hre member: {}".format(current_file))
                hre_provinces.add(int(current_file.split(".")[0]))
            next_file = _next_province_history(current_file)
            if next_file in files:
                current_file = next_file
                continue
            else:
                pd.DataFrame(hre_provinces).to_csv(output_file, **config.export_definitions_kwargs)
                print("finished")
                break

        else:
            print("could not find file: {}".format(current_file))

def _next_province_history(ph):
    cfname, ext = os.path.splitext(ph)
    if re.fullmatch(r"\d+$", cfname):
        return re.sub(r"\d+$", _increment, cfname) + ext
    else:
        return -1

def _increment_date(date:str):
    assert re.fullmatch(r"\d+\.\d+\.\d+", date), date
    y, m, d = date.split(".")
    if m == "12":
        y = str(int(y) + 1)
        m = "1"
    else:
        m = str(int(m) + 1)
    return ".".join([y, m, d])

def _find_span_in_game_state():
    pass

def _find_closing_bracket(text, bracket="{"):
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

x = None
def main():
    global x
    x = HistoryMaker()
    x.load_definitions(config.definitions_path, **config.load_definitions_kwargs)
    x.load_province_map(config.test_province_map_path, resize=(75, 100))
    x.redefine(output_file=r"C:\Grand Archives\shitty projects\eu4-renderer\resources\xd.csv")

def hre():
    _get_hre_members(config.province_history_path, r"C:\Grand Archives\shitty projects\eu4-renderer\resources\voltaires_nightmare_hremembers.csv")

def matcher():
    global x
    x = HistoryMaker()
    x.load_frames(r"C:\Grand Archives\shitty projects\eu4-renderer\resources\bad_apple_frames", "frame1.jpg")
    x.load_definitions(config.definitions_path, **config.load_definitions_kwargs)
    x.load_province_map(config.test_province_map_path, resize=(45, 60))
    x.create_histories()
    x.export_histories(r"C:\Grand Archives\shitty projects\eu4-renderer\resources\ba_histories.csv")

def load_history():
    global x
    x = HistoryMaker()
    x.load_histories(r"C:\Grand Archives\shitty projects\eu4-renderer\resources\ba_histories.csv")

def apply_history():
    global x
    x = HistoryMaker()
    x.load_histories(r"C:\Grand Archives\shitty projects\eu4-renderer\resources\ba_histories.csv")
    x.apply_histories(config.test_eu4_save, r"C:\Grand Archives\shitty projects\eu4-renderer\resources\bad_apple.eu4")

if __name__ == "__main__":
    apply_history()


# t = np.unique(x.province_map.reshape(-1, x.province_map.shape[2]), axis=0)
#voltaires nightmare: total unique colors: 7294
#voltaires nightmare: definitions length: 7299