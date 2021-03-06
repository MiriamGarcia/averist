__author__ = "Miriam Garcia Soto"
__email__ = "miriam.garcia@imdea.org"


from sage.libs.ppl import *
import time


#----------------------------------------------------------------------------------------------#
def create_elements(LE):
	"""
	Generate elements of a partition from a list of linear expressions.
	input:	LE	Linear Expressions      list of ppl.Linear_Expressions	
											
	output:	E	Elements                list of ppl.NNC_Polyhedron
	"""
    
	print 'LE=\n',LE

	# Starting time
	creation_time = time.time()

	# Element list
	E = []
	

	# We will check the first linear expression in the input list
	first_le = True
	for le in LE:
		
		# Constraints definition
		#ceq = le == _sage_const_0 					# Equality ppl.constraint
		#cbg = le > _sage_const_0 					# Bigger than zero ppl.constraint
		#csm = le < _sage_const_0 					# Smaller than zero ppl.constraint
		ceq = le == 0 					# Equality ppl.constraint
		cbg = le > 0 					# Bigger than zero ppl.constraint
		csm = le < 0 					# Smaller than zero ppl.constraint




		# Construct polyhedra with the constraints
		peq = NNC_Polyhedron(ceq)
		pbg = NNC_Polyhedron(cbg)
		psm = NNC_Polyhedron(csm)


		if first_le == True:

			# Add polyhedra to the element list
			E.append(peq)
			E.append(pbg)
			E.append(psm)

			# We will not check the first linear expression anymore
			first_le = False

		else:
			# Duplicate de element list
			aux_E = []
			# SPLIT ELEMENTS
			# Check if the elements are divided by the new linear expression
			for e in E:
				# the element is divided in case intersections with cbg and csm are different from emptiness
				# element intersected with pbg
				new_ebg = NNC_Polyhedron(e)
				new_ebg.intersection_assign(pbg)
                    
				if (new_ebg.is_empty() == False) and (new_ebg != e):
					# element intersected with psm
					new_esm = NNC_Polyhedron(e)
					new_esm.intersection_assign(psm)
                    
					if new_esm.is_empty() == False:
						# in the case the element is divided, this one disappears and three new elements are defined
						new_eeq = NNC_Polyhedron(e)
						new_eeq.intersection_assign(peq)
						aux_E.append(new_ebg)
						aux_E.append(new_esm)
						aux_E.append(new_eeq)

				else:
					# the element is not divided
					aux_E.append(e)

			E = aux_E[:]
                
	creation_time = time.time() - creation_time

	return E,creation_time



#----------------------------------------------------------------------------------------------#
def get_regions_and_faces(E):

	dim = E[0].space_dimension()
	
	RG = []
	F = []

	for element in E:
		if element.affine_dimension() == dim:
			RG.append(element)
		else:
			F.append(element)

	return RG,F




#----------------------------------------------------------------------------------------------#
def create_new_elements(E,LE):
	"""
		Generate elements of a partition of elements from a list of linear expressions.
		input:	E		Elements					list of ppl.NNC_Polyhedron
				LE		Linear Expressions			list of ppl.Linear_Expressions
		
		output:	new_E	Elements					list of ppl.NNC_Polyhedron
		"""
    
	print 'LE=\n',LE

	# Starting time
	creation_time = time.time()
	
	# Element list
	new_E = E
	
	
	# We will check the first linear expression in the input list
	#	first_le = True
	for le in LE:
		
		# Constraints definition
		#ceq = le == _sage_const_0 					# Equality ppl.constraint
		#cbg = le > _sage_const_0 					# Bigger than zero ppl.constraint
		#csm = le < _sage_const_0 					# Smaller than zero ppl.constraint
		ceq = le == 0 					# Equality ppl.constraint
		cbg = le > 0 					# Bigger than zero ppl.constraint
		csm = le < 0 					# Smaller than zero ppl.constraint
		
		
		# Construct polyhedra with the constraints
		peq = NNC_Polyhedron(ceq)
		pbg = NNC_Polyhedron(cbg)
		psm = NNC_Polyhedron(csm)
		

		# Duplicate de element list
		aux_E = []
		# SPLIT ELEMENTS
		# Check if the elements are divided by the new linear expression
		for e in new_E:
			# the element is divided in case intersections with cbg and csm are different from emptiness
			# element intersected with pbg
			new_ebg = NNC_Polyhedron(e)
			new_ebg.intersection_assign(pbg)
			
			if (new_ebg.is_empty() == False) and (new_ebg != e):
				# element intersected with psm
				new_esm = NNC_Polyhedron(e)
				new_esm.intersection_assign(psm)
				
				if new_esm.is_empty() == False:
					# in the case the element is divided, this one disappears and three new elements are defined
					#print 'Element ',e.constraints(),' divided.'
					new_eeq = NNC_Polyhedron(e)
					new_eeq.intersection_assign(peq)
					aux_E.append(new_ebg)
					aux_E.append(new_esm)
					aux_E.append(new_eeq)
			
			else:
				# the element is not divided
				aux_E.append(e)
		
		new_E = aux_E[:]

	creation_time = time.time() - creation_time
	
	return new_E,creation_time









