# SPDX-FileCopyrightText: © Andrew Betson
# SPDX-License-Identifier: GPL-3.0-or-later

import argparse, os, subprocess, sys
from pathlib import Path
from mido import *

from binio import BinWriter
from mus import MusFile

parser = argparse.ArgumentParser(
	prog='MIDtoMUS',
	description='Converts Harmonix-style (GH/RB/CH/YARG) MIDI files to PopStar Guitar\'s MUS format.'
)
parser.add_argument( '-m', '--mode', help='Whether to convert a MID or build a song folder.', required=True, choices=[ 'convert_mid', 'build_song' ] )
parser.add_argument( '-i', '--input', help='File or folder to convert or build.', required=True, type=Path )
parser.add_argument( '-o', '--output', help='Path to save output to.', default='./', type=Path )
args = parser.parse_args()

if getattr( sys, 'frozen', False ) and hasattr( sys, '_MEIPASS' ):
    root_dir = Path( sys._MEIPASS )
else:
    root_dir = Path( os.getcwd() )

if not Path.exists( args.output ):
	os.makedirs( args.output )

match args.mode:
	case 'convert_mid':
		mus = MusFile.from_midi( args.input )

		bw = BinWriter( Path( Path.joinpath( args.output, 'music.mus' ) ) )
		bw.use_lbo = True
		mus.write( bw )
		bw.close()
	case 'build_song':
		mus_path = Path.joinpath( args.input, 'music.mus' )
		back_wav_path = Path.joinpath( args.input, 'back.wav' )
		guitar_mono_wav_path = Path.joinpath( args.input, 'guitar_mono.wav' )

		def ensure_exists( file_or_path: Path ):
			if not Path.exists( file_or_path ):
				raise FileNotFoundError( f'Failed to locate required file or path {file_or_path}!' )

		ensure_exists( mus_path )
		ensure_exists( back_wav_path )
		ensure_exists( guitar_mono_wav_path )

		tarcman_exe = Path.joinpath( root_dir, 'bsutils/tarcman.exe' )
		wavinterleaver_exe = Path.joinpath( root_dir, 'bsutils/WAVInterleaver.exe' )

		out_tc = Path.joinpath( args.output, 'DATA.TC' )
		out_raw = Path.joinpath( args.output, 'SONG.RAW' )

		subprocess.run( [ tarcman_exe, out_tc, '-a', 'music:mus', mus_path ], check=True )
		subprocess.run( [ wavinterleaver_exe, '196608', back_wav_path, guitar_mono_wav_path, out_raw ], check=True )
