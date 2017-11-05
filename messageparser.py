
class MessageParser(object):

    def __init__(self, message):
        self.message = message

        _, position, hand_number, betting_string, board_string = message.split(":")
        self.position = int(position)
        self.hand_number = int(hand_number)
        self.betting_string = betting_string.split("/")
        self.board_string = board_string.split("/")
        # preflop hole cards may need to be split by "|"
        pass



    def get_position(self):
        return self.position

    def get_hand_number(self):
        return self.hand_number


    # return betting string of round, last round by default
    def get_betting_string(self, rd=None):
        if not rd:
            return self.betting_string
        return self.betting_string[rd]

    def get_hole_cards(self, position):
        pass

    # if round is not given, then return all board cards
    def get_board_string(self, rd=None):
        if not round:
            return self.board_string[rd]



# str1 = 'MATCHSTATE:1:31:r300r900r3000:|JdTc'
# mp = MessageParser(str1)
#
# x = 1


