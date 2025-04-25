# SPDX-FileCopyrightText: © Andrew Betson
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse, enum, io, os, struct, sys, time
from pathlib import Path
from mido import *

from binio import BinWriter
from util import *
from mus import *

parser = argparse.ArgumentParser(
	prog='MIDtoMUS',
	description='Converts GH1/GH2-style MID files to PopStar Guitar\'s MUS format.'
)

parser.add_argument( '-i', '--input', help='MID file to convert to MUS', required=True )
parser.add_argument( '-o', '--output', help='File to save converted MUS to', default='music.mus' )
args = parser.parse_args()

midi_path: str = args.input
midi_name: str = ''
if not midi_path.endswith( '.mid' ) and not midi_path.endswith( '.midi' ):
	midi_name = os.path.split( midi_path )[ 1 ]
	midi_path += '.mid'
else:
	midi_name = os.path.split( os.path.splitext( midi_path )[ 0 ] )[ 1 ]

if not os.path.exists( midi_path ):
	raise FileNotFoundError( f'Failed to locate provided MIDI file "{midi_path}"!' )

mus = MusFile()
midi = MidiFile( midi_path )

ns_tempo = MusNoteStream()
ns_tempo.instrument = EMusInstrument.Tempo
ns_tempo.difficulty = EMusDifficulty.Control

ns_sections = MusNoteStream()
ns_sections.instrument = EMusInstrument.Section
ns_sections.difficulty = EMusDifficulty.Control

# no earthly idea what this section is but I think we need at least one?
covertake_section = MusNoteEvent()
covertake_section.time = 0.0
covertake_section.duration = 0.0
covertake_section.note = 0
covertake_section.flags = EMusSection.CoverTake
ns_sections.add_note( covertake_section )

ns_guitar_easy = MusNoteStream()
ns_guitar_easy.instrument = EMusInstrument.LeadGuitar
ns_guitar_easy.difficulty = EMusDifficulty.Easy

ns_guitar_medium = MusNoteStream()
ns_guitar_medium.instrument = EMusInstrument.LeadGuitar
ns_guitar_medium.difficulty = EMusDifficulty.Medium

ns_guitar_hard = MusNoteStream()
ns_guitar_hard.difficulty = EMusDifficulty.Hard
ns_guitar_hard.instrument = EMusInstrument.LeadGuitar

t = 0.0
tempo = 500000

delta_ticks = 0.0
last_msg_time = 0.0

# Filter down to only the relevant tracks.
midi_track_guitar = None
midi_track_beat = None
for track in midi.tracks:
	if track.name == 'PART GUITAR':
		midi_track_guitar = track
	elif track.name == 'T1 GEMS': # this is what GH1 calls it
		midi_track_guitar = track
	elif track.name == midi_name:
		midi_track_beat = track

	if not midi_track_guitar == None and not midi_track_beat == None:
		break

if midi_track_guitar == None:
	raise Exception( 'Failed to find tracks "PART GUITAR" or "T1 GEMS" in provided MIDI file.' )

if midi_track_beat == None:
	raise Exception( f'Failed to find track "{midi_name}" in provided MIDI file.' )

def process_sustain( note: int ):
	if note in guitar_notes_easy:
		# Sustains must be at least 240 ticks to be considered a sustain.
		if delta_ticks < 240.0:
			return

		new_duration = t - ns_guitar_easy.notes[ -1 ].time

		ns_guitar_easy.notes[ -1 ].duration = new_duration

		ns_len = len( ns_guitar_easy.notes )
		if ns_len > 1:
			if ns_guitar_easy.notes[ -2 ].time == ns_guitar_easy.notes[ -1 ].time:
				ns_guitar_easy.notes[ -2 ].duration = new_duration
		if ns_len > 2:
			if ns_guitar_easy.notes[ -3 ].time == ns_guitar_easy.notes[ -1 ].time:
				ns_guitar_easy.notes[ -3 ].duration = new_duration
		if ns_len > 3:
			if ns_guitar_easy.notes[ -4 ].time == ns_guitar_easy.notes[ -1 ].time:
				ns_guitar_easy.notes[ -4 ].duration = new_duration
		if ns_len > 4:
			if ns_guitar_easy.notes[ -5 ].time == ns_guitar_easy.notes[ -1 ].time:
				ns_guitar_easy.notes[ -5 ].duration = new_duration
	elif msg.note in guitar_notes_medium:
		new_duration = t - ns_guitar_medium.notes[ -1 ].time
		if not new_duration > 0.1:
			return

		ns_guitar_medium.notes[ -1 ].duration = new_duration

		if ns_guitar_medium.notes[ -2 ].time == ns_guitar_medium.notes[ -1 ].time:
			ns_guitar_medium.notes[ -2 ].duration = new_duration

		ns_len = len( ns_guitar_medium.notes )
		if ns_len > 1:
			if ns_guitar_medium.notes[ -2 ].time == ns_guitar_medium.notes[ -1 ].time:
				ns_guitar_medium.notes[ -2 ].duration = new_duration
		if ns_len > 2:
			if ns_guitar_medium.notes[ -3 ].time == ns_guitar_medium.notes[ -1 ].time:
				ns_guitar_medium.notes[ -3 ].duration = new_duration
		if ns_len > 3:
			if ns_guitar_medium.notes[ -4 ].time == ns_guitar_medium.notes[ -1 ].time:
				ns_guitar_medium.notes[ -4 ].duration = new_duration
		if ns_len > 4:
			if ns_guitar_medium.notes[ -5 ].time == ns_guitar_medium.notes[ -1 ].time:
				ns_guitar_medium.notes[ -5 ].duration = new_duration
	elif msg.note in guitar_notes_expert:
		new_duration = t - ns_guitar_hard.notes[ -1 ].time
		if not new_duration > 0.1:
			return

		ns_guitar_hard.notes[ -1 ].duration = new_duration

		ns_len = len( ns_guitar_hard.notes )
		if ns_len > 1:
			if ns_guitar_hard.notes[ -2 ].time == ns_guitar_hard.notes[ -1 ].time:
				ns_guitar_hard.notes[ -2 ].duration = new_duration
		if ns_len > 2:
			if ns_guitar_hard.notes[ -3 ].time == ns_guitar_hard.notes[ -1 ].time:
				ns_guitar_hard.notes[ -3 ].duration = new_duration
		if ns_len > 3:
			if ns_guitar_hard.notes[ -4 ].time == ns_guitar_hard.notes[ -1 ].time:
				ns_guitar_hard.notes[ -4 ].duration = new_duration
		if ns_len > 4:
			if ns_guitar_hard.notes[ -5 ].time == ns_guitar_hard.notes[ -1 ].time:
				ns_guitar_hard.notes[ -5 ].duration = new_duration
	else:
		return

for msg in merge_tracks( [ midi_track_guitar, midi_track_beat ] ):
	if msg.type == 'set_tempo':
		tempo = msg.tempo

	t += tick2second( msg.time, midi.ticks_per_beat, tempo )

	delta_ticks = msg.time - last_msg_time
	last_msg_time = msg.time

	ne = MusNoteEvent()
	ne.time = t
	ne.duration = 0.0
	ne.note = 0
	ne.flags = EMusNoteState.Ready

	match msg.type:
		case 'set_tempo':
			ns_tempo.add_note( ne )
		case 'note_on':
			if not msg.note in guitar_notes_easy and not msg.note in guitar_notes_medium and not msg.note in guitar_notes_expert:
				continue

			# note_on events with 0 velocity are basically note_off events.
			if msg.velocity == 0.0:
				process_sustain( msg.note )
				continue

			ne.note = gh_note_to_psg_note( msg.note )

			if msg.note in guitar_notes_easy:
				ns_guitar_easy.add_note( ne )
			elif msg.note in guitar_notes_medium:
				ns_guitar_medium.add_note( ne )
			elif msg.note in guitar_notes_expert:
				ns_guitar_hard.add_note( ne )
		case 'note_off':
			process_sustain( msg.note )
		case 'end_of_track':
			ne.flags = EMusSection.Done
			ns_sections.add_note( ne )

mus.add_stream( ns_sections )
mus.add_stream( ns_tempo )
mus.add_stream( ns_guitar_easy )
mus.add_stream( ns_guitar_medium )
mus.add_stream( ns_guitar_hard )

bw = BinWriter( Path( args.output ) )
bw.use_lbo = True
mus.write( bw )
bw.close()
