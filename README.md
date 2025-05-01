Python utility for converting Guitar Hero (I/II/80's), Rock Band (probably all of them?) and Clone Hero/YARG MIDI files to PopStar Guitar's `MUS` chart format.

# Usage
If running from source, install dependencies using `pip install -r requirements.txt`

### Convert a MID to MUS
`python src/main.py` OR `MIDtoMUS.exe` `-m/--mode convert_mid -i/--input your_input_here.mid [-o/--output your_output_here.mus]`

### Build a song folder
`python src/main.py` OR `MIDtoMUS.exe` `-m/--mode build_song -i/--input folder/containing/song/data/ [-o/--output output/folder/]`

Song folder *must* contain `music.mus`, `back.wav` and `guitar_mono.wav`.

Additionally, both audio files *must* be 44.1 kHz and 16-bit, and `guitar_mono.wav` *must* be mono.

# TODO
- Import tempo map properly (currently just imports set_tempo events as they occur)
- Figure out how to generate or convert venue data to `visual.vis`
- Figure out what `judge.vis` is for

# License
This utility is licensed under version 3 of the GNU General Public License.

For more information, see `LICENSE.md`.
