import core
from core import ServerResponse
from dispatcher import Dispatcher
from terminal import TerminalWindow

from time import sleep


def quoted( line : str ) :
	return f"'{ line }'"


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


class TerminalCommandReader :
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


TERMINAL_LINE_HANDLING_MODE_COMMAND = 0
TERMINAL_LINE_HANDLING_MODE_INPUT = 1


class TerminalLineHandler :
	def __init__( self, command_reader, dispatcher ) :
		self._command_reader = command_reader
		self._dispatcher = dispatcher

		self._handling_mode = TERMINAL_LINE_HANDLING_MODE_COMMAND
		self.current_prompt_length = 0
		self.current_user_request = None
		self.current_user_account = None

	def set_window( self, window ) :
		self.current_prompt_length = len(window.prompt)

	# 1. Get the terminal line.
	# 2. Make a user request.
	def handle( self, line ) :
		prefix = "CLIENT : "

		d = self._dispatcher

		print( prefix + f"got line : {quoted( line )}" )

		if line == '' :
			return

		if self._handling_mode == TERMINAL_LINE_HANDLING_MODE_COMMAND :
			print( prefix + "handling mode COMMAND" )

			reader = self._command_reader
			request = reader.generate_request( line )

			if request is None :
				return

			if self.current_user_account is not None :
				request.requester_account = self.current_user_account

			self.current_user_request = request

			d.add_user_request( request )

			print( prefix + "request (command) -> ..." )

		elif self._handling_mode == TERMINAL_LINE_HANDLING_MODE_INPUT :
			print( prefix + "handling mode INPUT" )

			request = self.current_user_request
			request.data = line

			d.add_user_request( request )

			print( prefix + "request (input) -> ..." )

	def set_handling_mode(self, mode) :
		self._handling_mode = mode

	def reset( self, prompt_length ) :
		self.current_prompt_length = prompt_length
		self.current_user_request = None
		self._handling_mode = TERMINAL_LINE_HANDLING_MODE_COMMAND


class ServerResponseHandler :
	def __init__( self,
				  terminal_line_handler : TerminalLineHandler,
				  terminal_window : TerminalWindow ):
		self._tl_handler = terminal_line_handler
		self._window = terminal_window

	def handle( self, server_response : ServerResponse ):
		prefix = "CLIENT : "

		sr_type = server_response.sr_type
		dest_account = server_response.destination_account
		tl_handler = self._tl_handler
		w = self._window

		if sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_NOT_GIVEN:
			prompt = "Invent password : "
			w.display_prompt(prompt)

			tl_handler.current_prompt_length = len(prompt)
			tl_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)

			tl_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_SEND_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRM:
			prompt = "Confirm password : "
			w.display_prompt(prompt)

			tl_handler.current_prompt_length = len(prompt)
			tl_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)

			tl_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_CONFIRM_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRMATION_FAILED:
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_REGISTRATION_PASSED:
			username = server_response.data
			w.display_message(f"Welcome, {username}!")

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_REGISTRATION_FAILED_USER_SIGNED:
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_REGISTRATION_FAILED_A_USER_LOGGED :
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGIN_FAILED_USER_NOT_REGISTERED :
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGIN_ACCOUNT_PASSWORD_TO_ASK :
			prompt = "password : "
			w.prompt = prompt
			w.display_prompt( prompt )

			tl_handler.current_prompt_length = len(prompt)
			tl_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)
			tl_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_LOGIN_SEND_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_LOGIN_PASSED :
			new_prompt = "srv@" + server_response.data.username + " $ "
			w.prompt = new_prompt
			w.display_current_prompt()

			tl_handler.reset(len(self._window.prompt))
			tl_handler.current_user_account = server_response.data
		elif sr_type == core.SR_LOGIN_FAILED_WRONG_PASSWORD :
			w.display_error_message( server_response.error_message )

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGOUT_PASSED :
			w.reset_prompt()
			w.display_current_prompt()

			tl_handler.reset(len(self._window.prompt))
			tl_handler.current_user_account = None
		elif sr_type == core.SR_LOGOUT_FAILED_USER_NOT_LOGGED_IN :
			w.display_error_message( server_response.error_message )

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGIN_FAILED_A_USER_LOGGED :
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		else :
			print(prefix + f"Unknown server response type : value {sr_type}")


class CLIClient :
	def __init__( self, command_reader, dispatcher : Dispatcher ) :
		self._user_account = None
		self._window = None

		self._command_reader = command_reader
		self._dispatcher = dispatcher
		self._terminal_line_handler = TerminalLineHandler(command_reader, dispatcher)
		self._server_response_handler = ServerResponseHandler(
			terminal_line_handler=self._terminal_line_handler,
			terminal_window=self._window
		)

	# 1. Get the terminal line.
	# 2. Make a user request.
	# 3. Wait for a server response.
	# 4. Handle the response.
	def handle_enter_keystroke( self ) :
		prefix = "CLIENT : "

		w = self._window
		
		line = w.get_line(self._terminal_line_handler.current_prompt_length)

		self._terminal_line_handler.handle( line )

		if line == '' :
			w.display_current_prompt()

			return

		request = self._terminal_line_handler.current_user_request

		if request is None :
			print( prefix + "invalid command" )

			w.display_error_message( "invalid command" )

			return

		"""
		Wait for a server response.
		If we are using a client-notifying dispatcher,
		client doesn't have to wait for a response, because
		it will be notified by dispatcher, and this actually
		will be done in the separate server thread.
		"""
		d = self._dispatcher
		response = None
		while response is None :
			if d.has_server_response(request.requester_account) :
				response = d.get_server_response(request.requester_account)
			# else :
			# 	print( prefix + "... waiting for response ..." )

			# sleep( 0.2 )

		print( prefix + "... -> response" )
		print( prefix + "handle response ..." )

		self._server_response_handler.handle( response )

		print( prefix + "... response handled" )

	def set_window( self, window ) :
		self._window = window
		self._terminal_line_handler.set_window( window )
		self._server_response_handler._window = window
