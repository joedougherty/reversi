from reversiutils import alternate_player
from midas import find_max_nodes
from Board import Board
import sys

class Node():
    def __init__(self, val, parent=None, level=0, player=None, next_player=None):
        self.val = val
        self.children = []
        self.parent = parent
        self.player = player
        self.next_player = next_player
    
    def add_child(self, obj):
        self.children.append(obj)

    def is_a_leaf_node(self):
        return self.children == []

    def is_the_root_node(self):
        return self.parent is None

def create_tree():
    def add_children_to_parent(list_of_children, parent):
        for n in list_of_children:
            parent.add_child(n)

    b = Board()

    # Root node
    tree = Node(None, parent=None, next_player=b.BLACK)

    # next_player = b.WHITE 
    a1 = Node(9, parent=tree, next_player=b.WHITE)
    a2 = Node(11, parent=tree, next_player=b.WHITE)
    a3 = Node(13, parent=tree, next_player=b.WHITE)

    add_children_to_parent((a1, a2, a3), tree)

    b1 = Node(3, parent=a1, next_player=b.BLACK)
    b2 = Node(12, parent=a1, next_player=b.BLACK)
    b3 = Node(8, parent=a1, next_player=b.BLACK)

    add_children_to_parent((b1, b2, b3), a1)

    c1 = Node(2, parent=a2, next_player=b.BLACK)
    c2 = Node(4, parent=a2, next_player=b.BLACK)
    c3 = Node(6, parent=a2, next_player=b.BLACK)

    add_children_to_parent((c1, c2, c3), a2)

    d1 = Node(14, parent=a3, next_player=b.BLACK)
    d2 = Node(5, parent=a3, next_player=b.BLACK)
    d3 = Node(2, parent=a3, next_player=b.BLACK)

    add_children_to_parent((d1, d2, d3), a3)

    """
          NONE (root)       (self.next_player == b.BLACK)
        /      |      \
       B       C       D    (White moves next; self.next_player == b.WHITE)
       |       |       |
     / | \   / | \   / | \  (Black moves next; self.next_player == b.BLACK)
    3  12 8 2  4  6 14 5  2

    """

    return tree

def evaluate(node):
    return node.val

def minimax(node, max_player=None, min_player=None):
    """
    Implementation translated from pseudocode found on
    https://www.cs.cornell.edu/courses/cs312/2002sp/lectures/rec21.htm 

    fun minimax(n: node): int =
    if leaf(n) then return evaluate(n)
    if n is a max node
      v := L
      for each child of n
         v' := minimax (child)
         if v' > v, v:= v'
      return v
    if n is a min node
      v := W
      for each child of n
         v' := minimax (child)
         if v' < v, v:= v'
      return v

    """
    if node.is_a_leaf_node():
        return evaluate(node)

    if node.next_player == max_player:
        best_case = -1000000
        for child in node.children:
            v = minimax(child, max_player=max_player, min_player=min_player)
            if v > best_case:
                best_case = v
        return best_case

    if node.next_player == min_player:
        worst_case = 1000000
        for child in node.children:
            v = minimax(child, max_player=max_player, min_player=min_player)
            if v < worst_case:
                worst_case = v
        return worst_case

