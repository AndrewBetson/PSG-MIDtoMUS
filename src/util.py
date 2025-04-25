# SPDX-FileCopyrightText: © Andrew Betson
# SPDX-License-Identifier: GPL-3.0-or-later

from mus import EMusNoteColor

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

def gh_note_to_psg_note( note: int ) -> int:
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
	else:
		raise Exception( f'Unexpected note value {note} passed to gh_note_to_psg_note!' )
