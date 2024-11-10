#!/usr/bin/python3

import sys, getopt
from pathlib import Path

from omg import *
# import fluidsynth

verbose = False

if len(sys.argv) < 2:
    print("\n    Omgifol script: rip and render all midis from a given wad\n")
    print("    Usage:")
    print("    ripmidis.py [-v] [-a] source.wad \n")
    print("    -a: short for all, when not present midis not properly tied to maps, will not be exported\n")
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

    from_music_name_to_map_name = {}
    mapinfo = inwad.data["MAPINFO"].data.decode('ascii')
    previous_map_name = None
    for l in mapinfo.split("\n"):
        if l.startswith("map "):
            previous_map_name = l[4:].strip()
        if l.startswith("music "):
            music_track = l.split(" ")[1].strip()
            if music_track not in from_music_name_to_map_name:
                from_music_name_to_map_name[music_track] = previous_map_name

    wad_name = Path(sourcewad_filepath).stem
    export_path = Path(f"exports/{wad_name}")
    export_path.mkdir(exist_ok=True)
    for m in inwad.music:
        # todo get a different file name here based on the level
        if m not in from_music_name_to_map_name:
            # skip weird tracks unless -a arg is passed
            continue
        filename = ''.join(x for x in from_music_name_to_map_name[m] if x.isalnum()) if m in from_music_name_to_map_name else f"_{m}"
        midi_filepath = Path(export_path, f"{filename}.mid")
        inwad.music[m].to_file(str(midi_filepath))
        #fs = fluidsynth.Synth()
        #fs.start()
        #sfid = fs.sfload('C:\ProgramData\soundfonts\default.sf2')
        #fs.program_select(0, sfid, 0, 0)
        #break