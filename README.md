Python utility for converting Guitar Hero II (and maybe I?) MIDI files to PopStar Guitar's `MUS` chart format.

# Usage
Install dependencies using `pip install -r requirements.txt`

Run script using `python src/main.py -i|--input your_midi_here.mid`

# TODO
- Import tempo map properly (currently just imports set_tempo events as they occur)
- Convert GHII sections to PSG sections
- Add utilities for automagically converting entire songs (chart *and* audio) to `DATA.TC` and `SONG.RAW` with one command.
- Clean up code

# License
This utility is released under version 3 of the GNU General Public License.

For more information, see `LICENSE.md`.
