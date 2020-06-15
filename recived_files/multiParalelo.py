#Escalante Hernandez Alejandro
# #Multiparalelo utilizando operaciones de matrices propias
#Este programa se ejecutó en una laptop con 2 núcleos físicos

from misoperaciones import suma, mul, resta
from mpi4py import MPI

comm = MPI.COMM_WORLD
size = comm.Get_size()
rank = comm.Get_rank()

if rank == 0:
    #El procesador cero inicializa las matrices
    A = [[2,3,1,-1],[-2,0,-2,3],[2,3,1,2],[3,4,2,3]]
    B = [[2,1,3,2],[-1,2,-3,0],[1,0,2,0],[-1,0,2,0]]
else:
    pass
    A,B = None, None
#se comparten las matrices
A=comm.bcast(A, root=0)
B=comm.bcast(B, root=0)
#se definen los subconjuntos de las matrices
A11=[A[0][0:2],A[1][0:2]]
A12=[A[0][2:4],A[1][2:4]]
A21=[A[2][0:2],A[3][0:2]]
A22=[A[2][2:4],A[3][2:4]]

B11=[B[0][0:2],B[1][0:2]]
B12=[B[0][2:4],B[1][2:4]]
B21=[B[2][0:2],B[3][0:2]]
B22=[B[2][2:4],B[3][2:4]]
#se realizan las operaciones necesarias de acuerdo al anlaisis realizado en clase
#utilizando las operaciones definidas en misoperaciones.py y compartiendo información
#entre procesadores según sea necesario
if rank == 0:
    P1 = mul(suma(A11, A22), suma(B11,B22))
    P2 = mul(suma(A21, A22), B11)
    P6 = comm.recv()
    P3 = mul(A11,resta(B12,B22))
    C22 = resta(suma(P1,P3), suma(P2,P6))
    P5 = comm.recv()
    comm.send(P2, dest=1)
    C12 = suma(P3, P5)
    comm.send(P1,dest=1)
    C21 = comm.recv(tag=100)
    C11 = comm.recv(tag=110)
elif rank==1:
    P4 = mul(A22, resta(B21, B11))
    P6 = mul(resta(A21, A11), suma(B11, B12))
    comm.send(P6, dest=0)
    P5 = mul(suma(A11, A12), B22)
    P7 = mul(resta(A12, A22), suma(B21, B22))
    comm.send(P5, dest=0)
    P2 = comm.recv()
    C21 = suma(P2, P4)
    P1 = comm.recv()
    C11 = resta(suma(P1,P4), suma(P5, P7))
    comm.send(C21,dest=0,tag=100)
    comm.send(C11,dest=0,tag=110)
#El procesador cero imprime el resultado de todo el cómputo
if rank == 0:
    print('C11-> \n',C11)
    print('C12-> \n',C12)
    print('C21-> \n',C21)
    print('C22-> \n',C22)