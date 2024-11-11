#!/usr/bin/python3

import sys, getopt
from pathlib import Path
import subprocess

from omg import *

DEFAULT_DOOM2_TRACKNAMES_TO_MAP_MAPPINGS = {
                "D_DM2TTL": "_TITLE",
                "D_DM2TTL": "_INTERMISSION",
                "D_READ_M": "_TEXT",
                "D_RUNNIN": "MAP01",
                "D_RUNNI2": "MAP15",
                "D_STALKS": "MAP02",
                "D_STLKS2": "MAP11",
                "D_STLKS3": "MAP17",
                "D_COUNTD": "MAP03",
                "D_COUNT2": "MAP21",
                "D_BETWEE": "MAP04",
                "D_DOOM": "MAP05",
                "D_DOOM2": "MAP13",
                "D_THE_DA": "MAP06",
                "D_THEDA2": "MAP12",
                "D_THEDA3": "MAP24",
                "D_SHAWN": "MAP07",
                "D_SHAWN2": "MAP19",
                "D_SHAWN3": "MAP29",
                "D_DDTBLU": "MAP08",
                "D_DDTBL2": "MAP14",
                "D_DDTBL3": "MAP22",
                "D_IN_CIT": "MAP09",
                "D_DEAD": "MAP10",
                "D_DEAD2": "MAP16",
                "D_ROMERO": "MAP18",
                "D_ROMER2": "MAP27",
                "D_MESSAG": "MAP20",
                "D_MESSG2": "MAP26",
                "D_AMPIE": "MAP23",
                "D_ADRIAN": "MAP25",
                "D_TENSE": "MAP28",
                "D_OPENIN": "MAP30",
                "D_EVIL": "MAP31",
                "D_ULTIMA": "MAP32"
            }

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
        opts, args = getopt.getopt(sys.argv[1:], "vaf")
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
    try:
        wads = [str(x) for x in Path(args[0]).glob("**/*.wad")]
    except:
        wads = [args[0]]

    if verbose:
        print(wads)
    for sourcewad_filepath in wads:
        wad_name = Path(sourcewad_filepath).stem
        filename_prefix = f"{wad_name}_"
        print("Loading %s..." % sourcewad_filepath)
        inwad = WAD()
        try:
            inwad.from_file(sourcewad_filepath)
        except TypeError as e:
            print(f"Failed to load {sourcewad_filepath}, skipping")
            continue
        from_music_name_to_map_name = {
            # these might not be set in the MAPINFO so let's set the here
            "D_DM2TTL": "__TITLE",
            "D_DM2INT": "_INTERMISSION",
            "D_READ_M": "_TEXT",
        }
        n_initial_count = len(from_music_name_to_map_name)
        try:
            mapinfo = inwad.data["MAPINFO"].data.decode('ascii')
            previous_map_name = None
            for l in mapinfo.split("\n"):
                if verbose:
                    print(l)
                if l.strip(r" {").startswith("map "):
                    previous_map_name = l[4:].strip()
                    if verbose:
                        print(previous_map_name)
                if previous_map_name is not None and (l.strip().startswith("music ") or l.strip().startswith("music =")):
                    music_track = l.split("=")[1].strip() if "=" in l else l.split(" ")[1].strip()
                    if verbose:
                        print(music_track)
                    if music_track not in from_music_name_to_map_name:
                        from_music_name_to_map_name[music_track.strip("\"")] = previous_map_name
            if len(from_music_name_to_map_name) == n_initial_count:
                raise ValueError
        except KeyError:
            print(f"Failed to find MAPINFO lump in {sourcewad_filepath}, defaulting to Doom II music track to map mappings")
            # todo check if this is actually how it works, I'm pretty sure it is but let's confirm
            from_music_name_to_map_name = DEFAULT_DOOM2_TRACKNAMES_TO_MAP_MAPPINGS
        except ValueError:
            print(f"No music tracks defined in MAPINFO lump in {sourcewad_filepath}, defaulting to Doom II music track to map mappings")
            # todo check if this is actually how it works, I'm pretty sure it is but let's confirm
            from_music_name_to_map_name = DEFAULT_DOOM2_TRACKNAMES_TO_MAP_MAPPINGS
        
        if verbose:
            print(from_music_name_to_map_name)

        extraction_path = Path(f"exports/")
        extraction_path.mkdir(exist_ok=True)
        n = 0
        if verbose:
            print(f"Extracting midis from {wad_name} to {extraction_path}...")
        for m in inwad.music:
            if not all_midis and m not in from_music_name_to_map_name:
                # skip weird tracks unless -a arg is passed
                continue
            data = inwad.music[m].data
            file_extension = ".mid" 
            if data.startswith(b'Ogg'):
                file_extension = ".ogg"
            elif data.startswith(b'fLaC'):
                file_extension = ".flac"
            elif data.startswith(b'ID3') or data.startswith(b'\xff\xfbql'):
                file_extension = ".mp3"
            elif data.startswith(b'RIFF$8\xb9\x01WAVE'):
                file_extension = ".wav"
            elif not data.startswith(b'MThd'):
                # note to self: DOOM-specific MUS files start with b'MUS'
                # TODO figure out if we could convert MUS files to MIDI files, that would be sick, to allow for playing them outside of a doom source port
                if verbose:
                    print(f"Skipping {m} track for {wad_name} because we can only handle MIDI files for now")
                continue
            filename = ''.join(x for x in from_music_name_to_map_name[m] if x.isalnum() or x == '_') if m in from_music_name_to_map_name else f"_{m}"
            filepath = Path(extraction_path, f"{filename_prefix}{filename}{file_extension}")
            if not filepath.exists() or force:
                print(f"Writing to {filepath}")
                inwad.music[m].to_file(str(filepath))
                n += 1

        print(f"Exported {n} music tracks")

        if len(args) == 1:
            continue
        exported_extension = f".{args[1]}"
        if verbose:
            print(f"Rendering midis to {extraction_path}...")
        for f in extraction_path.glob(f"{filename_prefix}*.mid"):
            exported_filename = f.name.replace(".mid", exported_extension)
            exported_filepath = extraction_path.joinpath(exported_filename)
            if not exported_filepath.exists() or force:
                subprocess.run(["fluidsynth", f"-T{args[1]}", "-F", exported_filepath, f])