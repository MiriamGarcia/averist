__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"

import networkx as nx
import numpy as np
import ppl_functions as pplf
#import matplotlib.pyplot as plt

def var(var_string):
	
	variables = var_string.split(',')
	dim = len(variables)
	var_dict = {}
	for i in range(dim):
		var_dict.update({variables[i]:i})

		
	# inverse of the dictionary
	inv_var_dict = dict([(v,k) for (k,v) in var_dict.items()])
	# inverse of the dictionary for the dynamics
	inv_var_dict_dyn = dict([(v,'d'+k) for (k,v) in var_dict.items()])
	
	return var_dict, inv_var_dict, inv_var_dict_dyn


def location(loc_string):
	
	locations = loc_string.split(',')
	G = nx.DiGraph()
	G.add_nodes_from(locations)
	
	return G


def inv(G,P,inv_string,node,inv_var_dict):

	inv_poly = pplf.ppl_functions.get_polyhedron(inv_string,inv_var_dict)
	G.add_node(node,inv=inv_poly)
	
	expressions = inv_string.split('AND')
	for e in expressions:
		#P = np.hstack((P,e))
		P.append(e)
		
	return G,P


def dyn(G,dyn_string,node,inv_var_dict_dyn,HA_type):
	
	if HA_type == 'polyhedral':
		
		dyn_poly = pplf.ppl_functions.get_polyhedron(dyn_string,inv_var_dict_dyn)
		G.add_node(node,dyn=dyn_poly)
	
	elif HA_type == 'linear':
		
		G.add_node(node,dyn=dyn_string)

	return G


def guards(G,P,guard_string,initial_node,inv_var_dict):
	
	str_list = guard_string.split('when')
	after_when = str_list[1]
	guard_list= after_when.partition('goto')
	
	grd = guard_list[0]
	final_node = guard_list[2]
	
	guard_poly = pplf.ppl_functions.get_polyhedron(grd,inv_var_dict)
	G.add_edge(initial_node,final_node,guard=guard_poly)
	
	expressions = grd.split('AND')
	for e in expressions:
		#P = np.hstack((P,e))
		P.append(e)
		
	return G,P


# Draw the graph
#def draw_graph(G):
#    
#	nx.draw(G)
#	plt.show()


##########################
# HERE STARTS THE PARSER #
##########################
def read_input(namefile,HA_type):
	try:
		with open(namefile, 'r') as inp:
            # store the data file as a string
			input = inp.read()        
		# Remove breaklines and tabulations
		input = input.replace('\n','')
		input = input.replace('\t','')
		
		# Remove all blank spaces
		input = ''.join(input.split())
		
		# split the information by ;
		input = input.split(';')
		# Delete the last element (it is equal to a blank space)
		# THERE WILL BE A PROBLEM IF SOMEONE DOES NOT WRITE THE LAST ;
		input = input[:-1]
        
        
		# Predicates matrix [first 0 row (it will be deleted later)] *
		#P = np.array(0)
		P = []
        
		for l in input:
			n = l.find(':')			# If it is not found it returns -1

			if n != -1:
				
				tag = l[0:n]
				tail = l[n+1:]
				
				if tail == '': raise NameError
				
				if tag == 'var':
					var_dict, inv_var_dict, inv_var_dict_dyn = var(tail)
				elif tag == 'location':
					G = location(tail)
				elif tag == 'loc':
					node = tail
				elif tag == 'inv':
					G,P = inv(G,P,tail,node,inv_var_dict)
				elif tag == 'dyn':
					G = dyn(G,tail,node,inv_var_dict_dyn,HA_type)
				elif tag == 'guards':
					G,P = guards(G,P,tail,node,inv_var_dict)
				else:
					raise SyntaxError('Not possible tag')
			else:
				if l[:4] == 'when':
					G,P = guards(G,P,l,node,inv_var_dict)
				else:
					raise SyntaxError('Syntax error')
        
        
		# Delete the first row of the predicate matrix
		#P = P[1:]
		# Delete the common predicates in P
		P = list(set(P))

		print
		return var_dict,inv_var_dict,P,G
	
	except IOError:
		print 'Cannot open input file'
	except NameError:
		print 'Lack of tag information'
	except SyntaxError:
		raise
	else:
		print 'Syntax error'
