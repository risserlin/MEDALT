
import gc
import tracemalloc
import psutil
from datetime import datetime as dt_
from concurrent.futures import ThreadPoolExecutor


def pc_mem():
    """Return current process memory usage in GB."""
    process = psutil.Process()
    mem_bytes = process.memory_info().rss
    return mem_bytes / 1e9  # Convert to GB


def get_dynamic_chunk_size(base_chunk=5000, memory_fraction=0.1):
    """Determine chunk size based on available RAM."""
    available_mem = psutil.virtual_memory().available / 1e9  # GB
    # Assume each node costs ~1MB (adjust if needed)
    estimated_nodes_per_gb = 1000
    dynamic_size = int(available_mem * estimated_nodes_per_gb * memory_fraction)
    return max(base_chunk, dynamic_size)


def compute_rdmst(g, root, recursive=True, parallel=False, max_workers=4):
    tracemalloc.start()
    st_mem = pc_mem()
    t0 = dt_.now()
    print(f"Starting RD-MST computation. Initial memory: {st_mem:.2f} GB")

    chunk_size = get_dynamic_chunk_size()
    print(f"Dynamic chunk size set to {chunk_size} nodes based on available RAM.")

    if len(g) > chunk_size:
        print(f"Graph too large ({len(g)} nodes). Splitting into chunks of {chunk_size}...")
        chunks = chunk_graph(g, chunk_size)
        results = []
        for i, subgraph in enumerate(chunks, 1):
            print(f"\nProcessing chunk {i}/{len(chunks)}... Current memory: {pc_mem():.2f} GB")
            if recursive:
                rdmst_chunk = rdmst_recursor(subgraph, root, 0, t0, dt_.now(), st_mem)
            else:
                rdmst_chunk = rdmst_iterative(subgraph, root, parallel=parallel, max_workers=max_workers)
            results.append(rdmst_chunk)
        rdmst = merge_chunks(results)
    else:
        print(f"Processing full graph. Current memory: {pc_mem():.2f} GB")
        if recursive:
            rdmst = rdmst_recursor(g, root, 0, t0, dt_.now(), st_mem)
        else:
            rdmst = rdmst_iterative(g, root, parallel=parallel, max_workers=max_workers)

    print(f"\nTotal time: {dt_.now()-t0}")
    print(f"Final memory usage: {pc_mem():.2f} GB")
    log_memory()
    tracemalloc.stop()
    return rdmst


def log_memory():
    current, peak = tracemalloc.get_traced_memory()
    print(f"Memory usage: {current/1e9:.2f} GB; Peak: {peak/1e9:.2f} GB")


def chunk_graph(g, chunk_size):
    """Split graph into chunks for memory-safe processing."""
    nodes = list(g.keys())
    chunks = []
    for i in range(0, len(nodes), chunk_size):
        sub_nodes = nodes[i:i+chunk_size]
        subgraph = {n: {nbr: g[nbr] for nbr in g[n] if nbr in sub_nodes} for n in sub_nodes}
        chunks.append(subgraph)
    return chunks


def merge_chunks(chunks):
    """Merge processed chunks back into a single graph."""
    merged = {}
    for chunk in chunks:
        merged.update(chunk)
    return merged

def rdmst_recursor(g__inputed, root_node, recurr_idx, t0, ts, st_mem):
    recurr_idx += 1
    if recurr_idx % 5 == 0:
        print(f"\r{recurr_idx:4d} loops shrunk, elapsed: {dt_.now()-t0}, mem: {pc_mem()-st_mem:.2f} GB", end="")
        ts = dt_.now()

    g_reversed = reverse__graph(g__inputed)
    g_rev_cont = contract_graph(g_reversed, root_node)
    g_rdst_min = get_rdst_graph(g_rev_cont, root_node)
    loop_in_gr = find_graphloop(g_rdst_min)

    if not loop_in_gr:
        print(f"\nAll {recurr_idx:4d} loops contracted, recovering tree...")
        return reverse__graph(g_rdst_min)
    else:
        g_contract = reverse__graph(g_rev_cont)
        g___pruned, loop_nodes = prune____graph(g_contract, loop_in_gr)

        # Cleanup
        del g_reversed, g_rev_cont, g__inputed, g_rdst_min
        gc.collect()

        g_new_rdst = rdmst_recursor(g___pruned, root_node, recurr_idx, t0, ts, st_mem)
        g_expanded = expand___graph(g_contract, g_new_rdst, loop_in_gr, loop_nodes)
        return g_expanded

def rdmst_iterative(g, root, parallel=False, max_workers=4):
    stack = [(g, root)]
    result_graph = None
    t0 = dt_.now()
    st_mem = pc_mem()

    while stack:
        g_current, root_node = stack.pop()
        g_reversed = reverse__graph(g_current)
        g_rev_cont = contract_graph(g_reversed, root_node)
        g_rdst_min = get_rdst_graph(g_rev_cont, root_node)
        loop_in_gr = find_graphloop(g_rdst_min)

        if not loop_in_gr:
            result_graph = reverse__graph(g_rdst_min)
            break
        else:
            g_contract = reverse__graph(g_rev_cont)
            g___pruned, loop_nodes = prune____graph(g_contract, loop_in_gr)

            if parallel:
                with ThreadPoolExecutor(max_workers=max_workers) as executor:
                    future = executor.submit(expand___graph, g_contract, g___pruned, loop_in_gr, loop_nodes)
                    expanded_graph = future.result()
            else:
                expanded_graph = expand___graph(g_contract, g___pruned, loop_in_gr, loop_nodes)

            stack.append((expanded_graph, root_node))

        # Cleanup
        del g_reversed, g_rev_cont, g_rdst_min
        gc.collect()

    print(f"\nTotal time: {dt_.now()-t0}, Memory used: {pc_mem()-st_mem:.2f} GB")
    return result_graph

