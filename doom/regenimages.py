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


    maps = [x for x in Path(".").glob("wads/*/src/maps/*.wad")]

    branch = "HEAD~1"
    if len(args) > 0:
        branch = args[0]

    output = subprocess.run(["git", "diff", "--name-only", "HEAD", branch], capture_output=True)
    changed_files = [Path(p) for p in output.stdout.decode('ascii').strip().split('\n')]
    # run drawimages + dmvis and move the images where they need to be
    for m in maps:
        if m not in changed_files:
            print(f"Map {m} not changed so skipping image generation for it")
            continue
        cwd = m.parents[3].absolute()
        print(f"cwd: {cwd}, m: {m.absolute()}, m.stem: {m.stem}")
        subprocess.run(["poetry", "run", "python", "../doom/drawmaps2.py", m.absolute(), m.stem, "5000" ], cwd=cwd) 
        subprocess.run(["poetry", "run", "python", "../doom/dmvis.py", m.absolute(), m.stem ], cwd=cwd)
        for png in cwd.glob("*.png"):
            png.replace(m.parents[2].joinpath(f"img/{m.stem}.png"))
        for gif in m.parents[0].glob("*.gif"):
            gif.replace(m.parents[2].joinpath(f"img/{m.stem}.gif"))