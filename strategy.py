import pandas as pd
from gamestate import GameState
from enums import Round
from ctypes import cdll, c_int, c_double
from action import Action

dll = cdll.LoadLibrary("./so/eval.so")


class Strategy(object):

    def __init__(self, gamestate):
        self.d = {'2':0,'3':1,'4':2,'5':3,'6':4,'7':5,'8':6,'9':7,'T':8,'J':9,'Q':10,'K':11,'A':12}
        self.gamestate = gamestate
        self.win_table = pd.read_csv("./data/preflop/2346players.csv", index_col=0, header=0)
        self.round = gamestate.round
        self.player_number = gamestate.fold.count(False)
        self.my_hole = gamestate.holes[self.gamestate.viewing_player]
        self.my_hole_str = gamestate.hole[self.gamestate.viewing_player]
        self.boards = gamestate.boards
        self.pot = gamestate.pot
        self.max_bet = gamestate.max_bet
        self.my_bet = gamestate.spent[self.gamestate.viewing_player]

    def get_action(self):
        win_pr = self.get_win_pr()
        e_payoff = (self.max_bet * (self.player_number - 1)) * win_pr - (self.max_bet - self.my_bet) * (1-win_pr)

        if e_payoff < 0:
            return Action("f")
        elif e_payoff / self.pot < 0.2:
            return Action("c")
        elif e_payoff / self.pot < 0.4:
            return Action("c")
        else:
            return Action("c")

    def get_win_pr(self):

        if self.round == Round.PREFLOP:
            c1 = self.my_hole_str[0]
            c2 = self.my_hole_str[1]

            if self.d[c1[0]] < self.d[c2[0]]:
                c1, c2 = c2, c1
            suited = "s" if c1[1] == c2[1] else "u"
            key = c1[0] + "/" + c2[0] + " " + suited

            if not(self.player_number == 5):
                return self.win_table.loc[key, str(self.player_number) + 'Win']
            return (self.win_table.loc[key, '4Win'] + self.win_table.loc[key, '6Win']) / 2

        elif self.round == Round.FLOP:
            board = (c_int * 3)()
            hole = (c_int * 2)()

            for i in range(3):
                board[i] = self.boards[i]
            for i in range(2):
                hole[i] = self.my_hole[i]

            sample_3board_win_pr = dll.sample_3board_win_pr
            sample_3board_win_pr.restype = c_double

            return sample_3board_win_pr(board, hole, self.player_number-1, 10000)

        elif self.round == Round.TURN:
            board = (c_int * 4)()
            hole = (c_int * 2)()

            for i in range(4):
                board[i] = self.boards[i]
            for i in range(2):
                hole[i] = self.my_hole[i]

            sample_4board_win_pr = dll.sample_4board_win_pr
            sample_4board_win_pr.restype = c_double

            return sample_4board_win_pr(board, hole, self.player_number - 1, 10000)

        elif self.round == Round.RIVER:
            board = (c_int * 5)()
            hole = (c_int * 2)()

            for i in range(5):
                board[i] = self.boards[i]
            for i in range(2):
                hole[i] = self.my_hole[i]

            sample_5board_win_pr = dll.sample_5board_win_pr
            sample_5board_win_pr.restype = c_double

            return sample_5board_win_pr(board, hole, self.player_number - 1, 10000)


s = "MATCHSTATE:1:5:ccccc:|4h2s||||/3d4dAd"
g = GameState(s)

st = Strategy(g)
print(st.get_win_pr())
