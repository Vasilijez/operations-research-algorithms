# simplex metod
import numpy as np
import pandas as pd
import itertools

# deljenje sa nulom ignorisi warnings
np.seterr(divide='ignore')

# favorizacija krajnjih indeksa
def sortByLargestSum(arr):
    n = len(arr)

    for i in range(0, n-1):
        for j in range(i, n):
            if sum(arr[i]) < sum(arr[j]):
                tmp = arr[i]
                arr[i] = arr[j]
                arr[j] = tmp

def endOutput(minimum, variables_number, extreme_value, Xb_idx):
    ispis = 'Z'
    if minimum == True:
        print(ispis + 'min iznosi', extreme_value)
    else:
        print(ispis + 'max iznosi', extreme_value)
    
    i = 0
    for idx in Xb_idx:
        print('X' + str(idx+1) + ' odnosno Y' + str(idx+1) + ' iznosi', Xb[i])
        i += 1

    for idx in range(0, variables_number):
        if idx not in Xb_idx:
            print('X' + str(idx+1) + ' odnosno Y' + str(idx+1) + ' iznosi', 0)

# menjati matricu u skladu sa problemom maksimuma/minimuma
# A = np.array([  #max
#     [0.5,2,1,24],
#     [1,2,4,60],
#     [6,14,13,0]
# ])
# A = np.array([  #min
#     [-0.5, -1, -6],
#     [-2, -2, -14],
#     [-1, -4, -13],
#     [24, 60, 0]
# ])
# A = np.array([  #max
#     [1, 0, 4],
#     [0, 2, 12],
#     [3, 2, 18],
#     [3, 5, 0]
# ])
# A = np.array([  #min
#     [-1, -0, -3, -3],
#     [-0, -2, -2, -5],
#     [4, 12, 18, 0]
# ])
# A = np.array([  #max
#     [3, 3, 12000],
#     [2, 1, 6000],
#     [3000, 2500, 0]
# ])
# A = np.array([  #min
#     [-3, -2, -3000],
#     [-3, -1, -2500],
#     [12000, 6000, 0]
# ])
# A = np.array([  #min 
#     [-3,-1,-9],
#     [-1,-2,-8],
#     [-1,-6,-12],
#     [8,12,0]
# ])
# A = np.array([  #max
#     [6,3,1200],
#     [75,100,25000],
#     [2,1.5,0]
# ])
# A = np.array([  #max
#     [6,3,1200],
#     [75,100,25000],
#     [2,1.5,0]
# ])

'''
Z = 20x2 + 30x3 + 40x4 + 50x5 + 60x6
x2 + x3 + x4 + x5 + x6 <= broj stolova
2x2 + 3x3 + 4x4 + 5x5 + 6x6 <= broj stolica
x2...6 > 0
'''
A = np.array([
    [1, 1, 1, 1, 1, 10],
    [2, 3, 4, 5, 6, 40],
    [20, 30, 40, 50, 60, 0]
])


minimum = False
maximum = True

# 1. inicijalizacija simplexa
constraint_number = A.shape[0]-1
A_last_row = np.array(A[-1][:-1])
zeros = np.array(np.zeros(shape=constraint_number))
c = np.concatenate((A_last_row, zeros), axis = 0)

inv_matrix = np.eye(constraint_number)
constraints_coefficients_matrix = A[0:constraint_number,:-1]
A1 = np.concatenate((constraints_coefficients_matrix, inv_matrix), axis = 1)

b = np.array(A[:-1,-1])
B_inv = np.array([])
Xb = np.array([])
Xb_idx = np.array([np.inf for i in range(constraint_number)])
B = np.array([])
variables_number = constraint_number + A.shape[1] - 1

# 2. izbor baznih promenljivih po prvi put
all_variations = list(itertools.permutations(range(variables_number), constraint_number))
sortByLargestSum(all_variations)

for indexes in all_variations: 
    B = A1[:, indexes]
    try:
        B_inv = np.linalg.inv(B)
        if (B_inv @ b >= 0).all():
            Xb = B_inv @ b
            Xb_idx = list(indexes)
            break
    except np.linalg.LinAlgError:
        print('Matrica B nije inverzna, matrica B: ', B)
        continue

if len(Xb) == 0: 
    print('Ne postoji adekvatan izbor baznih promenljivih!')    # kraj -> izlaz, nemas resenje
else:
    for _ in range(1000):

        # 3. formiranje ostatka tabele
        Cb = c[Xb_idx]    
        W = Cb @ B_inv
        Zb = Cb @ B_inv @ b
        pivot_col = []
        free_variables = []
        for j in range(0, variables_number):
            if j in Xb_idx:
                continue
            else:
                aj = A1[:, j]
                cj = c[j]
                free_variables.append([j, W @ aj - cj])

        # 3.2. biranje nove bazne
        j = free_variables[0][0]
        extreme_value = free_variables[0][1]
        if minimum == True:
            for idx, value in free_variables:
                if value > extreme_value:
                    extreme_value = value
                    j = idx 
        else:
            for idx, value in free_variables:
                if value < extreme_value:
                    extreme_value = value
                    j = idx 
        if (minimum and extreme_value <= 0) or (maximum and extreme_value >= 0):
            # kraj -> izlaz, imas resenje
            endOutput(minimum, variables_number, Zb, Xb_idx)
            break

        aj = A1[:, j]   # aj od ekstremne vrednosti

        # 3.3. formiranje pivot kolone
        pivot_col = B_inv @ aj
        pivot_el = np.inf
        pivot_el_idx = np.inf
        least_pos_el = np.inf
        quotient = Xb/pivot_col

        for idx in range(len(pivot_col)):
            if quotient[idx] > 0 and quotient[idx] < least_pos_el:
                least_pos_el = quotient[idx] 
                pivot_el = pivot_col[idx]
                pivot_el_idx = idx

        if pivot_el == np.inf:  # deljenje slobodne kolone sa pivot kolonom i nemanje bar jednog pozitivnog kolicnika
            # trebalo bi da je uspesan kraj algoritma, iscitavas vrednosti
            endOutput(minimum, variables_number, Zb, Xb_idx)
            break

        pivot_row_idx = pivot_el_idx
        Xb_idx[pivot_row_idx] = j

        # 4. formiranje nove tabele preko pivot kolone, vrste i elementa pa vracanje na pocetak
        Xb_old = Xb.copy()
        B_inv_old = B_inv.copy()
        for i in range(constraint_number):
            for j in range(constraint_number + 1):    # +1 zbog slobodne kolone
                if i == pivot_row_idx:
                    if j == constraint_number:    # slobodna kolona
                        Xb[i] = Xb_old[i] / pivot_el
                    else: 
                        B_inv[i][j] = B_inv_old[i][j] / pivot_el
                else:
                    if j == constraint_number:    # slobodna kolona
                        Xb[i] = Xb_old[i] - ((Xb_old[pivot_row_idx] * pivot_col[i]) / pivot_el) 
                    else:
                        B_inv[i][j] = B_inv_old[i][j] - ((B_inv_old[pivot_row_idx][j] * pivot_col[i]) / pivot_el)
