import networkx as nx

def remove_edge(G, x, y):    
    if y not in G.nodes():
        return G

    # Returns successor nodes of y
    successors_y = list(G.successors(y))
    
    # Adds the edges with the merged node between 
    # successor nodes
    G.remove_node(y)
    for sucessor in successors_y:
        G.add_edge(x, sucessor)
    
    # Rename node for new merged name
    mapping = {x: x}
    if 'Merge_' not in x:
        mapping = {x: 'Merge_' + x}
    return nx.relabel_nodes(G, mapping)

def rule_1(G, x, y) -> bool:
    if G.in_degree(x) > 0 and G.out_degree(x) == 1:
        return True
    return False

def apply_rule1(G):
    is_rule_applied = True
    while(is_rule_applied):
        is_rule_applied = False

        # Get edges of the graph as lists
        edges = list(G.edges(data=False))

        for (x, y) in edges:       
            if rule_1(G, x, y):
                is_rule_applied = True
                G = remove_edge(G, x,y)
                break
    return G

def rule_2(G, x, y) -> bool:
    in_degree = G.in_degree(y)
    out_degree = G.out_degree(y)
        
    if in_degree == 1 and out_degree > 0:
        return True
    
    return False

def apply_rule2(G):
    G = apply_rule1(G)
    
    is_rule_applied = True
    while(is_rule_applied):
        is_rule_applied = False

        # Get edges of the graph as lists
        edges = list(G.edges(data=False))

        for (x, y) in edges:
            if rule_2(G, x, y):
                is_rule_applied = True
                G = remove_edge(G, x,y)
                break
    return G

def get_output_node(G):
    # Find the output node of the graph
    output_nodes = [n for n in G.nodes() if G.out_degree(n) == 0]
    assert len(output_nodes) == 1, "The graph must have exactly one output node."
    return output_nodes[0]

def get_idominators(G, w):
    output_node = get_output_node(G)
        
    # Initialize the list of inverse domains of w as the set of all nodes
    # of the graph, except w
    inv_dom = set(G.nodes()) - {w}
    
    # Check for selfloop, if there is w is inverse dominator of itself
    if w in G.successors(w):
        inv_dom = set(G.nodes())
        
        # If there is a selfloop and the node is the output node, w is its only inverse denominator
        if w == output_node:
            return list(w)
        
    # If w is the output node and there is no selfloop, w has no inverse denominators
    if w == output_node:
        return list()
        
    # For each path from w to the output node, remove from the dominator list
    # inverses of w nodes that are not present in all paths
    for path in nx.all_simple_paths(G, w, output_node):
        inv_dom &= set(path)
    
    # Returns the list of inverse dominators of w4
    return list(inv_dom)

def rule_3(G, x, y):
    # Check if OUT(x) >= 2
    if G.out_degree(x) < 2:
        return False

    # Get the set of nodes that have an edge from x (except y)
    neighbors = set(G.successors(x)) - {y}

    # Check if x is a inverse dominator of all w in neighbors
    for w in neighbors:
        # Check if x is in the set of inverse dominators of w
        if x not in set(get_idominators(G, w)):
            return False

    return True

def mark_inheritor_rule_3(G, x, y):
    # Check if (x, y) satisfies rule 3
    if rule_3(G, x, y):
        # Check if there is at least one incoming arc without the inheritor mark
        has_unmarked_incoming_arc = any(not G.edges(data=False)[incoming_arc]['inheritor'] for incoming_arc in G.in_edges(x))
        
        # Check if there is at least one outgoing arc without the inheritor mark, except (x, y)
        outgoing_arcs = set(G.out_edges(x)) - {(x, y)}
        paths_from_outgoing_arcs_to_x = []
        for outgoing_arc in outgoing_arcs:
            paths_from_outgoing_arcs_to_x.extend(nx.all_simple_paths(G, outgoing_arc[1], x))
        has_unmarked_outgoing_arc = any(
            not G.edges(data=False)[outgoing_arc]['inheritor'] for outgoing_arc in G.out_edges(paths_from_outgoing_arcs_to_x))
        
        # If there is at least one unmarked incoming or outgoing arc, mark (x, y) as inheritor
        if has_unmarked_incoming_arc or has_unmarked_outgoing_arc:
            G.edges(data=False)[x, y]['inheritor'] = True

    return G

def apply_rule_3(G):
    for (x, y) in G.edges(data=False):
        G = mark_inheritor_rule_3(G, x, y)
        
    return G

def get_input_node(G):
    # Find the input node of the graph
    input_nodes = [n for n in G.nodes() if G.in_degree(n) == 0]
    assert len(input_nodes) == 1, "The graph must have exactly one input node."
    return input_nodes[0]

def get_dominators(G, w):
    input_node = get_input_node(G)
        
    # Initialize the list of dominators of w as the set of all nodes
    # of the graph, except w
    dom = set(G.nodes()) - {w}
    
    # Check for selfloop, if there is w is dominator of itself
    if w in G.successors(w):
        dom = set(G.nodes())
        
        # If there is a selfloop and the node is the input node, w is its only dominator
        if w == input_node:
            return list(w)
        
    # If w is the input node and there is no selfloop, w has no dominators
    if w == input_node:
        return list()
        
    # For each path from input_node to w, remove from the dominator list
    # of w nodes that are not present in all paths
    for path in nx.all_simple_paths(G, input_node, w):
        dom &= set(path)
    
    # Returns the list of dominators of w
    return list(dom)

def rule_4(G, x, y):
    # Check if IN(y) >= 2
    if G.in_degree(y) < 2:
        return False
    
    # Get all nodes w such that (w, y) is an arc in G, w != x
    neighbors = set([w for (w, v) in G.in_edges(y) if w != x])
    
    # Check if x is a dominator of all w_nodes
    for w in neighbors:
        if x not in set(get_dominators(G, w)):
            return False
    
    # If all conditions are satisfied, (x, y) satisfies rule 4
    return True

def mark_inheritor_rule_4(G, x, y):
    if rule_4(G, x, y):
        # Check for unmarked outgoing arcs from y
        has_unmarked_outgoing_arc = any(not G.edges(data=False)[outgoing_arc]['inheritor'] for outgoing_arc in G.out_edges(y) if outgoing_arc != (x, y))

        # Get all nodes with incoming edges to y, except x
        input_nodes = [node for node in G.predecessors(y) if node != x]

        # Generate all simple paths from input nodes to y
        paths_to_y = []
        for node in input_nodes:
            paths_to_y.extend(nx.all_simple_paths(G, node, y))

        # Check if there is at least one arc without the inheritor mark in each path
        has_unmarked_arc = False
        for path in paths_to_y:
            for i in range(len(path) - 1):
                u, v = path[i], path[i+1]
                if u == x and v == y:
                    continue
                if G.edges.get((u, v)) is None or not G.edges[u, v].get('inheritor'):
                    has_unmarked_arc = True
                    break
            if has_unmarked_arc:
                break

        # Mark the inheritor of (x, y) as True, if necessary
        if has_unmarked_outgoing_arc or has_unmarked_arc:
            G.edges[x, y]['inheritor'] = True

    return G
