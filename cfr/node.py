

class Node(object):

    def __init__(self):
        self.parent = None
        self.node_type = None
        self.street = None
        self.board = None
        self.board_string = None
        self.current_player = None
        self.bets = None
        self.pot = None
        self.terminal = False
        self.depth = None
        self.strategy = None
        self.ranges_absolute = None # reach pr vector
        self.strategy = None
        # self.current_strategy = None
        self.cf_values = None
        self.cf_br_values = None
        self.cfv_infset = None
        self.cfv_br_infset = None
        self.regrets = None
        self.positive_regrets = None
        self.iter_weight_sum = None

        self.epsilon = None
        self.exploitability = None
