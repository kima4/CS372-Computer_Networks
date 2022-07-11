# Alexander Kim, kima4
# CS372 Programming Assignment 4

# the connection and socket code is largely taken from K&R, Chapter 2.7.2 Socket Programming with TCP,
# specifically TCPServer.py

from socket import *
from battleship import *


HOST = 'localhost'
PORT = 7534
RECV_BUFFER = 1024
BATTLESHIP_CMD = '/bs'

# header so client knows to not ask user for input in certain circumstances
CLIENT_SKIP = 'results~'


# looks for messages sent by the client and only sends the message once all characters are found
def listen(connect_socket):
    message = ''

    msg_start = connect_socket.recv(RECV_BUFFER).decode()

    # parse the beginning to determine how many characters to look for
    msg_length = int(msg_start[:msg_start.find('|')])
    message += msg_start[msg_start.find('|') + 1:]

    # keep looking for incoming data while the message length is shorter than expected
    while len(message) < msg_length:
        message += connect_socket.recv(RECV_BUFFER).decode()

    return message


# takes a plain message and adds a header to it that describes how long it is for the receiver to know
def create_message(msg_body):
    message = str(len(msg_body)) + '|' + msg_body
    return message


# prompt user for input, adds the header, and sends it
def speak(connect_socket):

    msg_body = input('>')

    # flag to determine if a genuine battleship request is being sent
    bs_cmd = False

    # if the user input is the battleship command, let the receiver know to not prompt client for input yet
    if msg_body == BATTLESHIP_CMD:
        msg_body = CLIENT_SKIP + msg_body
        bs_cmd = True
    message = create_message(msg_body)
    connect_socket.send(message.encode())

    # this is done this way so that it won't accidentally trigger if the server user types 'results~/bs'
    if bs_cmd:
        return BATTLESHIP_CMD

    return msg_body


# creates prompt for setting up battleship game with the ship name and length
def set_up_prompt(player_prompt, ship):
    prompt = player_prompt.replace('X', str(ship[1])).replace('SHIP', ship[0])
    return prompt


# sets up the game of battleship by having both players place their ships down
def set_up_game(connect_socket, b):
    print(b)
    ships = b.get_ship_types()

    player_prompt = 'Give coordinates separated by a colon to place your X space long SHIP on the board\n' \
                    'e.g. to place a ship from G3 to G7, enter g3:g7\n'

    # server player setup
    result = ''
    for ship in ships:
        status = -1
        while status != 0:  # status values other than 0 are errors
            print(result)
            print(set_up_prompt(player_prompt, ship))
            spaces = input('>')
            if spaces == '/q':  # can still quit using /q
                return '/q'
            status = b.add_ship(True, ship[0], ship[1], spaces)
            result = b.ship_messages(ship[0], status)
            print(b)
    print(result)
    print('Wait for your opponent to finish placing their ships...')

    # client player setup
    result = ''
    for ship in ships:
        status = -1
        while status != 0:
            # sending the prompts to the client through the socket connection
            msg_body = b.board_to_strings(False) + '\n'
            msg_body += set_up_prompt(player_prompt, ship)
            msg_body += result
            message = create_message(msg_body)
            connect_socket.send(message.encode())
            spaces = listen(connect_socket)
            if spaces == '/q':
                return '/q'
            status = b.add_ship(False, ship[0], ship[1], spaces)
            result = b.ship_messages(ship[0], status)

    # show client final setup, skips so that the server player always goes first
    msg_body = CLIENT_SKIP
    msg_body += b.board_to_strings(False) + '\n'
    msg_body += result
    message = create_message(msg_body)
    connect_socket.send(message.encode())
    return 'game set up complete'


# prompts the server user for a space to attack and sends the results to both players
def server_turn(connect_socket, b):
    def_result = ''

    while def_result == '':  # def_result will remain empty as long as an invalid attack is made
        print('Your turn! Fire Away!\nAttack a space by entering its coordinates, e.g. B4\n')
        space = input('>')
        if space == '/q':
            return '/q'

        atk_result, def_result = b.turn(True, space)
        print(atk_result)

    message = create_message(CLIENT_SKIP + def_result)
    connect_socket.send(message.encode())
    return 'server turn over'


# prompts the client user for a space to attack and sends the results to both players
# the logic for this is more or less the same as for server_turn(), but the prompts are sent through
# and answers received from the client via the socket connection
def client_turn(connect_socket, b):
    def_result = ''

    player_prompt = 'Your turn! Fire Away!\nAttack a space by entering its coordinates, e.g. B4\n'

    atk_result = ''

    while def_result == '':
        message = create_message(atk_result + player_prompt)
        connect_socket.send(message.encode())
        space = listen(connect_socket)
        if space == '/q':
            return '/q'
        atk_result, def_result = b.turn(False, space)
        atk_result += '\n'

    message = create_message(CLIENT_SKIP + atk_result)
    connect_socket.send(message.encode())
    print(def_result)
    return 'client turn over'


# contains the main structure for the battleship game, calls other functions to set the game up
# and perform tasks for each turn
# displays the winner of the game to both players
def battleship(connect_socket):
    b = Battleship()
    set_up_status = set_up_game(connect_socket, b)
    if set_up_status == '/q':
        return '/q'

    end_banner = '*****************************************************\n' \
                 '                    SERVER WINS!!\n' \
                 '*****************************************************'

    while not b.is_finished():
        print('Server Turn')
        message = server_turn(connect_socket, b)
        if message == '/q':
            return '/q'

        if b.is_finished():
            break

        print('Client Turn')
        message = client_turn(connect_socket, b)
        if message == '/q':
            return '/q'

    p1, p2 = b.get_ships_left()
    if p1 == 0:
        end_banner = end_banner.replace('SERVER', 'CLIENT')

    print(end_banner)
    message = create_message(end_banner)
    connect_socket.send(message.encode())
    return 'Now back to your regularly scheduled text chat'


# contains the main structure for the chat messages between client and server
# keeps a lookout for the special commands /q and /bs and acts appropriately when found
# otherwise just alternates sending and receiving messages
def communicate(server_socket):
    exchanges = 0

    connect_socket, addr = server_socket.accept()
    print('Connected by (\'%s\', %s)' % addr)
    print('Waiting for message...')

    while True:
        message = listen(connect_socket)

        # if the client asks to play battleship
        if message == BATTLESHIP_CMD:
            message = battleship(connect_socket)

            # after the game finishes, determines what to do
            if message.startswith('Now'):
                pass
            # if the game finished because someone entered /q, tell the client just in case
            else:
                connect_socket.send(create_message(message).encode())

        # if someone entered /q, exit the loop
        if message == '/q':
            break
        else:
            print(message)

        # if this is the first message the server is sending, give some guidance
        if exchanges == 0:
            print('Type /q to quit')
            print('Type ' + BATTLESHIP_CMD + ' to play Battleship')
            print('Enter message to send...')

        # send a message
        message = speak(connect_socket)

        # if the server asks to play battleship
        if message == BATTLESHIP_CMD:
            message = battleship(connect_socket)

            if message.startswith('Now'):
                print(message)
            else:
                connect_socket.send(create_message(message).encode())

        if message == '/q':
            break

        exchanges += 1

    connect_socket.close()


# creates the server socket, sets the socket reuse option, and binds it to the specified address
def create_server():
    server_port = PORT
    server_socket = socket(AF_INET, SOCK_STREAM)
    server_socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
    server_socket.bind(('', server_port))
    server_socket.listen(1)

    print('Server listening on: ' + HOST + ' on port: ' + str(server_port))

    return server_socket


# creates the server, starts communication, and closes the socket once communication is completed
def main():
    server_socket = create_server()
    communicate(server_socket)
    server_socket.close()


if __name__ == '__main__':
    main()