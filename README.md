# doom

## Docs

Generate overhead editor-esque PNGs for maps like so:

```
poetry run python doom/drawmaps.py wads/castle_of_doom/castle_of_doom.wad MAP01 4096 PNG
```

Rip midi tracks from the given wad like so:

```
poetry run python doom/ripmidis.py C:\games\doom\maps\aaliens\aaliens_v1_2.wad
```

... if you've got fluidsynth set up with your soundfont of choice, then appending a supported audio file format like `oga` or `flac` will also export the midis files for easier sharing:

```
poetry run python doom/ripmidis.py C:\games\doom\maps\aaliens\aaliens_v1_2.wad oga
```