from server import Server
from client import CLIClient, TerminalCommandReader, \
	SrvRegisterCommandParser, \
	SrvLoginCommandParser, \
	SrvLogoutCommandParser
from dispatcher import Dispatcher
from terminal import TerminalWindow

import tkinter as tk
from tkinter import ttk


def set_main_window_location( root ) :
	# specify resolutions of both windows
	w0, h0 = 3840, 2160
	w1, h1 = 1920, 1080

	# set up a window for first display, if wanted
	# win0 = tk.Toplevel()
	# win0.geometry(f"{w0}x{h0}+0+0")

	# set up window for second display with fullscreen
	win1 = tk.Toplevel()
	# win1 = root
	win1.geometry(f"{w1}x{h1}+{w0}+0") # <- this is the key, offset to the right by w0
	win1.attributes("-fullscreen", True)


class Application :
	def __init__( self ):
		self.root = tk.Tk()
		self.root.title("Terminal")

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		# set_main_window_location(root)
		# self.root.geometry("1000x800")
		self.root.attributes( "-fullscreen", True )

		mainframe = tk.Frame(self.root, bg="black")
		mainframe.grid(
			row=0,
			column=0,
			sticky="news",
		)
		mainframe.grid_rowconfigure(0, weight=1)
		mainframe.grid_columnconfigure(0, weight=1)
		# mainframe.grid_columnconfigure(1, weight=1)

		dispatcher = Dispatcher()

		command_reader = TerminalCommandReader()
		command_reader.add_parser(SrvRegisterCommandParser())
		command_reader.add_parser(SrvLoginCommandParser())
		command_reader.add_parser(SrvLogoutCommandParser())

		cli_client = CLIClient(
			command_reader=command_reader,
			dispatcher=dispatcher
		)

		terminal_window = TerminalWindow(mainframe)

		cli_client.set_window(terminal_window)

		terminal_window._text_widget.bind("<Return>", lambda e: cli_client.handle_enter_keystroke())
		mainframe.bind_class("Text", "<Return>", lambda e: None)
		mainframe.bind_class("Text", "<BackSpace>", lambda e: terminal_window._backspace_binding())
		mainframe.bind_class("Text", "<Up>", lambda e: None)
		mainframe.bind_class("Text", "<Down>", lambda e: None)
		mainframe.bind_class("Text", "<Left>", lambda e: terminal_window._left_key_binding())

		terminal_window.show()

		self.server = Server(dispatcher)

	def run( self ) :
		self.server.run()

		print("Main Loop started ...")

		self.root.mainloop()

		print("... Main Loop stopped!")

		self.server.stop()
