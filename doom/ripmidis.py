#!/usr/bin/python3

import sys, getopt
from pathlib import Path

from omg import *

verbose = False

if len(sys.argv) < 2:
    print("\n    Omgifol script: rip and render all midis from a given wad\n")
    print("    Usage:")
    print("    ripmidis.py [-v] [-f] source.wad \n")
else:
    # process optional flags
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vdf")
        for o, a in opts:
            if o == "-v":
                verbose = True
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    # load WAD and draw map(s)
    sourcewad_filepath = args[0]
    print("Loading %s..." % sourcewad_filepath)
    inwad = WAD()
    inwad.from_file(sourcewad_filepath)

    ## TODO logic
    wad_name = Path(sourcewad_filepath).name
    export_path = Path(f"exports/{wad_name}")
    export_path.mkdir(exist_ok=True)
    for m in inwad.music:
        midi_filepath = Path(export_path, f"{m}.mid")
        inwad.music[m].to_file(str(midi_filepath))