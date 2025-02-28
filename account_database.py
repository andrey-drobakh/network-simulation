import os


class AccountDatabase :
	def __init__( self, db_file_path : str ) :
		self._db_file_path = db_file_path
		self._data = {}
		self._count = 0

		self._read_db_file()

	def contains( self, username ) :
		if username in self._data :
			return True

		return False

	def get_password( self, username ):
		return self._data[ username ]

	def add_account( self, user_account ) :
		self._data[ user_account.username] = user_account.password

		self._count += 1

		f = open( self._db_file_path, 'a' )

		f.write( "\n\n#" )
		f.write( str( self._count ) )
		f.write( "\n" )
		f.writelines( f"username : { user_account.username }")
		f.write( "\n" )
		f.writelines( f"password : { user_account.password }")

		f.close()


	def _read_db_file( self ) :
		file_path = self._db_file_path

		if os.stat( file_path ).st_size == 0 :
			return

		f = open( file_path, "r" )
		
		for line in f :
			if len( line ) <= 1 :
				continue

			words = line.split()
			if words[ 0 ] == "username" :				
				username = words[ 2 ]

				continue

			if words[ 0 ] == "password" :
				password = words[ 2 ]

				self._data[ username ] = password

				self._count += 1

		f.close()