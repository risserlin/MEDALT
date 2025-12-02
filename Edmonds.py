from Readfile import *
from ComputeDistance import *
from copy import *
from mdmst_copilot_rewrite3 import *
import time
import sys
import os

class Tree:
    def __init__(self, name, out_edge, in_edge):
        self.name = name  # name of node
        self.out_edge = out_edge  # dictionary of node name - distance pair
        self.in_edge = in_edge  # dictionary of node name - distance pair

    def get_out_degree(self):
        return len(self.out_edge)

    def get_in_degree(self):
        return len(self.in_edge)

#redo create_tree by chatgpt to use memory better and to print out stats as we go along. 


def create_tree(nodes, node_name_list, root):
    """
    Creates a tree-like dictionary of distances between nodes.
    Pure Python version for Python 2.7:
    - No NumPy, no psutil
    - Prints progress and performance stats
    """
    print "IN THE RIGHT VERSION"
    print "[INFO] Starting tree creation..."
    start_time = time.time()

    print "[INFO] Computing pairwise distances using nested loops..."
    sys.stdout.flush()
    tree_node_dict = {}
    total_nodes = len(node_name_list)

    for i, node in enumerate(node_name_list):
        if i % 100 == 0 and i > 0:
            print "[PROGRESS] Processed {} of {} nodes...".format(i, total_nodes)
            sys.stdout.flush()
        temp_out_edge = {}
        for j, other_node in enumerate(node_name_list):
            if i != j:
                # Assuming dist() is defined elsewhere
                temp_out_edge[other_node] = dist(nodes[node], nodes[other_node])
        tree_node_dict[node] = temp_out_edge

    elapsed_time = time.time() - start_time
    approx_mem = sys.getsizeof(tree_node_dict)

    print "[INFO] Tree creation complete."
    print "Execution Time: {:.4f} seconds".format(elapsed_time)
    print "Approx Memory Usage: {} bytes".format(approx_mem)
    print "Nodes: {}, Edges per node: {}".format(total_nodes, total_nodes - 1)
    sys.stdout.flush()

    return tree_node_dict

#def create_tree(nodes, node_name_list,root):
#    tree_node_dict = {}
#    for node in node_name_list:
#        temp_out_edge = {}
#        temp_in_edge = {}
#        for other_node in node_name_list:
#            if not node == other_node:
#                temp_out_edge[other_node] = dist(nodes[node], nodes[other_node])
#                temp_in_edge[other_node] = dist(nodes[other_node], nodes[node])
#        tree_node_dict[node] = temp_out_edge
#    return tree_node_dict
