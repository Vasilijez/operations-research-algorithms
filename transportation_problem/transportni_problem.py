
import numpy as np
import random

# A_init = np.array([[20,11,13,13,2], 
#                 [17,14,12,13,6],
#                 [15,12,18,18,7],
#                 [3,3,4,5,0]])

# A_init = np.array([[10,12,0,20], 
#                 [8,4,3,30],
#                 [6,9,4,20],
#                 [7,8,5,10],
#                 [10,40,30,0]])

# A_init = np.array([ # nije izbalansiran
#     [40,60,90,40],
#     [60,80,70,35],
#     [50,50,100,50],
#     [35,45,35,0]
# ])
# A_init = np.array([ # izbalansiran
#     [40,60,90,0,40],
#     [60,80,70,0,35],
#     [50,50,100,0,50],
#     [35,45,35,10,0]
# ])
# A_init = np.array([[6,4,5,6,3,260], # nije izbalansiran
#                 [9,5,4,3,3,280],
#                 [220,200,80,180,160,0]])

A_init = np.array([ # nije izbalansiran
    [40,60,90,40],
    [60,80,70,35],
    [50,50,100,50],
    [35,45,35,0]
])



class Node: 
    def __init__(self, coordinates, parent):
        self.coordinates = coordinates
        self.parent = parent


def balancing(A_init):
    kapacitet = sum(A_init[:-1, A_init.shape[1]-1].copy())
    potraznja = sum(A_init[A_init.shape[0]-1, :-1].copy())

    if kapacitet > potraznja:
        # prosiri A_init sa jednom kolonom koja ce imati sve nule, pri cemu je potraznja u toj koloni razlika izmedju kapaciteta i potraznje
        inserting_index = A_init.shape[1] - 1
        A_init = np.insert(A_init, inserting_index, 0, axis=1)
        A_init[A_init.shape[0]-1, inserting_index] = kapacitet - potraznja

    elif kapacitet < potraznja:
        # prosiri A_init sa jednim redom koji ce imati sve nule, pri cemu je kapacitet u tom redu jednak razlici izmedju potraznje i kapaciteta
        inserting_index = A_init.shape[0] - 1
        A_init = np.insert(A_init, inserting_index, 0, axis=0)
        A_init[inserting_index, A_init.shape[1] - 1] = potraznja - kapacitet

    return A_init


# formiranje tabele koja ce se koristiti za racunanje pocetnog resenja 
def formCalculationTable(A_init):
    return np.full((A_init.shape[0]-1, A_init.shape[1]-1), -np.inf)
    

def calculateMarkedElements(A, i, j):
    return np.sum(A[i, :] >= 0) + np.sum(A[:, j] >= 0)


def fulfillTable(A):
    n = A.shape[0]
    m = A.shape[1]
    while (n + m - 1 > np.sum(A >= 0)):
        marked_elements_number = 0
        optimal_zero_position = []
        for i in range(n):
            for j in range(m):
                if A[i][j] == -np.inf:
                    if calculateMarkedElements(A, i, j) >= marked_elements_number:
                        if calculateMarkedElements(A, i, j) == marked_elements_number:
                            optimal_zero_position.append((i, j))
                        else:
                            optimal_zero_position.clear()
                            optimal_zero_position.append((i, j))
                            marked_elements_number = calculateMarkedElements(A, i, j)

        if optimal_zero_position:
            chosen_position = random.choice(optimal_zero_position)
            A[chosen_position] = 0


def findParent(el, visited):   # prethodnik koji je roditelj 
    for temp_node in visited:
        if el.parent == temp_node:
            return temp_node    # vracam citavog prethodnika
    return None


def checkIfNodeExists(node, stack, visited):
    for tmp_node in visited:
        if tmp_node.coordinates == node.coordinates:
            if tmp_node.parent != None and node.parent != None:
                if tmp_node.parent.coordinates == node.parent.coordinates:
                    return True
    for tmp_node in stack:
        if tmp_node.coordinates == node.coordinates:
            if tmp_node.parent != None and node.parent != None:
                if tmp_node.parent.coordinates == node.parent.coordinates:
                    return True
    return False


def updateAvailableStates(visited, root_coordinates, parent, stack): # pamti par (i,j) i prethodnika

    # 1. slucaj, koren, njega razvijam i po vrsti i po koloni
    if parent.parent == None:  

        for i in range(A.shape[0]):    # fiksiram j, gledam kolonu u odnosu na element
            temp_coordinates = (i, parent.coordinates[1])
            if (temp_coordinates != parent.coordinates) and A[temp_coordinates] >= 0:
                child = Node(coordinates=temp_coordinates, parent=parent)
                if checkIfNodeExists(node=child, stack=stack, visited=visited) != True:
                    stack.insert(0, child)  

        for j in range(A.shape[1]):    # fiksiram i, gledam red u odnosu na element
            temp_coordinates = (parent.coordinates[0], j)
            if (temp_coordinates != parent.coordinates) and A[temp_coordinates] >= 0:
                child = Node(coordinates=temp_coordinates, parent=parent)
                if checkIfNodeExists(node=child, stack=stack, visited=visited) != True:
                    stack.insert(0, child)  
                # parent.children.append(child)
    
    # 2. slucaj, popunjen element
    else:

        # if parent.predecessor[0] == parent.coordinates[0]:  # formirali horizontalnu pravu, prelom na vertikalu
        if parent.parent.coordinates[0] == parent.coordinates[0]:  # formirali horizontalnu pravu, prelom na vertikalu
            for i in range(A.shape[0]):    # fiksiram j, gledam kolonu u odnosu na element
                temp_coordinates = (i, parent.coordinates[1])
                if (temp_coordinates != parent.coordinates) and ((A[temp_coordinates] >= 0) or (temp_coordinates == root_coordinates)): # provera da li je popunjeno polje ili ciljno polje u pitanju
                    child = Node(coordinates=temp_coordinates, parent=parent)
                    if checkIfNodeExists(node=child, stack=stack, visited=visited) != True:
                        stack.insert(0, child)   
        
        if parent.parent.coordinates[1] == parent.coordinates[1]:  # formirali vertikalnu pravu, prelom na horizontalu
            for j in range(A.shape[1]):    # fiksiram i, gledam red u odnosu na element
                temp_coordinates = (parent.coordinates[0], j)
                if (temp_coordinates != parent.coordinates) and ((A[temp_coordinates] >= 0) or (temp_coordinates == root_coordinates)): # provera da li je popunjeno polje ili ciljno polje u pitanju
                    child = Node(coordinates=temp_coordinates, parent=parent)
                    if checkIfNodeExists(node=child, stack=stack, visited=visited) != True:
                        stack.insert(0, child)  


# pre svega balansiranje tabele A_init
A_init = balancing(A_init)


# metod severozapadnog ugla
i, j = (0,0)
A = formCalculationTable(A_init)
kapacitet = A_init[:-1, A_init.shape[1]-1].copy()   # pravim kopiju zbog prenosa po referenci
potraznja = A_init[A_init.shape[0]-1, :-1].copy()


while (kapacitet[-1] != 0) and (potraznja[-1] != 0):
    razlika = min(kapacitet[i], potraznja[j])
    kapacitet[i] -= razlika
    potraznja[j] -= razlika
    A[(i,j)] = razlika

    if kapacitet[i] == 0 and i != len(kapacitet)-1:
        i += 1
    if potraznja[j] == 0 and j != len(potraznja)-1:
        j += 1


# dopuna tabele nulama ako je potrebno
fulfillTable(A)

Z = 0
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        if A[i][j] >= 0:
            Z += A[i][j] * A_init[i][j]

print('________________________________________')
print('1. Metod severozapadnog ugla: ')
print('A_init' + '\n', A_init)
print('A' + '\n', A)
print('Z iznosi:', int(Z))


# metod najmanjih cena
i, j = (0,0)
A = formCalculationTable(A_init)
kapacitet = A_init[:-1, A_init.shape[1]-1].copy()
potraznja = A_init[A_init.shape[0]-1, :-1].copy()

sorted_costs = {}
for i in range(A_init.shape[0]-1):
    for j in range(A_init.shape[1]-1):
        sorted_costs[(i,j)] = A_init[i][j]
sorted_costs = dict(sorted(sorted_costs.items(), key = lambda x: x[1]))

while len(sorted_costs) != 0:
    i,j = next(iter(sorted_costs))  # dobavljanje 0. elementa
    razlika = min(kapacitet[i], potraznja[j])
    kapacitet[i] -= razlika
    potraznja[j] -= razlika
    A[(i,j)] = razlika
    if kapacitet[i] == 0:
        sorted_costs = [cost for cost in sorted_costs if cost[0] != i]  # izbacujem neupotrebive celije iz i-te vrste
        if i != len(kapacitet)-1: 
            i += 1
    if potraznja[j] == 0:
        sorted_costs = [cost for cost in sorted_costs if cost[1] != j]  # izbacujem neupotrebive celije iz j-te kolone
        if j != len(potraznja)-1: 
            j += 1

# dopuna tabele nulama ako je potrebno
fulfillTable(A)

Z = 0
for i in range(A.shape[0]):
    for j in range(A.shape[1]):
        if A[i][j] >= 0:
            Z += A[i][j] * A_init[i][j]

print('________________________________________')
print('2. Metod najmanjih cena: ')
print('A_init' + '\n', A_init)
print('A' + '\n', A)
print('Z iznosi:', int(Z))
print('________________________________________')


# iterativni postupak
for i in range(10000):

    # dopuna tabele nulama ako je potrebno
    fulfillTable(A)

    # 0. postavi 0 u red u kom se nalazi bazna promenljiva sa najvecom vrednoscu
    u = [np.inf for _ in range(A_init.shape[0]-1)] 
    v = [np.inf for _ in range(A_init.shape[1]-1)]
    max_elements_row = np.unravel_index(A.argmax(), A.shape)[0] # pronalazi (i,j) elementa sa najvecom vrednoscu
    u[max_elements_row] = 0


    # 1. racunanje svih mogucih v, koristeci red u kom je u = 0
    filled_elements = [(i,j) for i in range(A.shape[0]) for j in range(A.shape[1]) if A[i][j] >= 0]
    for j in range(len(v)):
        if A[max_elements_row][j] >= 0:
            v[j] = A_init[max_elements_row][j] - 0
            if (max_elements_row,j) in filled_elements:
                filled_elements.remove((max_elements_row, j))

            # 2. racunanje svih mogucih u na osnovu popunjenih v i kolona kojima pripadaju
            for i in range(A.shape[0]):
                if A[i][j] >= 0 and u[i] == np.inf:
                    u[i] = A_init[i][j] - v[j]
                    if (i,j) in filled_elements:
                        filled_elements.remove((i,j))


    # 3. izracunati preostale vrednosti za u i v, na osnovu preostalih popunjenih elemenata
    counter = 0 
    while (len(filled_elements) != 0 and counter != 100):
        counter += 1 
        el = filled_elements.pop(0)
        # if el is computational: # computational
        #     filled_elements.append_end(el)
        if u[el[0]] == np.inf and v[el[1]] == np.inf:
            filled_elements.append(el)
            continue
        elif u[el[0]] == np.inf:
            u[el[0]] = A_init[el] - v[el[1]]
        else:
            v[el[1]] = A_init[el] - u[el[0]]

    # provera da li postoji slucaj prazna vrsta, prazna kolona i jedan presecan element
    if counter == 100:  
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if A[i][j] == 0:
                    A[i][j] = -np.inf
        continue


    # 4. izracunavanje nepopunjenih elemenata i pronalazenje minimalnog
    min_cost = np.inf
    min_cost_idx = (np.inf,np.inf)
    path = []
    for i in range(A.shape[0]):
        for j in range(A.shape[1]):
            if A[i][j] == -np.inf:  # nepopunjen element
                if (A_init[i][j] - u[i] - v[j]) < min_cost:
                    min_cost = A_init[i][j] - u[i] - v[j] 
                    min_cost_idx = (i,j)

    # kraj, ispis resenja
    if min_cost >= 0:   
        Z = 0
        for i in range(A.shape[0]):
            for j in range(A.shape[1]):
                if A[i][j] >= 0:
                    Z += A[i][j] * A_init[i][j]

        print('Tabela cena A: ')
        print(A)
        print('Z optimalno iznosi:', int(Z))

        break

    else:

        stack = []
        visited = []
        root = Node(coordinates=min_cost_idx, parent=None)
        updateAvailableStates(visited, root.coordinates, root, stack) 
        visited.append(root)

        while len(stack) != 0:
            el = stack.pop(0)
            visited.append(el)

            if el.coordinates == root.coordinates: # korenski, ali smo dosli do njega preko nekog drugog cvora
                path.append(el.coordinates)  # dodao kordinate korenskog

                while el.parent != root:  # dokle god ne dodjemo do korenskog opet
                    parent = el.parent
                    path.append(parent.coordinates)
                    el = parent    # sada tekuci element postaje roditelj

                break

            updateAvailableStates(visited, root.coordinates, el, stack)  


        # 6. pravljenje nove tabele na osnovu konture
        razlika = np.inf
        for redni_broj_elementa, value in enumerate(path):
            if value != min_cost_idx and (redni_broj_elementa % 2 != 0):
                if razlika > A[value]:
                    razlika = A[value]

        i = 0
        A[min_cost_idx] = 0  # pocetno teme postavljamo na 0, jer je prethodno bilo -np.inf

        for el_coordinates in path:
            if i % 2 == 0:
                A[el_coordinates] += razlika
            else: 
                A[el_coordinates] -= razlika

            if A[el_coordinates] == 0:  # ako se 0 pojave, to smatramo novim nepopunjenim elementom
                A[el_coordinates] = -np.inf

            i += 1




