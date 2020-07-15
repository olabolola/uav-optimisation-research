import gym

env_dict = gym.envs.registration.registry.env_specs.copy()
for env in env_dict:
     if 'HDS' in env:
          del gym.envs.registration.registry.env_specs[env]



import time
import os
import UAV_RL_env
import UAV_RL_env.envs.celes as celes
import numpy as np
import numpy as np
import random

    
random.seed(42)

#The save_result function appends the information from a run to a results csv file
def save_result(scenario_id, strategy, results, information):
    
    with open('results/results.txt', 'a') as f:

        print_string = strategy + ',' + str(scenario_id) + ',' + str(information[0]) + ',' + str(information[1]) + ',' + str(results[0]) + ',' + str(results[1]) + ',' + str(results[2]) + ',' + str(results[3]) + ',' + str(results[4]) + ',' + str(results[5]) + ',' + str(results[6]) + ',' + str(results[7]) + ',' + str(results[8]) + '\n'
        f.write(print_string)

def run_env(run_number, no_trucks = 3, no_clusters = 6, no_drones = 3, no_customers = 60, p = [1], load = False, load_file = None, strategy = 'next_closest', save_state=False, drone_capacity = 2):

    env = gym.make('HDS-v0', no_customers = no_customers, no_trucks = no_trucks, no_drones = no_drones, no_clusters=no_clusters, file_suffix=run_number, p = p, load = load, load_file = load_file, strategy=strategy, save_state=save_state, drone_capacity = drone_capacity)

    env.reset()

    truck_actions = []
    drone_actions = []



    for i in range(no_trucks):
        truck_actions.append("go_to_next_cluster")
        for _ in range(no_drones):
            drone_actions.append("deliver_next_package")

    action = (truck_actions, drone_actions)


    total_time = 0 #Here we store the number of steps for the trucks to return to the warehouse
    A = 0 #Here we stpre the number of steps until all packages are delivered

    # steps[0] will store the total time, while steps[1] will store the time it takes 
    steps = [0, 0]

    while True:

        obs, reward, done, info = env.step(action)
        total_time += 1
        
        #If we haven't delivered all packages then keep on counting A
        if not done[1]:
            A += 1

        # env.render()

        #When we are finished (trucks return to warehouse) we will return the results of the run
        if done[0]:
            
            #After the simulation is over store the total number of steps and A
            steps[0] = total_time
            steps[1] = A

            drone_travel_distance = 0
            truck_travel_distance = 0

            X1 = 0 #X1 is the total time spent by trucks in clusters
            X2 = 0 #X2 is the total active time of drones (including 2 minute dropoff time)

            #This is sum of time for each package to reach the customer
            total_package_waiting_time = 0
            total_customer_waiting_time = 0
            
            drones = obs[1][0]
            trucks = obs[0][0]

            for drone in drones:
                drone_travel_distance += drone.total_travel_distance
                X2 += drone.total_active_time
            
            for truck in trucks:
                total_package_waiting_time += truck.total_package_waiting_time
                total_customer_waiting_time += truck.total_customer_waiting_time
                truck_travel_distance += truck.total_travel_distance
                X1 += truck.total_time_in_cluster

            utilization = X2 / (X1 * no_drones)
            
            return (steps, drone_travel_distance, truck_travel_distance, X1, X2, utilization, total_package_waiting_time, total_customer_waiting_time)

        

#Number of times we want to create a different scenario and run it
no_runs = 10

#Different parameters for our run
no_trucks = 2
no_drones = 3
# no_customers = 200
# no_clusters = int(no_customers / 50)

#I want to try running no_runs scenarios with the 'next_closest' strategy, then trying the same no_runs 
#scenarios with the 'random' strategy and compare the number of steps
p = [0.9, 0.08, 0.02]

#This is the directory where our saved states are saved
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'

# This is just for testing
# for i in range(5):
#     drone_capacity = 5
#     filename = path + 'saved_state_50_' + str(i) + '.txt'
#     run_env(i, 1, None, no_drones, None, p, load=True, load_file = filename, strategy='farthest_package_first', save_state=False, drone_capacity = drone_capacity)

#Generate the 40 test files

no_customers_values = (50, 100, 200, 500)
# strategy = 'farthest_package_first'

# for no_customers in no_customers_values:

#     for i in range(10): 
    

#         run_env(i, no_trucks, 2, no_drones, no_customers, p, load=False, load_file=None, strategy=strategy, save_state=True, drone_capacity = 10)    





#Before we begin the simulation we want to initialize the csv file which will store the results

with open('results/results.txt', 'w') as f:
    f.write('strategy,scenario_id,drone_capacity,no_customers,total_time,A,drone_travel_distance,truck_travel_distance,X1,X2,utilization,avg_package_wait_time,avg_customer_wait_time\n')


drone_capacity_values = (1, 2, 3) # We will be testing these values of drone_capacity in our simulation


strategy = 'farthest_package_first'

for drone_capacity in drone_capacity_values:
    
    for no_customers in no_customers_values:
        for i in range(10):

            filename = path + 'saved_state_' + str(no_customers) + '_' + str(i) + '.txt'
            steps, drone_travel_distance, truck_travel_distance, X1, X2, utilization, package_wait_time, customer_wait_time = run_env(None, no_trucks, None, no_drones, None, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
            f = open(filename).readlines()
            no_packages = sum([int(i.split(',')[-1]) for i in f[1:]])
            save_result(i, strategy, (steps[0], steps[1], round(drone_travel_distance, 2), round(truck_travel_distance, 2), X1, X2, round(utilization, 2) , round(package_wait_time / no_packages, 2), round(customer_wait_time / no_customers, 2)), (drone_capacity, no_customers))


strategy = 'closest_package_first'

for drone_capacity in drone_capacity_values:
    
    for no_customers in no_customers_values:
        for i in range(10):

            filename = path + 'saved_state_' + str(no_customers) + '_' + str(i) + '.txt'
            steps, drone_travel_distance, truck_travel_distance, X1, X2, utilization, package_wait_time, customer_wait_time = run_env(None, no_trucks, None, no_drones, None, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
            f = open(filename).readlines()
            no_packages = sum([int(i.split(',')[-1]) for i in f[1:]])
            save_result(i, strategy, (steps[0], steps[1], round(drone_travel_distance, 2), round(truck_travel_distance, 2), X1, X2, round(utilization, 2) , round(package_wait_time / no_packages, 2), round(customer_wait_time / no_customers, 2)), (drone_capacity, no_customers))

strategy = 'most_packages_first'

for drone_capacity in drone_capacity_values:
    
    for no_customers in no_customers_values:
        for i in range(10):

            filename = path + 'saved_state_' + str(no_customers) + '_' + str(i) + '.txt'
            steps, drone_travel_distance, truck_travel_distance, X1, X2, utilization, package_wait_time, customer_wait_time = run_env(None, no_trucks, None, no_drones, None, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
            f = open(filename).readlines()
            no_packages = sum([int(i.split(',')[-1]) for i in f[1:]])
            save_result(i, strategy, (steps[0], steps[1], round(drone_travel_distance, 2), round(truck_travel_distance, 2), X1, X2, round(utilization, 2) , round(package_wait_time / no_packages, 2), round(customer_wait_time / no_customers, 2)), (drone_capacity, no_customers))
 
strategy = 'farthest_package_first_MPA'

for drone_capacity in drone_capacity_values:
    
    for no_customers in no_customers_values:
        for i in range(10):

            filename = path + 'saved_state_' + str(no_customers) + '_' + str(i) + '.txt'
            steps, drone_travel_distance, truck_travel_distance, X1, X2, utilization, package_wait_time, customer_wait_time = run_env(None, no_trucks, None, no_drones, None, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
            f = open(filename).readlines()
            no_packages = sum([int(i.split(',')[-1]) for i in f[1:]])
            save_result(i, strategy, (steps[0], steps[1], round(drone_travel_distance, 2), round(truck_travel_distance, 2), X1, X2, round(utilization, 2) , round(package_wait_time / no_packages, 2), round(customer_wait_time / no_customers, 2)), (drone_capacity, no_customers))


# strategy = 'farthest_package_first'
# for i in range(no_runs):
#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, (steps, drone_travel_distance, utilization), (no_customers, drone_capacity))

# random.seed(42)
# strategy = 'closest_package_first'
# for i in range(no_runs):
#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, (steps, drone_travel_distance, utilization), (no_customers, drone_capacity))

# random.seed(42)
# strategy = 'most_packages_first'
# for i in range(no_runs):
#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, (steps, drone_travel_distance, utilization), (no_customers, drone_capacity))

# random.seed(42)
# strategy = 'farthest_package_first_MPA'
# for i in range(no_runs):
#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, (steps, drone_travel_distance, utilization), (no_customers, drone_capacity))


        



        










        
