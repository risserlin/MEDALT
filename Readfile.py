import time
import sys

def read(filename):
    """
    Reads genomic data from a file and constructs nodes and root.
    Adds:
    - Progress messages
    - Summary stats (execution time, memory usage, node count)
    - Auto-flush for immediate output
    """

    print "[INFO] Starting file read: {}".format(filename)
    sys.stdout.flush()
    start_time = time.time()

    nodes = {}
    charlist = []
    chromosome = []
    CNV = {}

    # Chromosome list
    for ele in range(1, 23):
        chromosome.append("chr" + str(ele))
    chromosome.append("chrX")
    chromosome.append("chrY")

    # Open file
    data = open(filename)
    line = next(data)
    line = line[0:-1].split("\t")

    segDist = {}
    k = 0
    for ele in line:
        ele = ele.split("_")[0]
        segDist.setdefault(ele, []).append(k)
        k += 1

    # Build charlist
    for ele in chromosome:
        if segDist.has_key(ele):
            charlist.append((min(segDist[ele]), max(segDist[ele]) + 1))
    if segDist.has_key("chr23"):
        charlist.append((min(segDist["chr23"]), max(segDist["chr23"]) + 1))
    if segDist.has_key("chr24"):
        charlist.append((min(segDist["chr24"]), max(segDist["chr24"]) + 1))

    print "[INFO] Chromosome segments processed: {}".format(len(charlist))
    sys.stdout.flush()

    # Process data lines
    line_count = 0
    for line in data:
        line_count += 1
        if line_count % 100 == 0:
            print "[PROGRESS] Processed {} lines...".format(line_count)
            sys.stdout.flush()

        array = line.split()
        name = array.pop(0)
        snip = []
        CNVvalue = []
        for (a, b) in charlist:
            snip.append(map(int, array[a:b]))
            CNVvalue.extend(map(int, array[a:b]))
        nodes[name] = snip
        CNV[name] = list(set(CNVvalue))

    data.close()

    # Determine root
    root = 'NA'
    for ele in CNV.keys():
        if CNV[ele] == [2]:
            root = ele
    if root == "NA":
        snip = []
        for (a, b) in charlist:
            snip.append([2] * (b - a))
        nodes['root'] = snip
        root = 'root'

    elapsed_time = time.time() - start_time
    approx_mem = sys.getsizeof(nodes)

    # Summary stats
    print "[INFO] File read complete."
    print "Execution Time: {:.4f} seconds".format(elapsed_time)
    print "Approx Memory Usage: {} bytes".format(approx_mem)
    print "Total Nodes: {}".format(len(nodes))
    print "Root Node: {}".format(root)
    sys.stdout.flush()

    return nodes, root

# Returns a dictionary mapping node names to list of list of integers representing list of copy number list
#def read(filename):
#    nodes = {}
#    charlist=[]
#    chromosome=[]
#    CNV={}
#    for ele in range(1,23):
#        chromosome.append("chr"+str(ele))
#    chromosome.append("chrX")
#    chromosome.append("chrY")
#    data=open(filename)
#    line=next(data)
#    line=line[0:-1].split("\t")
#    segDist={}
#    k=0
#    for ele in line:
#        ele=ele.split("_")[0]
#        segDist.setdefault(ele,[]).append(k)
#        k=k+1
#    for ele in chromosome:
#        if segDist.has_key(ele):
#            charlist.append((min(segDist[ele]),max(segDist[ele])+1))
#    if segDist.has_key("chr23"):
#        charlist.append((min(segDist["chr23"]),max(segDist["chr23"])+1))
#    if segDist.has_key("chr24"):
#        charlist.append((min(segDist["chr24"]),max(segDist["chr24"])+1))
#    for line in data:
#        array = line.split()
#        name = array.pop(0)
#        snip = []
#        CNVvalue = []
#        for (a,b) in charlist:
#            snip.append(map(int, array[a:b]))
#            CNVvalue.extend(map(int, array[a:b]))
#        nodes[name] = snip
#        CNV[name]=list(set(CNVvalue))
#    data.close()
#    root = 'NA'
#    for ele in CNV.keys():
#        if CNV[ele] == [2]:
#            root=ele
#    if root == "NA":
#        snip=[]
#        for (a,b) in charlist:
#            snip.append([2]*(b-a))
#        nodes['root']=snip
#        root='root'
#    return nodes,root
