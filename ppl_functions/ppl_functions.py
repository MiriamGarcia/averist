from sage.all_cmdline import *
from sage.libs.ppl import *



#----------------------------------------------------------------------------------------------#
def get_linearexps(strLE,inv_var_dict):

	""" Generates a list of PPL linear expressions from a list of string linear expressions. """

#	Define variables
	for i in inv_var_dict:
		instr = str(inv_var_dict[i]) + ' = Variable(' + str(i) + ')'
		exec(instr)

#	Create each linear_expression
#	general linear expression (to set the space dimension)
	gen_le = ''
	for i in inv_var_dict:
			gen_le = gen_le + '0*' + str(inv_var_dict[i]) + '+'
	gen_le = gen_le[:-1]


	LE=[]
	for sle in strLE:
		
		le = eval(gen_le + '+' + sle)
		LE.append(le)

	return LE



#----------------------------------------------------------------------------------------------#
def get_linearexp(str_exp,inv_var_dict):

	""" Generates a PPL linear expression from a string linear expression. """
	
	#	general linear expression (to set the space dimension)
	gen_le = ''
	for i in inv_var_dict:
		gen_le = gen_le + '0*' + str(inv_var_dict[i]) + '+'
	gen_le = gen_le[:-1]

	le = eval(gen_le + '+' + str_exp)

	return le



#----------------------------------------------------------------------------------------------#
def get_polyhedron(str_exp,inv_var_dict):
	
	""" Generates a polyhedron from a string with the linear constraints determining.
	input:	str_exp			string      	'x>=0ANDx+y<=0'
		inv_var_dict		dict		{0: 'x', 1: 'y'}
	output: poly        		ppl.NNC_Polyhedron. """

	# state space dimension
	dim = len(inv_var_dict)
	# Define variables
	instr = '' 
	for i in inv_var_dict:
		instr += str(inv_var_dict[i]) + ' = Variable(' + str(i) + ')\n'

	exec(instr)
			
	poly = NNC_Polyhedron(dim,'universe')
	if str_exp != 'True':

		expr = str_exp.split('AND')		# Assumption: there are no OR expressions
		for e in expr:
			poly.add_constraint(eval(e))

	return poly



#----------------------------------------------------------------------------------------------#
def intersection(poly1,poly2):
	
	""" Creates a new polyhedron by intersecting two polyhedra. """
	
	cs1 = poly1.constraints()
	cs2 = poly2.constraints()
	
	for c in cs2:
        	cs1.insert(c)
		
	poly = NNC_Polyhedron(cs1)
	
	return poly



#----------------------------------------------------------------------------------------------#
def plane_element(element):

	""" Computation of the maximal polyhedron with the same dimension than element. It follows 
	the Plane(p) definition in 'An algorithmic approach to stability verification of polyhedral 
	switched systems', ACC 2014. """

	dim = element.space_dimension()
	planepoly = NNC_Polyhedron(dim,'universe')

	cs = element.constraints()
	for c in cs:
		if c.is_equality():
			planepoly.add_constraint(c)

	return planepoly



#----------------------------------------------------------------------------------------------#
def no_repetitions(list):

	""" Delete the repeated rays into a list. """

	coeff_list = []
	nr_list = []
	for l in list:
		coeff = l.coefficients()
		if coeff not in coeff_list:
			nr_list.append(l)
			coeff_list.append(coeff)

	return nr_list



#----------------------------------------------------------------------------------------------#
def delete_empty_poly(list):
	
	""" Delete the empty polyhedra into a list. """
	
	new_list = []
	for poly in list:
		if not poly.is_empty():
			new_list.append(poly)
	
	return new_list



#----------------------------------------------------------------------------------------------#
def poly2rays(poly):
	
	""" Given an initial polyhedron, it determines the rays associated to it. """
	
	dim = poly.space_dimension()
	gen_poly = poly.generators()
	
	ray_list = []

	for g in gen_poly:
		
		coeff = g.coefficients()
		# Check that the generator is not the zero point
		if not all(c==0 for c in coeff):
			le = ''
			for i in range(dim):
				le += str(coeff[i]) + '*Variable(' +str(i) + ')+'
			le = le[:-1]
			
			ray_instr = 'ray_list.append(Generator.ray(' + le + '))'
			exec(ray_instr)
	
	# Delete repetitions from ray list
	nr_ray_list = no_repetitions(ray_list)
	
	return nr_ray_list



#----------------------------------------------------------------------------------------------#
def get_rays(str_exp,inv_var_dict):
	
	""" Given a string of linear expressions determining a polyhedron, it returns the set of rays
	associated to the vertices.
	input:	str_exp         'x==-1ANDy>=1ANDy<=2'       string
		inv_var_dict    {0:'x', 1:'y'}              dictionary
	output:	rays            [ray(-1,1),ray(-1,2)]       list of ppl.Generator.ray. """

	poly = get_polyhedron(str_exp,inv_var_dict)
	rays = poly2rays(poly,inv_var_dict)
	
	return rays



#----------------------------------------------------------------------------------------------#
def zeros_before_ray(ray):
	""" Duplicates the coefficients of the ray and assigns value zero to the first half.
	--------------------------------------------------------------------------------------
	input:  ray		ray(1,2)        ppl.Generator.ray
	output: new_ray		ray(0,0,1,2)	ppl.Generator.ray """
	
	dim = ray.space_dimension()
	ddim = 2*dim
	new_ray_coeff = []
	
	for i in range(dim):
		new_ray_coeff.append(0)
	coeff = ray.coefficients()
	for c in coeff:
		new_ray_coeff.append(c)
	
	new_coeff_tuple = tuple(new_ray_coeff)
	new_ray_str = 'new_ray = Generator.ray('
	for i in range(ddim):
        	new_ray_str += '+' + str(new_ray_coeff[i]) + '*Variable(' + str(i) +')'
	new_ray_str += ')'
	exec(new_ray_str)
	
	return new_ray



#----------------------------------------------------------------------------------------------#
def swap_list(l):

	""" Swaps the first half values in the list by the second half values. """

	halfdim = len(l)/2

	for i in range(halfdim):
		l[i],l[i+halfdim]=l[i+halfdim],l[i]

	return l



#----------------------------------------------------------------------------------------------#
def new_constraint(constraint,new_coeff_list):
	
	""" Given a constraint and a new list of coefficients, a new constraint, as a string,  is
	returned with the same inequality relation and inhomogeneous value.
	input:	constraint		ppl.Constraint		2*x+3*y-4*z>=2
		new_coeff_list		integer list		[1,5,2] or [7,1]
	output:	new_const_str		string			'1*Variable(0)+5*Variable(1)+2*Variable(2)>=2'
								or '7*Variable(0)+1*Variable(1)>=2'. """
	
	dim = len(new_coeff_list)
	
	constant = constraint.inhomogeneous_term()
	type = constraint.type()
	
	new_const_str = ''
	for i in range(dim):
		new_const_str += '+' + str(new_coeff_list[i]) + '*Variable(' + str(i) + ')'
	
	new_const_str += '+' + str(constant)
	if type == 'equality':
		new_const_str += '==0'
	elif type == 'nonstrict_inequality':
		new_const_str += '>=0'
	elif type == 'strict_inequality':
		new_const_str += '>0'

	return new_const_str




#----------------------------------------------------------------------------------------------#
def swap_variables(poly):

	""" Given a polyhedron, the half first variables are swapped by the half last ones. """

	dim = poly.space_dimension()

	swap_poly = NNC_Polyhedron(dim,'universe')

	for const in poly.constraints():

		coeff_list = list(const.coefficients())
		new_coeff_list = swap_list(coeff_list)
		new_const_str = new_constraint(const,new_coeff_list)
				
		swap_poly.add_constraint(eval(new_const_str))

	return swap_poly



#----------------------------------------------------------------------------------------------#
def swap_last_values(l):
	
	""" Given a list of coefficients for three multivariables, swaps the last values to the 
	first values. 
	input:	l		list		[1,2,3,4,5,6] 
	output:	l		list		[5,6,1,2,3,4]. """
	
	dim = len(l)
	vardim = dim/3
	dvardim = 2*vardim

	new_l = l[dvardim:] + l[:dvardim]

	return new_l



#----------------------------------------------------------------------------------------------#
def swap_last_variables(poly):
	
	""" Given a polyhedron, the half first variables are swapped by the half last ones. """
	
	dim = poly.space_dimension()
	
	swap_poly = NNC_Polyhedron(dim,'universe')
	
	for const in poly.constraints():
		
		coeff_list = list(const.coefficients())
		new_coeff_list = swap_last_values(coeff_list)
		new_const_str = new_constraint(const,new_coeff_list)

		swap_poly.add_constraint(eval(new_const_str))

	return swap_poly



#----------------------------------------------------------------------------------------------#
def projection(poly,coordlist):
	
	""" Obtains the projected polyhedron in a subspace of the total space.
		input:  poly            ppl.NNC_Polyhedron
		coordlist		integer list
		output: projpoly        ppl.NNC_Polyhedron. """
	
	dim = poly.space_dimension()
	
	if poly.is_empty():
		return NNC_Polyhedron(dim,'empty')
	
	elif poly.is_universe():
		return NNC_Polyhedron(dim,'universe')

	else:
		
		projpoly = NNC_Polyhedron(poly)
		polycoord = NNC_Polyhedron(dim,'universe')
		
		for i in range(dim):
			if i not in coordlist:
				projpoly.unconstrain(Variable(i))
				polycoord.add_constraint(Variable(i)==0)

		projpoly.intersection_assign(polycoord)

	return projpoly



#----------------------------------------------------------------------------------------------#
def reduce_multivar(poly):
	
	""" Given a polyhedron, the second of the three multivariables is deleted. 
	input:  poly            ppl.NNC_Polyhedron
	output: redpoly		ppl.NNC_Polyhedron. """

	dim = poly.space_dimension()
	vardim = dim/3
	dvardim = 2*vardim

	redpoly = NNC_Polyhedron(dvardim,'universe')
	for const in poly.constraints():
		coeffs = const.coefficients()
		new_coeffs = coeffs[0:vardim] + coeffs[dvardim:dim]
		if not all (c==0 for c in new_coeffs):
			new_coeff_list = list(new_coeffs)
			new_const_str = new_constraint(const,new_coeff_list)
			redpoly.add_constraint(eval(new_const_str))

	return redpoly


#----------------------------------------------------------------------------------------------#
def reduce_var(poly,varlist):
	
	""" Given a polyhedron, the variables in the list are mantained.
	input:  poly            ppl.NNC_Polyhedron
		varlist		list			[2,3]
	output: redpoly		ppl.NNC_Polyhedron. """
	
	dim = poly.space_dimension()
	newdim = dim - len(varlist)
	
	redpoly = NNC_Polyhedron(newdim,'universe')
	for const in poly.constraints():
		coeffs = const.coefficients()
		new_coeff_list = []
		for i in varlist:
			new_coeff_list.append(coeffs[i])
		if not all (c==0 for c in new_coeff_list):
			new_const_str = new_constraint(const,new_coeff_list)
			redpoly.add_constraint(eval(new_const_str))

	return redpoly



#----------------------------------------------------------------------------------------------#
def get_hybridization_poly(str_exp,inv_var_dict,element):
	
	""" Generates a polyhedron from a string with the linear constraints determining.
	input:	str_exp		string			'dx==10*yANDdy==-1*x' or 'dx+dy>0'
		inv_var_dict	dict			{0: 'x', 1: 'y'}
		element		ppl.NNC_Polyhedron
	output: rdpoly		ppl.NNC_Polyhedron. """
	
	# state space dimension
	dim = len(inv_var_dict)
	# Define variables (the first half have the names in the inv_var_dict, while the second
	# half set of variables have no name)
	instr = ''
	for i in inv_var_dict:
		instr += str(inv_var_dict[i]) + ' = Variable(' + str(i) + ')\n'
		# derivative variables
		instr += 'd' + str(inv_var_dict[i]) + ' = Variable(' + str(i+dim) + ')\n'
	
	exec(instr)
	
	poly = NNC_Polyhedron(2*dim,'universe')
	
	if str_exp != 'True':
		
		expr = str_exp.split('AND')		# Assumption: there are no OR expressions
		
		for e in expr:
			poly.add_constraint(eval(e))

	# Add element constraints
	for c in element.constraints():
		poly.add_constraint(c)
				
	# projection in the derivative variables
	coordlist = list(range(dim,2*dim))
	dpoly = projection(poly,coordlist)
	# reduce the polyhedron to the projected variables
	rdpoly = reduce_var(dpoly,coordlist)

	return rdpoly


#----------------------------------------------------------------------------------------------#
def is_zero(poly):

	""" Given a polyhedron, it is checked if it is just the zero point.
	input:	poly			NNC_Polyhedron
	output:	True/False		boolean. """

	if poly.is_discrete():
		gs = poly.minimized_generators()
		if len(gs) == 1:
			if all([c==0 for c in gs[0].coefficients()]):
				return True
			
	return False



#----------------------------------------------------------------------------------------------#
def copy_polyhedron(poly):

	""" Creates a polyhedron with the same constraints and space dimension. """

	dim = poly.space_dimension()
	poly_const = poly.constraints()
	
	cpoly = NNC_Polyhedron(dim,'universe')
	for c in poly_const:
		cpoly.add_constraint(c)
	
	return cpoly

#----------------------------------------------------------------------------------------------#
def copy_closed_polyhedron(poly):
	
	""" Creates a closed polyhedron with the same constraints and space dimension. """
	
	cpoly = copy_polyhedron(poly)
	cpoly.topological_closure_assign()

	return cpoly



#----------------------------------------------------------------------------------------------#
def create_zero_point(dim):

	zero_string = 'zero = point('
	for i in range(dim):
		zero_string += '0*Variable(' + str(i) + ')+'

	zero_string = zero_string[:-1] + ')'
	exec(zero_string)

	return zero



#----------------------------------------------------------------------------------------------#
def create_ray(coefflist):
	
	ray_string = 'r = ray('
	for i in range(len(coefflist)):
		ray_string += str(coefflist[i]) + '*Variable(' + str(i) + ')+'
	
	ray_string = ray_string[:-1] + ')'
	exec(ray_string)
	
	return r



#----------------------------------------------------------------------------------------------#
def create_linearexp(coefflist,term):
	
	""" Given a set of coefficients, a linear expression is created with such coefficients. """
	
	le_str = 'le = Linear_Expression('
	lenc = len(coefflist)
	for i in range(lenc):
		le_str += str(coefflist[i]) + '*Variable(' + str(i) + ') +'
	
	le_str += str(term) + ')'
	exec(le_str)
	
	return le






