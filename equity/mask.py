import torch
from setting import arguments


class Mask(object):
    # [1326 * 1326 mask out conflict hole combinations]
    hole_mask = None

    @classmethod
    def get_hole_mask(cls):
        if cls.hole_mask is None:
            valid_hole_mask = torch.FloatTensor(arguments.hole_count, arguments.hole_count).fill_(1)

            for s_card in range(arguments.card_count - 1):
                for b_card in range(s_card + 1, arguments.card_count):
                    row_index = b_card * (b_card - 1) // 2 + s_card

                    # find conflict col_index
                    for s in range(arguments.card_count - 1):
                        for b in range(s + 1, arguments.card_count):
                            if s == s_card or b == b_card or s == b_card or b == s_card:
                                col_index = b * (b - 1) // 2 + s
                                valid_hole_mask[row_index][col_index] = 0
            cls.hole_mask = valid_hole_mask
        return cls.hole_mask

    # return [1326] one dim vector
    @classmethod
    def get_board_mask(cls, board):
        out = arguments.tensor(arguments.hole_count).fill_(1)
        s = set([int(x) for x in board])
        for s_card in range(arguments.card_count - 1):
            for b_card in range(s_card + 1, arguments.card_count):
                if s_card in s or b_card in s:
                    index = b_card * (b_card - 1) // 2 + s_card
                    out[index] = 0
        return out

# a = Mask.get_hole_mask()
# for i in range(1326):
#     assert (a[i].sum() == 1225.0)
#     assert (a[:,i].sum() == 1225.0)
#
# b = Mask.get_board_mask([1,2,3,4,5])
# assert (b.sum() == 1081.0)

