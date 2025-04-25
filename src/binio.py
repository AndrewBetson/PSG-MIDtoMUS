# SPDX-FileCopyrightText: © Andrew Betson
# SPDX-License-Identifier: GPL-3.0-or-later

import io, struct
from pathlib import Path
from typing import Any

# This only implements as much as is needed
# for writing .mus files.
class BinWriter:
	writer: io.BufferedWriter
	use_lbo: bool = False

	@classmethod
	def __init__( self, name: Path ):
		self.writer = name.open( 'wb' )

	def close( self ):
		if ( not self.writer.closed ):
			self.writer.close()

	def write( self, fmt: str, value: Any ):
		self.writer.write( struct.pack( ( '' if self.use_lbo else '>' ) + fmt, value ) )

	def u16( self, value: int ):
		self.write( 'H', value )

	def u32( self, value: int ):
		self.write( 'I', value )

	def f32( self, value: float ):
		self.write( 'f', value )
