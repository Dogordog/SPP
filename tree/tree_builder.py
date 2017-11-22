from tree.state import State
from preflopabstraction import PreflopBettingAbstraction
from cardtool import CardTool
from enums import Round, ActionType
from copy import deepcopy


class TreeBuilder(object):

    def __init__(self):
        self.abs = PreflopBettingAbstraction(first_raise=[200], pot_fraction=[1.0])

    def build_preflop(self):
        root = Node()
        root.holes, root.boards = CardTool.deal_all_cards(rd=Round.PREFLOP)
        state = State()
        root.round = state.round
        root.spent = state.spent
        root.current_player = state.current_player
        root.action_cnt = 0
        self.build_tree_dfs(root, state)
        return root

    def build_tree_dfs(self, node, state):

        valid_actions = self.abs.get_actions(state)

        for action in valid_actions:

            # if action count reach max number, raise action will be invalid
            if node.action_cnt >= 3 and action.type == ActionType.RAISE:
                continue

            child_node = Node()
            child_node.parent = node
            child_node.action_cnt = node.action_cnt + 1

            # share same holes and boards with parent node
            child_node.holes = node.holes
            child_node.boards = node.boards
            # do action from parent state
            next_state = deepcopy(state)
            next_state.do_action(action)
            # fill attributes from next state
            child_node.round = next_state.round
            child_node.spent = next_state.spent
            child_node.current_player = next_state.current_player
            self.build_tree_dfs(child_node, next_state)
            node.children.append(child_node)


class Node(object):

    def __init__(self):
        self.action_cnt = None
        self.spent = None
        self.round = None
        self.current_player = None
        self.holes = None
        self.boards = None
        self.children = []
        self.parent = None



