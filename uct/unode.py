

class UNode(object):

    def __init__(self):
        self.current_player = None
        self.visited = None # True or False
        self.action_seqs = None
        self.parent = None
        self.hole = None
        self.payoff = None
        self.visted_count = 0
        self.action = None
        self.children = None
        self.finished = None

