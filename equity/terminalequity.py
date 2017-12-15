from setting import arguments, constants
import torch
from ctypes import cdll, c_int, c_double
from equity.mask import Mask
import sys


dll = cdll.LoadLibrary("../so/handeval.so")


class TerminalEquity(object):

    def __init__(self):
        self.hole_mask = Mask.get_hole_mask()
        self.board_mask = None
        self.call_matrix = None
        self.fold_matrix = None

    def set_board(self, board):

        # matrix [1326*1326]

        # [1.0] set call matrix (only works for last round)
        assert board.size(0) == 5

        call_matrix = arguments.tensor(arguments.hole_count, arguments.hole_count)
        # self.board_mask = Mask.get_board_mask(board)

        # hand evaluation, get strength vector
        _strength = (c_int * 1326)()
        _board = (c_int * 5)()
        for i in range(board.size(0)):
            _board[i] = int(board[i])
        dll.eval5Board(_board, 5, _strength)
        strength_list = [x for x in _strength]
        strength = arguments.tensor(strength_list)

        self.board_mask = strength.clone().fill_(1)
        self.board_mask[strength < 0] = 0

        # bm = Mask.get_board_mask(board)
        # print((bm == self.board_mask).sum())

        assert int((self.board_mask > 0).sum()) == 1081

        # construct row view and column view, construct win/lose/tie matrix
        strength_view1 = strength.view(arguments.hole_count, 1).expand_as(call_matrix)
        strength_view2 = strength.view(1, arguments.hole_count).expand_as(call_matrix)

        call_matrix[torch.lt(strength_view1, strength_view2)] = 1
        call_matrix[torch.gt(strength_view1, strength_view2)] = -1
        call_matrix[torch.eq(strength_view1, strength_view2)] = 0.5
        # mask out hole cards which conflict each other
        call_matrix[self.hole_mask < 1] = 0
        # mask out hole card which conflict boards
        call_matrix[strength_view1 == -1] = 0
        call_matrix[strength_view2 == -1] = 0


        # [2.0] set fold matrix
        fold_matrix = arguments.tensor(arguments.hole_count, arguments.hole_count)
        # make sure player hole don't conflict with opponent hole
        fold_matrix.copy_(self.hole_mask)
        # make sure hole don't conflict with board
        fold_matrix[strength_view1 == -1] = 0
        fold_matrix[strength_view2 == -1] = 0

        self.call_matrix = call_matrix
        self.fold_matrix = fold_matrix


# t = TerminalEquity()
# t.set_board(torch.IntTensor([0, 5, 16, 29, 34]))
#
# m = t.call_matrix[115]
# invalid_count = (m == 0).sum()
# assert invalid_count == 336
#
# tie_count = (m==0.5).sum()
# win_count = (m==1).sum()
# lose_count = (m==-1).sum()
# print(win_count, lose_count, tie_count)


