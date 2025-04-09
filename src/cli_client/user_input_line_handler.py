import core

TERMINAL_LINE_HANDLING_MODE_COMMAND = 0
TERMINAL_LINE_HANDLING_MODE_INPUT = 1


def quoted( line : str ) :
	return f"'{ line }'"


class UserInputLineHandler :
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
