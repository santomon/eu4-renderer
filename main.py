import argparse

import config
import torment


def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument("--input", "-i", type=str, required=True, nargs="+",
                        help="can be an .mp4; can be an a directory of frames;"
                             "if a directory, you also need to specify --f1")
    parser.add_argument("--f1", "-f1", type=str, default=None, nargs="+",
                        help="When using a folder of frames, the first frame has to be specified. Next frames will be loaded "
                             "by incrementing the number at the end.")
    parser.add_argument("--output", "-o", type=str, required=True, nargs="+",
                        help="specify where to save the output; file name has to end with '.eu4'")
    parser.add_argument("--eu4", "-e", type=str, required=True, nargs="+",
                        help="specify which eu4-save to edit; should be an .eu4; accepts any ziplike. the file "
                             "itself will not be modified")
    parser.add_argument("--mod_dir", "-m", type=str, nargs="+",
                        help="specify the folder of the mod or eu4, from which all the relevant data will be inferred. "
                             "e.g. 'C:/Europa Universalis4/")
    parser.add_argument("--tmp_dir", "-t", type=str, default=[config.tmp_dir], nargs="+",
                        help="specify where to save baggage generated along the way; might have to manually delete afterwards")

    parser.add_argument("--definition", "-d", type=str, nargs="+", default=None,
                        help="where to find the definition.csv; this file maps every colour to a specific province;"
                             "used in conjunction with the appropriate provinces.bmp (--pbmp); if not specified, will be"
                             " inferred from the mod_dir"
                        )
    parser.add_argument("--pbmp", "-p", type=str, nargs="+", default=None,
                        help="where to find the provinces.bmp; this file essentially maps pixel positions to a certain colour;"
                             "these colours stand for their respective provinces, which can be looked up in the appropriate "
                             "definition.csv file (--definition); if not specified, will be inferred from the mod_dir")
    parser.add_argument("--crop", "-c", type=int, nargs=4, default=None,
                        help="crops the province map so that the video will only be played above the selected area;"
                             "expects for params: left top right bottom")
    parser.add_argument("--resize", "-r", type=int, nargs=2, required=False, default=None,
                        help="resizes the images before computation; this can save time, but comes at the cost of worse "
                             "pixel matching and dead provinces.")
    parser.add_argument("--redefine", "-rd", action="store_true", default=False,
                        help="redefinition recreates the definition based on the crop of the province map (reduces the "
                             "number of provinces that need to be searched; probably doesnt even matter at all")

    return parser.parse_args()


args = None


def main():
    global args
    args = parse_args()

    hm = torment.HistoryMaker()
    hm.fake_construct(
        _input=" ".join(args.input),
        output=" ".join(args.output),
        f1=" ".join(args.f1) if args.f1 is not None else None,
        mod_dir=" ".join(args.mod_dir) if args.mod_dir is not None else None,
        tmp_dir=" ".join(args.tmp_dir),
        eu4=" ".join(args.eu4),
        definition=" ".join(args.definition),
        pbmp=" ".join(args.pbmp),
        crop=args.crop,
        resize=args.resize,
        redefine=args.redefine,
    )
    hm.match()
    hm.make_history()


if __name__ == '__main__':
    main()
