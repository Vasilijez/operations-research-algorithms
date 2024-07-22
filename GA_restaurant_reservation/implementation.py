# Autori
# Luka Stajic
# Vasilije Zekovic

import random
import numpy as np
import matplotlib.pyplot as plt
import math

from mpl_toolkits import mplot3d

pi = 3.1415


class Reservation():
  def __init__(self, reservation_id, start_time, duration, chairs):
    self.reservation_id = reservation_id  # 2. slucaj - unapređen GA
    self.start_time = start_time
    self.duration = duration
    self.chairs = chairs

# reservations_number - broj rezervacija u danu
# tables_number - broj stolova u restoranu
# pop_size - velicina populacije tj broj hromozoma
# duration_limit - duzina rezervacije: 1 - 15min, 2 - 30min, 3 - 45min
# tables_types - tables_types[0] broj stolova sa 2 stolice, tables_types[1] broj stolova sa 4 stolice, tables_types[2] broj stolova sa 6 stolice
def generate_inital_chromosomes(reservations_number, tables_number, pop_size, duration_limit, tables_types): 
  if tables_types[0] + tables_types[1] + tables_types[2] != tables_number:
    print("NIJE DOBAR TABLE TYPES")
    return

  reservations = []
  for reservation_id in range(0, reservations_number):
    start_time = random.randint(0, 47-duration_limit)
    tables = [2, 4, 6]
    tables_probability = [tables_types[0] / tables_number, tables_types[1] / tables_number, tables_types[2] / tables_number]
    reservation = Reservation(reservation_id + 1, start_time, random.randint(1, duration_limit), random.choices(tables, weights=tables_probability)[0])

    reservations.append(reservation)

  population = []  

  for _ in range(pop_size):
    chromosome = np.zeros(shape=(tables_number, 12 * 4))

    for id, reservation in enumerate(reservations):

      iterations_number = 0

      random_table = 0
      upisao = False
      while iterations_number < 10:
        if reservation.chairs == 2:
          random_table = random.randint(0, tables_types[0]-1)
        if reservation.chairs == 4:
          random_table = random.randint(tables_types[0], tables_types[0] + tables_types[1]-1)
        if reservation.chairs == 6:
          random_table = random.randint(tables_types[0] + tables_types[1], tables_number-1)
        
        continue_searcing = False
        for i in range(reservation.duration):

          if chromosome[random_table][reservation.start_time + i] != 0:
            continue_searcing = True
            break

        iterations_number += 1

        if continue_searcing:
          continue

        for i in range(reservation.duration):
          chromosome[random_table][reservation.start_time + i] = reservation.reservation_id
          upisao = True
        
        break

      if upisao == False:
        if random.randint(0, 1):
          add_reservation = True

          for i in range(8):

            if reservation.start_time + i > 47:
              add_reservation = False
              break

            for j in range(reservation.duration):
              if reservation.start_time + i + j > 47:
                add_reservation = False
                break

              if chromosome[random_table][reservation.start_time + i + j] != 0:
                add_reservation = False
                break
            
            finish_current_reservation = False
            if add_reservation:
              for j in range(reservation.duration):
                chromosome[random_table][reservation.start_time + i + j] = reservation.reservation_id
                finish_current_reservation = True
                break

            if finish_current_reservation:
              break


          # -------------------------------------------------------------------------
          # 2. slucaj - unapređen GA
          # pomeranje 2 sata unazad ako unapred nije uspelo
          if add_reservation == False:
            for i in range(8):

              if reservation.start_time - 8 + i < 0:
                add_reservation = False
                break

              for j in range(reservation.duration):
                if reservation.start_time - 8 + i + j > 47:
                  add_reservation = False
                  break

                if chromosome[random_table][reservation.start_time - 8 + i + j] != 0:
                  add_reservation = False
                  break
              
              finish_current_reservation = False
              if add_reservation:
                for j in range(reservation.duration):
                  chromosome[random_table][reservation.start_time - 8 + i + j] = reservation.reservation_id
                  finish_current_reservation = True
                  break

              if finish_current_reservation:
                break
          # -------------------------------------------------------------------------


    population.append(chromosome)
  
  return population, reservations


def population_stats(costs):
  return costs[0], sum(costs)/len(costs)


def rank_chromosomes(cost, chromosomes):
  costs = list(map(cost, chromosomes))
  # ranked  = sorted( list(zip(chromosomes,costs)), key = lambda c:c[1])
  ranked = sorted(list(zip(chromosomes, costs)), key=lambda c: c[1], reverse=True)

  return list(zip(*ranked))


def natural_selection(chromosomes, n_keep):
  return chromosomes[:n_keep]


def roulette_selection(parents):

  pairs = []
  i = 0
  for i in range(0, len(parents), 2):

    weights=[];
    for i in range(len(parents)):
        weights.append((len(parents)-i)*random.random()) #za minimum
      #  weights.append((i+1)*random.random()) #za maksimum
    if (weights[0]>=weights[1]):
        maxInd1=0;
        maxInd2=1;
    else:
        maxInd1=1;
        maxInd2=0;
    
    for i in range(2,len(parents)):
        if weights[i]>weights[maxInd1]:
            maxInd2=maxInd1
            maxInd1=i
        elif weights[i]>weights[maxInd2]:
            maxInd2=1
    pairs.append([parents[maxInd1], parents[maxInd2]])
      
  return pairs


def two_point_crossover(pairs, tables_types): 
  children = []

  for pair in pairs:
    a = pair[0]
    b = pair[1]

    childA = np.concatenate((a[:tables_types[0], :], b[tables_types[0]:tables_types[0] + tables_types[1], :], a[-tables_types[2]:, :]), axis=0)
    childB = np.concatenate((b[:tables_types[0], :], a[tables_types[0]:tables_types[0] + tables_types[1], :], b[-tables_types[2]:, :]), axis=0)
    children.append(childA)
    children.append(childB)

  return children


def mutation(chromosomes, mutation_rate, tables_types, reservations, adding_unused_reservations_percent, tables_number):
  mutated_chromosomes = []

  for chromosome in chromosomes: 
    
    # -------------------------------------------------------------------------
    # 2. slucaj - unapređen GA
    chromosome_reservations_number = reservations_number_function(chromosome)
    for _ in range(chromosome_reservations_number):
    # -------------------------------------------------------------------------
      
      for idx in range(len(tables_types)):
        table_number_by_type = tables_types[idx]
        time_slot_number = len(chromosome[0])

        # biram pocetni indeks bloka
        if idx == 0:
          table_type_start_idx = 0
        else:
          table_type_start_idx += tables_types[idx-1]

        if random.random() < mutation_rate:
          
          old_reservation_table_idx = random.randint(table_type_start_idx, 
                                table_type_start_idx + table_number_by_type - 1)
          
          # pronadji rezervaciju
          reservation_id = 0
          reservation_duration = 0
          reservation_old_idx = 0
          exit = 0

          # nasumican pocetni index za neki red
          # pocinjes od nekog indexa samo ako je nezauzet rezervacijom
          iterations_number = 0
          random_start_idx = 0
          while(iterations_number != 20):  
            random_start_idx = random.randint(0, time_slot_number - 1)
            if chromosome[old_reservation_table_idx][random_start_idx] == 0:
              break
            iterations_number += 1
          
          # ako ne uspe da nadje indeks posle razumnog roka
          if iterations_number == 20:
            random_start_idx = 0

          for time_slot_idx in range(random_start_idx, time_slot_number):
            time_slot = chromosome[old_reservation_table_idx][time_slot_idx]
            if time_slot > 0:
              reservation_id = time_slot  
              reservation_old_idx = time_slot_idx   # kasnije za oslobadjanje 
              for i in range(time_slot_idx, time_slot_number):
                if chromosome[old_reservation_table_idx][i] == reservation_id:
                  reservation_duration += 1
                else:
                  exit = 1
                  break


              if exit == 1:
                break

          # a sta ako nema rezervacija tu
          if reservation_id == 0:
            continue

          # pronasao rezervaciju
          # ide redom i pokusava da je zameni
          free_to_alocate = False
          for new_reservation_table_idx in range(table_type_start_idx, 
                                                table_type_start_idx + table_number_by_type):
            if old_reservation_table_idx != new_reservation_table_idx:
              free_to_alocate = True
              for i in range(reservation_duration): 
                if chromosome[new_reservation_table_idx][reservation_old_idx + i] > 0:
                  free_to_alocate = False
                  break
              
              if free_to_alocate == True:
                for k in range(reservation_duration): 
                  chromosome[new_reservation_table_idx][reservation_old_idx + k] = reservation_id

                # oslobodi mesto stare rezervacije
                for tmp_idx in range(reservation_duration):
                  chromosome[old_reservation_table_idx][reservation_old_idx + tmp_idx] = 0

                # print('\nreservation_id', reservation_id)
                # print('\n new_reservation_table_idx', new_reservation_table_idx)
                # print('\nold_reservation_table_idx', old_reservation_table_idx)
                # print('\nreservation_time_slot', reservation_old_idx)
                # print('\nredni_br_hromozoma', chromosome_idx)
                # print('\ntable_type_start_idx', table_type_start_idx)
                # print('\n')

                break

    # -------------------------------------------------------------------------
    # 2. slucaj - unapređen GA
    if random.random() < mutation_rate:
      chromosome = try_to_add_unused_reservations(chromosome, reservations, adding_unused_reservations_percent, tables_types, tables_number)
    # -------------------------------------------------------------------------

    mutated_chromosomes.append(chromosome)
        
  return mutated_chromosomes


# 2. slucaj - unapređen GA
def random_select_reservations(reservations, percent):
  num_to_select = round(len(reservations) * percent)

  if len(reservations) < 10:
      selected_reservations = reservations  
  else:
      selected_reservations = random.sample(reservations, num_to_select)

  return selected_reservations


# 2. slucaj - unapređen GA
def find_all_reservations_id(chromosome):
  chromosome_reservations_ids = []
  current_reservation_id = 0

  for table in chromosome:
    for time_slot in table:
      if time_slot > 0 and current_reservation_id != time_slot:
        current_reservation_id = time_slot
        chromosome_reservations_ids.append(current_reservation_id)

  return chromosome_reservations_ids
  

# 2. slucaj - unapređen GA
def try_to_add_unused_reservations(chromosome, reservations, adding_unused_reservations_percent, tables_types, tables_number):

  random_selected_reservations = random_select_reservations(reservations, adding_unused_reservations_percent)

  chromosome_reservations_ids = find_all_reservations_id(chromosome)

  chromosome_unused_random_selected_reservations = []

  for random_selected_reservation in random_selected_reservations:
    if random_selected_reservation.reservation_id not in chromosome_reservations_ids:
      chromosome_unused_random_selected_reservations.append(random_selected_reservation)

  for id, reservation in enumerate(chromosome_unused_random_selected_reservations):

    iterations_number = 0

    random_table = 0
    upisao = False
    while iterations_number < 10:
      if reservation.chairs == 2:
        random_table = random.randint(0, tables_types[0]-1)
      if reservation.chairs == 4:
        random_table = random.randint(tables_types[0], tables_types[0] + tables_types[1]-1)
      if reservation.chairs == 6:
        random_table = random.randint(tables_types[0] + tables_types[1], tables_number-1)
      
      continue_searcing = False
      for i in range(reservation.duration):

        if chromosome[random_table][reservation.start_time + i] != 0:
          continue_searcing = True
          break

      iterations_number += 1

      if continue_searcing:
        continue

      for i in range(reservation.duration):
        chromosome[random_table][reservation.start_time + i] = reservation.reservation_id
        upisao = True
      
      break

    if upisao == False:
      if random.randint(0, 1):
        add_reservation = True

        for i in range(8):

          if reservation.start_time + i > 47:
            add_reservation = False
            break

          for j in range(reservation.duration):
            if reservation.start_time + i + j > 47:
              add_reservation = False
              break

            if chromosome[random_table][reservation.start_time + i + j] != 0:
              add_reservation = False
              break
          
          finish_current_reservation = False
          if add_reservation:
            for j in range(reservation.duration):
              chromosome[random_table][reservation.start_time + i + j] = reservation.reservation_id
              finish_current_reservation = True
              break

          if finish_current_reservation:
            break


        # -------------------------------------------------------------------------
        # 2. slucaj - unapređen GA
        # pomeranje 2 sata unazad ako unapred nije uspelo
        if add_reservation == False:
          for i in range(8):

            if reservation.start_time - 8 + i < 0:
              add_reservation = False
              break

            for j in range(reservation.duration):
              if reservation.start_time - 8 + i + j > 47:
                add_reservation = False
                break

              if chromosome[random_table][reservation.start_time - 8 + i + j] != 0:
                add_reservation = False
                break
            
            finish_current_reservation = False
            if add_reservation:
              for j in range(reservation.duration):
                chromosome[random_table][reservation.start_time - 8 + i + j] = reservation.reservation_id
                finish_current_reservation = True
                break

            if finish_current_reservation:
              break
        # -------------------------------------------------------------------------

  return chromosome


def reservations_number_function(chromosome):
  reservations_number = 0
  current_reservation = 0

  for table in chromosome:
    for time_slot in table:
      if time_slot > 0 and current_reservation != time_slot:
        current_reservation = time_slot
        reservations_number += 1

  return reservations_number


def elitis(chromosomes_old,chromosomes_new, elitis_rate, population_size):
 
  old_ind_size=int(np.round(population_size*elitis_rate))
  return chromosomes_old[:old_ind_size]+chromosomes_new[:(population_size-old_ind_size)]


# 16 x 48 = 768 time slotova
# prosecan duration je 2
# sto znaci 768 / 384 = 384 rezervacije za smestiti

def genetic(cost_func , population_size = 100, mutation_rate = 0.8,elitis_rate=0.1, reservations_number = 600, 
            max_iter = 500, tables_number = 16, duration_limit = 3, tables_types = [8, 5, 3], adding_unused_reservations_percent = 0.2):

  
  avg_list = []
  best_list = []
  curr_best = np.inf
  same_best_count = 0
  reservations = []
  
  
  chromosomes, reservations = generate_inital_chromosomes(reservations_number, tables_number, population_size, duration_limit, tables_types)

  for iter in range(max_iter):
      
    ranked_parents, costs = rank_chromosomes(cost_func, chromosomes)  
    best, average = population_stats(costs)
    parents = natural_selection(ranked_parents, population_size) 

    pairs = roulette_selection(parents)
    children = two_point_crossover(pairs, tables_types) 
    chromosomes = mutation(children, mutation_rate, tables_types, reservations, adding_unused_reservations_percent, tables_number) 

    ranked_children, costs = rank_chromosomes(cost_func, chromosomes)
    chromosomes=elitis(ranked_parents, ranked_children, elitis_rate, population_size) 
    
    print("Generation: ",iter+1," Average: {:.3f}".format(average)," Curr best: {:.3f}".format(best)) 
    print("-------------------------")
    



    avg_list.append(average)
    if best < curr_best:
      best_list.append(best)
      curr_best = best
      same_best_count = 0
    else:
      same_best_count += 1
      best_list.append(best)
      
    
    if (cost_func(chromosomes[0]) == reservations_number):
      
      avg_list = avg_list[:iter]
      best_list = best_list[:iter]
      all_avg_list.append(avg_list)
      all_best_list.append(best_list)
      generations_list.append(iter)
     
      print("\nSolution found ! Best chromosome: \n", chromosomes[0])
      print("\n")
      return
        
    if same_best_count > 20:
      print("\nStopped due to convergance. Solution not found! \n")
      
      with np.printoptions(threshold=np.inf, linewidth=np.inf):
        print(chromosomes[0])
        print("\n")



      avg_list = avg_list[:iter]
      best_list = best_list[:iter]
      all_avg_list.append(avg_list)
      all_best_list.append(best_list)
      generations_list.append(iter)
      
      return
    
    if iter == 499:
      avg_list = avg_list[:iter]
      best_list = best_list[:iter]
      all_avg_list.append(avg_list)
      all_best_list.append(best_list)
      generations_list.append(iter)
      
      print("\nStopped due to max number of iterations, solution not found. Best chromosome: \n", chromosomes[0])
      print("\n")



def display_stats(all_avg_list, all_best_list, generations_list):
  
  c = 0
  colors = ['red', 'green', 'blue', 'yellow', 'orange']
  

  for average_list in all_avg_list:
      x_axis = list(range(generations_list[c]))
      y_axis = average_list
      plt.plot(x_axis, y_axis, linewidth=3, color=colors[c], label=str(c + 1))
      plt.title('Average cost function value', fontsize=19)
      plt.xlabel('Generation', fontsize=10)
      plt.ylabel('Cost function')
      c += 1
  plt.legend(loc='upper right')
  plt.show()

  c = 0

  for best_list in all_best_list:
      x_axis = list(range(generations_list[c]))
      y_axis = best_list
      plt.plot(x_axis, y_axis, color=colors[c], label=str(c + 1))
      plt.title('Best cost function value', fontsize=19)
      plt.xlabel('Generation')
      plt.ylabel('Cost function')
      c += 1
  plt.legend(loc='upper right')
  plt.show()



number_of_chromosomes = [20,100,500]
# 350 / 384 = 91% popunjenost   i  
#
reservations_number = 250
all_avg_list = []
generations_list = []
all_best_list = []
run_number = 2

for x in number_of_chromosomes:
  
  print("==========================")
  
  for k in range(0, run_number):
    
    print("\n", k + 1, ": run of genetic algorithm with ", x ," chromosomes.\n")    
    genetic(reservations_number_function , population_size = x, mutation_rate = 0.8,elitis_rate=0.9, reservations_number = reservations_number, 
            max_iter = 500, tables_number = 16, duration_limit = 3, tables_types = [8, 5, 3], adding_unused_reservations_percent=0.1)

  display_stats(all_avg_list, all_best_list, generations_list)
  all_best_list = []
  all_avg_list = []
  generations_list = []

