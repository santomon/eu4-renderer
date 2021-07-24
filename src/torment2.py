from PIL import Image
import numpy as np
import pandas as pd
from tqdm import tqdm

import os
import zipfile
import re
import shutil

from src import torment
import src.util as util
import src.config as config
import src.matching as province_to_colour_matching


class HistoryMaker2(torment.HistoryMaker):
    """
    New HistoryMaker; instead of choosing tags and changing ownership:

    idea: add as many new tags as there are provinces: change province ownership to one of these each;
    change colour of the tag to the colour of the pixel at that position
    """

    # override
    def load_frame(self, full_frame_name, resize=None):
        im: Image.Image = Image.open(full_frame_name)
        im = im.convert("RGB")
        im = im.quantize(palette=self.palette, dither=0, colors=self.ncolours)
        im = im.convert("RGB")
        if resize is not None:
            im = im.resize(resize)
            self.size = None

        self.frame = np.asarray(im)
        return self.frame

    def make_palette(self):

        if self.colouring == "bw":
            palette_img = Image.fromarray(config.bws)
            self.palette = palette_img.quantize(palette=Image.WEB, dither=0, colors=2)
        elif self.colouring == "grays":
            palette_img = Image.fromarray(config.grays)
            self.palette = palette_img.quantize(palette=Image.WEB, dither=0, colors=self.ncolours)
        elif self.colouring == "simple":
            palette_img = Image.fromarray(config.simple_colours)
            self.palette = palette_img.quantize(palette=Image.WEB, dither=0, colors=self.ncolours)
        elif self.colouring == "infer":
            # currently only infers from the first frame;
            palette_img = Image.open(self.frames[0]).convert("RGB")
            self.palette = palette_img.quantize(palette=Image.WEB, dither=0, colors=self.ncolours)
        else:
            raise ValueError("colouring method not understood; has to be one of {}, but it is {}".format(config.colouring_choices, self.colouring))

    # override
    def _create_histories(self):
        for full_frame_name in tqdm(self.frames, desc="Matching Pixel to Province"):
            self.match_frame_to_map2(self.load_frame(full_frame_name, *self.frame_args, **self.frame_kwargs),
                                     cmatching=self.colour_matching,
                                     pmatching=self.ptp)
        self.histories = pd.DataFrame(self.histories)


    # override
    def match(self):
        self.load_frames(self.input, self.f1_name)
        self.make_palette()

        colours = util.get_colours_from_palette(self.palette)
        tags = util.get_n_tags(self.get_available_tags_from_save(eusave=self.eu4, tmp_dir=self.tmp_dir),len(colours), config.desired_tags)
        self.colour_matching = util.combine_tags_colours(tags, colours)

        self._create_histories()
        self._export_histories(os.path.join(self.tmp_dir, config.histories_name))

    def get_available_tags_from_save(self, eusave=None, tmp_dir=config.tmp_dir):
        eu = zipfile.ZipFile(eusave)
        eu_save_dir = os.path.abspath(os.path.join(tmp_dir, config.eu_extract))
        eu.extractall(eu_save_dir)
        eu.close()

        with open(os.path.join(eu_save_dir, "gamestate"), "r", encoding=config.encoding) as f:
            gamestatet = f.read()

        return util.get_available_tags(gamestatet)

    # override
    def _apply_histories(self, eusave: str, output_file: str, offset_date, tmp_dir=config.tmp_dir, *args, **kwargs):

        eu = zipfile.ZipFile(eusave)
        eu_save_dir = os.path.abspath(os.path.join(tmp_dir, config.eu_extract))
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
        gamestatet = util.insert_mapcolours_into_gamestate(gamestatet, start_date, self.colour_matching)
        for _ in range(offset_date[0]):
            start_date = util.increment_date(start_date)
        end_date = start_date
        for _ in range(self.histories.shape[0] + offset_date[1]):
            end_date = util.increment_date(end_date)

        provinces = [int(p) for p in self.histories.columns]
        self.histories.columns = [int(p) for p in self.histories.columns]
        provinces.sort(reverse=True)

        for p in tqdm(provinces, desc="writing history"):
            history = self._generate_single_history(self.histories[p], start_date)
            gamestatet = self._insert_history(p, history, gamestatet, *args, **kwargs)
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


    def match_frame_to_map2(self, frame: np.ndarray, cmatching=config.bw_match, pmatching="first"):

        frame = np.asarray(Image.fromarray(frame).resize(self.size, Image.NEAREST))

        province_map = self.province_map.reshape((self.size[0] * self.size[1], 3))
        frame = frame.reshape((self.size[0] * self.size[1], 3))

        self.pairs = pd.DataFrame({"pcolour": [tuple(x) for x in province_map], "frame": [tuple(x) for x in frame]})
        self.pairs["pcolour"] = self.pairs["pcolour"].astype(str)
        self.pairs = self.pairs.merge(self.definitions, how="inner", on="pcolour")[
            ["province", "frame"]]  # slow i think
        self.pairs["province"] = self.pairs["province"].astype(int)

        self.pairs = province_to_colour_matching.choices[pmatching](self.pairs)

        self.pairs = self.pairs.astype(str)
        self.pairs = self.pairs.replace(cmatching)

        if self.histories is None:
            self.histories = [self.pairs]
        else:
            self.histories.append(self.pairs)