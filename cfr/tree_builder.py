from game.enums import Round
from setting import arguments, constants
from game.betsizing import BetSizing
from tree.node import Node



class TreeBuilder(object):

    def __init__(self):
        self.bet_sizing = None
        self.limit_to_street = None

    def build_tree(self, params):
        self.bet_sizing = params['bet_sizing']
        self.limit_to_street = params['limit_to_street']
        root = Node()
        root.current_player = params['current_player']
        root.street = params['street']
        root.board = params['board'].clone()
        root.bets = params['bets'].clone()

        self._build_tree_dfs(root)
        return root

    def _build_tree_dfs(self, current_node):
        current_node.pot = current_node.bets.min()
        children = self._get_children(current_node)
        current_node.children = children

        child_number = len(children)
        depth = 0
        current_node.actions = arguments.tensor(child_number)

        for i in range(child_number):
            children[i].parent = current_node
            self._build_tree_dfs(children[i])
            depth = children[i].depth if children[i].depth > depth else depth

            if i == 0:
                current_node.actions[i] = constants.fold_action
            elif i == 1:
                current_node.actions[i] = constants.ccall_action
            else:
                current_node.actions[i] = children[i].bets.max()

        current_node.depth = depth + 1


    def _get_children(self, parent_node):
        # transition call -> chance node
        is_transition_call = False # is parent node a transition call node
        is_chance_node = parent_node.current_player == constants.chance_player

        if parent_node.terminal:
            return []
        elif is_chance_node:
            assert (False)
            return self._get_children_of_chance(parent_node)
        else:
            return self._get_children_of_player(parent_node)

    def _get_children_of_chance(self, parent_node):
        assert False
        if self.limit_to_street:
            return []

    def _get_children_of_player(self, parent_node):
        assert (parent_node.current_player != constants.chance_player)
        children = []

        # ??
        # fold
        fold_node = Node()
        fold_node.node_type = constants.terminal_fold_node
        fold_node.terminal = True
        fold_node.current_player = 1 - parent_node.current_player
        fold_node.street = parent_node.street
        fold_node.board = parent_node.board
        fold_node.board_string = parent_node.board_string
        fold_node.bets = parent_node.bets.clone()
        children.append(fold_node)

        # check/transition call/terminal call
        is_check, is_transition_call, is_terminal_call = False, False, False

        # check - parent bets equal and first player to act, first round have no check node
        if parent_node.bets[0] == parent_node.bets[1] and parent_node.current_player == constants.p1_player:
            is_check = True

        # transition call
        # 1. PREFLOP round:
        #   second player(p1) call at a equal bet
        #   player call to a larger bet, and the bet is not BB, not all-in
        # 2. FLOP,TURN round,
        #   second player(p2) call at a equal bet
        #   player call to a larger bet, and the bet is not all-in
        if parent_node.street < Round.RIVER:
            if parent_node.street == Round.PREFLOP:
                cp = parent_node.current_player
                if parent_node.bets[0] == parent_node.bets[1] and cp == constants.p1_player:
                    is_transition_call = True
                elif parent_node.bets[cp] < parent_node.bets[1-cp] and arguments.stack > parent_node.bets[1-cp] > arguments.BB:
                    is_transition_call = True
            else: # FLOP, TURN
                cp = parent_node.current_player
                if parent_node.bets[0] == parent_node.bets[1] and cp == constants.p2_player:
                    is_transition_call = True
                elif parent_node.bets[cp] < parent_node.bets[1-cp] < arguments.stack:
                    is_transition_call = True

        # terminal call
        if parent_node.street == Round.RIVER:
            cp = parent_node.current_player
            if parent_node.bets[0] == parent_node.bets[1] and cp == constants.p2_player:
                is_terminal_call = True
            elif parent_node.bets[cp] < parent_node.bets[1 - cp]:
                is_terminal_call = True

        FLAG = [is_check, is_transition_call, is_terminal_call]
        assert (FLAG.count(True) == 1)

        if is_check:
            check_node = Node()
            check_node.node_type = constants.check_node
            check_node.terminal = False
            check_node.current_player = 1 - parent_node.current_player
            check_node.street = parent_node.street
            check_node.board = parent_node.board
            check_node.board_string = parent_node.board_string
            check_node.bets = parent_node.bets.clone()
            children.append(check_node)
        elif is_transition_call:
            assert (False)
            chance_node = Node()
            chance_node.terminal = self.limit_to_street # terminal
            chance_node.node_type = constants.chance_node
            chance_node.street = parent_node.street
            chance_node.board = parent_node.board
            chance_node.board_string = parent_node.board_string
            chance_node.current_player = constants.chance_player
            chance_node.bets = parent_node.bets.clone().fill_(parent_node.bets.max())
            children.append(chance_node)
        elif is_terminal_call:
            terminal_call_node = Node()
            terminal_call_node.node_type = constants.terminal_call_node
            terminal_call_node.terminal = True
            terminal_call_node.current_player = 1-parent_node.current_player
            terminal_call_node.board = parent_node.board
            terminal_call_node.board_string = parent_node.board_string
            terminal_call_node.bets = parent_node.bets.clone().fill_(parent_node.bets.max())
            children.append(terminal_call_node)
        else:
            raise Exception

        assert ([is_check, is_transition_call, is_terminal_call].count(True) == 1)

        # bet actions
        possible_bets = self.bet_sizing.get_possible_bets(parent_node)

        if possible_bets.dim() != 0:
            assert (possible_bets.size(1) == 2)

            for i in range(possible_bets.size(0)):
                child = Node()
                child.terminal = False
                child.node_type = constants.inner_node
                child.parent = parent_node
                child.current_player = 1 - parent_node.current_player
                child.street = parent_node.street
                child.board = parent_node.board
                child.board_string = parent_node.board_string
                child.bets = possible_bets[i]
                if child.bets[0] == 9000 == child.bets[1]:
                    print("!!!")
                children.append(child)

        return children














