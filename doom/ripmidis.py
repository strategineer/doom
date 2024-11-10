#!/usr/bin/python3

import sys, getopt
from pathlib import Path
import subprocess

from omg import *

verbose = False
all_midis = False
force = False

if len(sys.argv) < 1:
    print("\n    Omgifol script: rip all midis from a given wad\n")
    print("    Usage:")
    print("    ripmidis.py [-v] [-a] [-f] source.wad [export format] \n")
    print("    -a: short for all, midis not properly tied to maps will not be extracted unless this option is selected \n")
    print("    -f: force ripmidis.py to overwrite any previously exported files\n")
    print("    [export extension]: render midis in the given format (eg. flac)using your system's default fluidsynth soundfont \n")
    print("                     choices: 'aiff','au','auto','avr','caf','flac','htk','iff','mat','mpc','oga','paf','pvf','raw','rf64','sd2','sds','sf','voc','w64','wav','wve','xi'\n")
    
else:
    # process optional flags
    try:
        opts, args = getopt.getopt(sys.argv[1:], "vdaf")
        for o, a in opts:
            if o == "-v":
                verbose = True
            if o == "-a":
                all_midis = True
            if o == "-f":
                force = True
    except getopt.GetoptError as err:
        print(str(err))
        sys.exit(2)

    # load WAD and draw map(s)
    sourcewad_filepath = args[0]
    if verbose:
        print("Loading %s..." % sourcewad_filepath)
    inwad = WAD()
    inwad.from_file(sourcewad_filepath)

    from_music_name_to_map_name = {}
    mapinfo = inwad.data["MAPINFO"].data.decode('ascii')
    previous_map_name = None
    for l in mapinfo.split("\n"):
        if verbose:
            print(l)
        if l.strip(r" {").startswith("map "):
            previous_map_name = l[4:].strip()
            print(previous_map_name)
        if l.strip().startswith("music ") or l.strip().startswith("music ="):
            music_track = l.split("=")[1].strip() if "=" in l else l.split(" ")[1].strip()
            print(music_track)
            if music_track not in from_music_name_to_map_name:
                from_music_name_to_map_name[music_track.strip("\"")] = previous_map_name
    
    if verbose:
        print(from_music_name_to_map_name)

    wad_name = Path(sourcewad_filepath).stem
    filename_prefix = f"{wad_name}_"
    extraction_path = Path(f"exports/")
    extraction_path.mkdir(exist_ok=True)
    n = 0
    if verbose:
        print(f"Extracting midis from {wad_name} to {extraction_path}...")
    for m in inwad.music:
        # todo these files aren't always midis, I should detect that somehow
        if not all_midis and m not in from_music_name_to_map_name:
            # skip weird tracks unless -a arg is passed
            continue
        filename = ''.join(x for x in from_music_name_to_map_name[m] if x.isalnum()) if m in from_music_name_to_map_name else f"_{m}"
        midi_filepath = Path(extraction_path, f"{filename_prefix}{filename}.mid")
        if not midi_filepath.exists() or force:
            inwad.music[m].to_file(str(midi_filepath))
            n += 1

    if verbose:
        print(f"Exported {n} music tracks")

    if len(args) == 1:
        sys.exit()
    exported_extension = f".{args[1]}"
    if verbose:
        print(f"Rendering midis to {extraction_path}...")
    for f in extraction_path.glob(f"{filename_prefix}*.mid"):
        exported_filename = f.name.replace(".mid", exported_extension)
        exported_filepath = extraction_path.joinpath(exported_filename)
        if not exported_filepath.exists() or force:
            subprocess.run(["fluidsynth", f"-T{args[1]}", "-F", exported_filepath, f])