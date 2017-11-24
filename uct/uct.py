import sys
sys.path.append('..')
from tree.state import State

class UCT(object):

    def __init__(self, action_seq, my_seat_no, pot, my_hole):
        self.action_seq = action_seq
        self.my_seat_no = my_seat_no
        self.pot = pot
        self.my_hole = my_hole


    def run_uct_iteration(self, iteration):
        pass


    def run_uct_time(self, time):
        pass


def main():

    state = State()
    action_seq = state.get_action_seq()
    my_seat_no = state.current_player
    pot = state.pot
    my_hole = [0, 1]
    dictionary = {}

    # opponent range?

    uct = UCT(action_seq, my_seat_no, pot, my_hole)
    # uct.run_uct_iteration(1000)
    # uct.run_uct_time(1000)



if __name__ == '__main__':
    main()



