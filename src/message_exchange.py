import core


UR_SEND_MESSAGE = 6

SR_MESSAGING_FAILED_USER_IS_NOT_REGISTERED = 13
SR_MESSAGING_FAILED_USER_IS_OFFLINE = 14
SR_MESSAGING_PASSED = 15
SR_MESSAGING_A_MESSAGE_CAME = 16


class SrvSendCommandParser :
    # '$ send <username> <text>'
    # '$ send tom "Hello"'
    # '$ send "Hello, my friend!" tom'
    # '$ srv send bob "hi"' -> show info message if not logged in.
    def parse( self, line : str ) :
        line = line.strip()

        parts = line.split("\"")

        if len(parts) == 3:
            p0 = parts[0].strip()
            p2 = parts[2].strip()

            if p2 == '':
                words0 = p0.split()

                if len(words0) == 2 and words0[0] == 'send':
                    username = words0[1]
                else:
                    return ( False, )
            else:
                words0 = p0.split()
                words2 = p2.split()

                if len(words0) == 1 and p0 == 'send' and len(words2) == 1:
                    username = p2
                else:
                    return ( False, )

            text = parts[1]

            request = core.UserRequest(
                None,
                UR_SEND_MESSAGE,
                data=[username, text]
            )

            return True, request

        return ( False, )
