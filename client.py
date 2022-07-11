# Alexander Kim, kima4
# CS372 Programming Assignment 4

# the connection and socket code is largely taken from K&R, Chapter 2.7.2 Socket Programming with TCP,
# specifically TCPClient.py

from socket import *


HOST = 'localhost'
PORT = 7534
RECV_BUFFER = 1024
BATTLESHIP_CMD = '/bs'

# header so client knows to not ask user for input in certain circumstances
CLIENT_SKIP = 'results~'


# looks for messages sent by the client and only sends the message once all characters are found
def listen(client_socket):
    message = ''

    msg_start = client_socket.recv(RECV_BUFFER).decode()

    # parse the beginning to determine how many characters to look for
    msg_length = int(msg_start[:msg_start.find('|')])
    message += msg_start[msg_start.find('|') + 1:]

    # keep looking for incoming data while the message length is shorter than expected
    while len(message) < msg_length:
        message += client_socket.recv(RECV_BUFFER).decode()

    return message


# takes a plain message and adds a header to it that describes how long it is for the receiver to know
def create_message(msg_body):
    message = str(len(msg_body)) + '|' + msg_body
    return message


# prompt user for input, adds the header, and sends it
def speak(client_socket):
    msg_body = input('>')
    message = create_message(msg_body)
    client_socket.send(message.encode())
    return msg_body


# contains the main structure for the client side of the battleship game
# the logic is close enough to the function communicate() that I probably didn't
# need to have it as its own function, but having it separated makes it much
# easier to read and prevents communicate() from having more nested if-else
# statements than it already has
def battleship(client_socket):
    displaying_results = True

    print('Wait for your opponent to finish placing their ships...')

    while True:
        # if displaying results, the server does not want a response back so skip
        if not displaying_results:
            message = speak(client_socket)
            if message == '/q':
                return '/q'

        displaying_results = False

        message = listen(client_socket)
        if message == '/q':
            return '/q'

        # check to see if the message should be responded to
        if message.startswith('results~'):
            message = message[8:]  # removing the heading
            print(message)
            displaying_results = True

        # check to see if the game is over
        elif message.startswith('********'):
            print(message)
            return 'Now back to your regularly scheduled text chat'
        else:
            print(message)


# contains the main structure for the chat messages between client and server
# keeps a lookout for the special commands /q and /bs and acts appropriately when found
# otherwise just alternates sending and receiving messages
def communicate(client_socket):
    exchanges = 0

    print('Type /q to quit')
    print('Type ' + BATTLESHIP_CMD + ' to play Battleship')
    print('Enter message to send...')

    while True:

        message = speak(client_socket)

        if message == BATTLESHIP_CMD:
            message = battleship(client_socket)

            if message.startswith('Now'):
                print(message)
            else:
                client_socket.send(create_message(message).encode())

        if message == '/q':
            break
        elif exchanges == 0:
            print('Waiting for message...')

        message = listen(client_socket)

        if message == CLIENT_SKIP + BATTLESHIP_CMD:
            message = battleship(client_socket)
            if message.startswith('Now'):
                pass
            else:
                client_socket.send(create_message(message).encode())
        if message == '/q':
            break
        else:
            print(message)

        exchanges += 1


# creates the client socket and displays the address specifics
def create_client():
    client_port = PORT
    client_socket = socket(AF_INET, SOCK_STREAM)
    client_socket.connect((HOST, PORT))

    print('Connected to: ' + HOST + ' on port: ' + str(client_port))

    return client_socket


# creates the client, starts communication, and closes the socket once communication is completed
def main():
    client_socket = create_client()
    communicate(client_socket)
    client_socket.close()


if __name__ == '__main__':
    main()
