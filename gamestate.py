import re
from messageparser import MessageParser
from action import Action
from enums import ActionType, Round

class GameState(object):

    def __init__(self, message):
        self.message_parser = MessageParser(message)
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
        self.spent = [50, 100, 0, 0, 0, 0]
        self.active = [True] * 6
        self.fold = [False] * 6
        self.allin = [False] * 6
        self.pot = 150
        self.max_bet = 100

        self.current_player = 2  # player at seat 2 is first player to act in PREFLOP round
        self.finished = False
        self.round = Round.PREFLOP
        self.boards = [[], ]  # first round have no board cards
        self.holes = [[]] * 6  # initialize hole array for 6 players
        self.min_no_limit_raise_to = 2 * 100
        self.max_no_limit_raise_to = 20000

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
        # [1.0] do action, update player [spent] and [active]
        if action.type == ActionType.CALL:
            self.spent[self.current_player] = self.max_bet
            self.call_number += 1
            # if current player called ALLIN action -> not active
            if self.max_bet == 20000:
                self.active[self.current_player] = False
                self.allin[self.current_player] = True

        #if current player folded -> not active
        elif action.type == ActionType.FOLD:
            self.active[self.current_player] = False
            self.fold[self.current_player] = True

        else: # must be a raise action
            self.call_number = 1
            # a raise action happened, min_no_limit_raise_to need to be updated
            if action.amount + action.amount - max(self.spent) > self.min_no_limit_raise_to:
                self.min_no_limit_raise_to = action.amount + action.amount - max(self.spent)
            # make sure it <= 20000
            self.min_no_limit_raise_to = min([self.min_no_limit_raise_to, 20000])
            # update {max_bet}
            self.max_bet = action.amount
            self.spent[self.current_player] = action.amount
            # if current player raised to stack size -> not active
            if action.amount == 20000:
                self.active[self.current_player] = False
                self.allin[self.current_player] = True

        # if all players choose all in, then game ends, which no active players
        if self.active.count(True) == 0:
            self.finished = True
            return

        # [3.0] if all active player spent same amount, which means they are reaching next round
        amount_set = set()
        for p, amount in zip(self.active, self.spent):
            if p:
                amount_set.add(amount)
        next_round_reaching_flag = len(amount_set) == 1 and self.call_number == self.fold.count(False)

        if next_round_reaching_flag:
            # reset call number
            self.call_number = 0
            # we are going to reach next round
            # if current round == 4, then there is no more next round and the game ends here
            if self.round == Round.RIVER:
                self.finished = True

            # there are next round
            else:
                # update round
                self.round += 1
                # update min_no_limit_raise_to
                self.min_no_limit_raise_to += self.max_bet
                self.min_no_limit_raise_to = min([self.min_no_limit_raise_to, 20000])
                # find next active player from seat 0
                next_player = 0
                while not self.active[next_player]:
                    next_player = (next_player + 1) % 6
                self.current_player = next_player
        else:
            # we are still at current round
            # update {current player}, find next active player

            # if more than one active player left, find next active player
            if self.active.count(True) > 1:
                # game is not finished yet
                # find next active player
                next_player = (self.current_player + 1) % 6
                while not self.active[next_player]:
                    next_player = (next_player + 1) % 6
                self.current_player = next_player
            elif self.active.count(True) == 1:
                # game may finish now
                # if there is no all-in player, which means other players all folded, only one player left
                if self.allin.count(True) == 0:
                    # game ends
                    self.finished = True
                # else, there are all-in player, the only one player who is active is the next current player
                else:
                    self.current_player = self.active.index(True)
            else:
                # active player number is 0, which means they are at least one player all-in, the rest are folded
                # game is finished
                self.finished = True


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

# str1 = 'MATCHSTATE:1:31:r300r900r3000ccccc/r9000ffffc/cc/cc:|JdTc||||/2c2d2h/3c/3d'
#s = "MATCHSTATE:4:2:fr16524cccc/cr16799r18449:||||Td6c|/Qd9sJc"
s = "MATCHSTATE:1:5:cccccc/cc:|4h2s||||"
g = GameState(s)
print(g.current_player)
print(g.active)
#
# print(g.get_next_valid_raise_size())
# print(g.finished)
# print(g.max_bet)