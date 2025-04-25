# SPDX-FileCopyrightText: © Andrew Betson
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse, enum, io, os, struct, sys, time
from enum import IntEnum

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

		i = 0
		for note in self.notes:
			note.write( bw )
			i += 1

class MusFile:
	streams: list[ MusNoteStream ]

	def __init__( self ):
		self.streams = []

	def add_stream( self, new_stream: MusNoteStream ):
		self.streams.append( new_stream )

	def write( self, bw: BinWriter ):
		use_lbo = bw.use_lbo

		bw.use_lbo = False
		bw.write( 'I', 0x534D5553 ) # "SMUS"
		bw.use_lbo = use_lbo

		bw.u16( len( self.streams ) )

		i = 0
		for stream in self.streams:
			stream.write( bw )
			i += 1
