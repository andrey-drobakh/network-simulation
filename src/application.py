from server import Server
from cli_client.cli_client import CLIClient
from cli_client.cli_client_manager import ClientManager
from cli_client import parsers
from cli_client.command_reader import CommandReader
from dispatcher import Dispatcher
from terminal import TerminalWindow
import terminal
from message_exchange import SrvSendCommandParser
from simulation import Simulation

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


ctrl_t_is_pressed = False
def ctrl_t_binding(
		mainframe,
		command_reader : CommandReader,
		dispatcher : Dispatcher,
		client_manager : ClientManager
) :
	global ctrl_t_is_pressed

	print( "Ctrl-T pressed" )

	if ctrl_t_is_pressed :
		print( "No effect!" )

		return

	tw_2 = TerminalWindow( mainframe )

	cli_client = CLIClient(
		command_reader=command_reader,
		dispatcher=dispatcher
	)

	cli_client.set_window( tw_2 )
	client_manager.add_client( cli_client )

	text_widget_2 = tw_2._text_widget

	text_widget_2.grid(
		row = 0,
		column = 2,
		padx = 10,
		pady = 10,
		sticky = "news",
	)

	text_widget_2.focus()

	mainframe.grid_columnconfigure(2, weight=1)

	tw_2._text_widget.bind("<Return>", lambda e: cli_client.handle_enter_keystroke())

	ctrl_t_is_pressed = True


class Application :
	def __init__( self ):
		self.root = tk.Tk()
		self.root.title("Terminal")

		self.root.columnconfigure(0, weight=1)
		self.root.rowconfigure(0, weight=1)

		# set_main_window_location(root)
		self.root.geometry("1300x800")
		# self.root.attributes( "-fullscreen", True )

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

		command_reader = CommandReader()
		command_reader.add_parser(parsers.SrvRegisterCommandParser())
		command_reader.add_parser(parsers.SrvLoginCommandParser())
		command_reader.add_parser(parsers.SrvLogoutCommandParser())
		command_reader.add_parser(SrvSendCommandParser())

		cli_client = CLIClient(
			command_reader=command_reader,
			dispatcher=dispatcher
		)

		cli_client_2 = CLIClient(
			command_reader=command_reader,
			dispatcher=dispatcher
		)

		terminal_windows = []

		terminal_window = TerminalWindow(mainframe)

		cli_client.set_window(terminal_window)

		# Bindings
		terminal_window._text_widget.bind("<Return>", lambda e: cli_client.handle_enter_keystroke())
		mainframe.bind_class("Text", "<Return>", lambda e: None)
		mainframe.bind_class("Text", "<Up>", lambda e: None)
		mainframe.bind_class("Text", "<Down>", lambda e: None)
		mainframe.bind_class("Text", "<Control-Key-t>", lambda e: None)
		mainframe.bind_class("Text", "<BackSpace>", lambda  e: None)
		mainframe.bind_class("Text", "<Left>", lambda e: None)

		self.server = Server(dispatcher)

		self.client_manager = ClientManager()
		self.client_manager.add_client( cli_client )

		self.simulation = Simulation(dispatcher)

		self.root.bind("<Control-Key-t>", lambda e: ctrl_t_binding(
			mainframe,
			command_reader,
			dispatcher,
			self.client_manager))

	def run( self ) :
		self.server.run()
		self.client_manager.run()
		self.simulation.run()

		print("Main Loop started ...")

		self.root.mainloop()

		print("... Main Loop stopped!")

		self.server.stop()
