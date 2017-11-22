import pandas as pd
from sklearn.cluster import KMeans
from action import Action


class PreflopCardAbstraction(object):

    def __init__(self):
        # load data
        pass

    def f1(self, x):
        return (float(x.rstrip('%'))) / 100.00

    def f2(self, x):
        if 'Pair' in x:
            return x[8] + "/" + x[8] + " u"

        return x[0:5]

    def f3(self, x):
        return x[2]+x[1]+x[0] + x[3:]

    def do_abstraction(self, k=20):
        # load raw data
        p2346_data = pd.read_csv("./data/preflop/2346players.csv", header=0, index_col=0)
        # construct X
        X2 = p2346_data.drop(['3Win', '4Win', '6Win'], axis=1)
        X3 = p2346_data.drop(['2Win', '4Win', '6Win'], axis=1)
        X4 = p2346_data.drop(['2Win', '3Win', '6Win'], axis=1)
        X6 = p2346_data.drop(['2Win', '3Win', '4Win'], axis=1)
        # clustering
        kmeans2 = KMeans(n_clusters=k, random_state=0).fit(X2)
        kmeans3 = KMeans(n_clusters=k, random_state=0).fit(X3)
        kmeans4 = KMeans(n_clusters=k, random_state=0).fit(X4)
        kmeans6 = KMeans(n_clusters=k, random_state=0).fit(X6)
        # save result
        p2346_data['2Bucket'] = kmeans2.labels_
        p2346_data['3Bucket'] = kmeans3.labels_
        p2346_data['4Bucket'] = kmeans4.labels_
        p2346_data['6Bucket'] = kmeans6.labels_

        p2346_data.to_csv("./data/preflop/2346players_bucket.csv", index=True)


    # return bucket index
    # card_string "c1/c2 suited or unsuited"
    # left_players non-folded player number
    def get_bucket(self, card_string, left_players=6):
        pass


class PreflopBettingAbstraction(object):

    def __init__(self, first_raise=[200, 500, 2000, 20000], pot_fraction=[0.33, 0.5, 1.0, 2.0, 5.0]):
        self.first_raise = first_raise
        self.pot_fraction = pot_fraction

    def get_actions(self, state):
        actions = []
        if state.finished or state.next_round_flag:
            return actions

        current_bet = state.spent[state.current_player]

        # is fold valid?
        if current_bet < state.max_bet:
            actions.append(Action("f", state.current_player))

        # is no one raises before? -> raise set to be special amount
        if state.max_bet == 100:
            for amount in self.first_raise:
                actions.append(Action("r" + str(amount), state.current_player))
        # some one raised before
        else:
            for fraction in self.pot_fraction:
                amount = int(state.pot * fraction)
                if state.min_no_limit_raise_to <= amount <= state.max_no_limit_raise_to:
                    actions.append(Action("r" + str(amount), state.current_player))

        # call is always valid
        actions.append(Action("c", state.current_player))

        return actions

