import os

import torment
import config

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
        self.hm.load_definitions(self.test_definition_file, **config.load_definitions_kwargs)


