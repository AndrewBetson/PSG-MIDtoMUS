# SPDX-FileCopyrightText: © Andrew Betson
# SPDX-License-Identifier: GPL-3.0-or-later

import enum, math, os
from enum import IntEnum
from mido import *

from binio import BinWriter

@enum.unique
class EMusNoteColor( IntEnum ):
	Green: int = 0
	Red: int = 1
	Yellow: int = 2
	Blue: int = 3
	Orange: int = 4

@enum.unique
class EMusSection( IntEnum ):
	Chorus: int = 0
	Verse: int = ( 1 << 8 )
	Bridge: int = ( 2 << 8 )
	Intro: int = ( 3 << 8 )
	Outro: int = ( 4 << 8 )
	Solo: int = ( 5 << 8 )
	PreChorus: int = ( 6 << 8 )
	FadeDown: int = ( 7 << 8 )
	Done: int = ( 8 << 8 )
	AuditionBegin: int = ( 9 << 8 )
	AuditionEnd: int = ( 10 << 8 )
	CoverTake: int = ( 11 << 8 )

@enum.unique
class EMusInstrument( IntEnum ):
	LeadGuitar: int = 0

# unused begin
	RhythmGuitar: int = 1
	BassGuitar: int = 2
	Drums: int = 3
# unused end

	Tempo: int = 4
	Section: int = 5

@enum.unique
class EMusDifficulty( IntEnum ):
	Easy: int = 0
	Medium: int = 1
	Hard: int = 2
	MixMode: int = 3
	Control: int = 4

@enum.unique
class EMusNoteState( IntEnum ):
	Ready: int = 0
	Hit: int = 1
	Missed: int = 2
	Wrong: int = 3
	BeingPlayed: int = 4

class MusNoteEvent:
	time: float = 0.0
	duration: float = 0.0
	note: int = EMusNoteColor.Green
	flags: int = EMusNoteState.Ready

	def write( self, bw: BinWriter ):
		bw.f32( self.time )
		bw.f32( self.duration )
		bw.u16( self.note )
		bw.u16( self.flags )

class MusNoteStream:
	instrument: int
	difficulty: int
	notes: list[ MusNoteEvent ]

	def __init__( self ):
		self.instrument = EMusInstrument.LeadGuitar
		self.difficulty = EMusDifficulty.Easy
		self.notes = []

	def add_note( self, new_note: MusNoteEvent ):
		self.notes.append( new_note )

	def write( self, bw: BinWriter ):
		bw.u16( self.instrument )
		bw.u16( self.difficulty )
		bw.u16( len( self.notes ) )
		bw.u16( 0 ) # Padding

		for note in self.notes:
			note.write( bw )

class MusFile:
	streams: list[ MusNoteStream ]

	def __init__( self ):
		self.streams = []

	@classmethod
	def from_midi( cls, midi_path: str ):
		o = cls()

		if not os.path.exists( midi_path ):
			raise FileNotFoundError( f'Failed to locate provided MIDI file "{midi_path}".' )
		midi = MidiFile( midi_path )

		# Filter down to only the relevant tracks.
		midi_track_beat = midi.tracks[ 0 ]
		midi_track_guitar = None
		midi_track_events = None
		for track in midi.tracks:
			if track.name == 'PART GUITAR':
				midi_track_guitar = track
			elif track.name == 'T1 GEMS': # this is what GH1 calls it
				midi_track_guitar = track
			elif track.name == 'EVENTS':
				midi_track_events = track

		if midi_track_guitar == None:
			raise Exception( 'Failed to find track "PART GUITAR" or "T1 GEMS" in provided MIDI file.' )

		if midi_track_events == None:
			raise Exception( 'Failed to find track "EVENTS" in provided MIDI file.' )

		ns_tempo = MusNoteStream()
		ns_tempo.instrument = EMusInstrument.Tempo
		ns_tempo.difficulty = EMusDifficulty.Control

		ns_sections = MusNoteStream()
		ns_sections.instrument = EMusInstrument.Section
		ns_sections.difficulty = EMusDifficulty.Control

		# No earthly idea what this section is but I think we need at least one?
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

		current_time = 0.0
		tempo = 500000
		min_sustain_time = 0.0

		for msg in merge_tracks( [ midi_track_beat, midi_track_guitar, midi_track_events ] ):
			if msg.type == 'set_tempo':
				tempo = msg.tempo

			current_time += tick2second( msg.time, midi.ticks_per_beat, tempo )
			min_sustain_time = tick2second( 240, midi.ticks_per_beat, tempo )

			ne = MusNoteEvent()
			ne.time = current_time
			ne.duration = 0.0
			ne.note = 0
			ne.flags = EMusNoteState.Ready

			match msg.type:
				case 'set_tempo':
					ns_tempo.add_note( ne )
				case 'note_on':
					if not is_valid_note( msg.note ):
						continue

					# note_on events with 0 velocity are basically note_off events.
					if msg.velocity == 0.0:
						process_sustain( msg.note, current_time, min_sustain_time, ns_guitar_easy )
						process_sustain( msg.note, current_time, min_sustain_time, ns_guitar_medium )
						process_sustain( msg.note, current_time, min_sustain_time, ns_guitar_hard )
						continue

					ne.note = midi_note_to_psg_note( msg.note )

					if msg.note in guitar_notes_easy:
						ns_guitar_easy.add_note( ne )
					elif msg.note in guitar_notes_medium:
						ns_guitar_medium.add_note( ne )
					elif msg.note in guitar_notes_expert:
						ns_guitar_hard.add_note( ne )
				case 'note_off':
					if not is_valid_note( msg.note ):
						continue

					process_sustain( msg.note, current_time, min_sustain_time, ns_guitar_easy )
					process_sustain( msg.note, current_time, min_sustain_time, ns_guitar_medium )
					process_sustain( msg.note, current_time, min_sustain_time, ns_guitar_hard )
				case 'text':
					if midi_section_to_psg_section( msg.text, ne ):
						ns_sections.add_note( ne )
				case 'end_of_track':
					# Ensure we have a Done section.
					if ns_sections.notes[ -1 ].flags != EMusSection.Done:
						ne.flags = EMusSection.Done
						ns_sections.add_note( ne )

		o.add_stream( ns_sections )
		o.add_stream( ns_tempo )
		o.add_stream( ns_guitar_easy )
		o.add_stream( ns_guitar_medium )
		o.add_stream( ns_guitar_hard )

		return o

	def add_stream( self, new_stream: MusNoteStream ):
		self.streams.append( new_stream )

	def write( self, bw: BinWriter ):
		use_lbo = bw.use_lbo

		bw.use_lbo = False
		bw.write( 'I', 0x534D5553 ) # "SMUS"
		bw.use_lbo = use_lbo

		bw.u16( len( self.streams ) )

		for stream in self.streams:
			stream.write( bw )

# Valid guitar notes, excluding SP, P1/2 sections, and hard difficulty notes.
guitar_notes = [
	[ 60, 61, 62, 63, 64 ], # Easy GRYBO
	[ 72, 73, 74, 75, 76 ], # Medium GRYBO
	[ 96, 97, 98, 99, 100 ] # Expert GRYBO
]

guitar_notes_easy = guitar_notes[ 0 ]
guitar_notes_medium = guitar_notes[ 1 ]
guitar_notes_expert = guitar_notes[ 2 ]

guitar_notes_green = [ guitar_notes_easy[ 0 ], guitar_notes_medium[ 0 ], guitar_notes_expert[ 0 ] ]
guitar_notes_red = [ guitar_notes_easy[ 1 ], guitar_notes_medium[ 1 ], guitar_notes_expert[ 1 ] ]
guitar_notes_yellow = [ guitar_notes_easy[ 2 ], guitar_notes_medium[ 2 ], guitar_notes_expert[ 2 ] ]
guitar_notes_blue = [ guitar_notes_easy[ 3 ], guitar_notes_medium[ 3 ], guitar_notes_expert[ 3 ] ]
guitar_notes_orange = [ guitar_notes_easy[ 4 ], guitar_notes_medium[ 4 ], guitar_notes_expert[ 4 ] ]

def is_valid_note( note: int ) -> bool:
	return note in guitar_notes_easy or note in guitar_notes_medium or note in guitar_notes_expert

def midi_note_to_psg_note( note: int ) -> EMusNoteColor:
	if note in guitar_notes_green:
		return EMusNoteColor.Green
	elif note in guitar_notes_red:
		return EMusNoteColor.Red
	elif note in guitar_notes_yellow:
		return EMusNoteColor.Yellow
	elif note in guitar_notes_blue:
		return EMusNoteColor.Blue
	elif note in guitar_notes_orange:
		return EMusNoteColor.Orange

def midi_section_to_psg_section( section: str, ne: MusNoteEvent ) -> bool:
	section = section.lower()

	match section:
		case 'chorus':
			ne.flags = EMusSection.Chorus
			return True
		case 'verse':
			ne.flags = EMusSection.Verse
			return True
		case 'solo':
			ne.flags = EMusSection.Solo
			return True
		case 'end':
			ne.flags = EMusSection.Done
			return True

	if 'section ' in section:
		if 'intro' in section:
			ne.flags = EMusSection.Intro
			return True
		elif 'prechorus' in section or 'pre-chorus' in section:
			ne.flags = EMusSection.PreChorus
			return True
		elif 'chorus' in section:
			ne.flags = EMusSection.Chorus
			return True
		if 'verse' in section:
			ne.flags = EMusSection.Verse
			return True
		elif 'bridge' in section:
			ne.flags = EMusSection.Bridge
			return True
		elif 'solo' in section:
			ne.flags = EMusSection.Solo
			return True
		elif 'outro' in section:
			ne.flags = EMusSection.Outro
			return True

	return False

def process_sustain( note: int, current_time: float, min_sustain_time: float, ns: MusNoteStream ):
	new_duration = current_time - ns.notes[ -1 ].time
	if new_duration < min_sustain_time:
		return

	ns.notes[ -1 ].duration = new_duration

	ns_len = len( ns.notes )
	if ns_len > 1:
		if math.isclose( ns.notes[ -2 ].time, ns.notes[ -1 ].time ):
			ns.notes[ -2 ].duration = new_duration
	if ns_len > 2:
		if math.isclose( ns.notes[ -3 ].time, ns.notes[ -1 ].time ):
			ns.notes[ -3 ].duration = new_duration
	if ns_len > 3:
		if math.isclose( ns.notes[ -4 ].time, ns.notes[ -1 ].time ):
			ns.notes[ -4 ].duration = new_duration
	if ns_len > 4:
		if math.isclose( ns.notes[ -5 ].time, ns.notes[ -1 ].time ):
			ns.notes[ -5 ].duration = new_duration
