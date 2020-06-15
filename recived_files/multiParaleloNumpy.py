#Escalante Hernandez Alejandro
#Multiparalelo utilizando operaciones de numpy
#Este programa se ejecutó en una laptop con 2 núcleos físicos

import numpy as np #se importa la librería
from mpi4py import MPI
comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    #El procesador cero inicializa las matrices utilizando numpy 
    A = np.array([[2,3,1,-1],[-2,0,-2,3],[2,3,1,2],[3,4,2,3]])
    B = np.array([[2,1,3,2],[-1,2,-3,0],[1,0,2,0],[-1,0,2,0]])

else:
    pass
    A,B = None, None
#se comparten las matrices 
A=comm.bcast(A, root=0)
B=comm.bcast(B, root=0)
#se definen los subconjuntos de las matrices utilizando numpy
A11=A[np.ix_([0,1],[0,1])]
A12=A[np.ix_([0,1],[2,3])]
A21=A[np.ix_([2,3],[0,1])]
A22=A[np.ix_([2,3],[2,3])]

B11=B[np.ix_([0,1],[0,1])]
B12=B[np.ix_([0,1],[2,3])]
B21=B[np.ix_([2,3],[0,1])]
B22=B[np.ix_([2,3],[2,3])]
#se realizan las operaciones necesarias de acuerdo al anlaisis realizado en clase
#utilizando las operaciones incluidas en numpy y compartiendo información
#entre procesadores según sea necesario
if rank == 0:
    P1 = np.dot(A11+A22,B11+B22)
    P2 = np.dot(A21+A22,B11)
    P6 = comm.recv()
    P3 = np.dot(A11,B12-B22)
    C22 = (P1+P3)-(P2+P6)
    P5 = comm.recv()
    comm.send(P2,dest=1)
    C12 = P3+P5
    comm.send(P1,dest=1)
    C21 = comm.recv(tag=100)
    C11 = comm.recv(tag=110)

elif rank == 1:
    P4 = np.dot(A22, B21-B11)
    P6 = np.dot(A21-A11,B11+B12)
    comm.send(P6, dest=0)
    P5 = np.dot(A11+A12,B22)
    P7 = np.dot(A12-A22,B21+B22)
    comm.send(P5,dest=0)
    P2 = comm.recv()
    C21 = P2 + P4
    P1 = comm.recv()
    C11 = (P1+P4)-(P5+P7)
    comm.send(C21,dest=0,tag=100)
    comm.send(C11,dest=0,tag=110)
#El procesador cero imprime el resultado de todo el cómputo
if rank == 0:
    print('C11-> \n',C11)
    print('C12-> \n',C12)
    print('C21-> \n',C21)
    print('C22-> \n',C22)
