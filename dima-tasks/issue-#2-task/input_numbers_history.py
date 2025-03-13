

def run_program() :
    exit_lines = ( 'q', 'quit', 'exit' )
    input_history_lines = ( '<=', '=>', 'back', 'forth' )

    while True :
        input_line = input( "Enter a number : " )

        if input_line == '' :
            continue

        # Если ввод не является зарезервированным словом,
        # то есть если это число или что-то другое.
        if input_line not in input_history_lines and input_line not in exit_lines :
            # add input line to history
            pass
        elif input_line in ( '<=', 'back' ) :
            # print previous input line
            pass
        elif input_line in ( '=>', 'forth' ) :
            # print next input line
            pass
        elif input_line in exit_lines :
            break

    print( "Stopped!" )


run_program()