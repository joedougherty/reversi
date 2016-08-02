from reversiutils import alternate_player
from midas import find_max_nodes
from Board import Board

class Node():
    def __init__(self, val, parent=None, level=0, player=None):
        self.val = val
        self.children = []
        self.parent = parent
        self.player = player

        if self.player is None: # if this is the opening board
            board = Board()
            self.next_player = board.BLACK
        else:
            self.next_player = alternate_player(player)
    
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

    tree = Node(None, parent=None)

    a1 = Node(1, parent=tree)
    a2 = Node(4, parent=tree)
    a3 = Node(7, parent=tree)

    add_children_to_parent((a1, a2, a3), tree)

    b1 = Node(2, parent=a1)
    b2 = Node(12, parent=a1)

    add_children_to_parent((b1, b2), a1)

    b3 = Node(4, parent=a2)
    b4 = Node(7, parent=a2)

    add_children_to_parent((b3, b4), a2)

    b5 = Node(6, parent=a3)
    b6 = Node(15, parent=a3)
    b7 = Node(5, parent=a3)

    add_children_to_parent((b5, b6, b7), a3)

    return tree

b = Board()

def minimax(tree, current_player=b.BLACK):

    if tree.is_a_leaf_node():
        return [] + [tree.val]
    elif current_player == b.BLACK:
        for child in tree.children:
            try:
                return max(minimax(child))
            except TypeError:
                print(minimax(child))
    else: # current_player == b.WHITE
        for child in tree.children:
            return min(minimax(child))
        
