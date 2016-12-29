import numpy as np


#----------------------------------------------------------------------------------------------#
def str2file(string,namefile):

	""" Write a string into a file. """

	f = open(namefile,'w')
	f.write(string)
	f.close()


#----------------------------------------------------------------------------------------------#
def list2file(l,namefile):
	
	""" Write a list into a file. """
	
	f = open(namefile,'w')
	
	for i in l:
		f.write(str(i)+'\n')
		
	f.close()


#----------------------------------------------------------------------------------------------#
def load(namefile):

	""" Load data from file to a numpy array. """

	A = []
	with open(namefile) as f:
		for line in f:
			A.append(line.strip())
			
	return A


#----------------------------------------------------------------------------------------------#
def split_expression(expression, relation):

	""" Split an expression in expression before symbol and expression after it. 
	 a*x+b*y<=c --> expr_before: a*x+b*y, expr_after: c 
	 dx=a*x+b*y --> expr_before: dx, expr_after: a*x+b*y. """

	sp_exp = expression.split(relation)

	expr_before = sp_exp[0]
	expr_after = sp_exp[1]

	return expr_before,expr_after


#----------------------------------------------------------------------------------------------#
def transform_P(P):

	""" Transform the matrix P into a matrix H 
	 P=['x-y=0','x-y>=0','x+y=0','y=2'] --> PLE=['x-y','x+y']. """

	# Delete the non-homogeneous expressions and store only the coefficients of the expression
	# The order in the if clause is important, the equality (=) has to be in the last instantiation
	PLE = []
	for p in P:
		if p != 'True':
			if '>=' in p:
				expr,cte = split_expression(p,'>=')
			elif '<=' in p:
				expr,cte = split_expression(p,'<=')
			elif '>' in p:
				expr,cte = split_expression(p,'>')
			elif '<' in p:
				expr,cte = split_expression(p,'<')
			else:
				expr,cte = split_expression(p,'=')
		
			if (cte == '0'):
				PLE.append(expr)


	PLE = list(set(PLE))
	return PLE



#----------------------------------------------------------------------------------------------#
def initialize_time():
	return 0., 0., 0., 0., 0., 0., 0., 0.


