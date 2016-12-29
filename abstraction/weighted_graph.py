__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"

import abstraction_functions as absf
import ppl_functions as pplf
import networkx as nx
import optimization as opt
import sys


#----------------------------------------------------------------------------------------------#
def set_nodes(WG,G,E):
	
	""" Creation of the nodes for the weighted abstract graph. They correspond to location-element
	pairs. The location is in the graph G and the element is in E. """
	
	for node in G.nodes():
        	for element in E:
			invariant = G.node[node]['inv']
			element_str = str(element.constraints())
            		# check if the element is contained in the invariant
			if invariant.contains(element):
				node_tuple = (node,element_str)
				dim = element.affine_dimension()
				WG.add_node(node_tuple,dim=dim)

	return WG



#----------------------------------------------------------------------------------------------#
def set_edges_and_weights(WG,G,E):
	
	""" Creation of the edges in the weighted abstract graph. They correspond to the presence
	of an element execution between location-element pairs. The weight on an edge corresponds
	to an upper-bound on the scaling of the executions represented by the edges. """
	
	subgraph_time = 0
	optimization_time = 0
	
	""" Creation of all the subgraphs associated to elements. """
	SG_dict = dict()
	
	for element in E:
		
		element_SG,sg_time = absf.subgraph(G,element)
		subgraph_time = subgraph_time + sg_time
		SG_dict[str(element.constraints())] = element_SG
	
	""" Loop for edge construction. """
	for element in E:
		str_element = str(element.constraints())
		
		""" We check only for elements which are not points. """
		dim_element = element.affine_dimension()
		SG = SG_dict[str_element]
		if (dim_element != 0) and (SG.nodes()):
			
			""" Extraction of the strongly connected components of the subgraph associated with the element 
			and construction of a graph with such components. """
			scc_list = list(nx.strongly_connected_component_subgraphs(SG))
			SCCG = nx.condensation(SG,scc_list)
			SCCG_nodes = SCCG.nodes()
			
			""" Addition of the subgraph part associated to the strongly connected component to a node tag, named 
			int_graph. """
			for i in range(len(scc_list)):
				SCCG.node[i]['int_graph'] = scc_list[i]
				
				
			""" Iteration over pairs of nodes in the strongly connected components graph. """
			for C1 in SCCG_nodes:
				for C2 in SCCG_nodes:

					phi_rel_list = pplf.relation_reach.phi_rel_reach(element,C1,C2,SCCG)

					if phi_rel_list:
						""" Computation of the adjacent elements of the choosen element. """
						ae_list = absf.adjacent_elements(E,element)
							
						""" Iteration over pairs of adjacent elements. """
						for ae1 in ae_list:
							for ae2 in ae_list:
								
								str_ae1 = str(ae1.constraints())
								str_ae2 = str(ae2.constraints())
								
								if not pplf.ppl_functions.is_zero(ae1) and not pplf.ppl_functions.is_zero(ae2):
									
#									print '-------------------------------------------'
#									print '    ae1 =', ae1.constraints()
#									print '    ae2 =', ae2.constraints()
#									print '-------------------------------------------'

								
									#print 'Calling to initial relation'
									init_rel = pplf.relation_reach.rel_reach(ae1,element,C1,SCCG
									#print 'Calling to final relation'
									final_rel = pplf.relation_reach.rel_reach(element,ae2,C2,SCCG)
										
									if (not init_rel.is_empty()) and not (final_rel.is_empty()):

										""" Obtains the maximum scaling for an execution starting at element ae1,
										evolving through element between the connected components C1 and C2, and
										ending at element ae2. """
										scaling,relpoly,opt_set_time = opt.optimization.optimization_set(init_rel,phi_rel_list,final_rel)
										optimization_time = optimization_time + opt_set_time

										""" List of locations in the connected component C1 such that contain one of the adjacent elements. """
										ae1_loc_list = absf.CC_node_inclusion(SCCG,ae1,C1)
										""" List of locations in the connected component C2 such that contain the other adjacent element. """
										ae2_loc_list = absf.CC_node_inclusion(SCCG,ae2,C2)
										""" List of locations in ae1_loc_list such that the adjacent element ae1 can enter C1 through them. """
										enter_loc_list = absf.performance_locs(ae1_loc_list,ae1,element,C1,SCCG)
										""" List of locations in ae2_loc_list such that the adjacent element ae2 can exit C2 through them. """
										exit_loc_list = absf.performance_locs(ae2_loc_list,element,ae2,C2,SCCG)
										
										""" List of locations from we can reach some of the locations in enter location list going through
											the adjacent element ae1. """
										ae1_SG = SG_dict[str(ae1.constraints())]
										loc1_list = pplf.reach.pre_reach_loc_v2(enter_loc_list,ae1,ae1_SG)
														 
										""" List of locations we can reach from some of the locations in exit location list going through
											the adjacent element ae2. """
										ae2_SG = SG_dict[str(ae2.constraints())]
										loc2_list = pplf.reach.post_reach_loc_v2(exit_loc_list,ae2,ae2_SG)


										""" Iteration over pairs of locations on the last lists. """
										for q1 in loc1_list:
											for q2 in loc2_list:

												""" If there is no edge from (ae1,q1) to (ae2,q2) in the weighted abstract graph, it is tagged 
												with the scaling value and the weight is set to the scaling value. In case there exist such edge 
												it is tagged with the new scaling value and the weight is the maximum of the tagged values. """
												wg_node1 = (q1,str_ae1)
												wg_node2 = (q2,str_ae2)
													
												if WG.has_edge(wg_node1,wg_node2):
													
													weight = WG.edge[wg_node1][wg_node2]['weight']
													if scaling > weight:
														WG.edge[wg_node1][wg_node2]['weight'] = scaling
														WG.edge[wg_node1][wg_node2]['element'] = element
														WG.edge[wg_node1][wg_node2]['relation'] = relpoly

												else:

													if scaling > -1:
														WG.add_edge(wg_node1,wg_node2,weight=scaling,element=element,relation=relpoly)
				

	return WG,subgraph_time,optimization_time



#----------------------------------------------------------------------------------------------#
def construct_weighted_graph(G,E):

	""" Construction of the abstract weighted graph, given an input automaton and a set of
	elements determining a partition of the state space. """

#   NEED TO DECIDE IF THE WEIGTHED GRAPH IS A DIRECTED GRAPH OR AL MULTI DIRECTED GRAPH. ??????????????????????????????????????????????????????????????????????????????????????????????????????????????????????????

	WG = nx.DiGraph()
	WG = set_nodes(WG,G,E)
	print 'AFTER SET NODES *****************************'
	print 'WG nodes(data=True)'
	for wgn in WG.nodes(data=True):
		print wgn
	print 'WG edges '
	for wge in WG.edges():
		print wge
		print 'weight=',WG.edge[wge[0]][wge[1]]['weight']
		print 'element =',WG.edge[wge[0]][wge[1]]['element'].constraints()
		print 'relation =',WG.edge[wge[0]][wge[1]]['relation'].constraints()
		print '\n'

	WG,subgraph_time,optimization_time = set_edges_and_weights(WG,G,E)

	print 'AFTER SET EDGES *****************************'
	print 'WG nodes(data=True)'
	for wgn in WG.nodes(data=True):
		print wgn
	print 'WG edges '
	for wge in WG.edges():
		print wge
		print 'weight=',WG.edge[wge[0]][wge[1]]['weight']
		print 'element =',WG.edge[wge[0]][wge[1]]['element'].constraints()
		print 'relation =',WG.edge[wge[0]][wge[1]]['relation'].constraints()
		print '\n'


	return WG,subgraph_time,optimization_time


