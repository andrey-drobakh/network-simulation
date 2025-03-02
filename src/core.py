UR_REGISTER = 0
UR_SEND_ACCOUNT_PASSWORD = 1
UR_CONFIRM_ACCOUNT_PASSWORD = 2
UR_LOGIN = 3
UR_LOGIN_SEND_ACCOUNT_PASSWORD = 4
UR_LOGOUT = 5

SR_REGISTRATION_PASSED = 0
SR_REGISTRATION_FAILED_USER_SIGNED = 1
SR_REGISTRATION_FAILED_A_USER_LOGGED = 2
SR_REGISTRATION_ACCOUNT_PASSWORD_NOT_GIVEN = 3
SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRM = 4
SR_REGISTRATION_ACCOUNT_PASSWORD_CONFIRMATION_FAILED = 5
SR_LOGIN_ACCOUNT_PASSWORD_TO_ASK = 6
SR_LOGIN_FAILED_USER_NOT_REGISTERED = 7
SR_LOGIN_FAILED_A_USER_LOGGED = 8
SR_LOGIN_PASSED = 9
SR_LOGIN_FAILED_WRONG_PASSWORD = 10
SR_LOGOUT_PASSED = 11
SR_LOGOUT_FAILED_USER_NOT_LOGGED_IN = 12


class UserAccount :
	def __init__( self, username, password = None ) :
		self.username = username
		self.password = password


class UserRequest :
	def __init__( self,
				  requester_account : UserAccount,
				  user_request_type,
				  data = None ) :
		self.requester_account = requester_account
		self.ur_type = user_request_type
		self.data = data


class ServerResponse :
	def __init__( self,
				  server_response_type,
				  destination_account : UserAccount,
				  data = None,
				  error_message = "" ) :
		self.sr_type = server_response_type
		self.destination_account = destination_account
		self.data = data
		self.error_message = error_message
