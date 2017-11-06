import socket
import sys

class Agent(object):

    def __init__(self, address):
        self.address = address
        self.version_string = b'VERSION:2.0.0\r\n'
        self.connection = self.connect()
        self.send_version_string()
        self.message = ""

    # connect to acpc server address=(ip, port)
    def connect(self):
        connection = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        connection.connect(self.address)
        return connection

    # encode string to binary string and send it to acpc server
    def send_string(self, string):
        self.connection.send(string.encode())

    def receive_string(self):
        message = ""

        while True:
            single_character = self.connection.recv(1).decode()
            message += single_character

            count = message.count("\n")
            if count < 1:
                continue
            elif count == 1:
                message = message.strip("\r\n")
                break
        return message

    def play_hands(self, hand):
        for i in range(hand):
            self.play_one_hand()

    def play_one_hand(self):
        self.message = self.receive_string()

        # message -> gamestate

        # while game not finished
            # if my turn

                # gamestate -> rules

                # rules -> strategy

                # strategy -> action

                # original message + action -> response
                response_string = self.generate_response(action=None)

                # send
                self.send_string(response_string.encode())

            # else not my turn
                # do nothing

    def generate_response(self, action=None):
        response_string = ""
        if not action:
            response_string = self.message + ":c\r\n"
        # else todo
        return response_string


def main(argv=None):
    assert (len(argv) == 4)
    ip = argv[1]
    port = argv[2]
    hand = argv[3]
    agent = Agent((ip, port))
    agent.play_hands(hand)

if __name__ == '__main__':
    main(sys.argv)

