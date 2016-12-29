import time
import ppl_functions as pplf
import networkx as nx
from sage.libs.ppl import NNC_Polyhedron

#----------------------------------------------------------------------------------------------#
def node_inclusion(G,element):
	
	""" Look for the locations in the hybrid automaton graph G including an element. """
	
	loc_list = []
	
	nodes = G.nodes()
	for node in nodes:
		invariant = G.node[node]['inv']
		
		if invariant.contains(element):
			loc_list.append(node)
	
	return loc_list


#----------------------------------------------------------------------------------------------#
def cls_node_inclusion(G,element):
	
	""" Look for the locations in the graph G including an element into the closure of the invariant. """
	
	loc_list = []
	
	nodes = G.nodes()
	for node in nodes:
		invariant = G.node[node]['inv']
		invariant.topological_closure_assign()
		
		if invariant.contains(element):
			loc_list.append(node)
	
	return loc_list



#----------------------------------------------------------------------------------------------#
def CC_node_inclusion(SCCG,element,CC):
	
	""" Obtains a list of locations in the connected component CC such that the closure of the 
	invariant contains the element. """

	G = SCCG.node[CC]['int_graph']
	loc_list = cls_node_inclusion(G,element)

	return loc_list



#----------------------------------------------------------------------------------------------#
def performance_locs(loc_list,element1,element2,C,SCCG):

	""" List of locations in loc_list such that the first element can reach the second one. """

	CG = SCCG.node[C]['int_graph']
	perf_loc_list = []
	for loc in loc_list:
		dyn = CG.node[loc]['dyn']
		relpoly = pplf.relation_reach.relation_polyhedron(element1,element2,[dyn])
		if not relpoly.is_empty():
			perf_loc_list.append(loc)

	return perf_loc_list

#----------------------------------------------------------------------------------------------#
def belong_to_border(element1,element2):
	
	""" Check if the element2 belongs to the border of element1. """
	""" Gets the topological closure of the element1. """
	aux_elem = NNC_Polyhedron(element1)
	aux_elem.topological_closure_assign()
	
	""" The element2 belongs to the border if its intersection with the topological closure of
	element1 is not empty and the dimension of element2 is smaller than the one of element1. """
	if not pplf.ppl_functions.intersection(aux_elem,element2).is_empty() and (element2.affine_dimension() < element1.affine_dimension()):
		return True
	else:
		return False


#----------------------------------------------------------------------------------------------#
def adjacent_elements(E,element):
	
	""" Get the elements in the boundary of an element. """
	
	# Consider the elements belonging to the closure of the element
	adj_elem = []
	for e in E:
		if belong_to_border(element,e):
			#print 'element',element.constraints(),'has in the border',e.constraints()
			adj_elem.append(e)
	
	return adj_elem



#----------------------------------------------------------------------------------------------#
def adjacent_elements_v2(E,element):
	
	""" Get the adjacent elements of an element. """
	
	# Consider the elements belonging to the closure of the element
	dim = element.space_dimension()
	adj_elem = []
	aux_element = NNC_Polyhedron(element)
	aux_element.topological_closure_assign()
	for e in E:
		if aux_element.contains(e) and e.affine_dimension()<dim:        # The maximal elements are not considered as adjacent elements of themselves
			#print 'element',element.constraints(),'has as adjacent element',e.constraints()
			adj_elem.append(e)
	
	return adj_elem



#----------------------------------------------------------------------------------------------#
def subgraph(G,element):
	#print 'ELEMENT for the subgraph =', element.constraints()
	""" Determine a subgraph of G related to a particular element. """
	
	subgraph_time = time.time()
    
	#new_invariants = []
	new_dyn_list = []
	nodes_subgraph = []
    
	""" Gets the nodes in G such that the element is contained in the invariant and the new flows 
	are computed. """
	nodes = G.nodes()
	for node in nodes:
		
		invariant = G.node[node]['inv']
		dynamics = G.node[node]['dyn']
	
		if invariant.contains(element):

			#new_inv = pplf.ppl_functions.intersection(element,invariant)
			#new_invariants.append(new_inv)
			ppoly = pplf.ppl_functions.plane_element(element)
			new_dyn = pplf.ppl_functions.intersection(ppoly,dynamics)
			new_dyn_list.append(new_dyn)
			nodes_subgraph.append(node)
	
	""" Obtains the subgraph of G with the selected nodes. """
	SubG = nx.subgraph(G,nodes_subgraph)
	# we make a copy to avoid that any change in the subgraph affects to the original graph
	SG = nx.DiGraph(SubG)

	""" Set the new invariants and dynamics. """
	for i in range(len(nodes_subgraph)):
		#SG.node[nodes_subgraph[i]]['inv'] = new_invariants[i]
		SG.node[nodes_subgraph[i]]['inv'] = element
		SG.node[nodes_subgraph[i]]['dyn'] = new_dyn_list[i]
	
	""" Deletes the edges where the element is not contained in the guard and set the new guard. """
	edges = SG.edges()
	for edge in edges:
		
		prenode = edge[0]
		postnode = edge[1]
		
		guard = G[prenode][postnode]['guard']
		
		#if guard.contains(element) == False:
			#SG.remove_edge(edge[0],edge[1])
		#print 'guard =',guard
		if guard.contains(element):
			SG[prenode][postnode]['guard'] = element
	
		else:
			SG.remove_edge(prenode,postnode)
	
	
	subgraph_time = time.time() - subgraph_time

	return SG,subgraph_time


#----------------------------------------------------------------------------------------------#
def delete_empty_dyn(SG):

	""" Delete the nodes in the subgraph with empty dynamics. """
	for node in SG.nodes():
		dyn_poly = SG.node[node]['dyn']
		if dyn_poly.is_empty():
			SG.remove_node(node)

	return SG






