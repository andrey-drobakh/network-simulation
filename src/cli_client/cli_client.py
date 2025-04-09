import core
from cli_client.user_input_line_handler import UserInputLineHandler
from cli_client.user_input_line_handler import \
	TERMINAL_LINE_HANDLING_MODE_INPUT, \
	TERMINAL_LINE_HANDLING_MODE_COMMAND
from cli_client.server_response_handler import ServerResponseHandler
# from dispatcher import Dispatcher

from threading import Thread
from time import sleep


class CLIClient:
    def __init__(self, command_reader, dispatcher):
        self.user_account = None
        self._window = None

        self._command_reader = command_reader
        self._dispatcher = dispatcher
        self._user_input_line_handler = UserInputLineHandler(command_reader, dispatcher)
        self._server_response_handler = ServerResponseHandler(
            user_input_line_handler=self._user_input_line_handler,
            terminal_window=self._window
        )

    # 1. Get the terminal line.
    # 2. Make a user request.
    # 3. Wait for a server response.
    # 4. Handle the response.
    def handle_enter_keystroke(self):
        prefix = "CLIENT : "

        w = self._window

        line = w.get_line(self._user_input_line_handler.current_prompt_length)

        if line == '':
            w.display_current_prompt()

            return

        self._user_input_line_handler.handle(line)

        request = self._user_input_line_handler.current_user_request

        if request is None:
            print(prefix + "invalid command")

            w.display_error_message("invalid command")

            return

        m = self._user_input_line_handler.error_message
        if m is not None:
            w.display_error_message(m)
            self._user_input_line_handler.error_message = None

            return

    # """
    # Wait for a server response.
    # If we are using a client-notifying dispatcher,
    # client doesn't have to wait for a response, because
    # it will be notified by dispatcher, and this actually
    # will be done in the separate server thread.
    # """

    # ???
    def listen_to_dispatcher(self) -> core.ServerResponse:
        d = self._dispatcher
        user_account = self._user_input_line_handler.current_user_account

        while True:
            if d.has_server_response(user_account):
                return d.get_server_response(request.requester_account)

    def set_window(self, window):
        self._window = window
        self._user_input_line_handler.set_window(window)
        self._server_response_handler._window = window
