import re
from game.messageparser import MessageParser
from game.action import Action
from game.enums import ActionType, Round


class GameState(object):

    def __init__(self, message):
        self.message_parser = MessageParser(message)
        # hole, [['2c', '2d'],...] for 6 players
        self.hole = self.message_parser.hole
        # board ['2c', '2d', '2h', ...] for at most 5 board cards
        self.board = self.message_parser.board
        self.viewing_player = self.message_parser.get_position()
        self.betting_string = self.message_parser.get_betting_string(rd=None)
        self.board_string = self.message_parser.get_board_string(rd=None)
        # a two-dimension list, dim-1 is round, dim-2 is i-th action of a round
        self.betting_action = self.get_betting_action()
        # a one-dimension list, store each {action string} as an element
        self.action_list = []
        # store each {action object} of all round actions in a one-dimension list
        for each_round_action in self.betting_action:
            for action in each_round_action:
                self.action_list.append(Action(action))
        # set up basic data structure
        self.spent = [50, 100]

        self.pot = 150
        self.max_bet = 100

        self.current_player = 1
        self.finished = False
        self.round = Round.PREFLOP
        self.boards = None  # first round have no board cards
        self.holes = None  # hole array for 6 players
        self.min_no_limit_raise_to = 2 * 100
        self.max_no_limit_raise_to = 20000

        self.next_round_flag = False

        self.call_number = 0

        # update [hole] and [board]
        self.holes = self.message_parser.get_hole_card(position=None)
        self.boards = self.message_parser.get_board_card(rd=None)

        # after setting up basic data structure, start to do each action and update data structure
        cnt = 0
        for action in self.action_list:
            cnt+=1
            self.do_action(action)

    def do_action(self, action):

        if action.type == ActionType.FOLD:
            self.finished = True
        elif action.type == ActionType.CALL:
            self.spent[self.current_player] = self.max_bet
            if self.max_bet == 20000:
                self.finished = True
            else:
                self.call_number += 1
            # if we are reaching next round
            if self.call_number == 2:
                if self.round == Round.RIVER:
                   self.finished = True
                else:
                    self.current_player == 0
                    self.call_number = 0
                    # update round
                    self.round += 1
                    # update min_no_limit_raise_to
                    self.min_no_limit_raise_to = self.max_bet + 100
                    self.min_no_limit_raise_to = min([self.min_no_limit_raise_to, 20000])
            else:
                self.current_player = 1 - self.current_player
        elif action.type == ActionType.RAISE:
            self.call_number = 1

            # a raise action happened, min_no_limit_raise_to need to be updated
            if action.amount + action.amount - max(self.spent) > self.min_no_limit_raise_to:
                self.min_no_limit_raise_to = action.amount + action.amount - max(self.spent)
                # make sure it <= 20000
                self.min_no_limit_raise_to = min([self.min_no_limit_raise_to, 20000])

            self.spent[self.current_player] = action.amount
            self.max_bet = action.amount
            self.current_player = 1 - self.current_player




    # split betting string into single betting actions
    # if rd=None, by default, handle betting string of all rounds
    def get_betting_action(self, rd=None):
        pattern = re.compile(r'r\d+|f|c')
        if rd is not None:
            string = self.betting_string[rd]
            current_round_action = []
            # parse string into sigle action string
            for m in pattern.finditer(string):
                current_round_action.append(m.group())
            return current_round_action
        else:
            betting_action = []
            for string in self.betting_string:
                # parse string into single action string
                current_round_action = []
                for m in pattern.finditer(string):
                    current_round_action.append(m.group())
                betting_action.append(current_round_action)
            return betting_action

    # who just did an action
    def get_current_player(self):
        return self.current_player

    # return active player
    # a list containing True/False
    def get_active_player(self):
        return self.active

    def get_active_player_number(self):
        return self.active.count(True)

    def get_max_bet(self):
        return self.max_bet

    def get_min_bet(self):
        return self.min_bet

    def get_pot(self):
        return sum(self.pot)

    def get_next_valid_raise_size(self):
        return [self.min_no_limit_raise_to, self.max_no_limit_raise_to]

    def is_my_turn(self):
        return self.viewing_player == self.current_player


s = 'MATCHSTATE:0:0:r200:5d5c|'
gs = GameState(s)
pass