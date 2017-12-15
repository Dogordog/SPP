from setting import arguments, constants
from equity.terminalequity import TerminalEquity
from equity.mask import Mask
import torch

class TreeValues(object):

    def __init__(self):
        self._cached_terminal_equity = {}

    def _fill_ranges_dfs(self, node, ranges_absolute):
        node.ranges_absolute = ranges_absolute.clone()

        player_index = node.current_player
        opponent_index = 1 - player_index

        if node.terminal:
            return

        assert (node.strategy is not None)

        actions_count = len(node.children)

        strategy_to_check = node.strategy

        hand_mask = Mask.get_board_mask(node.board)

        if node.current_player != constants.chance_player:
            check_sum = strategy_to_check.sum(0)

            assert (strategy_to_check.lt(0).sum() == 0)
            assert (check_sum.lt(0.999).sum() == 0)
            assert (check_sum.gt(1.001).sum() == 0)
            assert (check_sum.ne(check_sum).sum() == 0)

        assert (node.ranges_absolute.lt(0).sum() == 0)
        assert (node.ranges_absolute.gt(1).sum() == 0)

        impossible_hand_mask = hand_mask.clone().fill_(1) - hand_mask
        impossible_range_sum = node.ranges_absolute.clone()\
            .mul_(impossible_hand_mask.view(1, arguments.hole_count).expand_as(node.ranges_absolute))

        assert (impossible_range_sum.sum() == 0)

        children_ranges_absolute = arguments.tensor(actions_count, 2, arguments.hole_count)

        if node.current_player == constants.chance_player:
            children_ranges_absolute[:, 0, :].copy_(node.ranges_absolute[0].repeat(actions_count, 1))
            children_ranges_absolute[:, 1, :].copy_(node.ranges_absolute[1].repeat(actions_count, 1))

            children_ranges_absolute[:, 0, :].mul_(node.strategy)
            children_ranges_absolute[:, 1, :].mul_(node.strategy)
        else:
            children_ranges_absolute[:, opponent_index, :] = \
                node.ranges_absolute[opponent_index].clone().repeat(actions_count,1)

            ranges_mul_matrix = node.ranges_absolute[player_index].repeat(actions_count, 1)
            children_ranges_absolute[:, player_index, :] = node.strategy * ranges_mul_matrix

        # fill ranges for children
        for i in range(actions_count):
            child_node = node.children[i]
            child_range = children_ranges_absolute[i]

            self._fill_ranges_dfs(child_node, child_range)

    def fill(self, node, ranges_absolute):
        self._fill_ranges_dfs(node, ranges_absolute)

    def _compute_values_dfs(self, node):

        player_index = node.current_player
        opponent_index = 1 - player_index

        if node.terminal:
            assert (node.node_type == constants.terminal_fold_node or node.node_type == constants.terminal_call_node)

            # construct equity matrix
            key = ' '.join([str(int(x)) for x in node.board])
            terminal_equity = self._cached_terminal_equity.get(key, None)
            if terminal_equity is None:
                terminal_equity = TerminalEquity()
                terminal_equity.set_board(node.board)
                self._cached_terminal_equity[key] = terminal_equity

            # compute terminal node values
            values = node.ranges_absolute.clone().fill_(0)
            if node.node_type == constants.terminal_call_node:
                values[0] = torch.matmul(node.ranges_absolute[1], terminal_equity.call_matrix)
                values[1] = torch.matmul(node.ranges_absolute[0], terminal_equity.call_matrix)
            else: # terminal fold node
                values[0] = torch.matmul(node.ranges_absolute[1], terminal_equity.fold_matrix)
                values[1] = torch.matmul(node.ranges_absolute[0], terminal_equity.fold_matrix)
                values[opponent_index, :].mul_(-1)

            values.mul_(node.pot)
            node.cf_values = values.view_as(node.ranges_absolute)
            node.cf_br_values = values.view_as(node.ranges_absolute)
        else:
            actions_count = len(node.children)
            hole_count = node.ranges_absolute.size(1)

            cf_values_allactions = arguments.tensor(actions_count, 2, hole_count).fill_(0)
            cf_br_values_allactions = arguments.tensor(actions_count, 2, hole_count).fill_(0)

            for i in range(actions_count):
                child_node = node.children[i]
                self._compute_values_dfs(child_node)
                cf_values_allactions[i] = child_node.cf_values
                cf_br_values_allactions[i] = child_node.cf_br_values
            # end for

            # compute values of this node according to its children values
            node.cf_values = arguments.tensor(2, hole_count).fill_(0)
            node.cf_br_values = arguments.tensor(2, hole_count).fill_(0)

            # strategy [actions * range]
            strategy_mul_matrix = node.strategy.view(actions_count, hole_count)

            # compute cfvs
            if player_index == constants.chance_player:
                node.cf_values = cf_values_allactions.sum(0)
                node.cf_br_values = cf_br_values_allactions.sum(0)
            else:
                node.cf_values[player_index] = (strategy_mul_matrix * cf_values_allactions[:, player_index, :]).sum(0)
                node.cf_values[opponent_index] = cf_br_values_allactions[:, opponent_index, :].sum(0)

                # compute br strategy
                node.cf_br_values[opponent_index] = cf_br_values_allactions[:, opponent_index, :].sum(0)
                node.cf_br_values[player_index] = cf_br_values_allactions[:, player_index, :].max(0)[0]
        # end if terminal else

        # cf values weighted by reach probability
        node.cfv_infset = arguments.tensor(2)
        node.cfv_infset[0] = (node.cf_values[0] * node.ranges_absolute[0]).sum()
        node.cfv_infset[1] = (node.cf_values[1] * node.ranges_absolute[1]).sum()

        # cfv-br values weighted by reach probability
        node.cfv_br_infset = arguments.tensor(2)
        node.cfv_br_infset[0] = (node.cfv_br_infset[0] * node.ranges_absolute[0]).sum()
        node.cfv_br_infset[1] = (node.cfv_br_infset[1] * node.ranges_absolute[1]).sum()

        node.epsilon = node.cfv_br_infset - node.cfv_infset
        node.exploitability = node.epsilon.mean()

    def compute_values(self, root, starting_ranges):
        self._fill_ranges_dfs(root, starting_ranges)
        self._compute_values_dfs(root)