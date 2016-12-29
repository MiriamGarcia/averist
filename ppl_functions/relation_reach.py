from sage.libs.ppl import *
import ppl_functions as pplf
import reach as r
import abstraction as a


#----------------------------------------------------------------------------------------------#
def relation_polyhedron(init_poly,final_poly,dyn_list):
	
	""" Given two polyhedra and a list of rays defining the dynamics of the system, it returns 
	the relational set of points. 
	input:	init_poly	ppl.NNC_Polyhedron
		final_poly	ppl.NNC_Polyhedron
		dyn_list	ppl.NNC_Polyhedron list
	output:	rel_poly	ppl.NNC_Polyhedron. """
	
	""" Gets the dimension of the original state space. """
	dim = init_poly.space_dimension()
	""" Gets the dimension of the new state space. """
	newdim = 2*dim
	
	""" First, the polyhedra are replicated in order to not modify the original ones. """
	initpoly = NNC_Polyhedron(init_poly)
	finalpoly = NNC_Polyhedron(final_poly)

	""" The initial polyhedron dimension is duplicated and the new variables are constrained 
	in the same way as the older ones. For instance, from {(x,y): x>2, y<0} it is obtained 
	{(x,y,z,t): x>2, y<0, z>2, t<0}. """
	initpoly.concatenate_assign(initpoly)
	
	""" Add the equality constraints between the original variables and the new ones.
	For instance, in the current example, x == z and y == t. """
	for i in range(dim):
		initpoly.add_constraint(Variable(i) == Variable(i+dim))
	
	""" Duplication of the dimension of the dynamic polyhedra, preserving the coefficients in the
	second half part and adding at the initial half part zero coefficients. And computation of the 
	new dynamics convex hull. """
	dynpoly = NNC_Polyhedron(newdim,'empty')
	for dyn in dyn_list:
		dyn_poly = NNC_Polyhedron(dyn)
		dyn_poly.add_space_dimensions_and_project(dim)
		dyn_poly = pplf.swap_variables(dyn_poly)
		dynpoly.poly_hull_assign(dyn_poly)

	""" Obtains the rays of the convex hull polyhedron, constructed with the dynamics. """
	dyn_ray_list = pplf.poly2rays(dynpoly)
	
	""" The final polyhedron duplicates its coefficients. The first half of coefficients are
	whatever value and the second half of coefficients are the final polyhedron coefficients. """
	finalpoly.add_space_dimensions_and_embed(dim)
	finalpoly = pplf.swap_variables(finalpoly)

	rel_poly = r.reach_ray(initpoly,finalpoly,dyn_ray_list)

	return rel_poly



#----------------------------------------------------------------------------------------------#
def composition_rel(poly_rel1,poly_rel2):
	
	""" Computation of the composition of two relation polyhedra, P_1(x,y) and P_2(y,z). """
	
	dim = poly_rel1.space_dimension()
	vardim = dim/2
	dvardim = 2*vardim
	
	polyrel1 = NNC_Polyhedron(poly_rel1)
	polyrel2 = NNC_Polyhedron(poly_rel2)
        
	if polyrel1.is_universe():
		return polyrel2
	elif polyrel2.is_universe():
		return polyrel1
	else:
		""" Add space dimensions: P_1(x,y) --> P_1(x,y,z) and P_2(y,z) --> P_2(y,z,x). """
		polyrel1.add_space_dimensions_and_embed(vardim)
		polyrel2.add_space_dimensions_and_embed(vardim)
		
		""" Swap last multivariable in the second polyhedron, P_2(y,z,x) --> P_2(x,y,z). """
		polyrel2 = pplf.swap_last_variables(polyrel2)

		polyrel1.intersection_assign(polyrel2)

		""" Projection on the first and third multivariable. """
		new_dim = polyrel1.space_dimension()
		coordlist = range(0,vardim) + range(dvardim,new_dim)
		polyrel1 = pplf.projection(polyrel1,coordlist)

	""" A polyhedron with the initial dimension is constructed from polyrel1. The second 
	multivariable disappears."""
	if polyrel1.is_empty():
		comppoly = NNC_Polyhedron(dim,'empty')
	else:
		comppoly = pplf.reduce_multivar(polyrel1)

	return comppoly



#----------------------------------------------------------------------------------------------#
def phi_rel_reach(element,C1,C2,SCCG):

	""" Computation of the reach relations between the strongly connected components C1 and C2 
	by considering all the single paths joining them in the graph SCCG. """
	
	n_nodes = len(SCCG.nodes())
	
	if (C1 == C2):
		cpath_list = [[C1]]

	else:
		cpath_generator = a.graph_functions.all_simple_paths(SCCG,C1,C2,n_nodes)	# It returns a list or nothing
		cpath_list = list(cpath_generator)


	phi_rel_list = []
	for cpath in cpath_list:		
		clen = len(cpath)
		# Initialize comp_rel as corresponding depending on the compostion_rel function
		dim = element.space_dimension()
		comp_rel = NNC_Polyhedron(dim,'universe')
		for i in range(clen):
			dyn_list = []
			for C in cpath:
				CG = SCCG.node[C]['int_graph']
				for n in CG.nodes():
					dyn = CG.node[n]['dyn']
					dyn_list.append(dyn)
			
			rel = relation_polyhedron(element,element,dyn_list)
			comp_rel = composition_rel(comp_rel,rel)

		phi_rel_list.append(comp_rel)

	return phi_rel_list



#----------------------------------------------------------------------------------------------#
def rel_reach(element1,element2,C,SCCG):
	
	""" Obtains the reachability relation polyhedron considering execution from one element to
	other element through the strongly connected component C. """
	
	CG = SCCG.node[C]['int_graph']
	dyn_list = []
	for n in CG.nodes():
		dyn_list.append(CG.node[n]['dyn'])

	relpoly = relation_polyhedron(element1,element2,dyn_list)

	return relpoly



#----------------------------------------------------------------------------------------------#
def composition(relpolylist):
	
	""" Given a list of relation polyhedra we get the final relation polyhedron by composition.
	In case of getting emptiness, the last non empty composed relation polyhedron is returned.
	input:	relpolylist	relation polyhedron list			list of ppl.NNC_Polyhedron
	
	output:	comppoly	composed relation polyhedron			ppl.NNC_Polyhedron
		pre_comppoly	last non empty composed relation polyhedron	ppl.NNC_Polyhedron """
	
	lenlist = len(relpolylist)
	prerelpoly = relpolylist[0]

	for i in range(1,lenlist):

		posrelpoly = relpolylist[i]
		comppoly = composition_rel(prerelpoly,posrelpoly)

		if comppoly.is_empty():
			break
		else:
			prerelpoly = NNC_Polyhedron(comppoly)

	return comppoly,prerelpoly


#----------------------------------------------------------------------------------------------#
def composition_ref(initrelpoly,relpolylist):
	
	""" Given a list of relation polyhedra we get the final relation polyhedron by composition.
	In case of getting emptiness, the last non empty composed relation polyhedron is returned.
	
	input:	relpolylist	relation polyhedron list			list of ppl.NNC_Polyhedron

	output:	comppoly	composed relation polyhedron			ppl.NNC_Polyhedron
		pre_comppoly	last non empty composed relation polyhedron	ppl.NNC_Polyhedron """
	
	lenlist = len(relpolylist)
	prerelpoly = initrelpoly
	nodeind = -1
	
	for i in range(lenlist):
		
		posrelpoly = relpolylist[i]
		comppoly = composition_rel(prerelpoly,posrelpoly)
		
		if comppoly.is_empty():
			# node index before emptiness
			nodeind = i
			break
		else:
			prerelpoly = NNC_Polyhedron(comppoly)
	
	return nodeind,comppoly,prerelpoly



