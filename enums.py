from enum import IntEnum


class ActionType(IntEnum):

    CALL = 0
    RAISE = 1
    FOLD = 2


class Round(IntEnum):

    PREFLOP = 0
    FLOP = 1
    TURN = 2
    RIVER = 3

    def __add__(self, other):
        return Round(self.value + other)

    def __eq__(self, other):
        return self.value == other


class CardType(IntEnum):
    HOLE = 0
    PUBLIC = 1


ActionNames = {
    ActionType.NEXT_ROUND : "NEXT_ROUND",
    ActionType.CALL : "CALL",
    ActionType.RAISE : "RAISE",
    ActionType.FOLD : "FOLD",
}


RoundNames = {
    Round.PREFLOP : "PREFLOP",
    Round.FLOP : "FLOP",
    Round.TURN : "TURN",
    Round.RIVER : "RIVER",
}


CardNames = {
    CardType.HOLE : "HOLE",
    CardType.PUBLIC : "PUBLIC",
}
