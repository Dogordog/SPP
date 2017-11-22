from tree.tree_builder import TreeBuilder
from visual.tree_visualizer import TreeVisualizer

tb = TreeBuilder()
root = tb.build_preflop()

tv = TreeVisualizer()
tv.graphviz(root, 'preflop.dot')

