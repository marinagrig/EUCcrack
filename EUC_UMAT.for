*USER SUBROUTINES
      SUBROUTINE UMAT(STRESS,STATEV,DDSDDE,SSE,SPD,SCD,
     1 RPL,DDSDDT,DRPLDE,DRPLDT,
     2 STRAN,DSTRAN,TIME,DTIME,TEMP,DTEMP,PREDEF,DPRED,CMNAME,
     3 NDI,NSHR,NTENS,NSTATEV,PROPS,NPROPS,COORDS,DROT,PNEWDT,
     4 CELENT,DFGRD0,DFGRD1,NOEL,NPT,LAYER,KSPT,KSTEP,KINC)
	 
	! ***************************************************************
	! date 13.3.2019
	! list of changes compared to prev versions:
	! 1. current increment is saved to D:\inc_num.dat 
	!	 to be used in micro analysis py2
    ! 2. notes added
	! 
	! date 18.2.2021
	! list of changes compared to prev versions:
	! 1. added saving all input parameters to umat_info.txt
	! ***************************************************************
C
c     USE IFPORT
      include 'ABA_PARAM.INC'
C
      CHARACTER*8 CMNAME
      double precision, DIMENSION(4) :: stress_from_micro

      character*128 current_dir, str_strain, str_stress, str_batch, str_umat_info
      character*128 str_inc, str_time    
      character*57 tmpstr
	  character*3 nelem
	  integer date_time(8)
      character*10 b(3)
		
      DIMENSION STRESS(NTENS),STATEV(NSTATEV),
     1 DDSDDE(NTENS,NTENS),DDSDDT(NTENS),DRPLDE(NTENS),
     2 STRAN(NTENS),DSTRAN(NTENS),TIME(2),PREDEF(1),DPRED(1),
     3 PROPS(NPROPS),COORDS(3),DROT(3,3),DFGRD0(3,3),DFGRD1(3,3)
C
C

      PARAMETER (ONE=1.0D0, TWO=2.0D0)

      call date_and_time( b(1), b(2), b(3), date_time )

      E_11_22=PROPS(1)
      E_12=PROPS(2)
      E_44=PROPS(3)
C
      DO I=1,NTENS
       DO J=1,NTENS
        DDSDDE(I,J)=0.0D0
       ENDDO
      ENDDO
      DDSDDE(1,1)=E_11_22
      DDSDDE(2,2)=DDSDDE(1,1)
      DDSDDE(3,3)=DDSDDE(1,1)
      DDSDDE(4,4)=E_44
      DDSDDE(5,5)=E_44
      DDSDDE(6,6)=E_44
      DDSDDE(1,2)=E_12
      DDSDDE(1,3)=E_12
      DDSDDE(2,3)=E_12      
      DDSDDE(2,1)=DDSDDE(1,2)
      DDSDDE(3,1)=DDSDDE(1,3)
      DDSDDE(3,2)=DDSDDE(2,3)

	  print*,"****************"
      print*,"element number  ", NOEL
      print*,"int point number", NPT
      print*,"step number     ", KSTEP
      print*,"inc number      ", KINC
      print*,"ntens           ", NTENS
      print*,"ndi             ", NDI
      print*,"nshr            ", NSHR
      DO I=1,NTENS
         print*, "strain[",I,"]", STRAN(I)
		 print*, "dstrain[",I,"]", DSTRAN(I)
      ENDDO
	  print*, 'TIME=',b(2)
  
	!	  "*** read path of current folder from MarinaPath.txt"	  
      open(unit=10,file='D:\MarinaPath.txt',status='unknown')
      read(10,*) current_dir
      print*, trim(current_dir)  
      close(10)
	  
	!	  "*** save current increment number to _inc_num.txt file"
	  str_inc = trim(adjustl(current_dir)) // '\_inc_num.txt'      
      open(unit=11,file=str_inc, status='unknown')
      write(unit=11, fmt=*) KINC  
      close(11)

    !	  "*** save current UMAT info to text file"
	  str_umat_info = trim(adjustl(current_dir)) // '\_UMAT_info.txt'
      open(unit=12,file=str_umat_info, access = 'append', status='unknown')
      write(unit=12, fmt=*) ' element number=',NOEL
      write(unit=12, fmt=*) ' int point number=',NPT
      write(unit=12, fmt=*) ' step number=',KSTEP
      write(unit=12, fmt=*) ' inc number=',KINC
      write(unit=12, fmt=*) ' number of stress components=',NDI
      write(unit=12, fmt=*) ' number of shear components=',NSHR
      write(unit=12, fmt=*) ' start step time=',TIME(1)
      write(unit=12, fmt=*) ' start total time=',TIME(2)
      write(unit=12, fmt=*) ' time increment=',DTIME    
      DO I=1,NTENS
         write(unit=12, fmt=*) ' strain[', I, ']', STRAN(I)
		 write(unit=12, fmt=*) ' dstrain[', I, ']', DSTRAN(I)
      ENDDO
      write(unit=12, fmt=*) ' UMAT start PC time is =', b(2)    
      close(12)
      
	!	  "*** create temp file that contains path to strain_NOEL.dat	
	!	  "*** and read the path to parameter str1	
	!	  "*** this is the way to create valid path string 		
      write (nelem,"(I0)") NOEL
	  str_strain = trim(adjustl(current_dir)) // '\_strainfilename.dat'
      open(unit=13,file=str_strain, status='unknown')
      write(unit=13, fmt=*) trim(adjustl(current_dir)),'\strain_',trim(nelem),'.dat'  
      close(13)
      open(unit=13,file=str_strain, status='unknown')
      read(unit=13, fmt=*) str_strain  
      print*, trim(str_strain)
      close(13)

	!	  "*** create temp file that contains path to S_ave_.dat"	
	!	  "*** and read the content to parameter str1"	  	  
	  str_stress = trim(adjustl(current_dir)) // '\_stressfilename.dat'
      open(unit=14,file=str_stress, status='unknown')
      write(unit=14, fmt=*) trim(adjustl(current_dir)),'\S_ave_',trim(nelem),'.dat'  
      close(14)
      open(unit=14,file=str_stress, status='unknown')
      read(unit=14, fmt=*) str_stress  
      print*, trim(str_stress)
      close(14)
	  	  
	!	  "*** write total strain array to strain_NOEL.dat file "		  
      open(unit=15, file=str_strain, status='unknown') 	  
      do i = 1,NTENS
		Strain_total=(STRAN(I)+DSTRAN(I))
        write(15, "(E17.10)") Strain_total
      ENDDO
      close(15)

	!	  "*** create temp file that contains path to _Python2_caller.bat"	
	!	  "*** and read the content to parameter str1"	  	  
	!	  "*** this is the way to create valid path string 		
	  str_batch = trim(adjustl(current_dir)) // '\_batchfilename.dat'
      open(unit=16,file=str_batch, status='unknown')
      write(unit=16, fmt=*) trim(current_dir),'\_Python2_Caller.bat'  
      close(16)
      open(unit=16,file=str_batch, status='unknown')
      read(unit=16, fmt=*) str_batch  
      print*, trim(str_batch)
      close(16)
	  
      call date_and_time( b(1), b(2), b(3), date_time )

	  str_time = trim(adjustl(current_dir)) // '\_EUC_WorkingTime_log.txt'
	  open(unit=17,file=str_time, access = 'append', status='unknown')
      write(unit=17, fmt=*) ' UMAT PC time before calling Python2 is =', b(2)    
	  write(unit=17, fmt=*) ' ******************************'   
      close(17)
 	  
	  
	!	  "*** run batch file that include cmd line to execute t_EUC_2.py 			  
      call system (str_batch)

      call date_and_time( b(1), b(2), b(3), date_time )
	  str_time = trim(adjustl(current_dir)) // '\_EUC_WorkingTime_log.txt'
	  open(unit=18,file=str_time, access = 'append', status='unknown')
      write(unit=18, fmt=*) ' UMAT time after return from Python2 is =', b(2)    
	  write(unit=18, fmt=*) ' ******************************'   
      close(18)

	!	  "*** write micro stress array to S_ave_.dat file "		      
      open(unit=19, file=str_stress, status='unknown')
      do i = 1, NTENS
          read(19, '(d18.10, 5(",", d18.10))') stress_from_micro(i)
          print*, "stress[",i,"]", stress_from_micro(i)
       end do
       close(19)

	!	  "*** return micro stress to abaqus"	  	  
       DO I=1,NTENS
          STRESS(I)=stress_from_micro(i)
       ENDDO

      call date_and_time( b(1), b(2), b(3), date_time )
	  str_time = trim(adjustl(current_dir)) // '\_EUC_WorkingTime_log.txt'
	  open(unit=20,file=str_time, access = 'append', status='unknown')
      write(unit=20, fmt=*) ' UMAT exit PC time =', b(2)    
	  write(unit=20, fmt=*) ' ******************************'   
      close(20)

       RETURN
      END 
