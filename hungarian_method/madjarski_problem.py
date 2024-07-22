
import numpy as np


def findMinElByRows(A):
    return [min(A[i]) for i in range(A.shape[0])]


def getRestCoordinates(ref_zero_coordinate):
    ref_i, ref_j = ref_zero_coordinate
    rest_coordinates = []

    rest_j = [j for j in range(0,A.shape[0]) if j != ref_j]
    rest_i = [i for i in range(0,A.shape[0]) if i != ref_i]

    # fiksiras j, gledas po koloni
    rest_coordinates = [(i, ref_j) for i in rest_i if A[i,ref_j] == 0]

    # fiksiras i, gledas po vrsti
    rest_coordinates += [(ref_i, j) for j in rest_j if A[ref_i, j] == 0]
    
    return rest_coordinates


# A = np.array([[10,4,6,10,12], # min
#               [11,7,7,9,14],
#               [13,8,12,14,15],
#               [14,16,13,17,1],
#               [17,11,17,20,19]])

# A = np.array([[100,40,60,100,120],  # min
#               [110,70,70,90,140],
#               [130,80,120,140,150],
#               [140,160,130,170,10],
#               [170,110,170,200,190]])

# A = np.array([[20,28,19,13],  # min
#               [15,30,31,28],
#               [40,21,20,17],
#               [21,28,26,12]])

# A = np.array([[14,12,16,9,10],
#               [17,14,20,9,8],
#               [16,10,19,8,9],
#               [16,9,17,6,10],
#               [16,10,13,8,9]])

A = np.array([[100,40,60,100,120],  # min
              [110,70,70,90,140],
              [130,80,120,140,150],
              [140,160,130,170,10],
              [170,110,170,200,190]])

maximum = False

A_original = A.copy()   # potrebno za rekonstrukciju resenja

print(-A)

if maximum == True:
    A = -A

for _ in range(10000):
    # 1. otkrivanje minimalnih el. po vrstama
    min_elements_r = findMinElByRows(A)

    # 2. oduzimanje minimalnog el. vrste od svakog el. vrste
    for i in range(A.shape[0]):
        for j in range(A.shape[0]):
            A[i][j] = A[i][j] - min_elements_r[i]

    # 3. otkrivanje minimalnih el. po kolonama
    A_T = np.transpose(A)   # lakse se radi ako se transponuje matrica A
    min_elements_c = findMinElByRows(A_T)

    # 4. oduzimanje minimalnog el. kolone od svakog el. kolone
    for i in range(A_T.shape[0]):
        for j in range(A_T.shape[0]):
            A_T[i][j] = A_T[i][j] - min_elements_c[i]
    A = np.transpose(A_T)

    # 5. formiranje recnika i dodavanje svih nula
    zeros_dict = {}
    # zeros_dict[(0, 0)] = 13

    print(A)

    for i in range(A.shape[0]):
        for j in range(A.shape[0]):
            if A[i][j] == 0:
                zeros_dict[(i,j)] = -1


    independent_zeros = [] # nezavisne nule
    while len(zeros_dict) != 0:
        # 6. racunanje damage-a pri izboru svake nule
        for zero_coordinate in zeros_dict:
            zeros_dict[zero_coordinate] = 0 # reset damage-a
            rest_coordinates = getRestCoordinates(zero_coordinate)

            for c in rest_coordinates:
                if c in zeros_dict:
                    zeros_dict[zero_coordinate] += 1    # damage++ 

        # 7. biranje minimalnog
        independent_zero = min(zeros_dict, key=zeros_dict.get)
        independent_zeros.append(independent_zero)

        zeros_dict.pop(independent_zero)
        for c in getRestCoordinates(independent_zero):
            zeros_dict.pop(c, 0)    # 0 je def. vrednost koju vrati ako ne postoji el. sa tim kljucem, da ne bi pukao program

    if len(independent_zeros) == A.shape[0]:   # kraj algoritma
        z = 0
        for independent_zero in independent_zeros:
            z += A_original[independent_zero]
        print('Z iznosi: ', z)
        break

    # 8. formiranje nove tabele
    selected_rows = []  
    selected_cols = []
    marked_cols = []    # precrtane kolone
    marked_rows = []    # prectrani redovi

    # 8.1. oznacavanje redova sa iskljucivo zavisnim nulama
    for i in range(A.shape[0]):
        independent_zero_exists = False

        for j in range(A.shape[0]):
            if (i,j) in independent_zeros: 
                independent_zero_exists = True

        if A[i].any(0) and independent_zero_exists == False:
            selected_rows.append(i)

    # 8.2. precrtavanje kolona
    for i in selected_rows:
        for j in range(A.shape[0]):
            if A[i][j] == 0:
                marked_cols.append(j)

    marked_cols = list(set(marked_cols))    # ciscenje duplikata

    # 8.3. oznacavanje reda ukoliko se nezavisna nula nalazi u precrtanoj koloni
    for independent_zero in independent_zeros: # iteriram kroz nezavisne nule
        for marked_col in marked_cols:
            if independent_zero[1] == marked_col:
                selected_rows.append(independent_zero[0])

    # 8.4. precrtavanje preostalih redova
    for row in range(A.shape[0]):
        if row not in selected_rows:
            marked_rows.append(row)

    # 8.5. pronalazak vrednosti minimalnog neprectranog elementa 
    min_unmarked_el_val = np.inf
    for i in range(A.shape[0]):
        for j in range(A.shape[0]):
            if i not in marked_rows and j not in marked_cols:
                if A[i][j] < min_unmarked_el_val:
                    min_unmarked_el_val = A[i][j]

    # 8.6. konacno formiranje nove tabele
    for i in range(A.shape[0]):
        for j in range(A.shape[0]):
            if i in marked_rows and j in marked_cols:
                A[i][j] += min_unmarked_el_val
            elif i not in marked_rows and j not in marked_cols:
                A[i][j] -= min_unmarked_el_val

