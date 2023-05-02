import networkx as nx
import matplotlib.pyplot as plt


def extract_idominators(idominator_tree, node):
    idominators = []
    while idominator_tree[node] != node:
        node = idominator_tree[node]
        idominators.append(node)

    return idominators

def extract_dominators(dominator_tree, node):
    dominators = []
    while dominator_tree[node] != node:
        node = dominator_tree[node]
        dominators.append(node)

    return dominators

def idominator_of_node(G, x, end):
    # Invert the edges
    inverted_edges = [(v, u) for u, v in G.edges()]

    # Create a new graph with inverted edges
    inverted_G = nx.DiGraph()
    inverted_G.add_edges_from(inverted_edges)

    # Compute the IDominator Tree
    idominator_tree = nx.dominance.immediate_dominators(inverted_G, end)

    # Extract IDominator
    return extract_idominators(idominator_tree, node=x)

def dominator_of_node(G, x, start):
    # Compute the Dominator Tree
    dominator_tree = nx.dominance.immediate_dominators(G, start)

    # Extract Dominator
    return extract_dominators(dominator_tree, node=x)

def cond_in(G, x, marked) -> bool:
    ingoing_edges = G.in_edges(x)

    number_of_ingoing = 0
    for ingoing_edge in ingoing_edges:
        if ingoing_edge in marked:
            number_of_ingoing += 1
    
    if number_of_ingoing >= len(ingoing_edges):
        return False
    
    return True

def cond_out(G, x, marked) -> bool:
    outgoing_edges = G.out_edges(x)

    number_of_outgoing = 0
    for outgoing_edge in outgoing_edges:
        if outgoing_edge in marked:
            number_of_outgoing += 1
    
    if number_of_outgoing >= len(outgoing_edges):
        return False
    
    return True

def cond_cycle(G, x, y, marked) -> bool:
    cycles = nx.algorithms.cycles.simple_cycles(G)

    for cycle in cycles:
        if cycle[0] != x:
            continue

        cycle_edges = [(cycle[i], cycle[i+1]) for i in range(len(cycle)-1)]
        cycle_edges.append((cycle[-1], cycle[0]))

        number_of_marked = sum(1 for edge in cycle_edges if edge != (x, y) and edge in marked)
        less_one = (x, y) in cycle_edges

        if less_one and number_of_marked >= len(cycle_edges) - 1:
            return False
        elif not less_one and number_of_marked >= len(cycle_edges):
            return False
    
    return True

def cond_cycle_inverse(G, x, y, marked) -> bool:
    inverted_edges = [(v, u) for u, v in G.edges()]

    inverted_G = nx.DiGraph()
    inverted_G.add_edges_from(inverted_edges)

    return cond_cycle(inverted_G, x, y, marked)

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


#TODO: Não funciona para 2 ou mais w
def rule_3(G, x, y, end) -> bool:
    out_degree = G.out_degree(x)
        
    if out_degree >= 2:
        outgoing_edges = G.out_edges(x)
        
        for outgoing_edge in outgoing_edges:
            w = outgoing_edge[1]
            
            if w != y:
                if x in idominator_of_node(G, w, end):
                    return True
                
    return False

#TODO: Não funciona para 2 ou mais w
def rule_4(G, x, y, start) -> bool:
    in_degree = G.in_degree(y)
        
    # If the number of incoming edges is greater than 0 and the number of outgoing edges is 1
    if in_degree >= 2:
        ingoing_edges = G.in_edges(y)
        
        for ingoing_edge in ingoing_edges:
            w = ingoing_edge[0]
            
            if w != x:
                if x in dominator_of_node(G, w, start):
                    return True
                
    return False

def remove_edge(G, x, y):
    outgoing_edges = G.out_edges(y)
    
    for outgoing_edge in outgoing_edges:
        G.add_edge(x, outgoing_edge[1])
        G.remove_node(y)

    return G

# Read the .dot file into a NetworkX graph object
G = nx.MultiDiGraph(nx.drawing.nx_pydot.read_dot('Cal_jan1.dot'))

start_node = '0'
end_node = '52'

# RULE 1
is_rule_applied = True
while(is_rule_applied):
    is_rule_applied = False

    # Get edges of the graph as lists
    edges = list(G.edges())

    for edge in edges:
        x = edge[0]
        y = edge[1]

        if rule_1(G, x, y):
            is_rule_applied = True

            G = remove_edge(G, x,y)

            break

# RULE 2
is_rule_applied = True
while(is_rule_applied):
    is_rule_applied = False

    # Get edges of the graph as lists
    edges = list(G.edges())

    for edge in edges:
        x = edge[0]
        y = edge[1]

        if rule_2(G, x, y):
            is_rule_applied = True

            G = remove_edge(G, x,y)

            break


marked_inheritor = []

# RULE 3
is_rule_applied = True
while(is_rule_applied):
    is_rule_applied = False

    # Get edges of the graph as lists
    edges = list(G.edges())

    for edge in edges:
        x = edge[0]
        y = edge[1]

        if rule_3(G, x, y, end_node) and (cond_in(G, x, marked_inheritor) or cond_cycle(G, x, y, marked_inheritor)):
            marked_inheritor.append((x,y))

            is_rule_applied = True

            break


# RULE 4
is_rule_applied = True
while(is_rule_applied):
    is_rule_applied = False

    # Get edges of the graph as lists
    edges = list(G.edges())

    for edge in edges:
        x = edge[0]
        y = edge[1]

        if rule_4(G, x, y, start_node) and (cond_out(G, y, marked_inheritor) or cond_cycle_inverse(G, x, y, marked_inheritor)):
            marked_inheritor.append((x,y))

            is_rule_applied = True

            break


for edge in marked_inheritor:
    edges = list(G.edges())
    if edge in edges:
        G = remove_edge(G, edge[0], edge[1])



# Write the modified graph to a new .dot file
nx.drawing.nx_pydot.write_dot(G, 'modified.dot')


