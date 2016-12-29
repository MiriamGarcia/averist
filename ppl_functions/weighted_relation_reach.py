from sage.libs.ppl import *
from fractions import Fraction


#----------------------------------------------------------------------------------------------#
def interval_weight_poly_rel_restriction(poly_rel,weight,epsilon):

	dim = poly_rel.space_dimension()
	vardim = dim/2

	weighted_poly_rel_list = []
	
	for i in range(vardim):
		for j in range(vardim,dim):
			
			aux_ind_i = range(vardim)
			del aux_ind_i[i]
			aux_ind_j = range(vardim,dim)
			del aux_ind_j[j-vardim]

			weighted_poly_rel = NNC_Polyhedron(poly_rel)
			print 'weight =',weight
			print 'weight fraction =',Fraction(weight)
			
			weight_fraction = Fraction(weight)
			weightminus = weight_fraction - epsilon
			weightplus = weight_fraction + epsilon
			
			print 'weightminus =',weightminus
			print 'weightplus =',weightplus
			if weightminus.denominator == weightplus.denominator:
				resize = weightminus.denominator
			else:
				resize = weightminus.denominator * weightplus.denominator
				
			weighted_poly_rel.add_constraint(resize*Variable(j) - int(resize * weightminus) * Variable(i) >= 0)
			weighted_poly_rel.add_constraint(resize*Variable(j) - int(resize * weightplus) * Variable(i) <= 0)
			
			for k in aux_ind_i:
				weighted_poly_rel.add_constraint(Variable(i) >= Variable(k))
			for l in aux_ind_j:
				weighted_poly_rel.add_constraint(Variable(j) >= Variable(l))
			
			weighted_poly_rel_list.append(weighted_poly_rel)

#	Now, since the union of the polyrel is not a polyhedron, we can construct the convex hull
#	but it could exists a better solution

	weight_poly_rel = NNC_Polyhedron(dim,'empty')
	for wpr in weighted_poly_rel_list:
		print 'iwpr =',wpr.constraints()
		weight_poly_rel.poly_hull_assign(wpr)

	print 'weight_poly_rel =',weight_poly_rel.constraints()
	return weight_poly_rel



#----------------------------------------------------------------------------------------------#
def weight_poly_rel_restriction(poly_rel,weight,epsilon):
	
	dim = poly_rel.space_dimension()
	vardim = dim/2
	
	weighted_poly_rel_list = []
	
	for i in range(vardim):
		for j in range(vardim,dim):
			
			aux_ind_i = range(vardim)
			del aux_ind_i[i]
			aux_ind_j = range(vardim,dim)
			del aux_ind_j[j-vardim]
			
			weighted_poly_rel = NNC_Polyhedron(poly_rel)
			print 'weight =',weight
			str_weight = str(weight)
			nd = str_weight[::-1].find('.')
			print 'number of decimals for weight =',nd
			resize = 10**nd
			print 'resize * weight =',int(resize*weight)
			print '------------------------------------------'
			weighted_poly_rel.add_constraint(resize*Variable(j) - int(resize*weight) * Variable(i) == 0)
			
			for k in aux_ind_i:
				weighted_poly_rel.add_constraint(Variable(i) >= Variable(k))
			for l in aux_ind_j:
				weighted_poly_rel.add_constraint(Variable(j) >= Variable(l))
			
			weighted_poly_rel_list.append(weighted_poly_rel)

#	Now, since the union of the polyrel is not a polyhedron, we can construct the convex hull
#	but it may exist a better solution

	weight_poly_rel = NNC_Polyhedron(dim,'empty')
	for wpr in weighted_poly_rel_list:
		print 'wpr =',wpr.constraints()
		weight_poly_rel.poly_hull_assign(wpr)

	print 'weight_poly_rel =',weight_poly_rel.constraints()
	return weight_poly_rel




#----------------------------------------------------------------------------------------------#
def weighted_composition_rel(poly_rel1,poly_rel2,weight):
	
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

		""" Restriction to the pair of points with scaling equal to the weight value. """
		weighted_poly = weight_poly_rel_restriction(polyrel1,weight)


	""" A polyhedron with the initial dimension is constructed from polyrel1. The second
	multivariable disappears."""
	if weighted_poly.is_empty():
		comppoly = NNC_Polyhedron(dim,'empty')
	else:
		comppoly = pplf.reduce_multivar(weighted_poly)
	
	return comppoly



#----------------------------------------------------------------------------------------------#
def weighted_composition_ref(initrelpoly,relpolylist,weight_list):
	
	""" Given a list of relation polyhedra we get the final relation polyhedron by composition.
	In case of getting emptiness, the last non empty composed relation polyhedron is returned.
	
	input:	relpolylist	relation polyhedron list				list of ppl.NNC_Polyhedron

	output:	comppoly	composed relation polyhedron				ppl.NNC_Polyhedron
		pre_comppoly	last non empty composed relation polyhedron		ppl.NNC_Polyhedron """
	
	lenlist = len(relpolylist)
	prerelpoly = initrelpoly
	nodeind = -1
	
	for i in range(lenlist):
		
		posrelpoly = relpolylist[i]
		weight = weight_list[i]
		comppoly = weighted_composition_rel(prerelpoly,posrelpoly,weight)
		
		if comppoly.is_empty():
			# node index before emptiness
			nodeind = i
			break
		else:
			prerelpoly = NNC_Polyhedron(comppoly)

	return nodeind,comppoly,prerelpoly

