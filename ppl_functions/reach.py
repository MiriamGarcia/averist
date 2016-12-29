__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"

from sage.libs.ppl import *
import ppl_functions as pplf
import abstraction as a
import networkx as nx


#----------------------------------------------------------------------------------------------#
def reach_ray(initpoly,finalpoly,dyn_ray_list):
	
	""" Obtain a reach polyhedron given two polyhedra, the initial and the final one, and the 
	dynamics as a list of rays.
	-------------------------------------------------------------------------------------------
	input:	initpoly		Initial polyhedron		ppl.NNC_Polyhedron
		finalpoly		Final polyhedron		ppl.NNC_Polyhedron
		dyn_ray_list		Dynamics			ppl.Generator_System (list of rays)
		
	output:	reachpoly		Reach polyhedron		ppl.NNC_Polyhedron. """
	
	# Get the generators from the initial polyhedron
	initgen = initpoly.minimized_generators()
	
	# Minkowski's sum of the initial polyhedron and the dynamics
	gen = Generator_System()
	
	# rays of the dynamics
	for d in dyn_ray_list:
		gen.insert(d)
	
	# generators of the initial polyhedron
	for g in initgen:
		gen.insert(g)

	reachpoly = NNC_Polyhedron(gen)

	# Intersection of the Minkowski's sum and final polyhedron,
	# which gives the reach set.
	reachpoly.intersection_assign(finalpoly)

	return reachpoly



#----------------------------------------------------------------------------------------------#
def reach(initpoly,finalpoly,dyn_poly):
	
	""" Obtain a reach polyhedron given three polyhedra, the initial, the final one, and the dynamics.
        -------------------------------------------------------------------------------------------
        input:	initpoly		Initial polyhedron		ppl.NNC_Polyhedron
		finalpoly		Final polyhedron		ppl.NNC_Polyhedron
		dyn_ray_list		Dynamics			ppl.NNC_Polyhedron
		
        output:	reachpoly		Reach polyhedron		ppl.NNC_Polyhedron. """
	
	dyn_rays = pplf.poly2rays_v2(dyn_poly,inv_var_dict)
	reachpoly = reach_ray(initpoly,finalpoly,dyn_rays)
	
	return reachpoly



#----------------------------------------------------------------------------------------------#
def pre_reach_loc(enter_loc_list,loc_list,C,SCCG):

	""" Obtains the set of locations in loc_list such that there exists an edge, in the subgraph 
	contained in the strongly connected component C, from it to an enter location. """

	CG = SCCG.node[C]['int_graph']
	pre_loc_list = []
	for loc in loc_list:
		for eloc in enter_loc_list:
			if (CG.has_edge(loc,eloc) and loc not in pre_loc_list) or loc == eloc:
				pre_loc_list.append(loc)

	return pre_loc_list



#----------------------------------------------------------------------------------------------#
def post_reach_loc(exit_loc_list,loc_list,C,SCCG):
	
	""" Obtains the set of locations in loc_list such that there exists an edge, in the subgraph
	contained in the strongly connected component C, to it from an exit location. """
	
	CG = SCCG.node[C]['int_graph']
	post_loc_list = []
	for loc in loc_list:
		for eloc in exit_loc_list:
			if (CG.has_edge(eloc,loc) and loc not in post_loc_list) or eloc == loc:
				post_loc_list.append(loc)

	return post_loc_list



#----------------------------------------------------------------------------------------------#
def pre_reach_loc_v2(loc_list,element,SG):
	
	""" Obtains the set of original input locations in the subgraph SG such that there exists 
	an edge from the original location to one in the location list. """

	pre_loc_list = loc_list[:]
	for loc in loc_list:
		for nsg in SG.nodes():
			if nx.has_path(SG,nsg,loc):
				pre_loc_list.append(nsg)

	return pre_loc_list



#----------------------------------------------------------------------------------------------#
def post_reach_loc_v2(loc_list,element,SG):
	
	""" Obtains the set of original input locations in the subgraph SG such that there exists
	an edge from one location in the list to the original location. """

	post_loc_list = loc_list[:]
	for loc in loc_list:
		for nsg in SG.nodes():
			if nx.has_path(SG,loc,nsg):
				post_loc_list.append(nsg)
	
	return post_loc_list



