import os

import torment
import config
import util
import hre

class TestTorment:

    def setup(self):
        self.hm = torment.HistoryMaker()
        self.test_first_frame = r"frame40.jpg"
        self.test_frame_folder = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\test"
        self.test_definition_file = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\voltaires_nightmare_definition.csv"
        self.test_province_map_file = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\voltaires_nightmare_provinces.bmp"

    def test_load_frame(self):
        self.hm.load_frame(os.path.join(self.test_frame_folder, self.test_first_frame))

    def test_load_frames(self):
        self.hm.load_frames(self.test_frame_folder, self.test_first_frame)
        assert len(self.hm.frames) == len(os.listdir(self.test_frame_folder))  # as long as no other files are there...

    def test_load_definitions(self):
        self.hm._load_definitions(self.test_definition_file, **config.load_csv_kwargs)


class TestUtil:

    def setup(self):
        self.iterable = [3, 4, 7, 10, 1]
        self.colour = (21, 76, 101)
        self.available_colours = config._simple_coloursteps

    def test_closest_neighbour(self):
        assert util._closest_neighbour(-2, self.iterable) == 1
        assert util._closest_neighbour(24, self.iterable) == 10
        assert util._closest_neighbour(6, self.iterable) == 7
        assert util._closest_neighbour(8, self.iterable) == 7

    def test_upper_neighbour(self):
        assert util._upper_neighbour(15,  self.iterable) == 10
        assert util._upper_neighbour(6, self.iterable) == 7
        assert util._upper_neighbour(-1, self.iterable) == 1

    def test_lower_neighbour(self):
        assert util._lower_neighbour(-1, self.iterable) == 1
        assert util._lower_neighbour(100, self.iterable) == 10
        assert util._lower_neighbour(6, self.iterable) == 4

    def test_interpolate_colour(self):
        assert util.interpolate_colour(self.colour, self.available_colours) == (0, 51, 102)