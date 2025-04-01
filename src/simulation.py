from threading import Thread
from time import sleep
import random

import core
from dispatcher import Dispatcher
import message_exchange as msg


"""
The goal of the Simulation class is to provide one or
a number of additional fake users to the network. They
will be able to talk to the application user. Simulation
has to make them responsive and smart enough.
"""
class Simulation :
    def __init__(self, dispatcher : Dispatcher ):
        self._dispatcher = dispatcher

        self._t = Thread(
            target = self._run,
            daemon = True,
        )

        self._greeting_messages = [
            "Hello!",
            "How are you?!",
            "Hi! Let's play!",
            "Hi! Any plans today?",
        ]

    def run( self ) :
        self._t.start()

    def _run(self):
        prefix = "SIMULATION : "
        print(prefix + "started")

        # self._run_sending_mode( "tom", "a3", "andrey" )
        self._run_sending_and_answering_mode( "tom", "a3", "andrey" )

    def _login( self, username, password ) :
        prefix = "SIMULATION : "

        # 1. The client logs in.
        account = core.UserAccount(username)

        login_request = core.UserRequest(
            account,
            core.UR_LOGIN,
            data = username
        )

        d = self._dispatcher

        d.add_user_request(login_request)

        response : core.ServerResponse

        response = self._wait_for_server_response( account )

        print(prefix + f"response {response.sr_type}")

        # If the server is asking about password,
        # then send a new request with the password.
        if response.sr_type == core.SR_LOGIN_ACCOUNT_PASSWORD_TO_ASK:
            login_password_request = core.UserRequest(
                account,
                core.UR_LOGIN_SEND_ACCOUNT_PASSWORD,
                password
            )

            d.add_user_request(login_password_request)
        else:
            print(prefix + "login error : server didn't ask for password")

        response = self._wait_for_server_response( account )

        if response.sr_type != core.SR_LOGIN_PASSED :
            print( prefix + "login error : wrong password given" )

    def _logout( self, username ) :
        prefix = "SIMULATION : "

        d = self._dispatcher

        logout_request = core.UserRequest(
            core.UserAccount( username ),
            core.UR_LOGOUT
        )

        d.add_user_request( logout_request )

        response = self._wait_for_server_response( logout_request.requester_account )

        if response.sr_type != core.SR_LOGOUT_PASSED :
            print( prefix + "logout error : logout is not done" )

    def _wait_for_server_response( self, requester_account : core.UserAccount ) -> core.ServerResponse :
        d = self._dispatcher

        while True :
            if d.has_server_response( requester_account ) :
                return d.get_server_response( requester_account )

    def _send_message_from_to( self, sender : str, receiver : str, message : str ) :
        request = core.UserRequest(
            core.UserAccount( sender ),
            msg.UR_SEND_MESSAGE,
            data=[receiver, message]
        )

        self._dispatcher.add_user_request(request)

    def _run_sending_mode( self, sender : str, sender_password : str, receiver : str ) :
        username1 = sender
        password1 = sender_password
        account1 = core.UserAccount(username1, password1)

        self._login(username1, password1)

        while True:
            self._send_message_from_to(
                username1,
                receiver,
                random.choice(self._greeting_messages)
            )

            response = self._wait_for_server_response(account1)

            sleep(4.0)

    def _run_sending_and_answering_mode( self, sender : str, sender_password : str, receiver : str ) :
        username1 = sender
        password1 = sender_password

        self._login(username1, password1)

        while True:
            self._send_message_from_to(
                username1,
                receiver,
                random.choice(self._greeting_messages)
            )

            account1 = core.UserAccount(username1, password1)
            response : core.ServerResponse
            response = self._wait_for_server_response(account1)

            # Check for responses.
            d = self._dispatcher
            if d.has_server_response(account1):
                print( "abcde" )
                response = d.get_server_response(account1)

                # Handle the response.
                if response.sr_type == msg.SR_MESSAGING_A_MESSAGE_CAME :
                    sender2 = response.data[ 1 ].username

                    self._send_message_from_to(
                        username1,
                        sender2,
                        random.choice(self._greeting_messages)
                    )

                    response = self._wait_for_server_response(account1)
                else :
                    # print( f"\nresponse {response.sr_type}\n" )
                    pass

            sleep(4.0)


