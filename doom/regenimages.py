#!/usr/bin/python3

import sys, getopt
from pathlib import Path
import subprocess

verbose = False

if len(sys.argv) < 1:
    print("\n    script: regen all images and build .gifs for all maps \n")
    print("    Usage:")
    print("    regenimages.py [-v] \n")
    
else:
    # process optional flags
    try:
        opts, args = getopt.getopt(sys.argv[1:], "v")
        for o, a in opts:
            if o == "-v":
                verbose = True
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    # load WAD and draw map(s)

    # todo do work
    maps = [str(x) for x in Path(".").glob("/wads/*/src/maps/*")]

    # run drawimages + dmvis and move the images where they need to be
    for m in maps:
        subprocess.run(["poetry", "run", "python", "doom/drawmaps2.py", m, m.slug, "5000" ]) 
        subprocess.run(["poetry", "run", "python", "doom/dmvis.py", m, m.slug ])