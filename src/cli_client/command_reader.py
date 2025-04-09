import core


class CommandReader :
	def __init__( self ) :
		self._parsers = []

	# Variant 1 : Creates and gets a user request from a command line passed.
	# Variant 2 : Creates (through a parser) and gets a result object from a command line passed.
	# read_command_line
	# generate_request, create_request
	def generate_request( self, line ) -> core.UserRequest | None:
		for parser in self._parsers :
			# Parsing result : ( True/False, UserRequest/None, ... )
			result = parser.parse( line )
			if result[ 0 ] :
				return result[ 1 ]

		return None

	def add_parser( self, parser ) :
		self._parsers.append( parser )
