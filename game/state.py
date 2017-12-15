from game.enums import Round, ActionType
from game.action import Action

class State(object):

    def __init__(self):

        self.round = Round.PREFLOP
        self.spent = [100, 50]
        self.finished = False
        self.max_bet = 100
        self.call_number = 0
        self.current_player = 1
        self.min_no_limit_raise_to = 2 * 100
        self.max_no_limit_raise_to = 20000

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
                # no more future round
                if self.round == Round.RIVER:
                    self.finished = True
                else:
                # still has future round
                    self.current_player == 0
                    self.call_number = 0
                    # update round
                    self.round += 1
                    # update min_no_limit_raise_to
                    self.min_no_limit_raise_to = self.max_bet + 100 # max_spent + BB
                    self.min_no_limit_raise_to = min([self.min_no_limit_raise_to, 20000])
        elif action.type == ActionType.RAISE:
            self.call_number = 1
            self.spent[self.current_player] = action.amount
            self.max_bet = action.amount

            # a raise action happened, min_no_limit_raise_to need to be updated
            if action.amount + action.amount - max(self.spent) > self.min_no_limit_raise_to:
                self.min_no_limit_raise_to = action.amount + action.amount - max(self.spent)
            # make sure it <= 20000
            self.min_no_limit_raise_to = min([self.min_no_limit_raise_to, 20000])

    def get_pot(self):
        return sum(self.spent)