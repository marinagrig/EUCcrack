#Python Script for two-scale linear analysis

import inspect
import sys
import os
import job
import datetime

from odbAccess import *
from numpy import *


current_dir=os.getcwd()

current_time = datetime.datetime.now().time()
print ('Python2 starting time is ', current_time)
file_time = open('_EUC_WorkingTime_log.txt','a')
file_time.write('Python2 starting time is %r\n' % current_time)
file_time.close()	

file3 = open ('_stressfilename.dat','r')
stressfilepath = file3.readline()
stressfilepath = stressfilepath.lstrip()
stressfilepath = stressfilepath.strip('\n')
file3.close()

file1 = open ('_strainfilename.dat','r')
strainfilepath = file1.readline()
strainfilepath = strainfilepath.lstrip()
strainfilepath = strainfilepath.strip('\n')
file1.close()

nelem = strainfilepath.partition('_')[2]
nelem = nelem.partition('_')[2]
nelem = nelem.partition('.')[0]

file0 = open ('_tempfile.dat','a')
file0.write("\n%s\n"%stressfilepath)
file0.write("%s\n"%strainfilepath)
file0.write("%s\n"%nelem)
file0.close()


current_time = datetime.datetime.now().time()
print ('Python2 start reading strain.dat time is ', current_time)
file_time = open('_EUC_WorkingTime_log.txt','a')
file_time.write('Python2 start reading strain.dat time is %r\n' % current_time)
file_time.close()

file_lastStrain = open (strainfilepath,'r')
file_allStrain = open ('_Strain_all.dat','a')
Strain_from_UMAT = ['']*6
ind=0
done=0
while not done:
   line = file_lastStrain.readline()      
   if line != "":  # End-of-file has not been reached
      Strain_from_UMAT[ind]=line.rstrip('\n') # remove end of line characters
      file_allStrain.write("%s\n"%Strain_from_UMAT[ind])
      ind=ind+1
   else:
      done=1 # End-of-file reached
file_allStrain.write("**************\n")	  
print "_Strain_all.dat was created"

file_lastStrain.close()
file_allStrain.close()


# ####################           MICRO_Results          #####################################
inc_file = open ('_inc_num.txt','r')
inc_file.seek(0,0)
inc_number = inc_file.readline()
inc_number = inc_number.lstrip()
inc_number = inc_number.strip('\n')

# Step 6: 
# prepare the input file by using 3_EUC_Results.inp
inpfile = open ('3_EUC_Micro.inp','r')
outfile = open ('3_EUC_Micro_new.inp','w')
inpfile.seek(0,0)
done=0
while not done:
   line = inpfile.readline()
   outfile.write(line)
   if line != "":  # End-of-file has not been reached
      # attach values of homogenized L to the input file
      if line.find('*Expansion, type=ANISO')  != -1:
         #The first line for type=anisotropic
         outfile.write("%s, %s, %s, %s, %s, %s\n"%(Strain_from_UMAT[0],Strain_from_UMAT[1],Strain_from_UMAT[2],Strain_from_UMAT[3],Strain_from_UMAT[4],Strain_from_UMAT[5]))
         line = inpfile.readline()      
   else:
      done=1 # End-of-file reached
      
inpfile.close()
outfile.close()

current_time = datetime.datetime.now().time()
print ('Python2 start micro solver time is ', current_time)
file_time = open('_EUC_WorkingTime_log.txt','a')
file_time.write('Python2 start micro solver time is %r\n' % current_time)
file_time.close()

# create and submit the job for coarse scale analysis
job_name = '3_EUC_Micro_inc' + inc_number + '_elem' + nelem

file0 = open ('_tempfile.dat','a')
file0.write("%s\n"%job_name)
file0.close()

myJob = mdb.JobFromInputFile(name=job_name, inputFileName='3_EUC_Micro_new.inp', userSubroutine='EUC_MPC.for')
myJob.submit()	# submit the job to ABAQUS kernel for analysis
myJob.waitForCompletion()	# halts the execution of this script until the end of the analysis

current_time = datetime.datetime.now().time()
print ('Python2 end micro solver time is ', current_time)
file_time = open('_EUC_WorkingTime_log.txt','a')
file_time.write('Python2 end micro solver time time is %r\n' % current_time)
file_time.close()

################################ Micro Stress Average Result##################
# Step 7: access odb files, calculate the Stress Average of EUC
odb_name = job_name + '.odb'
odb1 = openOdb ( odb_name )

Frame=[]	# access the last frames of six steps
Frame.append(odb1.steps['Step-1'].frames[-1])

#access heat flux objects
heatflux=Frame[0].fieldOutputs['S']
       
# access integration point volume
ivol = Frame[0].fieldOutputs['IVOL']

vol=0.0
weight = 1.0
prod=zeros(6,float) 
S_ave_Inc = zeros(6,float);

# loop over all the integration points
for intNd in range( len( heatflux.values ) ):
        stress_values =(heatflux.values[intNd])  # 6 values
        ivol_values =(ivol.values[intNd])        # 1 value
        prod = prod + stress_values.data*ivol_values.data  # 6 values
for ind in range( 6 ):
        S_ave_Inc[ind] = prod[ind]/96

odb1.close()

current_time = datetime.datetime.now().time()
print ('Python2 end micro odb analysis time is ', current_time)
file_time = open('_EUC_WorkingTime_log.txt','a')
file_time.write('Python2 end micro odb analysis time is %r\n' % current_time)
file_time.close()

file4 = open (stressfilepath,'w')
file4.write("%17.10e, \n%17.10e, \n%17.10e, \n%17.10e, \n%17.10e, \n%17.10e"%(S_ave_Inc[0],S_ave_Inc[1],S_ave_Inc[2],S_ave_Inc[3],S_ave_Inc[4],S_ave_Inc[5]))
file4.close()

file0 = open ('_tempfile.dat','a')
file0.write("%s\n"%S_ave_Inc[0])
file0.close()

current_time = datetime.datetime.now().time()
print ('Python2 end time is ', current_time)
file_time = open('_EUC_WorkingTime_log.txt','a')
file_time.write('Python2 end time is %r\n' % current_time)
file_time.close()
# Back to UMAT with (S_ave_Inc), for Stress Calculate (S=S_ave_Inc)and begin the next increment