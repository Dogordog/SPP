
class CardTool(object):

    rank = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'A']
    suit = ['c', 'd', 'h', 's']

    # construct a dict key='ranksuit' value in 0-51
    card_dict ={}
    # todo

    string_dict={} # a reverse dict of card_dict
    # todo

    # return int number represent card
    @classmethod
    def string_2_card(cls, string):
        cls.card_dict[string]

    # return string represent card
    @classmethod
    def card_to_string(cls, string):
        # todo
        return