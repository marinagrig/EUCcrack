      SUBROUTINE MPC(UE,A,JDOF,MDOF,N,JTYPE,X,U,UINIT,MAXDOF,LMPC,
     * KSTEP,KINC,TIME,NT,NF,TEMP,FIELD,LTRAN,TRAN)
C
      INCLUDE 'ABA_PARAM.INC'
C
      DIMENSION UE(MDOF),A(MDOF,MDOF,N),JDOF(MDOF,N),X(6,N),
     * U(MAXDOF,N),UINIT(MAXDOF,N),TIME(2),TEMP(NT,N),
     * FIELD(NF,NT,N),LTRAN(N),TRAN(3,3,N)
C
		print*, 'jtype=',JTYPE, ' , KINC=',KINC, ' , mdof=',MDOF, ' , N=',N
!		DO IND = 1, N
!			print*, 'N=', IND, ' [x,y,z]=[', X(1,IND),X(2,IND),X(3,IND),X(4,IND),X(5,IND),X(6,IND), ']'		
!		END DO	     
		
		IF (JTYPE .EQ. 11) THEN  ! right side
			DO IND = 1, N
				A(1,1,IND) = 1
				A(2,2,IND) = -1
				JDOF(1,IND) = 1
				JDOF(2,IND) = 2
			END DO	 
		END IF

		IF (JTYPE .EQ. 12) THEN ! left side
			DO IND = 1, N
				A(1,1,IND) = -1
				A(2,2,IND) = 1
				JDOF(1,IND) = 1
				JDOF(2,IND) = 2
			END DO	 
		END IF

		IF (JTYPE .EQ. 13) THEN ! top side
			DO IND = 1, N
				A(1,1,IND) = 1
				A(2,2,IND) = -1
				JDOF(1,IND) = 2
				JDOF(2,IND) = 1
			END DO	 
		END IF

		IF (JTYPE .EQ. 14) THEN ! bottom
			DO IND = 1, N
				A(1,1,IND) = -1
				A(2,2,IND) = 1
				JDOF(1,IND) = 2
				JDOF(2,IND) = 1
			END DO	 
		END IF
C
		IF (JTYPE .EQ. 21) THEN ! right bottom edge
			DO IND = 1, N
				A(1,1,IND) = 0.707
				A(2,2,IND) = -0.707
				JDOF(1,IND) = 1
				JDOF(2,IND) = 2
			END DO	 
		END IF

		IF (JTYPE .EQ. 22) THEN ! right top edge
			DO IND = 1, N
				A(1,1,IND) = 0.707
				A(2,2,IND) = 0.707
				JDOF(1,IND) = 1
				JDOF(2,IND) = 2
			END DO	 
		END IF

		IF (JTYPE .EQ. 23) THEN ! left top edge
			DO IND = 1, N
				A(1,1,IND) = -0.707
				A(2,2,IND) = 0.707
				JDOF(1,IND) = 1
				JDOF(2,IND) = 2
			END DO	 
		END IF

		IF (JTYPE .EQ. 24) THEN ! left bottom edge
			DO IND = 1, N
				A(1,1,IND) = -0.707
				A(2,2,IND) = -0.707
				JDOF(1,IND) = 1
				JDOF(2,IND) = 2
			END DO	 
		END IF
		
		RETURN
		END
