__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"

import sys



#----------------------------------------------------------------------------------- 15/06/2016 ---#
def user_questions():


	""" INPUT data for the Main program """
	""" Kind of hybrid automaton (linear or polyhedral). """
	HA_type = raw_input('What kind of hybrid automaton? (linear/polyhedral)\n')
	
	if HA_type != 'linear' and HA_type != 'polyhedral':
		sys.exit('Wrong answer')


	""" Name folder where the input folder containing the input automaton text file can be found. """
	namefolder = raw_input('\n* Please specify the path for the folder in which the experiment data (input.dat) is stored:\n')


	""" Set the way of choosing the linear expressions for partitioning the state space, manually by providing them into a file or automatically by
		determining the partition size. """
	am_answer = raw_input('\n* Do you want the linear expressions for creating the regions to be generated automatically (A) or do you want to add them manually (M)? Enter A/M:\n')

	if am_answer == 'A':
	
		given_linear_exp = 'nle'
		unif_linear_exp = int(raw_input('\n* The linear expressions will be generated in a uniform fashion. Please specify the granularity -- a natural number (higher number indicates finer partition):\n'))
	
		if unif_linear_exp < 0: sys.exit('Wrong value')


	elif am_answer == 'M':

		given_linear_exp = 'le'
		unif_linear_exp = -1
		print ('\nPlease specify the linear expressions for generating the regions in linearexp.dat\n')

	else:
		sys.exit('Wrong answer')

	""" Specify if the linear expressions involved in the input hybrid automaton definition are added to the set for partitioning the state space. """
	extract_answer = raw_input('\n* In addition, do you want to add the linear expressions appearing in the input hybrid automaton? Enter Y/N:\n')

	if extract_answer == 'Y':
		extract_linear_exp = 'exle'
	elif extract_answer == 'N':
		extract_linear_exp = 'nexle'
	else:
		sys.exit('Wrong answer')


	""" Maximum CEGAR iteration: bound in the CEGAR algorithm iterations to abort the loop in case of not
		obtaining any answer about stability or instability of the hybrid automaton. """
	max_CEGAR_iteration = int(raw_input('\n* Please specify the maximum number of CEGAR iterations:\n'))
	
	if max_CEGAR_iteration < 0:
		sys.exit('Wrong value')

	""" Specify if the linear expressions involved in cegar refinement are added by uniform creation or by separation selected predicates. """
	cegar_ref = raw_input('\n* Do you want to add the linear expressions for refinement creating uniformly or selecting by considering the counterexample? Enter unif/selected:\n')
	
	if cegar_ref != 'unif' and cegar_ref != 'selected':
		sys.exit('Wrong answer')
	
	if cegar_ref == 'unif':
		
		unif_linear_exp_cegar = int(raw_input('\n* The linear expressions will be generated in a uniform fashion. Please specify the granularity -- a natural number (higher number indicates finer partition):\n'))
		
		if unif_linear_exp < 0: sys.exit('Wrong value')

	elif cegar_ref == 'selected':
		unif_linear_exp_cegar = -1

	else:
		sys.exit('Wrong answer')
	



	return HA_type, namefolder, given_linear_exp, unif_linear_exp, extract_linear_exp, max_CEGAR_iteration, cegar_ref, unif_linear_exp_cegar




#----------------------------------------------------------------------------------- 15/06/2016 ---#
def internal_user_questions_poly():
	
	
	""" INPUT data for the Main program """
	""" Kind of hybrid automaton (linear or polyhedral). """
	HA_type = 'polyhedral'
	
	
	""" Name folder where the input folder containing the input automaton text file can be found. """
#	namefolder = '/Users/mgarcia/Software/2016_11_04_AVERIST_unified/EXPERIMENTS/Cegar/3D/exp_4quadrants_1'
	namefolder = '/Users/mgarcia/Software/2016_11_04_AVERIST_unified/EXPERIMENTS/OptimizationSample'
	
	
	""" Set the way of choosing the linear expressions for partitioning the state space, manually by providing them into a file or automatically by
		determining the partition size. """
	given_linear_exp = 'nle'
	unif_linear_exp = -1

#	given_linear_exp = 'le'
#	unif_linear_exp = -1

	""" Specify if the linear expressions involved in the input hybrid automaton definition are added to the set for partitioning the state space. """
	extract_linear_exp = 'exle'
	
	""" Maximum CEGAR iteration: bound in the CEGAR algorithm iterations to abort the loop in case of not
		obtaining any answer about stability or instability of the hybrid automaton. """
	max_CEGAR_iteration = 1
	
	
	""" Specify if the linear expressions involved in cegar refinement are added by uniform creation or by separation selected predicates. """
	cegar_ref = 'selected'
#	cegar_ref = 'unif'
	
	unif_linear_exp_cegar = 0
	
	
	return HA_type, namefolder, given_linear_exp, unif_linear_exp, extract_linear_exp, max_CEGAR_iteration, cegar_ref, unif_linear_exp_cegar



#----------------------------------------------------------------------------------- 15/06/2016 ---#
def internal_user_questions_lin():
	
	
	""" INPUT data for the Main program """
	""" Kind of hybrid automaton (linear or polyhedral). """
	HA_type = 'linear'
	
	
	""" Name folder where the input folder containing the input automaton text file can be found. """
	#namefolder = '/Users/mgarcia/Software/2016_11_04_AVERIST_unified/EXPERIMENTS/Hybridization/ArbitrarySwitching/4D/as_4D_example_3'
	namefolder = '/Users/mgarcia/Software/2016_11_04_AVERIST_unified/EXPERIMENTS/Hybridization/SwitchedSystem/4D/ssas4_4D_example_3'
	
	
	""" Set the way of choosing the linear expressions for partitioning the state space, manually by providing them into a file or automatically by
		determining the partition size. """
	given_linear_exp = 'nle'
	unif_linear_exp = 0
	
	#	given_linear_exp = 'le'
	#	unif_linear_exp = -1
	
	""" Specify if the linear expressions involved in the input hybrid automaton definition are added to the set for partitioning the state space. """
	extract_linear_exp = 'exle'
	
	""" Maximum CEGAR iteration: bound in the CEGAR algorithm iterations to abort the loop in case of not
		obtaining any answer about stability or instability of the hybrid automaton. """
	max_CEGAR_iteration = 3
	
	
	""" Specify if the linear expressions involved in cegar refinement are added by uniform creation or by separation selected predicates. """
	cegar_ref = 'selected'
	#	cegar_ref = 'unif'
	
	unif_linear_exp_cegar = 0
	
	
	return HA_type, namefolder, given_linear_exp, unif_linear_exp, extract_linear_exp, max_CEGAR_iteration, cegar_ref, unif_linear_exp_cegar


		

	



