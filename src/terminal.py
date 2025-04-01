import tkinter as tk
from tkinter import ttk
from tkinter.font import Font


class TerminalWindow :
	def __init__( self, parent ) :
		self._text_font = Font( size = 20, family = "Mono" )

		self._text_widget = tk.Text(
 			parent, 
 			bg = 'brown', 
 			fg = 'yellow', 
 			font = self._text_font,
 			insertbackground = 'white' )

		self._scrollbar = tk.Scrollbar(
			parent,
			command = self._text_widget.yview
		)
		self._text_widget[ "yscrollcommand" ] = self._scrollbar.set

		self._text_widget.grid(
			row=0,
			column=0,
			sticky="news",
			padx=10,
			pady=10,
		)
		self._text_widget.focus()

		# self._scrollbar.grid(
		# 	row = 0,
		# 	column = 1,
		# 	sticky = "news",
		# )

		self._standard_prompt = "$ "
		self.prompt = self._standard_prompt

		self._display_initial_text()
		self._set_bindings()

	def get_line( self, prefix_length ) :
		line_number = self._get_caret_line_number()

		line = self._text_widget.get(
			f"{ line_number }.{ prefix_length }",
			'end'
		)
		line = line.strip()

		return line

	def display_error_message( self, message ) :
		current_line_number = self._get_caret_line_number()
		self._text_widget.insert(
 			f"{ current_line_number + 1 }.{ 0 }", "\nerror : " + message )
		self.display_current_prompt()

		self._scroll_down()

	def display_message( self, message ) :
		current_line_number = self._get_caret_line_number()
		self._text_widget.insert(
 	 		f"{ current_line_number + 1 }.{ 0 }", "\n" + message )
		self.display_current_prompt()

		self._scroll_down()

	def display_prompt( self, prompt ) :
		self._display_prompt( prompt )

		self._scroll_down()

	def display_current_prompt(self) :
		self._display_prompt(self.prompt)

		self._scroll_down()

	def reset_prompt( self ) :
		self.prompt = self._standard_prompt


	def _scroll_down(self) :
		line_number = self._get_caret_line_number()
		self._text_widget.see( f"{line_number}.0" )

	def _display_prompt( self, prompt ) :
		line_number = self._get_caret_line_number()
		self._text_widget.insert(
			f"{line_number + 1}.{0}",
			f"\n{prompt}"
		)

	def _backspace_binding( self ) :
		# print( "backspace" )
		line_number = self._get_caret_line_number()

		from_line_start_to_caret = self._text_widget.get(
			f"{line_number}.0", "insert")
		if len( from_line_start_to_caret ) > len( self.prompt ) :
			self._text_widget.delete( 'insert -1c' )

		print( "backspace :", self.prompt )

	def _left_key_binding( self ) :
		line_number = self._get_caret_line_number()

		from_line_start_to_caret = self._text_widget.get(
			f"{line_number}.0", "insert")
		if len( from_line_start_to_caret ) != len( self.prompt ) :
			self._text_widget.mark_set( "insert", "insert-1c" )

	def _get_caret_line_number( self ) :
		return int( self._text_widget.index( tk.INSERT ).split( '.' )[ 0 ] )

	def _set_bindings( self ) :
		self._text_widget.bind( "<BackSpace>", lambda e: self._backspace_binding() )
		self._text_widget.bind( "<Left>", lambda e: self._left_key_binding() )

	def _display_initial_text(self) :
		self._text_widget.insert( "1.0", self.prompt)
