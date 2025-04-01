import core
from core import ServerResponse
from dispatcher import Dispatcher
from terminal import TerminalWindow
import message_exchange as msg

from threading import Thread
from time import sleep
from datetime import datetime


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
		self.error_message = None

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

			self.current_user_request = request

			if request is None :
				return

			if self.current_user_account is not None :
				request.requester_account = self.current_user_account

			# if online and request is about reg/login, then show error message.
			if self.current_user_account is not None and \
					(request.ur_type == core.UR_REGISTER or request.ur_type == core.UR_LOGIN):
				self.error_message = "to register or log in, you must logout first"

				return

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

		print( prefix + "SRH handle ..." )

		sr_type = server_response.sr_type
		dest_account = server_response.destination_account
		tl_handler = self._tl_handler
		w = self._window

		if sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_NOT_GIVEN:
			prompt = "Invent password : "
			w.prompt = prompt
			w.display_prompt(prompt)

			tl_handler.current_prompt_length = len(prompt)
			tl_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)

			tl_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_SEND_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRM:
			prompt = "Confirm password : "
			w.prompt = prompt
			w.display_prompt(prompt)

			tl_handler.current_prompt_length = len(prompt)
			tl_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)

			tl_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_CONFIRM_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRMATION_FAILED:
			w.reset_prompt()
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
			w.reset_prompt()
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
		elif sr_type == core.SR_LOGIN_FAILED_USER_ALREADY_LOGGED :
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == msg.SR_MESSAGING_FAILED_USER_IS_NOT_REGISTERED :
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == msg.SR_MESSAGING_FAILED_USER_IS_OFFLINE :
			w.display_error_message(server_response.error_message)

			tl_handler.reset(len(self._window.prompt))

			print( "user is offline" )
		elif sr_type == msg.SR_MESSAGING_PASSED :
			w.display_current_prompt()

			tl_handler.reset(len(self._window.prompt))
		elif sr_type == msg.SR_MESSAGING_A_MESSAGE_CAME :
			time_info = datetime.now().strftime( "%H:%M:%S" )
			sender_name = server_response.data[ 1 ].username
			text = f"\n  {time_info}\n  from <{sender_name}> : {server_response.data[ 0 ]}\n"

			w.display_message( text )
		else :
			print(prefix + f"Unknown server response type : value {sr_type}")


class CLIClient :
	def __init__( self, command_reader, dispatcher : Dispatcher ) :
		self.user_account = None
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

		if line == '' :
			w.display_current_prompt()

			return

		self._terminal_line_handler.handle( line )

		request = self._terminal_line_handler.current_user_request

		if request is None :
			print( prefix + "invalid command" )

			w.display_error_message( "invalid command" )

			return

		m = self._terminal_line_handler.error_message
		if m is not None :
			w.display_error_message( m )
			self._terminal_line_handler.error_message = None

			return

		# """
		# Wait for a server response.
		# If we are using a client-notifying dispatcher,
		# client doesn't have to wait for a response, because
		# it will be notified by dispatcher, and this actually
		# will be done in the separate server thread.
		# """

	# ???
	def listen_to_dispatcher( self ) -> core.ServerResponse :
		d = self._dispatcher
		user_account = self._terminal_line_handler.current_user_account

		while True :
			if d.has_server_response( user_account ) :
				return d.get_server_response(request.requester_account)

	def set_window( self, window ) :
		self._window = window
		self._terminal_line_handler.set_window( window )
		self._server_response_handler._window = window


class ClientManager :
	def __init__( self ) :
		self._cli_clients = []

		self._t = Thread(
			target = self._run,
			daemon = True
		)

	def run( self ) :
		self._t.start()

	def add_client( self, client : CLIClient ) :
		self._cli_clients.append( client )

	def remove_client( self, client : CLIClient ) :
		self._cli_clients.remove( client )

	def _run( self ) :
		prefix = "CLIENT MANAGER : "
		print( prefix + "started" )

		while True :
			self._check_for_response_and_handle_it()

			# print( prefix + "..." )

			sleep( 0.5 )

	def _check_for_response_and_handle_it( self ) :
		for client in self._cli_clients :
			client : CLIClient

			d = client._dispatcher
			user_account = client._terminal_line_handler.current_user_account

			if user_account is None :
				user_account = core.UserAccount( "" )

			if d.has_server_response(user_account) :
				response = d.get_server_response(user_account)

				# handle response
				client._server_response_handler.handle( response )