from enums import ActionType


class Action(object):

    def __init__(self, string):
        self.string = string
        if string[0] == "c":
            self.type = ActionType.CALL
        elif string[0] == "f":
            self.type = ActionType.FOLD
        elif string[0] == 'r':
            self.type = ActionType.RAISE
            self.amount = int(string[1:])
        else:
            raise Exception


