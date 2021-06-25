import os

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

bw_match = {"(0, 0, 0)": "BTA",
            "(255, 255, 255)": "HAB",
            }

brackets = {"{": "}", "[": "]", "(": ")"}

history_insert = "\t{date}={{\n\t\t\t\towner={tag}\n\t\t\t}}\n\t\t"

definitions_path = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\voltaires_nightmare_cropped_definitions.csv"
test_province_map_path = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\voltaires_nightmare_provinces_cropped.bmp"
province_history_path = r"C:\Program Files (x86)\Steam\steamapps\workshop\content\236850\684459310\history\provinces"
test_frame_path = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\test\frame51.jpg"
test_frame_folder = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\test"
test_frame_first = r"frame40.jpg"

test_eu4_save = r"C:\Grand Archives\shitty projects\eu4-renderer\resources\BadApple_Start_VoltairesNightmare.eu4"

tmp_dir = "./resources/tmp"
eu_extract = "save"