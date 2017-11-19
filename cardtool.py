

class CardTool(object):

    rank = ['2', '3', '4', '5', '6', '7', '8', '9', 'T', 'J', 'Q', 'K', 'A']
    suit = ['c', 'd', 'h', 's']

    # construct a dict key='ranksuit' value in 0-51
    card_dict ={}
    for i in range(len(rank)):
        for j in range(len(suit)):
            str_temp = rank[i] + suit[j]
            card_dict[str_temp] = i * len(suit) + j

    # a reverse dict of card_dict
    string_dict={}
    for k, v in card_dict.items():
        string_dict[v] = k

    # return int number represent card
    @classmethod
    def string_2_card(cls, string):
        return cls.card_dict[string]

    # return string represent card
    @classmethod
    def card_to_string(cls, value):
        return cls.string_dict[value]

    @classmethod
    def rank_of_card(cls, card):
        return card // 4

    @classmethod
    def suit_of_card(cls, card):
        return card % 4

    @classmethod
    def display(cls):
        print("card [0-51]")
        print('2c ' + str(cls.string_2_card('2c')))
        print('2d ' + str(cls.string_2_card('2d')))
        print('...')

# CardTool.display()

