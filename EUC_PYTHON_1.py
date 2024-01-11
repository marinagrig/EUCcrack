#Python Script for two-scale linear analysis

#
#	date 13.3.2019
#	list of changes compared to prev versions:
#	1. using of previous material properties calculation is fixed  
#   2. ***


import inspect
import sys
import os
import job
import ctypes  # An included library with Python install.
import datetime

from odbAccess import *	
from numpy import *

def get_script_dir(follow_symlinks=True):
    if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
        path = os.path.abspath(sys.executable)
    else:
        path = inspect.getabsfile(get_script_dir)
    if follow_symlinks:
        path = os.path.realpath(path)
    return os.path.dirname(path)

def Mbox(title, text, style):
    return ctypes.windll.user32.MessageBoxA(0, text, title, style)

	
def main():
	print ('\n**************************************** ')
	print ('\nPython script 1 is started ')
	
	current_dir=get_script_dir()	

	os.chdir(current_dir)    
	os.system("abaqus make library=umat directory=current_dir")
	current_time = datetime.datetime.now().time()

	file_batch = open('_Python2_Caller.bat','w')
	file_batch.write("D:\n")
	file_batch.write("CD \"" + current_dir + '"\n')
	file_batch.write("C:\\SIMULIA\\Abaqus2\\6.14-5\\code\\bin\\abq6145.exe cae noGui=\"" + current_dir + "\\EUC_PYTHON_2.py\"")
	file_batch.close()
	
	print ('Process Start Time is ', current_time)
	print ('\nCurrent working directory path is\n  ', current_dir) 
	
	file_dir = open('D:\MarinaPath.txt','w')
	file_dir.write(current_dir)
	file_dir.close()

	file_time = open('_EUC_WorkingTime_log.txt','a')
	file_time.write('Process Start Time is %r\n' % current_time)
	file_time.close()	
	
	# allocate space for the matrix of homogenized IE
	IE=zeros([6,3],float) 


	response=Mbox('Equivalent material properties calculation', 'Equivalent material properties calculation\n  Press Yes to bypass and use previous results', 4)  # return 6=bypass, 7=calculate again
	print response
	
	if response == 7:

		# Step 1: preprocessing - create and submit the job for unit cell problem
		myJob1 = mdb.JobFromInputFile(name='1_EUC_alfa11', inputFileName='1_EUC_alfa11.inp', userSubroutine='EUC_MPC.for')
		myJob1.submit()	# submit the job to ABAQUS kernel for analysis
		myJob1.waitForCompletion()

		myJob2 = mdb.JobFromInputFile(name='1_EUC_alfa22', inputFileName='1_EUC_alfa22.inp', userSubroutine='EUC_MPC.for')
		myJob2.submit()	# submit the job to ABAQUS kernel for analysis
		myJob2.waitForCompletion()

		myJob3 = mdb.JobFromInputFile(name='1_EUC_alfa12', inputFileName='1_EUC_alfa12.inp', userSubroutine='EUC_MPC.for')
		myJob3.submit()	# submit the job to ABAQUS kernel for analysis
		myJob3.waitForCompletion()

		print "\n  1_EUC_alfa11.odb, 1_EUC_alfa12.odb, 1_EUC_alfa22.odb are created\n"
	else:
		print "\n  Equivalent mat properties calc bypassed by user - using previous results\n"

		
	# Step 1.1: access odb files, calculate the homogenized L
	odb1 = openOdb ( '1_EUC_alfa11.odb' )
	Frame=[]	
	Frame.append(odb1.steps['Step-1'].frames[-1]) # access the last frame of Step-1
	heatflux=Frame[0].fieldOutputs['S']		# access heat flux objects
	ivol = Frame[0].fieldOutputs['IVOL']	# access integration point volume
	vol=0.0
	weight = 1.0
	prod=zeros(6,float) 
	# loop over all the integration points of all elements [type C3D8R=1 int.point per element]
	for intNd in range( len( heatflux.values ) ):
		stress_values =(heatflux.values[intNd])  # 4 values
		ivol_values =(ivol.values[intNd])        # 1 value
#		print ('number of integration points ', len(heatflux.values))
#		print ('stress values are ', stress_values.data)
#		print ('ivol values are ', ivol_values.data)
		prod = prod + stress_values.data*ivol_values.data  # 4 values   
	for ind in range( 6 ):
		IE[ind,0] = prod[ind]/8
	odb1.close()


	# Step 2.1: access odb files, calculate the homogenized L
	odb2 = openOdb ( '1_EUC_alfa22.odb' )
	Frame=[]	# access the last frames of six steps
	Frame.append(odb2.steps['Step-1'].frames[-1])
	# access heat flux objects
	heatflux=Frame[0].fieldOutputs['S']  
	# access integration point volume
	ivol = Frame[0].fieldOutputs['IVOL']
	vol=0.0
	weight = 1.0
	prod=zeros(6,float) 
	# loop over all the integration points
	for intNd in range( len( heatflux.values ) ):
		stress_values =(heatflux.values[intNd])  # 4 values
		ivol_values =(ivol.values[intNd])        # 1 value
		prod = prod + stress_values.data*ivol_values.data  # 4 values		   
	for ind in range( 6 ):
		IE[ind,1] = prod[ind]/8
	odb2.close()

	# Step 3.1: access odb files, calculate the homogenized L
	odb3 = openOdb ( '1_EUC_alfa12.odb' )
	Frame=[]	# access the last frames of six steps
	Frame.append(odb3.steps['Step-1'].frames[-1])
	# access heat flux objects
	heatflux=Frame[0].fieldOutputs['S']	   
	# access integration point volume
	ivol = Frame[0].fieldOutputs['IVOL']   
	# calculate the overall moduli
	vol=0.0
	weight = 1.0
	prod=zeros(6,float) 
	total_ivol=zeros(6,float)
	# loop over all the integration points
	for intNd in range( len( heatflux.values ) ):
		stress_values =(heatflux.values[intNd])  # 6 values
		ivol_values =(ivol.values[intNd])        # 1 value
		prod = prod + stress_values.data*ivol_values.data  # 6 values	
		total_ivol = total_ivol + ivol_values.data  # 6 values		   
	for ind in range( 6 ):
		IE[ind,2] = prod[ind]/8
	odb3.close()
	
	print ('****** total ivol is ', total_ivol);

	file1 = open ('Matrix_of_Materials.dat','w')
	file1.write("IE\n\
	%15.6f %15.6f %15.6f\n\
	%15.6f %15.6f %15.6f\n\
	%15.6f %15.6f %15.6f\n\
	%15.6f %15.6f %15.6f\n\
	%15.6f %15.6f %15.6f\n\
	%15.6f %15.6f %15.6f\n"\
	%(	IE[0,0],IE[0,1],IE[0,2],\
		IE[1,0],IE[1,1],IE[1,2],\
		IE[2,0],IE[2,1],IE[2,2],\
		IE[3,0],IE[3,1],IE[3,2],\
		IE[4,0],IE[4,1],IE[4,2],\
		IE[5,0],IE[5,1],IE[5,2]))
	file1.close()
#	The only non-zero elements of IE matrix are (0,0),(0,1),(1,0),(1,1),(3,2)
#	IE(0,0)=IE(1,1)
#	IE(0,1)=IE(1,0) 
	print "\n\n**********  Matrix_of_Materials.dat was created (for ref only)"

	##########################     MACRO    ######################################################
	# Step 4: prepare the input file for coarse scale analysis, then create and submit the job
	# prepare the input file by using global0.inp and homogenized L
	inpfile = open ('Macro.inp','r')
	outfile = open ('Macro_new.inp','w')
	inpfile.seek(0,0)
	done=0
	while not done:
	   line = inpfile.readline()
	   outfile.write(line)
	   if line != "":  # End-of-file has not been reached
		  # attach values of homogenized L to the input file
		  if line.find('*User Material, constants=3')  != -1:
			 #The first line for type=anisotropic
			 outfile.write( " %f, %f, %f, \n" \
							%(IE[0,0],IE[0,1],IE[3,2]) )
			 line = inpfile.readline()      
	   else:
		  done=1 # End-of-file reached
		  
	inpfile.close()
	outfile.close()

	print "\n Macro.inp file changed -->  Macro_new.inp was created"
	
	file2 = open('Strain.dat','w')
	file2.write("test")
	file2.close()
	
	
	current_time = datetime.datetime.now().time()
	print ('Macro solver starting time is ', current_time)
	file_time = open('_EUC_WorkingTime_log.txt','a')
	file_time.write('Macro solver starting time is %r\n' % current_time)
	file_time.close()	


	# create and submit the job for coarse scale analysis
	myJob = mdb.JobFromInputFile(name='Macro_new_test', inputFileName='Macro_new.inp', userSubroutine='EUC_UMAT.for')
	myJob.submit()	# submit the job to ABAQUS kernel for analysis
	myJob.waitForCompletion()	# halts the execution of this script until the end of the analysis

main()
