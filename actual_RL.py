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

def get_no_packages_per_category(filename, keys):
    f = open(filename).readlines()
    no_packages_per_category = {no:0 for no in keys}
    for line in f[1:]:
        no_packages = int(line.split(',')[-1])
        if no_packages > 1:
            no_packages_per_category[no_packages] += no_packages
    return no_packages_per_category

def get_no_customers_per_no_packages(filename, keys):
    f = open(filename).readlines()
    no_customers_per_no_packages = {no:0 for no in keys}
    for line in f[1:]:
        no_packages = int(line.split(',')[-1])
        if no_packages > 1:
            no_customers_per_no_packages[no_packages] += 1
    return no_customers_per_no_packages

def get_total_no_packages(filename):
    f = open(filename).readlines()
    total_no_packages = 0
    for line in f[1:]:
        no_packages = int(line.split(',')[-1])
        total_no_packages += no_packages
    return total_no_packages

# The save_result function appends the information from a run to a results csv file
def save_result(scenario_id, strategy, results, information):
    
    with open('results/results.csv', 'a') as f:

        print_string = strategy + ',' + str(scenario_id) + ',' + str(information[0]) + ',' + str(information[1]) + ','
        results_as_str = [str(res) for res in results]
        print_string += ','.join(results_as_str)
        print_string += '\n'
        f.write(print_string)

def run_env(run_number=0, no_trucks = 2, no_clusters = 2, no_drones = 3, no_customers = 60, p = [1], load = True, load_file = 'saved_states/saved_state_50_0.txt', strategy = 'farthest_package_first', save_state=False, drone_capacity = 2):

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

            #Total amount of time spent in the 2 min delay while delivering package
            total_delay_time = 0

            # The span is the time between the inital and final package deliveries for each customer
            # We store seperate values for each original_no_packages
            # Spans will be a dict with original_no_packages as the key and the total span as the value
            spans = {2:0,3:0,4:0}

            # Here we store the sum of the number of dropoffs for each customer grouped by original_no_packages
            no_dropoffs = {2:0,3:0,4:0} 
            

            drones = obs[1][0]
            trucks = obs[0][0]
            customers = obs[2]

            for customer in customers:
                if customer.original_no_packages in spans.keys():
                    spans[customer.original_no_packages] += (customer.time_final - customer.time_initial)
                    no_dropoffs[customer.original_no_packages] += customer.no_dropoffs

            for drone in drones:
                drone_travel_distance += drone.total_travel_distance
                X2 += drone.total_active_time
                total_delay_time += drone.total_delay_time
            
            for truck in trucks:
                total_package_waiting_time += truck.total_package_waiting_time
                total_customer_waiting_time += truck.total_customer_waiting_time
                truck_travel_distance += truck.total_travel_distance
                X1 += truck.total_time_in_cluster

            utilization = X2 / (X1 * no_drones)
            results = {
                'steps': steps,
                'drone_travel_distance': drone_travel_distance,
                'truck_travel_distance': truck_travel_distance,
                'X1': X1,
                'X2': X2,
                'utilization': utilization,
                'total_package_waiting_time': total_package_waiting_time,
                'total_customer_waiting_time': total_customer_waiting_time,
                'total_delay_time': total_delay_time,
                'spans': spans,
                'no_dropoffs': no_dropoffs    
            }
            return results

        

#Number of times we want to create a different scenario and run it
no_runs = 10

#Different parameters for our run
no_trucks = 2
no_drones = 3
# no_customers = 200
# no_clusters = int(no_customers / 50)

#I want to try running no_runs scenarios with the 'next_closest' strategy, then trying the same no_runs 
#scenarios with the 'random' strategy and compare the number of steps
p = [0.85, 0.09, 0.04, 0.02]

#This is the directory where our saved states are saved
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'

# This is just for testing
# drone_capacity = 3
# filename = path + 'saved_state_test.txt'
# run_env(6, 1, None, no_drones, None, p, load=True, load_file = filename, strategy='most_packages_first', save_state=False, drone_capacity = drone_capacity)

#Generate the 40 test files

no_customers_values = (50, 100, 200, 500)
# strategy = 'farthest_package_first'

# for no_customers in no_customers_values:

#     for i in range(10): 
    

#         run_env(i, no_trucks, 2, no_drones, no_customers, p, load=False, load_file=None, strategy=strategy, save_state=True, drone_capacity = 10)    




#Before we begin the simulation we want to initialize the csv file which will store the results

with open('results/results.csv', 'w') as f:
    f.write('strategy,scenario_id,drone_capacity,no_customers,total_time,A,drone_travel_distance,truck_travel_distance,X1,X2,utilization,avg_package_wait_time,avg_customer_wait_time,total_delay_time,avg_span_2,avg_span_3,avg_span_4,avg_nodropoffs_2,avg_nodropoffs_3,avg_nodropoffs_4\n')


drone_capacity_values = (1, 2, 3) # We will be testing these values of drone_capacity in our simulation
strategies = ('farthest_package_first_MPA', 'farthest_package_first', 'closest_package_first', 'most_packages_first')
# strategies = ('farthest_package_first_MPA', 'farthest_package_first_MPA_x')
for strategy in strategies:
    print(strategy)
    for drone_capacity in drone_capacity_values:
        
        for no_customers in no_customers_values:
            for i in range(10):

                print(drone_capacity, no_customers, i)
                filename = path + 'saved_state_' + str(no_customers) + '_' + str(i) + '.txt'
                params = {
                    'load_file' : filename,
                    'strategy' : strategy,
                    'drone_capacity' : drone_capacity
                }
                results = run_env(load_file=params['load_file'], strategy=params['strategy'], drone_capacity=params['drone_capacity'])

                spans = results['spans']
                no_dropoffs = results['no_dropoffs']
                
                # Here we store the number of packages for each group of no_packages.
                # You get the idea :)
                no_packages_total = get_total_no_packages(filename)
                no_packages_per_category = get_no_packages_per_category(filename, spans.keys())
                no_customers_per_no_packages = get_no_customers_per_no_packages(filename, spans.keys())
                # This is to prevent division by 0 errors
                if no_packages_per_category[2] == 0:
                    avg_span_2 = -10
                    avg_nodropoofs_2 = -10
                else:
                    avg_span_2 = round(spans[2] / no_customers_per_no_packages[2], 2)
                    avg_nodropoofs_2 = round(no_dropoffs[2] / no_packages_per_category[2], 2)
                if no_packages_per_category[3] == 0:
                    avg_span_3 = -10
                    avg_nodropoofs_3 = -10
                else:
                    avg_span_3 = round(spans[3] / no_customers_per_no_packages[3], 2)
                    avg_nodropoofs_3 = round(no_dropoffs[3] / no_packages_per_category[3], 2)
                if no_packages_per_category[4] == 0:
                    avg_span_4 = -10
                    avg_nodropoofs_4 = -10
                else:
                    avg_span_4 = round(spans[4] / no_customers_per_no_packages[4], 2)
                    avg_nodropoofs_4 = round(no_dropoffs[4] / no_packages_per_category[4], 2)
                save_result(i, strategy, (results['steps'][0], results['steps'][1], round(results['drone_travel_distance'], 2), round(results['truck_travel_distance'], 2), results['X1'], results['X2'], round(results['utilization'], 2) , round(results['total_package_waiting_time'] / no_packages_total, 2), round(results['total_customer_waiting_time'] / no_customers, 2), results['total_delay_time'], avg_span_2, avg_span_3, avg_span_4, avg_nodropoofs_2, avg_nodropoofs_3, avg_nodropoofs_4), (drone_capacity, no_customers))
