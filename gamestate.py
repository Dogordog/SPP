import re
from messageparser import MessageParser
from action import Action
from enums import ActionType, Round

class GameState(object):

    def __init__(self, message):
        self.message_parser = MessageParser(message)
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
        self._setup()
        # after setting up basic data structure, start to do each action and update data structure

        for action in self.action_list:
            self.do_action(action)
        x=1

    def _setup(self):
        self.spent = [50, 100, 0, 0, 0, 0]
        self.active = [True] * 6
        self.fold = [False] * 6
        self.allin = [False] * 6
        self.pot = 150
        self.max_bet = 100
        self.min_bet = 50
        self.current_player = 2 # player at seat 2 is first player to act in PREFLOP round
        self.finished = False
        self.round = Round.PREFLOP
        self.boards = [[],] # first round have no board cards
        self.holes = [[]]*6 # initialize hole array for 6 players
        self.min_no_limit_raise_to = 999 # todo
        self.max_no_limit_raise_to = 20000
        # fill hole array according to

    def do_action(self, action):
        # [1.0] do action, update player [spent] and [active]
        if action.type == ActionType.CALL:
            self.spent[self.current_player] = self.max_bet
            # if current player called ALLIN action -> not active
            if self.max_bet == 20000:
                self.active[self.current_player] = False
                self.allin[self.current_player] = True
        #if current player folded -> not active
        elif action.type == ActionType.FOLD:
            self.active[self.current_player] = False
            self.fold[self.current_player] = True
        else:
            self.spent[self.current_player] = action.amount
            # if current player raised to stack size -> not active
            if action.amount == 20000:
                self.active[self.current_player] = False
                self.allin[self.current_player] = True
            # a raise action happened, min_no_limit_raise_to need to be updated
            # todo

        # [2.0] update {pot}
        self.pot = sum(self.spent)

        # [3.0] if all active player spent same amount, which means they are reaching next round
        # todo [update round, update current player, then return]

        # update {current player}, find next active player
        # if more than one active player left, find next active player
        if self.active.count(True) > 1:
            # game is not finished yet
            # find next active player
            next_player = (self.current_player + 1) % 6
            while (self.active[next_player] == False):
                next_player = (next_player + 1) % 6
        elif self.active.count(True) == 1:
            # game may finish now
            # if there is no all-in player, which means other players all folded, only one player left

            # else, there are all-in player, the only one player who is active is the next current player
        else:
            # active player number is 0, which means they are at least one player all-in, the rest are folded
            # game is finished



    def get_betting_action(self, rd=None):

        pattern = re.compile(r'r\d+|f|c')
        if not rd:
            betting_action = []
            for string in self.betting_string:
                # parse string into single action string
                current_round_action = []
                for m in pattern.finditer(string):
                    current_round_action.append(m.group())
                betting_action.append(current_round_action)
            return betting_action
        else:
            string = self.betting_string[rd]
            current_round_action = []
            # parse string into sigle action string
            for m in pattern.finditer(string):
                current_round_action.append(m.group())
            return current_round_action

    # who just did an action
    def get_current_player(self):
        return self.current_player

    # return active player
    # a list containing True/False
    def get_active_player(self):
        pass

    def get_active_player_number(self):
        pass

    def get_max_bet(self):
        pass

    def get_min_bet(self):
        pass

    def get_pot(self):
        pass

    def get_next_valid_raise_size(self):
        pass

g = GameState('MATCHSTATE:1:31:r300r900r3000/r4000cccfrcr30000/fcr200:|JdTc')
