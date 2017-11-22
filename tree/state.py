import re
from messageparser import MessageParser
from action import Action
from enums import ActionType, Round


class State(object):

    def __init__(self):

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
        self.next_round_flag = False
        self.call_number = 0

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
        self.next_round_flag = next_round_reaching_flag
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


# s = State()
