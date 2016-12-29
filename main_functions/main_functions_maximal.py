import numpy as np
import files as f
import partition as par
import sys
import hybridization as hyb
import ppl_functions as pplf
from sage.libs.ppl import *
import abstraction as abs
import networkx as nx
import refinement as ref

#----------------------------------------------------------------------------------------------#
def initial_LE(P,given_linear_exp,extract_linear_exp,unif_linear_exp,inv_var_dict,namefolder):
	
	""" Construction of the linear expression matrix for the first CEGAR iteration. """
	
	strLE = []

	if given_linear_exp == 'le':
		strLE = f.functions.load(namefolder+'/input/linearexp.dat')

	if extract_linear_exp == 'exle':
		PLE = f.functions.transform_P(P)
		strLE = strLE + PLE
		
	if unif_linear_exp > -1:
		ULE = par.create_linear_exp.linear_expressions(unif_linear_exp,inv_var_dict)
		strLE = strLE + ULE

	if not strLE:
		sys.exit('There is no any linear expression to partition the state-space')

	strLE = list(set(strLE))

	# Now LE is transformed into a list of ppl.linear expressions
	LE = pplf.ppl_functions.get_linearexps(strLE,inv_var_dict)

	return LE



#----------------------------------------------------------------------------------------------#
def transformation_unif(G,LE,var_dict,inv_var_dict,namefolder_le):
	
	""" Automaton transformation: from linear hybrid automaton to polyhedral hybrid automaton,
	following the computational explanation in 'An algorithmic approach to stability verification
	of polyhedral switched systems', ACC 2014 . """
	
	PG,E,creation_time = hyb.automaton_transformation.LHA_to_PHA_maximal_unif(G,LE,var_dict,inv_var_dict,namefolder_le)
	
	return PG,E,creation_time



#----------------------------------------------------------------------------------------------#
def transformation_norm(G,LE,var_dict,inv_var_dict,namefolder_le,diameter_bound):

	""" Automaton transformation: from linear hybrid automaton to polyhedral hybrid automaton, 
	following the computational explanation in 'An algorithmic approach to stability verification 
	of polyhedral switched systems', ACC 2014 . """

	PG,E,new_LE,max_diameter,creation_time = hyb.automaton_transformation.LHA_to_PHA_maximal_norm(G,LE,var_dict,inv_var_dict,namefolder_le,diameter_bound)

	return PG,E,new_LE,max_diameter,creation_time



#----------------------------------------------------------------------------------------------#
def transformation_norm_v2(G,LE,var_dict,inv_var_dict,namefolder_le,diameter_percentage):
	
	""" Automaton transformation: from linear hybrid automaton to polyhedral hybrid automaton,
	following the computational explanation in 'An algorithmic approach to stability verification
	of polyhedral switched systems', ACC 2014 . """
	
	PG,E,new_LE,max_diameter,creation_time = hyb.automaton_transformation_v2.LHA_to_PHA_maximal_norm_v2(G,LE,var_dict,inv_var_dict,namefolder_le,diameter_percentage)
	
	return PG,E,new_LE,max_diameter,creation_time



#----------------------------------------------------------------------------------------------#
def check_explosion(G):
	
	""" Checks for the case of explosion, by asking if the invariants intersect with its dynamics 
	polyhedron. """
	
	explosion = False

	for n in G.nodes():
		invpoly = NNC_Polyhedron(G.node[n]['inv'])
		dynpoly = G.node[n]['dyn']
		# Check if dynpoly is just the point zero. In case of being zero there is no movement
		# and therefore explosion is not possible.
		if not pplf.ppl_functions.is_zero(dynpoly):
			# Compute the closed dynamics polyhedron (to avoid a not bounded problem in optimization)
			cdynpoly = pplf.ppl_functions.copy_closed_polyhedron(dynpoly)
			invpoly.intersection_assign(cdynpoly)
			if not invpoly.is_empty() and not pplf.ppl_functions.is_zero(invpoly):
				explosion = True
				break

	return explosion



#----------------------------------------------------------------------------------------------#
def construct_abstract_graph(PG,LE,E,var_dict,inv_var_dict,namefolder_le,HA_type,G):

	""" Construction of the weighted abstract graph. """


	subgraph_time = 0
	reach_relation_smt_time = 0
	reach_relation_opt_time = 0

	global scr_line
	scr_line = ''

	
	output = namefolder_le + '/output'
	explosion_in_graph = False

	# Create the output graph
	# NEW (02/03/2014)
	#WG = nx.DiGraph()
	WG = nx.MultiDiGraph()
	# (02/03/2014)
	wg_n = 0			# number of nodes in the weighted graph

	for element in E:

		#dim_element = element_dim(dim,element)
		dim_element = element.space_dimension()

		# We check only for elements different
		if (dim_element != 0):# and (element == [0, 1, 0, 3, 3, 1, 0, 3, 3, 2, 3, 3, 3, 3, 3, 3]):

			SG,sg_time = abs.subgraph(PG,element,inv_var_dict)

			subgraph_time = subgraph_time + sg_time

#			print '**************************************************************************************************'
#			print 'element =',element
#			print '**************************************************************************************************'
#
#			scr_line = scr_line+'**************************************************************************************************\n'
#			scr_line = scr_line + 'element =' + str(element) + '\n'
#			scr_line = scr_line+'**************************************************************************************************\n'


			if len(SG.nodes()) != 0:

				ae_list = abs.adjacent_elements(E,element)

				for ae1 in ae_list:

					for ae2 in ae_list:

						dim_ae1 = ae1.space_dimension()
						dim_ae2 = ae2.space_dimension()
						
						if (dim_ae1 < dim) and (dim_ae2 < dim):
							#list of locations containing ae1
							loc1 = node_inclusion(ae1,SG,inv_var_dict)
							#list of locations containing ae2
							loc2 = node_inclusion(ae2,SG,inv_var_dict)
			
							for q1 in loc1:
								for q2 in loc2:

									# Condition 1: we allow only discrete jumps in the case there is edge in the input
									# automaton between the locations
									c1 = (q1 != q2) and (ae1 == ae2)
									# Condition 2:
									c2 = (q1 == q2) and (ae1 != ae2)
									# Condition 3:
									c3 = (q1 != q2) and (ae1 != ae2)
									# Condition 4:
									c4 = (q1 == q2) and (ae1 == ae2)

									if c1:
										# Get the location in the initial automaton for q1 and q2
										G_q1 = hyb.automaton_transformation.npg_dict[q1][0]
										G_q2 = hyb.automaton_transformation.npg_dict[q2][0]
										# Check if there exist and edge from G_q1 to G_q2
										if (G.has_edge(G_q1,G_q2)):# or (G_q1 == G_q2)
											#print 'There exists edge from ',G_q1, ' to ',G_q2
											c5 = True
										else:
											#print "There doesn't exist edge from ",G_q1, ' to ',G_q2
											c5 = False

									if (c1 and c5) or c2 or c3 or c4:

										scaling,reach_rel_time,opt_time,max_cpath,locsg1,locsg2 = abs.reach_rel(LE,G,SG,element,ae1,q1,ae2,q2,var_dict,HA_type)
										if (scaling > 1.0) and c4:
											print 'SOME FLOW CRUISING AN ELEMENT'
											sys.exit()

										reach_relation_smt_time = reach_relation_smt_time + reach_rel_time
										reach_relation_opt_time = reach_relation_opt_time + opt_time

                                        #if sat:
										if (scaling != -1):
											WG,wg_n,explosion = add_information(WG,wg_n,ae1,q1,ae2,q2,scaling,element,max_cpath,locsg1,locsg2)
											if (explosion == True): explosion_in_graph = True

	# NEW (07/04/2014)
	# Delete the self edges under some conditions
	#WG = delete_selfloops(WG)
	# BORRAR later
	WG = delete_every_selfloop(WG)
	# (07/04/2014)
	return WG,explosion_in_graph,subgraph_time,reach_relation_smt_time,reach_relation_opt_time



#----------------------------------------------------------------------------------------------#
def refinement(WG,counterexample,refinement_type):
	
	if refinement_type == 1:
		separation_linearexp_list = ref.refinement.refinement_type_1(WG,counterexample)
	else:								# In this case refinement type is 2
		#separation_linearexp_list = ref.refinement.refinement_type_2(WG,counterexample)
		separation_linearexp_list = ref.refinement.refinement_type_3(WG,counterexample)
	
	return separation_linearexp_list



