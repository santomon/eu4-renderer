import os
import re
import typing as t

from PIL import Image
import numpy as np
import pandas as pd

import config


class HistoryMaker():

	def __init__(self):
		self.definitions = None
		self.province_map = None
		self.histories = None
		self.frames = None
		self.mp4 = None

		pass

	def load_mp4(self):
		pass

	def mp4_to_frames(self):
		pass

	def load_frames(self, frame_folder, first_frame_name, bw: bool=False):

		files = os.listdir(frame_folder)
		current_frame = first_frame_name
		self.frames = []

		while True:
			if current_frame in files:
				full_frame_name = os.path.join(frame_folder, current_frame)
				self.frames.append(self.load_frame(full_frame_name))
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


	def load_frame(self, full_frame_name):
		self.frame = np.asarray(Image.open(full_frame_name))

		return self.frame
	def load_definitions(self, fname, *args, **kwargs):

		self.definitions = pd.read_csv(fname, *args, **kwargs)

	def load_province_map(self, fname):
		self.province_map = Image.open(fname)


def _next_frame(current_frame):
	cfname, ext = os.path.splitext(current_frame)
	if re.fullmatch(r"[\d\D]*\D\d*", cfname):
		print(cfname)
		return re.sub(r"(?<=\D)\d*$", _increment, cfname) + ext
	else:
		return -1


def _increment(fnumber: t.Union[re.Match, str]):
	fnumber = fnumber.group(0) if isinstance(fnumber, re.Match) else fnumber
	return "0" if fnumber == "" else str(int(fnumber) + 1)



if __name__ == "__main__":
	test_load_frame()