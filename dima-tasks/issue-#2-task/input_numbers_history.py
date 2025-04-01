def run_program() :
    exit_lines = ( 'q', 'quit', 'exit' )
    input_history_lines = ( '<=', '=>', 'back', 'forth' )
    sx = dict()

    while True :
        input_line = input( "Enter a number : " )

        if input_line == '' :
            continue

        # Если ввод не является зарезервированным словом,
        # то есть если это число или что-то другое.
        if input_line not in input_history_lines and input_line not in exit_lines :
            # add input line to history

            d = len(sx)
            sx[d + 1] = input_line  # присваиваем значение инпут ключу по счетчику

        elif input_line in ( '<=', 'back' ) and sx:
            if sx and d >= 0:
                print(sx.get(d, 'НАЧАЛО ИСТОРИИ, ЛИСТАЙТЕ ВПЕРЁД!'))
                d -= 1
            else:
                print('НАЧАЛО ИСТОРИИ, ЛИСТАЙТЕ ВПЕРЁД!')

        elif input_line in ( '=>', 'forth' ) and sx:
            if sx and d < len(sx):
                d += 1
                print(sx.get(d+1, 'КОНЕЦ ИСТОРИИ, ЛИСТАЙТЕ НАЗАД!'))
            else:
                print('КОНЕЦ ИСТОРИИ, ЛИСТАЙТЕ НАЗАД!')

        elif input_line in exit_lines :
            break

    print( "Stopped!" )


run_program()
