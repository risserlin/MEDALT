import time
import resource
from collections import deque

def log_step(message):
    """Helper to print message with timestamp and memory usage."""
    mem_kb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss  # memory in KB
    print("[{}] {} | Memory: {} KB".format(time.strftime("%H:%M:%S"), message, mem_kb))

def reverse_g(g):
    log_step("Reversing graph...")
    rev_graph = {node: {} for node in g}
    for a_node in g:
        for b_node in g[a_node]:
            rev_graph[b_node][a_node] = g[a_node][b_node]
    log_step("Graph reversed.")
    return rev_graph

def update_dege(rg, root):
    log_step("Updating edge weights...")
    for node in rg:
        if node != root:
            min_val = float('inf')
            for in_nbr in rg[node]:
                if rg[node][in_nbr] < min_val:
                    min_val = rg[node][in_nbr]
            for in_nbr in rg[node]:
                rg[node][in_nbr] -= min_val
    log_step("Edge weights updated.")

def compute_rdst_candidate(rg, root):
    log_step("Computing RDST candidate...")
    candidate = {node: {} for node in rg}
    for node in rg:
        if node != root:
            min_val = float('inf')
            for in_nbr in rg[node]:
                if rg[node][in_nbr] < min_val:
                    min_val = rg[node][in_nbr]
            for in_nbr in rg[node]:
                if candidate[node] == {} and rg[node][in_nbr] == min_val:
                    candidate[node][in_nbr] = min_val
    log_step("RDST candidate computed.")
    return candidate

def get_cycle(rdst_candidate):
    log_step("Detecting cycle...")
    node_unvisited = list(rdst_candidate.keys())
    while node_unvisited:
        start_node = node_unvisited.pop()
        stack = [start_node]
        trail = []
        while stack:
            node = stack.pop()
            for nbr in rdst_candidate[node]:
                if nbr in trail:
                    log_step("Cycle detected: {}".format(trail[trail.index(nbr):]))
                    return tuple(trail[trail.index(nbr):])
                else:
                    stack.append(nbr)
                    trail.append(nbr)
                    if nbr in node_unvisited:
                        node_unvisited.remove(nbr)
    log_step("No cycle detected.")
    return False

def contract_cycle(g, cycle):
    log_step("Contracting cycle...")
    cstar = str(max(g.keys())) + "1"
    contracted_graph = {cstar: {}}
    for node in g:
        if node not in cycle:
            contracted_graph[node] = {}
    for node in g:
        for nbr in g[node]:
            if node in cycle:
                if nbr in cycle:
                    continue
                else:
                    contracted_graph[cstar][nbr] = min(contracted_graph[cstar].get(nbr, float('inf')), g[node][nbr])
            else:
                if nbr in cycle:
                    contracted_graph[node][cstar] = min(contracted_graph[node].get(cstar, float('inf')), g[node][nbr])
                else:
                    contracted_graph[node][nbr] = g[node][nbr]
    log_step("Cycle contracted.")
    return contracted_graph, cstar

def expand_graph(g, rdst_candidate, cycle, cstar):
    log_step("Expanding graph...")
    restored_graph = {node: {} for node in g}
    for node in rdst_candidate:
        for nbr in rdst_candidate[node]:
            if node == cstar:
                min_val = float('inf')
                for orig in cycle:
                    if nbr in g[orig] and g[orig][nbr] < min_val:
                        min_val = g[orig][nbr]
                        point = orig
                restored_graph[point][nbr] = min_val
            else:
                if nbr == cstar:
                    min_val = float('inf')
                    for orig_nbr in g[node]:
                        if orig_nbr in cycle and g[node][orig_nbr] < min_val:
                            min_val = g[node][orig_nbr]
                            start_pt = orig_nbr
                    restored_graph[node][start_pt] = min_val
                else:
                    restored_graph[node][nbr] = g[node][nbr]
    for i in range(len(cycle) - 1):
        restored_graph[cycle[i + 1]][cycle[i]] = g[cycle[i + 1]][cycle[i]]
    restored_graph[cycle[0]][cycle[-1]] = g[cycle[0]][cycle[-1]]
    idx = cycle.index(start_pt)
    if idx == len(cycle) - 1:
        restored_graph[cycle[0]].pop(cycle[idx])
    else:
        restored_graph[cycle[idx + 1]].pop(cycle[idx])
    log_step("Graph expanded.")
    return restored_graph

def bfs(g, startnode):
    log_step("Running BFS...")
    dist = {node: float('inf') for node in g}
    dist[startnode] = 0
    queue = deque([startnode])
    while queue:
        node = queue.popleft()
        for nbr in g[node]:
            if dist[nbr] == float('inf'):
                dist[nbr] = dist[node] + 1
                queue.append(nbr)
    log_step("BFS completed.")
    return dist

def compute_rdmst_iterative(g, root):
    log_step("Starting iterative RDMST computation...")
    
    # Step 1: Check reachability
    log_step("[STEP 1] Checking reachability from root '{}'...".format(root))
    
    distances = bfs(g, root)

    log_step("[STEP 2] Initializing contraction stack...")
    stack = [(g, root)]
    contracted_info = []
    
    iteration = 0
    while stack:
        iteration += 1
        current_g, current_root = stack.pop()
        log_step("[ITERATION {}] Processing graph with {} nodes".format(iteration, len(current_g)))
        
        rgraph = reverse_g(current_g)
        update_dege(rgraph, current_root)
        
        rdst_candidate = compute_rdst_candidate(rgraph, current_root)
        cycle = get_cycle(rdst_candidate)
        
        if not cycle:
            log_step("[INFO] No cycle detected. Candidate is final.")
            final_candidate = reverse_g(rdst_candidate)
            break
        else:
            log_step("[INFO] Cycle detected: {}".format(cycle))
            contracted_g, cstar = contract_cycle(reverse_g(current_g), cycle)
            contracted_info.append((cycle, cstar, reverse_g(rgraph)))
            stack.append((contracted_g, current_root))
    
    # Step 3: Expand contracted cycles
    log_step("[STEP 3] Expanding contracted cycles...")
    rdmst = final_candidate
    for idx, (cycle, cstar, original_graph) in enumerate(reversed(contracted_info), 1):
        log_step("[INFO] Expanding cycle {} of {}: {}".format(idx, len(contracted_info), cycle))
        rdmst = expand_graph(original_graph, rdmst, cycle, cstar)
    
    # Step 4: Compute weight
    log_step("[STEP 4] Computing total weight of RDMST...")
    rdmst_weight = sum(g[node][nbr] for node in rdmst for nbr in rdmst[node])
    log_step("[RESULT] Total weight: {}".format(rdmst_weight))
    
    return rdmst, rdmst_weight
