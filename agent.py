import socket
import sys
from gamestate import GameState
from action import Action
from random import choice
from strategy import Strategy

class Agent(object):

    def __init__(self, address):
        self.address = address
        self.version_string = 'VERSION:2.0.0\r\n'
        self.connection = self.connect()
        self.send_string(self.version_string)
        self.message = ""
        self.gamestate = None

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
            single_character = self.connection.recv(1)
            single_character = single_character.decode()
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
        self.gamestate = GameState(self.message)

        while not self.gamestate.finished:
            if self.gamestate.is_my_turn():
                # gamestate -> rules
                strategy = Strategy(self.gamestate)
                # rules -> strategy

                # strategy -> action

                # original message + action -> response
                # action = self.choose_random_action()
                response_string = self.generate_response(strategy.get_action())

                # send
                self.send_string(response_string)

            # else not my turn
                # do nothing
            # receive next message and update gamestate
            self.message = self.receive_string()
            self.gamestate = GameState(self.message)

    def choose_random_action(self):
        # CALL is always valid
        valid = [Action("c")]
        min_bet, max_bet = self.gamestate.get_next_valid_raise_size()

        # raise minimal amount or maximal amount
        if self.max_bet == 20000:
            valid.append(Action("f"))
        else:
            if min_bet == 20000:
                valid.append(Action("r20000"))
            else: # < 20000
                valid.append(Action("r" + min_bet))
                valid.append(Action("r" + max_bet))

        # fold
        if self.max_bet > self.gamestate.spent[self.gamestate.current_player]:
            valid.append(Action("f"))
        return choice(valid)

    def generate_response(self, action=None):
        response_string = ""
        if action is None:
            response_string = self.message + ":c\r\n"
        else:
            response_string = self.message + ":" + action.string + "\r\n"
        return response_string


def main(argv=None):
    assert (len(argv) == 4)
    ip = argv[1]
    port = argv[2]
    hand = argv[3]
    agent = Agent((ip, int(port)))
    agent.play_hands(int(hand))


if __name__ == '__main__':
    main(sys.argv)

