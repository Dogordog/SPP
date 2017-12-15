import torch
from setting import arguments
import math


class BetSizing(object):

    def __init__(self, pot_fractions=[1]):
        self.pot_fractions = pot_fractions

    def get_possible_bets(self, node):
        current_player = node.current_player
        player_bet = node.bets[current_player]
        opponent_bet = node.bets[1-current_player]

        assert (player_bet <= opponent_bet)

        max_raise_size = arguments.stack - opponent_bet
        min_raise_size = opponent_bet - node.bets[current_player]
        min_raise_size = max(min_raise_size, arguments.BB)
        min_raise_size = min(max_raise_size, min_raise_size)

        # [1]. raise is not valid (oppo bets 20000, player can only call)
        if min_raise_size == 0:
            return torch.FloatTensor()
        # [2]. can only all-in
        elif min_raise_size == max_raise_size:
            out = torch.FloatTensor(1,2).fill_(opponent_bet)
            out[0, current_player] = opponent_bet + min_raise_size
            return out
        else:
        # [3]. iterate through all bets, check if they are valid
            max_possible_bets_count = len(self.pot_fractions) + 1
            out = arguments.tensor(max_possible_bets_count, 2).fill_(opponent_bet)

            pot = 2 * opponent_bet
            used_bets_count = 0

            for i in range(len(self.pot_fractions)):
                raise_size = pot * self.pot_fractions[i]
                if min_raise_size <= raise_size < max_raise_size:
                    out[used_bets_count, current_player] = opponent_bet + raise_size
                    used_bets_count += 1
                # end if
            # end for

            assert (used_bets_count < max_possible_bets_count)

            out[used_bets_count, current_player] = opponent_bet + max_raise_size
            used_bets_count += 1

            return out[0:used_bets_count]


