from setting import constants, arguments
from equity.terminalequity import TerminalEquity
import torch

class TreeCFR(object):

    def __init__(self):
        self.regret_epsilon = 10**-9
        self._cached_terminal_equities = {}

    # run cfr iter_count times from given start_range
    def run_cfr(self, root, start_range, iter_count):

        iter_count = iter_count or 1000
        root.ranges_absolute = start_range

        for iters in range(iter_count):
            print('iter-', iters)
            self.cfr_iter_dfs(root, iters)

    # run cfr depth first search
    def cfr_iter_dfs(self, node, iters):
        player_index = node.current_player
        opponent_index = 1 - player_index

        assert (player_index == constants.p1_player or player_index == constants.p2_player or
                player_index == constants.chance_player)

        action_dim, hole_dim = 0, 1

        # store counterfactual values for this node
        values = node.ranges_absolute.clone().fill_(0)

        if node.terminal:

            # get terminal equity
            key = ' '.join([str(int(x)) for x in node.board])
            terminal_equity = self._cached_terminal_equities.get(key, None)
            if terminal_equity is None:
                terminal_equity = TerminalEquity()
                terminal_equity.set_board(node.board)
                self._cached_terminal_equities[key] = terminal_equity

            # use terminal equity to compute values
            if node.node_type == constants.terminal_call_node:
                values[0] = torch.matmul(node.ranges_absolute[1], terminal_equity.call_matrix)
                values[1] = torch.matmul(node.ranges_absolute[0], terminal_equity.call_matrix)

            elif node.node_type == constants.terminal_fold_node:
                values[0] = torch.matmul(node.ranges_absolute[1], terminal_equity.fold_matrix)
                values[1] = torch.matmul(node.ranges_absolute[0], terminal_equity.fold_matrix)
                values[opponent_index,:].mul_(-1)
            else:
                raise Exception

            values = values * node.pot
            node.cf_values = values.view_as(node.ranges_absolute)

        # not terminal node
        else:

            action_count = len(node.children)
            current_strategy = None

            if node.current_player == constants.chance_player:
                print("to do! not implemented yet!")
                raise Exception
            else:
                # compute current strategy for this node

                # init regret and positive regret in first iteration
                if node.regrets is None:
                    node.regrets = arguments.tensor(action_count, arguments.hole_count).fill_(self.regret_epsilon)
                if node.positive_regrets is None:
                    node.positive_regrets = arguments.tensor(action_count, arguments.hole_count)\
                        .fill_(self.regret_epsilon)

                # compute positive regrets, use positive regrets to compute current strategy
                node.positive_regrets.copy_(node.regrets)
                node.positive_regrets[torch.le(node.positive_regrets, self.regret_epsilon)] = self.regret_epsilon

                # compute current strategy
                regret_sum = node.positive_regrets.sum(action_dim)
                current_strategy = node.positive_regrets.clone()
                current_strategy.div_(regret_sum.expand_as(current_strategy))

            # end of computing current strategy

            # compute current cfvs [action, players, ranges]
            cf_values_allactions = arguments.tensor(action_count, 2, arguments.hole_count)

            children_ranges_absolute = {}

            if node.current_player == constants.chance_player:
                print("todo!")
                raise Exception
            else:
                ranges_mul_matrix = node.ranges_absolute[player_index].repeat(action_count, 1)
                children_ranges_absolute[player_index] = torch.mul(current_strategy, ranges_mul_matrix)
                children_ranges_absolute[opponent_index] = \
                    node.ranges_absolute[opponent_index].repeat(action_count, 1).clone()

            for i in range(action_count):
                child_node = node.children[i]
                child_node.ranges_absolute = node.ranges_absolute.clone()

                child_node.ranges_absolute[0].copy_(children_ranges_absolute[0][i])
                child_node.ranges_absolute[1].copy_(children_ranges_absolute[1][i])

                self.cfr_iter_dfs(child_node, iters)

                cf_values_allactions[i] = child_node.cf_values

            # use cfvs from actions(children) to compute cfvs for this node
            node.cf_values = arguments.tensor(2, arguments.hole_count).fill_(0)

            if player_index != constants.chance_player:
                strategy_mul_matrix = current_strategy.view(action_count, arguments.hole_count)
                node.cf_values[player_index] = (strategy_mul_matrix * cf_values_allactions[:, player_index, :]).sum(0)
                node.cf_values[opponent_index] = (cf_values_allactions[:, opponent_index, :]).sum(0)
            else:
                raise Exception

            if player_index != constants.chance_player:
                # compute regrets
                current_regrets = \
                    cf_values_allactions[:, player_index, :].resize_(action_count, arguments.hole_count).clone()
                current_regrets.sub_(node.cf_values[player_index]
                                     .view(1, arguments.hole_count).expand_as(current_regrets))

                self.update_regrets(node, current_regrets)

                self.update_average_strategy(node, current_strategy, iters)

    def update_regrets(self, node, current_regrets):
        # print(current_regrets)
        node.regrets.add_(current_regrets)
        node.regrets[torch.le(node.regrets, self.regret_epsilon)] = self.regret_epsilon

    def update_average_strategy(self, node, current_strategy, iters):
        if iters > 500:

            actions_count = len(node.children)
            if node.strategy is None:
                node.strategy = arguments.tensor(actions_count, arguments.hole_count).fill_(0)
            if node.iter_weight_sum is None:
                node.iter_weight_sum = arguments.tensor(arguments.hole_count).fill_(0)
            iter_weight_contribution = node.ranges_absolute[node.current_player].clone()
            iter_weight_contribution[torch.le(iter_weight_contribution, 0)] = self.regret_epsilon
            node.iter_weight_sum.add_(iter_weight_contribution)
            iter_weight = iter_weight_contribution / node.iter_weight_sum

            expanded_weight = iter_weight.view(1, arguments.hole_count).expand_as(node.strategy)
            old_strategy_scale = 1 - expanded_weight
            node.strategy.mul_(old_strategy_scale)
            node.strategy.add_(current_strategy * expanded_weight)



