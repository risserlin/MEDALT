from collections import *
from copy import *
import sys

def reverse_g(g):
    print("Reversing graph...")
    sys.stdout.flush()
    rev_graph = {}
    for node in g:
        rev_graph[node] = {}
    for a_node in g:
        for b_node in g[a_node]:
            rev_graph[b_node][a_node] = g[a_node][b_node]
    print("Graph reversed.")
    sys.stdout.flush()
    return rev_graph

def update_dege(rg, root):
    print("Updating edge weights...")
    sys.stdout.flush()
    for node in rg:
        if not node == root:
            min = float('inf')
            for in_nbr in rg[node]:
                if rg[node][in_nbr] < min:
                    min = rg[node][in_nbr]
            for in_nbr in rg[node]:
                rg[node][in_nbr] -= min
    print("Edge weights updated.")
    sys.stdout.flush()

def compute_rdst_candidate(rg, root):
    print("Computing RDST candidate...")
    sys.stdout.flush()
    candidate = {}
    for node in rg:
        candidate[node] = {}
    for node in rg:
        if not node == root:
            min = float('inf')
            for in_nbr in rg[node]:
                if rg[node][in_nbr] < min:
                    min = rg[node][in_nbr]
            for in_nbr in rg[node]:
                if candidate[node] == {}:  
                    if rg[node][in_nbr] == min:
                        candidate[node][in_nbr] = min
    print("RDST candidate computed.")
    sys.stdout.flush()
    return candidate

def get_cycle(rdst_candidate):
    print("Checking for cycles...")
    sys.stdout.flush()
    node_unvisited = []
    for node in rdst_candidate:  
        node_unvisited.append(node)
    while not node_unvisited == []:
        start_node = node_unvisited.pop()  
        stack = []  
        trail = []  
        stack.append(start_node)
        while not len(stack) == 0:
            node = stack.pop(-1)
                               print("Cycle detected.")
                    sys.stdout.flush()
                    return tuple(trail[trail.index(nbr):]) 
                else:
                    stack.append(nbr)
                    trail.append(nbr)
                    if nbr in node_unvisited:
                        node_unvisited.remove(nbr)
    print("No cycle found.")
    sys.stdout.flush()
    return False

def contract_cycle(g, cycle):
    print("Contracting cycle...")
    sys.stdout.flush()
    cstar = max(g.keys()) + "1"
    contracted_graph = {}
    contracted_graph[cstar] = {}
    for node in g:
        if not node in cycle:
            contracted_graph[node] = {}
    for node in g:
        for nbr in g[node]:
            if node in cycle:
                if nbr in cycle:
                    pass
                else: 
                    if nbr in contracted_graph[cstar]:
                        contracted_graph[cstar][nbr] = min(contracted_graph[cstar][nbr], g[node][nbr])
                    else:
                        contracted_graph[cstar][nbr] = g[node][nbr]
            else:
                if nbr in cycle:
                    if cstar in contracted_graph[node]:
                        contracted_graph[node][cstar] = min(contracted_graph[node][cstar], g[node][nbr])
                    else:
                        contracted_graph[node][cstar] = g[node][nbr]
                else:
                    contracted_graph[node][nbr] = g[node][nbr]
    print("Cycle contracted.")
    sys.stdout.flush()
    return contracted_graph, cstar

def expand_graph(g, rdst_candidate, cycle, cstar):
    print("Expanding graph...")
    sys.stdout.flush()
    restored_graph = {}
    for node in g:
        restored_graph[node] = {}
    for node in rdst_candidate:  
        for nbr in rdst_candidate[node]:
            if node == cstar:  
                min = float('inf')
                for orig in cycle:
                    if nbr in g[orig]:
                        if g[orig][nbr] < min:
                            min = g[orig][nbr]
                            point = orig
                restored_graph[point][nbr] = min
            else:
                if nbr == cstar:  
                    min = float('inf')
                   ]:
                        if orig_nbr in cycle:
                            if g[node][orig_nbr] < min:
                                min = g[node][orig_nbr]
                                start_pt = orig_nbr  
                    restored_graph[node][start_pt] = min
                else: 
                    restored_graph[node][nbr] = g[node][nbr]
    for index in range(len(cycle) - 1): 
        restored_graph[cycle[index + 1]][cycle[index]] = g[cycle[index + 1]][cycle[index]]
    restored_graph[cycle[0]][cycle[-1]] = g[cycle[0]][cycle[-1]]
    index = cycle.index(start_pt)
    if index == len(cycle) - 1:
        restored_graph[cycle[0]].pop(cycle[index])
    else:
        restored_graph[cycle[index + 1]].pop(cycle[index])
    print("Graph expanded.")
    sys.stdout.flush()
    restored_graph

def bfs(g, startnode):
    print("Running BFS...")
    sys.stdout.flush()
    dist = {}
    for node in g:
        dist[node] = float('inf')
    dist[startnode] = 0
    queue = deque([startnode])
    while queue:
        node = queue.popleft()
        for nbr in g[node]:
            if dist[nbr] == float('inf'):
                dist[nbr] = dist[node] + 1
                queue.append(nbr)
    return dist

def compute_rdmst(g, root):
    print("Computing RDMST...")
    sys.stdout.flush()
    if root not in g:
        print("The root node does not exist")
        sys.stdout.flush()
        return
    distances = bfs(g, root)
    for node in g:
        if distances[node] == float('inf'):
            print("The root does not reach every other node in the graph")
            sys.stdout.flush()
            return
    rdmst = compute_rdmst_helper(g, root)
    rdmst_weight = 0
    for node in rdmst:
        for nbr in rdmst[node]:
            rdmst[node][nbr] = g[node][nbr]
            rdmst_weight += rdmst[node][nbr]
    print("RDMST computation completed.")
    sys.stdout.flush()
    return (rdmst, rdmst_weight)

def compute_rdmst_helper(g, root):
    print("Computing RDMST helper...")
    sys.stdout.flush()
    rgraph = reverse_g(g)
    update_dege(rgraph, root)
    rdst_candidate = compute_rdst_candidate(rgraph, root)
    cycle = get_cycle(rdst_candidate)
    if not cycle:
        print("No cycle detected in helper.")
        sys.stdout.flush()
        return reverse_g(rdst_candidate)
    else:
        print("Cycle detected in helper, contracting...")
        sys.stdout.flush()
        g_copy = deepcopy(rgraph)
        g_copy = reverse_g(g_copy)
        (contracted_g, cstar) = contract_cycle(g_copy, cycle)
        new_rdst_candidate = compute_rdmst_helper(contracted_g, root)
        rdmst = expand_graph(reverse_g(rgraph), new_rdst_candidate, cycle, cstar)
        print("Helper completed.")
        sys.stdout.flush()
        return rdmsti

