import os
import re
import typing as t

import pandas as pd

from src import config
from src.util import increment
import src.util as util


def _get_hre_members(province_history_path, output_file):
    files = os.listdir(province_history_path)
    current_file = "1.txt"
    hre_provinces = set()

    while True:
        if current_file in files:
            with open(os.path.join(province_history_path, current_file)) as f:
                text = f.read()
            if re.search(r"(?<=\n)hre\s*=\s*yes", text):
                print("hre member: {}".format(current_file))
                hre_provinces.add(int(current_file.split(".")[0]))
            next_file = _next_province_history(current_file)
            if next_file in files:
                current_file = next_file
                continue
            else:
                pd.DataFrame(hre_provinces).to_csv(output_file, **config.export_csv_kwargs)
                print("finished")
                break

        else:
            print("could not find file: {}".format(current_file))


def _next_province_history(ph):
    cfname, ext = os.path.splitext(ph)
    if re.fullmatch(r"\d+$", cfname):
        return re.sub(r"\d+$", increment, cfname) + ext
    else:
        return -1


