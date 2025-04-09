import core


class AbstractTerminalCommandParser :
	def parse( self, line ) :
		pass

	def get_family_name( self ) -> str :
		pass

	def get_command_name( self ) -> str :
		pass

# Family : 'srv'
# Command : 'register'
# Args : 1 arg, a nickname.
class SrvRegisterCommandParser( AbstractTerminalCommandParser ) :
	# '$ srv register <username>' expected.
	def parse( self, line ) :
		words = line.split()

		if len( words ) == 3 and words[ 0 ] == "srv" and words[ 1 ] == "register" :
			user_request = core.UserRequest(
				core.UserAccount( "" ),
				core.UR_REGISTER,
				data = words[ 2 ]
			)

			return True, user_request
		else :
			return ( False, )


class SrvLoginCommandParser( AbstractTerminalCommandParser ) :
	# '$ srv login <username>'
	def parse(self, line):
		words = line.split()

		if len( words ) == 3 and words[ 0 ] == "srv" and words[ 1 ] == "login" :
			request = core.UserRequest(
				core.UserAccount( "" ),
				core.UR_LOGIN,
				data = words[ 2 ]
			)

			return True, request
		else :
			return ( False, )


class SrvLogoutCommandParser( AbstractTerminalCommandParser ) :
	def parse( self, line ):
		words = line.split()

		if len( words ) == 1 and words[ 0 ] == "logout" :
			request = core.UserRequest(
				core.UserAccount( "" ),
				core.UR_LOGOUT
			)

			return True, request
		else :
			return ( False, )