import core
import message_exchange as msg
from cli_client.user_input_line_handler import UserInputLineHandler
from cli_client.user_input_line_handler import \
	TERMINAL_LINE_HANDLING_MODE_INPUT, \
	TERMINAL_LINE_HANDLING_MODE_COMMAND
from terminal import TerminalWindow

from datetime import datetime


class ServerResponseHandler :
	def __init__(self,
				 user_input_line_handler : UserInputLineHandler,
				 terminal_window : TerminalWindow):
		self._uil_handler = user_input_line_handler
		self._window = terminal_window

	def handle( self, server_response : core.ServerResponse ):
		prefix = "CLIENT : "

		print( prefix + "SRH handle ..." )

		sr_type = server_response.sr_type
		dest_account = server_response.destination_account
		uil_handler = self._uil_handler
		w = self._window

		if sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_NOT_GIVEN:
			prompt = "Invent password : "
			w.prompt = prompt
			w.display_prompt(prompt)

			uil_handler.current_prompt_length = len(prompt)
			uil_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)

			uil_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_SEND_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRM:
			prompt = "Confirm password : "
			w.prompt = prompt
			w.display_prompt(prompt)

			uil_handler.current_prompt_length = len(prompt)
			uil_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)

			uil_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_CONFIRM_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRMATION_FAILED:
			w.reset_prompt()
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_REGISTRATION_PASSED:
			w.reset_prompt()
			username = server_response.data
			w.display_message(f"Welcome, {username}!")

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_REGISTRATION_FAILED_USER_SIGNED:
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_REGISTRATION_FAILED_A_USER_LOGGED :
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGIN_FAILED_USER_NOT_REGISTERED :
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGIN_ACCOUNT_PASSWORD_TO_ASK :
			prompt = "password : "
			w.prompt = prompt
			w.display_prompt( prompt )

			uil_handler.current_prompt_length = len(prompt)
			uil_handler.set_handling_mode(TERMINAL_LINE_HANDLING_MODE_INPUT)
			uil_handler.current_user_request = core.UserRequest(
				dest_account,
				core.UR_LOGIN_SEND_ACCOUNT_PASSWORD
			)
		elif sr_type == core.SR_LOGIN_PASSED :
			new_prompt = "srv@" + server_response.data.username + " $ "
			w.prompt = new_prompt
			w.display_current_prompt()

			uil_handler.reset(len(self._window.prompt))
			uil_handler.current_user_account = server_response.data
		elif sr_type == core.SR_LOGIN_FAILED_WRONG_PASSWORD :
			w.reset_prompt()
			w.display_error_message( server_response.error_message )

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGOUT_PASSED :
			w.reset_prompt()
			w.display_current_prompt()

			uil_handler.reset(len(self._window.prompt))
			uil_handler.current_user_account = None
		elif sr_type == core.SR_LOGOUT_FAILED_USER_NOT_LOGGED_IN :
			w.display_error_message( server_response.error_message )

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == core.SR_LOGIN_FAILED_USER_ALREADY_LOGGED :
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == msg.SR_MESSAGING_FAILED_USER_IS_NOT_REGISTERED :
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == msg.SR_MESSAGING_FAILED_USER_IS_OFFLINE :
			w.display_error_message(server_response.error_message)

			uil_handler.reset(len(self._window.prompt))

			print( "user is offline" )
		elif sr_type == msg.SR_MESSAGING_PASSED :
			w.display_current_prompt()

			uil_handler.reset(len(self._window.prompt))
		elif sr_type == msg.SR_MESSAGING_A_MESSAGE_CAME :
			time_info = datetime.now().strftime( "%H:%M:%S" )
			sender_name = server_response.data[ 1 ].username
			text = f"\n  {time_info}\n  from <{sender_name}> : {server_response.data[ 0 ]}\n"

			w.display_message( text )
		else :
			print(prefix + f"Unknown server response type : value {sr_type}")
