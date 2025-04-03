from account_database import AccountDatabase
from core import UserAccount, UserRequest, ServerResponse
import core
import message_exchange as msg

from threading import Thread
from time import sleep
import pathlib


class Server :
	def __init__( self, dispatcher ) :
		db_file_path = str( pathlib.Path(__file__).parent.joinpath("account_db.txt").resolve() )
		self._account_db = AccountDatabase( db_file_path )
		self._dispatcher = dispatcher

		self._data = {}
		self._online_users = []

		self._stop_flag = False
		self._t = Thread(
			target = self._run )

	def run( self ) :
		self._t.start()

	def stop( self ) :
		self._stop_flag = True
		self._t.join()


	def _run( self ) :
		prefix = "SERVER : "

		print( prefix + "Started!" )

		while not self._stop_flag :
			if not self._dispatcher.has_user_requests() :
				print( prefix + "No requests" )

				# Without this sleep, the terminal window is freezing
				# after a user enters a command.
				sleep( 0.5 )
			else :
				request = self._dispatcher.get_user_request()

				print( prefix + f"... -> request {request.ur_type}" )

				self._handle_request( request )

				print( prefix + "... request handled" )
				print( prefix + "response -> ..." )

		print( prefix + "Stopped!" )


	def _handle_request( self, user_request ) :
		ur_type = user_request.ur_type
		requester = user_request.requester_account

		if ur_type == core.UR_REGISTER :
			self._handle_register( user_request )
		elif ur_type == core.UR_SEND_ACCOUNT_PASSWORD :
			self._handle_account_password_sending( user_request )
		elif ur_type == core.UR_CONFIRM_ACCOUNT_PASSWORD :
			self._handle_account_password_confirming( user_request )
		elif ur_type == core.UR_LOGIN :
			self._handle_login( user_request )
		elif ur_type == core.UR_LOGIN_SEND_ACCOUNT_PASSWORD :
			self._handle_login_account_password_sending( user_request )
		elif ur_type == core.UR_LOGOUT :
			self._handle_logout( user_request )
		elif ur_type == msg.UR_SEND_MESSAGE :
			self._handle_send_message( user_request )
		else :
			print( f"SERVER : unknown user request type : value {ur_type}" )


	def _handle_register( self, user_request : UserRequest ) :
		requester = user_request.requester_account
		username = user_request.data

		if "someone logged" in self._data and self._data[ "someone logged" ] == "yes" :
			self._dispatcher.add_server_response(
				ServerResponse(
					core.SR_REGISTRATION_FAILED_A_USER_LOGGED,
					requester,
					data=None,
					error_message="to register a user, the current user must log out"
				)
			)

			return

		if not self._account_db.contains(user_request.data) :
			self._data[ "username" ] = user_request.data

			response = ServerResponse(
				core.SR_REGISTRATION_ACCOUNT_PASSWORD_NOT_GIVEN,
				requester
			)
		else :
			response = ServerResponse(
				core.SR_REGISTRATION_FAILED_USER_SIGNED,
				requester,
				data = None,
				error_message = "user with this username already exists"
			)

		self._dispatcher.add_server_response(response)
			
	def _handle_account_password_sending( self, user_request : UserRequest ) :
		requester = user_request.requester_account

		# This piece of data is shared between two request types.
		self._data[ "password" ] = user_request.data
		
		self._dispatcher.add_server_response(
			core.ServerResponse(
				core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRM,
				requester
			)
		)

	def _handle_account_password_confirming( self, user_request : UserRequest ) :
		requester = user_request.requester_account

		if user_request.data == self._data[ "password" ] :
			new_username = self._data["username"]

			# Add to database.
			new_user_account = UserAccount( new_username )
			new_user_account.password = self._data["password"]
			self._account_db.add_account( new_user_account )

			response = core.ServerResponse(
				core.SR_REGISTRATION_PASSED,
				requester,
				data = new_username
			)
		else :
			response = core.ServerResponse(
				core.SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRMATION_FAILED,
				requester,
				data = None,
				error_message = "password confirmation failed"
			)

		self._dispatcher.add_server_response(response)


	def _handle_login( self, user_request : UserRequest ) :
		requester_username = user_request.data

		# Checking if a user is online is responsibility of the client.

		if requester_username in self._online_users :
			self._dispatcher.add_server_response(
				ServerResponse(
					core.SR_LOGIN_FAILED_USER_ALREADY_LOGGED,
					user_request.requester_account,
					data=None,
					error_message=f"user {requester_username} is already logged in"
				)
			)

			return

		if self._account_db.contains( requester_username ) :
			self._data["username"] = requester_username

			response = core.ServerResponse(
				core.SR_LOGIN_ACCOUNT_PASSWORD_TO_ASK,
				user_request.requester_account
			)
		else :
			response = core.ServerResponse(
				core.SR_LOGIN_FAILED_USER_NOT_REGISTERED,
				user_request.requester_account,
				data = None,
				error_message = "username is not registered"
			)

		self._dispatcher.add_server_response( response )

	def _handle_login_account_password_sending( self, user_request ):
		username = self._data["username"]
		request_password = user_request.data

		if self._account_db.contains( username ) and request_password == self._account_db.get_password( username ) :
			self._online_users.append( username )

			response = core.ServerResponse(
				core.SR_LOGIN_PASSED,
				user_request.requester_account,
				data = UserAccount( username, request_password )
			)
		else :
			response = core.ServerResponse(
				core.SR_LOGIN_FAILED_WRONG_PASSWORD,
				user_request.requester_account,
				data = None,
				error_message = "wrong password"
			)

		self._dispatcher.add_server_response( response )

	def _handle_logout( self, user_request : UserRequest ) :
		username = user_request.requester_account.username

		if username in self._online_users :
			response = ServerResponse(
				core.SR_LOGOUT_PASSED,
				user_request.requester_account
			)

			self._online_users.remove( username )
		else :
			response = ServerResponse(
				core.SR_LOGOUT_FAILED_USER_NOT_LOGGED_IN,
				user_request.requester_account,
				data = None,
				error_message = "nobody is logged in yet"
			)

		self._dispatcher.add_server_response( response )

	def _handle_send_message( self, user_request : UserRequest ) :
		message_dest_username = user_request.data[ 0 ]

		if not self._account_db.contains( message_dest_username ) :
			response = ServerResponse(
				msg.SR_MESSAGING_FAILED_USER_IS_NOT_REGISTERED,
				user_request.requester_account,
				data=None,
				error_message=f"user {message_dest_username} is not registered"
			)
		elif self._account_db.contains( message_dest_username ) and message_dest_username not in self._online_users :
			response = ServerResponse(
				msg.SR_MESSAGING_FAILED_USER_IS_OFFLINE,
				user_request.requester_account,
				data = None,
				error_message = f"user {message_dest_username} is offline now"
			)
		else :
			response = ServerResponse(
				msg.SR_MESSAGING_PASSED,
				user_request.requester_account,
			)

			response2 = ServerResponse(
				msg.SR_MESSAGING_A_MESSAGE_CAME,
				UserAccount(message_dest_username),
				data = [ user_request.data[ 1 ], user_request.requester_account ]
			)

			self._dispatcher.add_server_response( response2 )

		self._dispatcher.add_server_response( response )


