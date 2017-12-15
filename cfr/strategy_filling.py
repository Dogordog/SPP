from setting import arguments, constants


class StrategyFilling(object):

    @classmethod
    def fill_uniform(cls, tree):
        cls._fill_uniform_dfs(tree)

    @classmethod
    def _fill_uniform_dfs(cls, node):
        if node.current_player == constants.chance_player:
            assert False
            cls._fill_chance(node)
        else:
            # fill this node
            cls._fill_uniformly(node)

        # fill children of this node
        for child in node.children:
            cls._fill_uniformly(child)

    @classmethod
    def _fill_chance(cls, node):
        pass

    @classmethod
    def _fill_player(cls, node):
        pass

    @classmethod
    def _fill_uniformly(cls, node):
        cp = node.current_player
        assert (cp == constants.p1_player or cp == constants.p2_player)

        if node.terminal:
            return

        children_number = len(node.children)
        node.strategy = arguments.tensor(children_number, 1326).fill_(1.0 / children_number)

