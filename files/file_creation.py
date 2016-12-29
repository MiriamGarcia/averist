__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"

import subprocess as sp
import functions as fun

	
	
#----------------------------------------------------------------------------------------------#
def folders(namefolder):
	
	sp.call(['mkdir',namefolder + '/output'])
	return



#----------------------------------------------------------------------------------------------#
def itfolders(LE,namefolder):
	
	""" Creation of the folders to store information about the process results. """

	n_le = len(LE)
	namefolder_le = namefolder+'/'+str(n_le)+'linearexp'
	sp.call(['mkdir',namefolder_le])
	sp.call(['mkdir',namefolder_le+'/output'])

	return namefolder_le



#----------------------------------------------------------------------------------------------#
def iterationfolders(LE,iteration,namefolder):
	
	""" Creation of the folders to store information about the process results. """

	n_le = len(LE)
	namefolder_le = namefolder+'/'+str(n_le)+'linearexp_'+str(iteration)
	sp.call(['mkdir',namefolder_le])
	sp.call(['mkdir',namefolder_le+'/output'])
	
	return namefolder_le



#----------------------------------------------------------------------------------------------#
def smtfolder(namefolder):

	sp.call(['mkdir',namefolder + '/smt'])
	return



#----------------------------------------------------------------------------------------------#
def store_graph(G,namefolder,HA_type):

	""" Store graph information into a file. """

	G_line = 'Nodes\n' + str(G.nodes(data=True)) + '\n'
	G_line += 'Edges\n' + str(G.edges(data=True)) + '\n'

	G_line = 'Nodes\n'+str(G.nodes(data=True))+'\n'
	G_line += 'Edges\n'+str(G.edges(data=True))+'\n'
	G_line += '******************************************************************************************************\n'
	G_line += ' Nodes for Input Hybrid Automaton\n'
	G_line += '---------------------------------------------------------------------\n'
	G_line += 'Number of nodes ='+str( G.number_of_nodes())+'\n'
	G_line += '---------------------------------------------------------------------\n'
	for n in G.nodes():
		G_line += str(n)+'\n'
		G_line += '		inv = '+ str(G.node[n]['inv'].constraints())+'\n'
		if HA_type == 'polyhedral':
			G_line += '		dyn = '+ str(G.node[n]['dyn'].constraints())+'\n'
		elif HA_type == 'linear':
			G_line += '		dyn = '+ str(G.node[n]['dyn'])+'\n'
	G_line += '---------------------------------------------------------------------\n'
	G_line += ' Edges for Input Hybrid Automaton\n'
	G_line += '---------------------------------------------------------------------\n'
	G_line += 'Number of edges = '+str(G.number_of_edges())+'\n'
	G_line += '---------------------------------------------------------------------\n'
	for e in G.edges():
		G_line += str(e)+'\n'
		G_line += '		guard = '+str(G[e[0]][e[1]]['guard'].constraints())+'\n'

#	print 'G_line = ', G_line

	fun.str2file(G_line,namefolder+'/output/graph_automaton.dat')

	return



#----------------------------------------------------------------------------------------------#
def store_le(le_list,namefolder_le):
	
	""" Store the linear expressions in a plain text. """
	
	f = open(namefolder_le+'/linear_expressions.dat','w')
	for le in le_list:
		f.write(str(le) + '\n')
	f.close()
	
	return




#----------------------------------------------------------------------------------------------#
def store_sep_le(le_list,namefolder_le):
	
	""" Store the linear expressions in a plain text. """
	
	f = open(namefolder_le+'/separating_linear_expressions.dat','w')
	for le in le_list:
		f.write(str(le) + '\n')
	f.close()
	
	return




#----------------------------------------------------------------------------------------------#
def store_pgraph(PG,namefolder_le):

	""" Store information about a polyhedral hybrid automaton into a file. """

	pa = open(namefolder_le+'/output/pol_automaton.dat','w')

	pa.write('PG.nodes(data=True)'+str(PG.nodes(data=True))+'\n')
	pa.write('PG.edges(data=True)'+str(PG.edges(data=True))+'\n')
	pa.write('******************************************************************************************************\n')
	pa.write( ' Nodes for Polyhedral Hybrid Automaton\n')
	pa.write( '---------------------------------------------------------------------\n')
	pa.write( 'Number of nodes ='+str( PG.number_of_nodes())+'\n')
	pa.write( '---------------------------------------------------------------------\n')
	for n in PG.nodes():
		pa.write(str(n)+'\n')
		pa.write( '		inv = '+ str(PG.node[n]['inv'].constraints())+'\n')
		pa.write( '		dyn = '+ str(PG.node[n]['dyn'].constraints())+'\n')
	pa.write( '---------------------------------------------------------------------\n')
	pa.write( ' Edges for Polyhedral Hybrid Automaton\n')
	pa.write( '---------------------------------------------------------------------\n')
	pa.write( 'Number of edges = '+str(PG.number_of_edges())+'\n')
	pa.write( '---------------------------------------------------------------------\n')
	for e in PG.edges():
		pa.write(str(e)+'\n')
		pa.write( '		guard = '+str(PG[e[0]][e[1]]['guard'].constraints())+'\n')

	pa.close()

	return



#----------------------------------------------------------------------------------------------#
def store_node_pg(node_pg_rel_list,node_rel_list,namefolder_output):

	""" Store the nodes of the polyhedral hybrid system, formed by a location of the linear one 
		and an element of the partition. """

	npg = open(namefolder_output+'/node_pg.dat','w')
	
	for i in range(len(node_pg_rel_list)):
		a = node_rel_list[i][1]
		b = node_pg_rel_list[i][1]
		for j in range(len(a)):
			npg.write(str(b[j]) + ':= (' + str(a[j][0]) + ', ' + str(a[j][1].constraints()) + ')\n')
			print b[j],':= (',a[j][0],', ',a[j][1].constraints(),')'

	npg.close()

	return



#----------------------------------------------------------------------------------------------#
def store_elements(elem_list,namefolder_le):
	
	""" Store the elements in a plain text. """
	
	f = open(namefolder_le+'/elements.dat','w')
	for elem in elem_list:
		f.write(str(elem.constraints()) + '\n')
	f.close()
	
	return



#----------------------------------------------------------------------------------------------#
def store_node_sc(G,namefolder_le):

	npg = open(namefolder_le+'/output/node_pg.dat','w')
	scr = open(namefolder_le+'/output/scaling_resume.dat','w')
	npg.write(at.npg_line)
	scr.write(nf.scr_line)
	npg.close()
	scr.close()

	return


#----------------------------------------------------------------------------------------------#
def store_WG(WG,namefile):

	""" Store the abstract graph in a plain text. """

	f = open(namefile,'w')
	f.write('Nodes\n')
	for wgn in WG.nodes(data=True):
		f.write(str(wgn) + '\n')
	f.write('Edges\n')
	for wge in WG.edges():
		f.write(str(wge) + '\n')
		f.write('    weight = ' + str(WG[wge[0]][wge[1]]['weight']) + '\n')
		f.write('    element = ' + str(WG[wge[0]][wge[1]]['element'].constraints()) + '\n')
		f.write('    relation = ' + str(WG[wge[0]][wge[1]]['relation'].constraints()) + '\n')
	f.close()

	return



#----------------------------------------------------------------------------------------------#
def store_stable_answer(message,counterexample,namefolder_le):

	""" Store the stability answer and the abstract counterexample in case of existence. """

	f = open(namefolder_le + '/stable.dat','w')
	f.write(message + '\n')
	for node_ce in counterexample:
		f.write(str(node_ce) + '\n')
	f.close()

	return



#----------------------------------------------------------------------------------------------#
def store_time(element_creation_time,automaton_transf_time,abstraction_time,subgraph_time,optimization_time,verification_time,validation_time, refinement_time,total_time,namefolder_le):
	
	f = open(namefolder_le+'/output/time.dat','w')
	
	f.write('Element creation time ..........' + str(element_creation_time) + ' seconds\n')
	f.write('Automaton transformation time...' + str(automaton_transf_time) + ' seconds\n')
	f.write('Abstraction time ...............' + str(abstraction_time) + ' seconds\n')
	f.write('   subgraph time ...............' + str(subgraph_time) + ' seconds\n')
	f.write('   optimization time ...........' + str(optimization_time) + ' seconds\n')
	f.write('Verification time ..............' + str(verification_time) + ' seconds\n')
	f.write('Validation time ..............' + str(validation_time) + ' seconds\n')
	f.write('Refinement time ..............' + str(refinement_time) + ' seconds\n')
	f.write('---------------------------------------------------------------------------\n')
	f.write('Total time .....................' + str(total_time) + ' seconds\n')
	
	f.close()



#----------------------------------------------------------------------------------------------#
def store_total_time(element_creation_time,automaton_transf_time,abstraction_time,subgraph_time,optimization_time,verification_time,validation_time, refinement_time,total_time,namefolder):
	
	f = open(namefolder+'/output/time.dat','w')
	
	f.write('Total element creation time ..........' + str(element_creation_time) + ' seconds\n')
	f.write('Total automaton transformation time...' + str(automaton_transf_time) + ' seconds\n')
	f.write('Total abstraction time ...............' + str(abstraction_time) + ' seconds\n')
	f.write('   Total subgraph time ...............' + str(subgraph_time) + ' seconds\n')
	f.write('   Total optimization time ...........' + str(optimization_time) + ' seconds\n')
	f.write('Total verification time ..............' + str(verification_time) + ' seconds\n')
	f.write('Total validation time ..............' + str(validation_time) + ' seconds\n')
	f.write('Total refinement time ..............' + str(refinement_time) + ' seconds\n')
	f.write('---------------------------------------------------------------------------\n')
	f.write('Total time .....................' + str(total_time) + ' seconds\n')
	
	f.close()



