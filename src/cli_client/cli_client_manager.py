import core
from cli_client.cli_client import CLIClient

from threading import Thread
from time import sleep


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
			user_account = client._user_input_line_handler.current_user_account

			if user_account is None :
				user_account = core.UserAccount( "" )

			if d.has_server_response(user_account) :
				response = d.get_server_response(user_account)

				# handle response
				client._server_response_handler.handle( response )