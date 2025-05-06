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

# This only implements as much as is needed
# for reading .mus files.
class BinReader:
	buf: bytes
	offset: int = 0
	length: int = 0
	use_lbo: bool = False

	@classmethod
	def from_data( cls, data: bytes ):
		o = cls()

		o.buf = data
		o.length = len( o.buf )

		return o

	@classmethod
	def from_path( cls, file_path: str ):
		f = open( file_path, 'rb' )
		return cls.from_data( f.read() )

	def at_end( self ) -> bool:
		return ( self.offset >= self.length )

	def read( self, fmt: str ) -> bytes:
		result: bytes = struct.unpack_from( ( '' if self.use_lbo else '>' ) + fmt, self.buf, self.offset )
		self.offset += struct.calcsize( fmt )
		return result

	def u16( self ) -> int:
		return self.read( 'H' )[ 0 ]

	def u32( self ) -> int:
		return self.read( 'I' )[ 0 ]

	def f32( self ) -> float:
		return self.read( 'f' )[ 0 ]
