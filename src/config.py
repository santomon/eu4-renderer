import os
import itertools

import numpy as np

encoding = "ISO-8859-1"
default_definition = os.path.abspath("map/definition.csv")
default_provincesbmp = os.path.abspath("map/provinces.bmp")

histories_name = "histories.csv"

load_csv_kwargs = {
    "encoding": encoding,
    "sep": ";",
    "dtype": {"province": int}
}
export_csv_kwargs = {
    "encoding": encoding,
    "sep": ";",
    "index": False
}

offset_date_default = (1, 1)

bw_values = (0, 255)
bw_match = {"(0, 0, 0)": "BTA",
            "(255, 255, 255)": "HAB",
            }


# colouring modes
default_colouring_mode = "simple"
gray_scale_colourings = ["bw", "gray"]
colour_colourings = ["simple", "infer"]
colouring_choices = gray_scale_colourings + colour_colourings

#pixel colour interpolation
_simple_coloursteps = range(0, 256, 10)
simple_colours = np.array(list(itertools.product(_simple_coloursteps, repeat=3)))
simple_colours: np.ndarray = simple_colours.reshape((simple_colours.shape[0], 1, 3)).astype(np.uint8)

grays = np.array([(i, i, i) for i in range(256)]).astype(np.uint8)
bws = np.array([(0, 0, 0), (255, 255, 255)]).astype(np.uint8)


ncolours = 256



brackets = {"{": "}", "[": "]", "(": ")"}

# str insert templates for the gamefile
complete_history_fragment = "\t\thistory={\n\t\t}\n"
history_fragment = "\t{date}={{\n\t\t\t\towner={tag}\n\t\t\t}}\n\t\t"
mapcolour_fragment = "\t{date}={{\n\t\t\t\tchanged_country_mapcolor_from={{\n\t\t\t\t\t{colour}\n\t\t\t\t" \
                     "}}\n\t\t\t}}\n\t\t"

hre_according_to_gamestate = "\n\t\thre=yes\n"  # relies on correct indendation to find hre provinces

#re matches


# misc
ineligible_tags = ["---", "REB", "NAT", "PIR"]
desired_tags = ["HAB", "FRA", "RUS", "PRU", "BYZ", "MNG", "TTL", "SOO"] # list of tags that are prioritized, should they exist

#shitty paths
definitions_path = r"/resources/voltaires_nightmare_cropped_definitions.csv"
test_province_map_path = r"/resources/voltaires_nightmare_provinces_cropped.bmp"
province_history_path = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\684459310\history\provinces"
test_frame_path = r"/resources/test/frame51.jpg"
test_frame_folder = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\test"
test_frame_first = r"frame40.jpg"

test_eu4_save = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\BadApple_Start_VoltairesNightmare.eu4"

tmp_dir = "../resources/tmp"
eu_extract = "save"