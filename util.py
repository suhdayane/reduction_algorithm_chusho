import networkx as nx

def extract_idominators(idominator_tree, node):
    idominators = []
    while idominator_tree[node] != node:
        node = idominator_tree[node]
        idominators.append(node)

    return idominators

def idominator_of_node(G, x):
    end = get_output_node(G)

    # Invert the edges
    inverted_edges = [(v, u) for u, v in G.edges()]

    # Create a new graph with inverted edges
    inverted_G = nx.MultiDiGraph()
    inverted_G.add_edges_from(inverted_edges)

    # Compute the IDominator Tree
    idominator_tree = nx.dominance.immediate_dominators(inverted_G, end)

    # Extract IDominator
    return extract_idominators(idominator_tree, node=x)

def rule_3(G, x, y):
    # Check if OUT(x) >= 2
    if G.out_degree(x) < 2:
        return False

    # Get the set of nodes that have an edge from x (except y)
    neighbors = set(G.successors(x)) - {y}

    # Check if x is a inverse dominator of all w in neighbors
    for w in neighbors:
        # Check if x is in the set of inverse dominators of w
        if x not in set(idominator_of_node(G, w)):
            return False

    return True

def get_input_node(G):
    # Find the input node of the graph
    input_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
    #assert len(input_nodes) == 1, "The graph must have exactly one input node."
    return input_nodes[0]

def get_output_node(G):
    # Find the input node of the graph
    output_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
    #assert len(input_nodes) == 1, "The graph must have exactly one output node."
    return output_nodes[0]

def extract_dominators(dominator_tree, node):
    dominators = []
    while dominator_tree[node] != node:
        node = dominator_tree[node]
        dominators.append(node)

    return dominators

def dominator_of_node(G, x):
    start = get_input_node(G)
    
    # Compute the Dominator Tree
    dominator_tree = nx.dominance.immediate_dominators(G, start)

    # Extract Dominator
    return extract_dominators(dominator_tree, node=x)

def rule_4(G, x, y):
    # Check if IN(y) >= 2
    if G.in_degree(y) < 2:
        return False
    
    # Get all nodes w such that (w, y) is an arc in G, w != x
    neighbors = set(G.predecessors(y)) - {x}
    
    # Check if x is a dominator of all w_nodes
    for w in neighbors:
        if x not in set(dominator_of_node(G, w)):
            return False
    
    # If all conditions are satisfied, (x, y) satisfies rule 4
    return True

def remove_edge(G, x, y, map={}):    
    if (x, y) not in G.edges():
        return G
    
    # Returns successor nodes of y
    successors_x = list(G.out_edges(x))
    predecessors_x = list(G.in_edges(x))

    # Returns successor nodes of y
    successors_y = list(G.out_edges(y))
    predecessors_y = list(G.in_edges(y))

    for predecessors in predecessors_x:
        map[(predecessors[0], x + ',' + y)] = (predecessors[0], x)
    
    for successors in successors_x:
        map[(x + ',' + y, successors[1])] = (x, successors[1])

    for predecessors in predecessors_y:
        map[(predecessors[0], x + ',' + y)] = (predecessors[0], y)
    
    for successors in successors_y:
        map[(x + ',' + y, successors[1])] = (y, successors[1])

    map[(x, y)] = 'REMOVED'
    
    # Adds the edges with the merged node between 
    # successor nodes
    for sucessor in successors_y:
        if sucessor[1] == y:
            G.add_edge(x, x)
            #map[(x + ',' + y, x + ',' + y)] = (y, y) 
        else:
            G.add_edge(x, sucessor[1])    
            #map[(x + ',' + y, sucessor[1])] = (y, sucessor[1])    

    # Adds the edges with the merged node between 
    # successor nodes
    for predecessors in predecessors_y:
        if predecessors[0] != x and predecessors[0] != y:
            G.add_edge(predecessors[0], x)
            #map[(predecessors[0], x + ',' + y)] = (predecessors[0], y) 

    G.remove_node(y)

    # Rename node for new merged name
    mapping = {x: x + ',' + y}
    return nx.relabel_nodes(G, mapping)

def rule_1(G, x, y) -> bool:
    in_degree = G.in_degree(x)
    out_degree = G.out_degree(x)

    if in_degree > 0 and out_degree == 1:
        return True
    return False

def rule_2(G, x, y) -> bool:
    in_degree = G.in_degree(y)
    out_degree = G.out_degree(y)
        
    if in_degree == 1 and out_degree > 0:
        return True
    
    return False

def apply_rule1(G, map={}):
    is_rule_applied = True
    while(is_rule_applied):
        is_rule_applied = False

        # Get edges of the graph as lists
        edges = list(G.edges(data=False))

        for (x, y) in edges:       
            if (x != y) and rule_1(G, x, y):
                is_rule_applied = True

                G = remove_edge(G, x, y, map)

                break
    return G

def apply_rule2(G, map={}):    
    is_rule_applied = True
    while(is_rule_applied):
        is_rule_applied = False

        # Get edges of the graph as lists
        edges = list(G.edges(data=False))

        for (x, y) in edges:
            if (x != y) and rule_2(G, x, y):
                is_rule_applied = True
                G = remove_edge(G, x,y, map)
                break
    return G

def cond_in(G, x, marked) -> bool:
    ingoing_edges = G.in_edges(x)

    for ingoing_edge in ingoing_edges:
        if ingoing_edge not in marked:
            return True
    
    return False

def cond_out(G, y, marked) -> bool:
    outgoing_edges = G.out_edges(y)

    for outgoing_edge in outgoing_edges:
        if outgoing_edge not in marked:
            return True
    
    return False

def cond_cycle(G, x, y, marked) -> bool:
    cycles = nx.algorithms.cycles.simple_cycles(G)

    for cycle in cycles:
        if x not in cycle:
            continue

        cycle_edges = [(cycle[i], cycle[(i+1) % len(cycle)]) for i in range(len(cycle)) if (cycle[i], cycle[(i+1) % len(cycle)]) != (x,y)]

        for edge in cycle_edges:
            if edge not in marked:
                return True
    
    return False

def cond_cycle_inverse(G, x, y, marked) -> bool:
    inverted_edges = [(v, u) for u, v in G.edges()]

    inverted_G = nx.MultiDiGraph()
    inverted_G.add_edges_from(inverted_edges)

    return cond_cycle(inverted_G, y, x, marked)

def apply_rule3_and_4(G):
    for edge in G.edges(data=True): edge[2]['label'] = str(edge[0]) + ',' + str(edge[1])

    map_edges = {}
    marked = []

    # Get edges of the graph as lists
    edges = list(G.edges())

    for (x, y) in edges:
        if rule_3(G, x, y) and (cond_in(G, x, marked) or cond_cycle(G, x, y, marked)):
            marked.append((x,y))

    # Get edges of the graph as lists
    edges = list(G.edges())

    for edge in edges:
        x = edge[0]
        y = edge[1]

        if rule_4(G, x, y) and (cond_out(G, y, marked) or cond_cycle_inverse(G, x, y, marked)):
            marked.append((x,y))

    removed_map = {}

    for mark in marked:
        x = mark[0]
        y = mark[1]

        print('prev: ', (x,y))

        if x in removed_map:
            x = removed_map[x]
        
        if y in removed_map:
            y = removed_map[y]

        print('after: ', (x,y))
        print(removed_map)

        # Returns successor nodes of y
        successors_y = list(G.out_edges(y))
        predecessors_y = list(G.in_edges(y))

        # Adds the edges with the merged node between 
        # successor nodes
        for sucessor in successors_y:
            if sucessor[1] == y:
                G.add_edge(x, x)
            else:
                G.add_edge(x, sucessor[1])  
                
        # Adds the edges with the merged node between 
        # successor nodes
        for predecessors in predecessors_y:
            if predecessors[0] != x and predecessors[0] != y:
                G.add_edge(predecessors[0], x)

        if y in G.nodes:    
            G.remove_node(y)

        removed_map[x] = x + ',' + y
        removed_map[y] = x + ',' + y

        # Rename node for new merged name
        mapping = {x: x + ',' + y}
        G = nx.relabel_nodes(G, mapping)
        
    return G

def apply_all_rules(G):
    G = apply_rule1(G)
    G = apply_rule2(G)
    G = apply_rule3_and_4(G)
    
    return G