from game.enums import Round
from game.betsizing import BetSizing
from setting import arguments, constants
from tree.tree_builder import TreeBuilder
from cfr.tree_cfr import TreeCFR
from equity.mask import Mask
from cfr.tree_values import TreeValues

params = {}
params['street'] = Round.RIVER
params['bets'] = arguments.tensor(2).fill_(3000)
params['current_player'] = constants.p1_player
params['board'] = arguments.tensor([0,5,16,29,34])
# params['board'] = arguments.tensor([47, 48, 49, 50, 51])
params['bet_sizing'] = BetSizing(pot_fractions=[1])
params['limit_to_street'] = True

tb = TreeBuilder()
root = tb.build_tree(params)

ranges = arguments.tensor(2, arguments.hole_count).fill_(1)

tree_cfr = TreeCFR()
valid_hole_mask = Mask.get_board_mask(root.board).view(1, arguments.hole_count)
expand_mask = valid_hole_mask.expand_as(ranges)

ranges.mul_(expand_mask)
ranges_sum = ranges.sum(1).view(2,1)
ranges.div_(ranges_sum.expand(2, arguments.hole_count))

tree_cfr.run_cfr(root, ranges, 10000)
print('----------')
tree_value = TreeValues()
tree_value.compute_values(root, ranges)
print(root.exploitability)