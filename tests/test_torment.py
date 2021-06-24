import pytest
import torment

class TestTorment:

    def setup(self):
        self.hm = torment.HistoryMaker()

    def test_load_frames(self):
        self.hm.load_frame(r"C:\Grand Archives\shitty projects\eu4-renderer\resources\test\frame40.jpg")