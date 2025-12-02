from collections import *
from copy import *
import sys
import time
import resource


def log_step(message):
    """Helper to print message with timestamp and memory usage."""
    mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # memory in KB
    print("[{}] {} | Memory: {} KB".format(time.strftime("%H:%M:%S"), message, mem_kb))

def reverse_g(g):
    log_step("Reversing graph...")
    rev_graph = {}
    for node in g:
        rev_graph[node] = {}
    for a_node in g:
        for b_node in g[a_node]:
            rev_graph[b_node][a_node] = g[a_node][b_node]
    log_step("graph reversed.")    
    return rev_graph

def update_dege(rg, root):
    log_step("Updating edge weights...")
    for node in rg:
        if not node == root:
            min = float('inf')
            for in_nbr in rg[node]:
                if rg[node][in_nbr] < min:
                    min = rg[node][in_nbr]
            for in_nbr in rg[node]:
                rg[node][in_nbr] -= min

    log_step("Edge weights updated.")

def compute_rdst_candidate(rg, root):
    log_step("Computing rdst candidates...")
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
    log_step("Computed candidates.")
    return candidate

def get_cycle(rdst_candidate):
    log_step("Get cycles....")
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
            for nbr in rdst_candidate[node]:
                if nbr in trail:
                    return tuple(trail[trail.index(nbr):]) 
                else:
                    stack.append(nbr)
                    trail.append(nbr)
                    if nbr in node_unvisited:
                        node_unvisited.remove(nbr)
    log_step("There are no cycles detected.")
    return False

def contract_cycle(g, cycle):
    log_step("Contracting cycle...")
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

    log_step("Cycle contracted.")
    return contracted_graph, cstar


def expand_graph(g, rdst_candidate, cycle, cstar):
    log_step("Expanding cycle...")
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
                    for orig_nbr in g[node]:
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

    log_step("Cycle expanded")
    return restored_graph

def bfs(g, startnode):
    log_step("Computing Bredth first search...")
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

    log_step("BFS computed.")
    return dist

def compute_rdmst_iterative(g, root):
    
    if root not in g:
        print("The root node does not exist")
        sys.stdout.flush()
        return
    
    # Step 1: Check reachability
    log_step("[STEP 1] Checking reachability from root '{}'...".format(root))

    distances = bfs(g, root)
    
    for node in g:
        if distances[node] == float('inf'):
            print("The root does not reach every other node in the graph")
            sys.stdout.flush()
            return
    
    rdmst = compute_rdmst_helper_iterative(g, root)
    
    log_step("[STEP 4] Computing total weight of RDMST...")
    rdmst_weight = 0
    for node in rdmst:
        for nbr in rdmst[node]:
            rdmst[node][nbr] = g[node][nbr]
            rdmst_weight += rdmst[node][nbr]
    log_step("[RESULT] Total weight: {}".format(rdmst_weight))
    
    return rdmst, rdmst_weight

def compute_rdmst_helper_iterative(g, root):
    log_step("Starting iterative RDMST helper...")
    stack = [(g, None, None, None)]  # (graph, rdst_candidate, cycle, cstar)
    log_step("[STEP 2] Initializing contraction stack...")

    results = []
    iteration = 0 
    while stack:
        iteration += 1
        current_g, rdst_candidate, cycle, cstar = stack.pop()
        
        log_step("[ITERATION {}] Processing graph with {} nodes".format(iteration, len(current_g)))

        if rdst_candidate is None:
            rgraph = reverse_g(current_g)
            update_dege(rgraph, root)
            rdst_candidate = compute_rdst_candidate(rgraph, root)
            cycle = get_cycle(rdst_candidate)
            if not cycle:
                log_step("[INFO] No cycle detected. Candidate is final.")
                results.append(reverse_g(rdst_candidate))
                continue
            log_step("[INFO] Cycle detected: {}".format(cycle))
            g_copy = deepcopy(rgraph)
            g_copy = reverse_g(g_copy)

            contracted_g, new_cstar = contract_cycle(g_copy, cycle)
            stack.append((current_g, rdst_candidate, cycle, new_cstar))
            stack.append((contracted_g, None, None, None))
        else:
            new_rdst_candidate = results.pop()
            expanded = expand_graph(reverse_g(reverse_g(current_g)), new_rdst_candidate, cycle, cstar)
            results.append(expanded)
    log_step("Iterative helper completed.")
    return results.pop()

