from queue import Queue
import core


class Dispatcher :
	def __init__( self ) :
		self._request_queue = Queue()
		self._username_to_response_queue = dict()

	def add_user_request( self, user_request ) :
		self._request_queue.put( user_request )

	def get_user_request( self ) -> core.UserRequest :
		return self._request_queue.get()

	def add_server_response( self, server_response ) :
		dest = server_response.destination_account
		username = dest.username

		if username not in self._username_to_response_queue :
			self._username_to_response_queue[ username ] = Queue()

		self._username_to_response_queue[ username ].put( server_response )

	def get_server_response( self, user_account ) -> core.ServerResponse :
		username = user_account.username
		return self._username_to_response_queue[ username ].get()

	def has_user_requests( self ) :
		return not self._request_queue.empty()

	def has_server_response( self, user_account ) :
		username = user_account.username

		if username not in self._username_to_response_queue :
			return False

		return not self._username_to_response_queue[ username ].empty()
