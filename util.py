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
        edges = list(G.edges())

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
    # G = apply_rule1(G)
    
    is_rule_applied = True
    while(is_rule_applied):
        is_rule_applied = False

        # Get edges of the graph as lists
        edges = list(G.edges())

        for (x, y) in edges:
            if rule_2(G, x, y):
                print('entrou')
                is_rule_applied = True
                G = remove_edge(G, x,y)
                break
    return G