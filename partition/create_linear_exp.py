__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"


from fractions import gcd
from sage.libs.ppl import Linear_Expression


#----------------------------------------------------------------------------------------------#
def add_coefficients(dim,i,j,coeff1,coeff2):
	
	""" Create uniform predicates coefficients
		-------------------------------------------------------------------------------
		input:	pred
		i
		j
		coeff1
		coeff2
		output:			list of predicates. """
	
	pred = [0]*dim
	pred[i] = coeff1
	pred[j] = coeff2
	
	return pred



#----------------------------------------------------------------------------------------------#
def get_coefficients(dim,iteration):
	
	""" Determine uniform linear expressions coefficients
		-------------------------------------------------------------------------------
		input: 	dim 		state space dimension
		iteration	constructing linear expressions iteration
		output:	C		list of linear expressions coefficients. """
	
	C = []
	# We will get (2**iteration) number of predicates
	n_pred = int(2**(iteration-1))
	
	# loop for dim-1, which is the number of directions for constructing predicates
	for i in xrange(0,dim):
		pred = [0]*dim
		pred[i] = 1
		C.append(pred[:])
		for j in xrange(i+1,dim):
			
			for k in xrange(1,n_pred+1):
				
				div = gcd(k,n_pred)
				a = k/div
				b = n_pred/div
				
				C.append(add_coefficients(dim,i,j,a,-b))
				if (a != b):	# this is just important in iteration 1
					C.append(add_coefficients(dim,i,j,b,-a))
				C.append(add_coefficients(dim,i,j,a,b))
				if (a!=b):
					C.append(add_coefficients(dim,i,j,b,a))
	
	return C


#----------------------------------------------------------------------------------------------#
def coeff_to_linear_exp(coefficients,inv_var_dict):
	
	""" Create a linear expression from coefficients
		-------------------------------------------------------------------------------
		input: 	coefficients	linear expression coefficients
		inv_var_dict	dictionary with state space variables
		output:	le		linear expression. """
	
	
	first = False
	coord = 0
	linear_exp = ''
	
	for coeff in coefficients:
		
		if coeff != 0:
			if coeff > 0:
				if first:
					coeff_str = '+' + str(coeff) + '*'
				else:
					if coeff == 1:
						coeff_str = ''
					if coeff != 1:
						coeff_str = str(coeff) + '*'
			else:
				if coeff == -1:
					coeff_str = '-'
				else:
					coeff_str = str(coeff) + '*'
			
			first = True
			
			linear_exp =  linear_exp + coeff_str + inv_var_dict[coord]
		
		coord += 1

	return linear_exp


#----------------------------------------------------------------------------------------------#
def coeff_to_linear_exps(C,inv_var_dict):
	
	""" Create a list of linear expressions from their coefficients
		-------------------------------------------------------------------------------
		input: 	C 		matrix of linear expressions coefficients
		inv_var_dict	dictionary with state space variables
		output:	ULE		list of linear expressions. """
	
	ULE = []
	for c in C:
		le = coeff_to_linear_exp(c,inv_var_dict)
		ULE.append(le)
	
	return ULE


#----------------------------------------------------------------------------------------------#
def linear_expressions(iteration,inv_var_dict):
	
	""" Create uniform linear expressions
		-------------------------------------------------------------------------------
		input: 	iteration			constructing linear expressions iteration
				inv_var_dict		dictionary with state space variables
		output:	ULE					list of linear expressions. """
	
	# state space dimension
	dim = len(inv_var_dict)
	
	C = get_coefficients(dim,iteration)
	ULE = coeff_to_linear_exps(C,inv_var_dict)
	
	return ULE


#----------------------------------------------------------------------------------------------#
def coeff_to_linear_exps_v2(C,dim):
	
	""" Create a list of linear expressions from their coefficients
		-------------------------------------------------------------------------------
		input: 	C 		matrix of linear expressions coefficients
		inv_var_dict	dictionary with state space variables
		output:	ULE		list of linear expressions. """
	
	ULE = []
	for c in C:
		le = Linear_Expression(c,0)
		ULE.append(le)
	
	return ULE

#----------------------------------------------------------------------------------------------#
def add_unif_linear_expressions(iteration,inv_var_dict,LE):
	
	""" Create uniform linear expressions
		-------------------------------------------------------------------------------
		input: 	iteration			constructing linear expressions iteration
				inv_var_dict		dictionary with state space variables
		output:	ULE					list of linear expressions. """
	
	# state space dimension
	dim = len(inv_var_dict)
	
	C = get_coefficients(dim,iteration)
	ULE = coeff_to_linear_exps_v2(C,dim)
	
	#LE = LE + ULE
	
	coeffs_LE = []
	for le in LE:
		coeffs_LE.append(le.coefficients())
	
	coeffs_ULE = []
	for le in ULE:
		coeffs_ULE.append(le.coefficients())

	for cle in coeffs_ULE:
		if cle not in coeffs_LE:
			coeffs_LE.append(cle)

	new_LE = []
	for cle in coeffs_LE:
		le = Linear_Expression(cle,0)
		new_LE.append(le)

	
	return new_LE



