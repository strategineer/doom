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
    maps = [x for x in Path(".").glob("wads/*/src/maps/*.wad")]

    # run drawimages + dmvis and move the images where they need to be
    for m in maps:
        cwd = m.parents[3].absolute()
        print(f"cwd: {cwd}, m: {m.absolute()}, m.stem: {m.stem}")
        subprocess.run(["poetry", "run", "python", "../doom/drawmaps2.py", m.absolute(), m.stem, "5000" ], cwd=cwd) 
        subprocess.run(["poetry", "run", "python", "../doom/dmvis.py", m.absolute(), m.stem ], cwd=cwd)
        for png in cwd.glob("*.png"):
            png.replace(m.parents[2].joinpath(f"{m.stem}.png"))
        for gif in m.parents[0].glob("*.gif"):
            gif.replace(m.parents[2].joinpath(f"{m.stem}.gif"))