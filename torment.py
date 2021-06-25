import os
import re
import shutil
import zipfile

import numpy as np
import pandas as pd
from PIL import Image
from tqdm import tqdm

import config
from hre import _get_hre_members
import util
import matching as province_to_colour_matching


class HistoryMaker:

    def __init__(self):
        self.definitions = None
        self.province_map = None
        self.histories = None
        self.frames = None
        self.mp4 = None
        self.frame = None
        self.pairs = None
        self.frame_kwargs = None
        self.frame_args = None
        self.p_path = None
        self.eu4 = None
        self.d_path = None

        self.crop = None
        self.size = None
        self.resize = None

        self.input = None
        self.output = None
        self.tmp_dir = None
        self.f1_name = None

    def fake_construct(self,
                       _input,
                       output,
                       tmp_dir,
                       mod_dir,
                       eu4,
                       definition,
                       pbmp,
                       crop,
                       redefine=False,
                       resize=None,
                       f1=None,
                       ):
        if os.path.isfile(os.path.abspath(definition)):
            self.d_path = os.path.abspath(definition)
        else:
            self.d_path = os.path.abspath(os.path.join(mod_dir, config.default_definition))

        if os.path.isfile(os.path.abspath(pbmp)):
            self.p_path = os.path.abspath(pbmp)
        else:
            self.p_path = os.path.abspath(os.path.join(mod_dir, config.default_provincesbmp))

        self.eu4 = os.path.abspath(eu4)

        self.definitions = None
        self.province_map = None

        self._load_definitions(self.d_path, **config.load_csv_kwargs)
        self._load_province_map(self.p_path, crop=crop, resize=resize)

        if redefine:
            self.d_path = os.path.abspath(os.path.join(tmp_dir, "redefinition.csv"))
            self.redefine(self.d_path)

        self.histories = None
        self.frames = None
        self.mp4 = None
        self.frame = None

        self.crop = crop
        self.size = (self.province_map.shape[1], self.province_map.shape[0])

        self.pairs = None
        self.frame_kwargs = None
        self.frame_args = None

        self.input = os.path.abspath(_input)
        self.output = os.path.abspath(output)
        self.tmp_dir = os.path.abspath(tmp_dir)

        if not os.path.isdir(self.tmp_dir):
            os.makedirs(self.tmp_dir)
        self.f1_name = f1

    def load_mp4(self):
        pass

    def mp4_to_frames(self):
        pass

    def match(self):
        self.load_frames(self.input, self.f1_name)
        self._create_histories()
        self._export_histories(os.path.join(self.tmp_dir, config.histories_name))

    def make_history(self, eu4: str = None, output: str = None):

        if eu4 is None:
            eu4 = self.eu4
        if output is None:
            output = self.output

        if self.histories is None:
            self._load_histories(os.path.join(self.tmp_dir, config.histories_name))
        self._apply_histories(eu4, output)

    def load_frames(self, _input, first_frame_name, *args, **kwargs):

        if not os.path.isdir(_input):
            raise NotImplementedError("currently only directories of frames supported!")
        files = os.listdir(_input)
        current_frame = first_frame_name
        self.frames = []
        self.frame_args = args
        self.frame_kwargs = kwargs

        while True:
            if current_frame in files:
                full_frame_name = os.path.join(_input, current_frame)
                self.frames.append(full_frame_name)
                next_frame = util.next_frame(current_frame)
                if next_frame in files:
                    current_frame = next_frame
                    continue
                else:
                    print("finished with frame: {}".format(current_frame))
                    break

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

    def match_frame_to_map(self, frame: np.ndarray, matching=config.bw_match, av_cvalues=config.bw_values):
        """
        whatever the case; should produce entries for self.histories
        should add a tag in the appropriate province entries;
        --
        this version simply resizes the frame to the map; uses Image.NEAREST for resizing;
        exact colour => tag
        --
        for every province, simply count which pixelcolour is most prevalent and choose that colour

        :param av_cvalues:
        :param frame:
        :param matching: a dict that matches a colour to a tag
        :return:
        """
        frame = np.asarray(Image.fromarray(frame).resize(self.size, Image.NEAREST))

        province_map = self.province_map.reshape((self.size[0] * self.size[1], 3))
        frame = frame.reshape((self.size[0] * self.size[1], 3))

        self.pairs = pd.DataFrame({"pcolour": [tuple(x) for x in province_map], "frame": [tuple(x) for x in frame]})
        self.pairs["pcolour"] = self.pairs["pcolour"].astype(str)
        self.pairs = self.pairs.merge(self.definitions, how="inner", on="pcolour")[["province", "frame"]]
        self.pairs["province"] = self.pairs["province"].astype(int)

        self.pairs = province_to_colour_matching.choose_most_occuring(self.pairs)
        self.pairs = self.pairs.map(lambda x: util.interpolate_colour(x, av_cvalues))

        self.pairs = self.pairs.astype(str)
        self.pairs = self.pairs.replace(matching)

        if self.histories is None:
            self.histories = [self.pairs]
        else:
            self.histories.append(self.pairs)

    def _create_histories(self):
        for full_frame_name in tqdm(self.frames):
            self.match_frame_to_map(self.load_frame(full_frame_name, *self.frame_args, **self.frame_kwargs))
        self.histories = pd.DataFrame(self.histories)

    def _export_histories(self, output_file):
        self.histories.to_csv(output_file, **config.export_csv_kwargs)

    def _load_histories(self, histories_file):
        self.histories = pd.read_csv(histories_file, **config.load_csv_kwargs)

    def _apply_histories(self, eusave: str, output_file: str, tmp_dir=config.tmp_dir):
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
        eu_save_dir = os.path.join(tmp_dir, config.eu_extract)
        eu.extractall(eu_save_dir)
        eu.close()

        metaf = open(os.path.join(eu_save_dir, "meta"), "r", encoding=config.encoding)
        metat = metaf.read()
        metaf.close()
        gamestatef = open(os.path.join(eu_save_dir, "gamestate"), "r", encoding=config.encoding)
        gamestatet = gamestatef.read()
        gamestatef.close()

        start_date = re.search(r"(?<=date=)\d+\.\d+\.\d+", metat).group()
        start_date = ".".join([*start_date.split(".")[:2], "28"])
        end_date = start_date
        for _ in range(self.histories.shape[0]):
            end_date = util.increment_date(end_date)

        provinces = [int(p) for p in self.histories.columns]
        self.histories.columns = [int(p) for p in self.histories.columns]
        provinces.sort(reverse=True)

        for p in tqdm(provinces):
            history = self._generate_single_history(self.histories[p], start_date)
            gamestatet = self._insert_history(p, history, gamestatet)
        metat = re.sub(r"(?<=date=)\d+\.\d+\.\d+", end_date, metat)

        self.metat = metat
        self.gamestatet = gamestatet
        with open(os.path.join(eu_save_dir, "meta"), "w", encoding=config.encoding) as metaf:
            metaf.write(metat)
        with open(os.path.join(eu_save_dir, "gamestate"), "w", encoding=config.encoding) as gamestatef:
            gamestatef.write(gamestatet)
        shutil.make_archive(output_file, "zip", eu_save_dir)

        if os.path.isfile(output_file):
            os.remove(output_file)
        os.rename(output_file + ".zip", output_file)

    def redefine(self, output_file, reload_def=True):
        assert self.definitions is not None and self.province_map is not None

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
            new_def.to_csv(output_file, **config.export_csv_kwargs)
        if reload_def:
            self._load_definitions(output_file, **config.load_csv_kwargs)

    def _load_definitions(self, fname, *args, **kwargs):

        self.definitions = pd.read_csv(fname, *args, **kwargs)
        self.definitions["pcolour"] = self.definitions[["red", "green", "blue"]].apply(
            lambda x: str((x["red"], x["green"], x["blue"])), axis=1)
        self.definitions = self.definitions[["province", "pcolour"]]

    def _load_province_map(self, fname, crop, resize=None):
        im = Image.open(fname)

        if crop is not None:
            im = im.crop(crop)

        if resize is not None:
            im = im.resize(resize, Image.NEAREST)
            self.size = resize
        self.province_map = np.asarray(im)

    def _generate_single_history(self, ownership_history, start_date) -> str:

        date = start_date
        history = ""
        for tag in ownership_history:
            history = history + config.history_insert.format(date=date, tag=tag)
            date = util.increment_date(date)
        return history

    def _insert_history(self, p: int, history: str, gamestate: str) -> str:
        query = r"(?<=-{}=){{".format(p)
        start_pos = re.search(query, gamestate).span()[0]
        end_pos = start_pos + util.find_closing_bracket(gamestate[start_pos:])

        new_string = gamestate[start_pos:end_pos]
        query = r"(?<=history=){"
        start_inner = re.search(query, new_string).span()[0]
        end_inner = start_inner + util.find_closing_bracket(new_string[start_inner:])
        new_string = new_string[:end_inner] + history + new_string[end_inner:]

        return gamestate[:start_pos] + new_string + gamestate[end_pos:]

if __name__ == "__main__":
    pass

# voltaires nightmare: total unique colors: 7294
# voltaires nightmare: definitions length: 7299
