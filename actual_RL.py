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

def save_result(i, strategy, results, characteristic):

    if i == 0:
        with open('results/result_' + strategy + '_' + str(characteristic[0]) + '_' + str(characteristic[1]) +'.txt', 'w') as f:
            f.write('no_steps,drone_travel_distance,utilization\n')
            f.write(str(results[0]) + ',' + str(results[1]) + ',' + str(results[2]) + '\n')
    else:
        with open('results/result_' + strategy + '_' + str(characteristic[0]) + '_' + str(characteristic[1]) +'.txt', 'a') as f:
            f.write(str(results[0]) + ',' + str(results[1]) + ',' + str(results[2]) + '\n')


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
    steps = 0
    
    while True:
        obs, reward, done, info = env.step(action)
        steps += 1
        # env.render()

        #When we are finished we will return the results of the run
        if done:
            drone_travel_distance = 0
            drone_active_time = 0
            
            drones = obs[1][0]

            for drone in drones:
                drone_travel_distance += drone.total_travel_distance
                drone_active_time += drone.total_active_time

            utilization = drone_active_time / (steps * no_trucks * no_drones)
            
            return (steps, drone_travel_distance, utilization)

        

#Number of times we want to create a different scenario and run it
no_runs = 10

#Different parameters for our run
no_trucks = 2
no_drones = 3
drone_capacity = 3
no_customers = 200
no_clusters = int(no_customers / 50)

#I want to try running no_runs scenarios with the 'next_closest' strategy, then trying the same no_runs 
#scenarios with the 'random' strategy and compare the number of steps
p = [0.9, 0.08, 0.02]

#This is the directory where our saved states are saved
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'


# for i in range(5):
#    run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy='farthest_package_first', save_state=False, drone_capacity = drone_capacity)



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




# drone_capacity_values = (1, 2, 3)
# no_customers_values = (200,)

#Here we will generate our states and save them

# for no_customers in no_customers_values:
#     pass

# results_FPF_avg = 0
# results_FPF_MPA_avg = 0
# results_MPF_avg = 0

# no_clusters = 0

# for drone_capacity in drone_capacity_values:

#     for no_customers in no_customers_values:

#         if no_customers == 50:
#             no_clusters = 2
#         else:
#             no_clusters = int(no_customers / 50)

#         strategy = 'farthest_package_first'
#         results_FPF = []

#         for i in range(no_runs):
        #     filename = path + 'saved_state' + str(i) + '.txt'
        #     steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#             results_FPF.append((steps, drone_travel_distance, utilization))

#         #Here we will average the results and save them
#         steps_FPF_avg = sum([n[0] for n in results_FPF]) / no_runs
#         drone_travel_distance_FPF_avg = sum([n[1] for n in results_FPF]) / no_runs
#         utilization_FPF_avg = sum([n[2] for n in results_FPF]) / no_runs

#         results_FPF_avg = (steps_FPF_avg, drone_travel_distance_FPF_avg, utilization_FPF_avg)

#         save_result(0, strategy, results_FPF_avg, (no_customers, drone_capacity))
        

#         strategy = 'farthest_package_first_MPA'
#         results_FPF_MPA = []
#         for i in range(no_runs):
            
#             filename = path + 'saved_state' + str(i) + '.txt'
#             steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    

#             results_FPF_MPA.append((steps, drone_travel_distance, utilization))
        
        
#         steps_FPF_MPA_avg = sum([n[0] for n in results_FPF_MPA]) / no_runs
#         drone_travel_distance_FPF_MPA_avg = sum([n[1] for n in results_FPF_MPA]) / no_runs
#         utilization_FPF_MPA_avg = sum([n[2] for n in results_FPF_MPA]) / no_runs

#         results_FPF_MPA_avg = (steps_FPF_MPA_avg, drone_travel_distance_FPF_MPA_avg, utilization_FPF_MPA_avg)

#         save_result(0, strategy, results_FPF_MPA_avg, (no_customers, drone_capacity))
        
#         strategy = 'most_packages_first'
#         results_MPF = []
#         for i in range(no_runs):
          
#             filename = path + 'saved_state' + str(i) + '.txt'
#             steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    

#             results_MPF.append((steps, drone_travel_distance, utilization))

#         steps_MPF_avg = sum([n[0] for n in results_MPF]) / no_runs
#         drone_travel_distance_MPF_avg = sum([n[1] for n in results_MPF]) / no_runs
#         utilization_MPF_avg = sum([n[2] for n in results_MPF]) / no_runs

#         results_MPF_avg = (steps_MPF_avg, drone_travel_distance_MPF_avg, utilization_MPF_avg)
        
#         save_result(0, strategy, results_MPF_avg, (no_customers, drone_capacity))

        



        









# strategy = 'farthest_package_first'

# for drone_capacity in drone_capacity_values:
#     for no_customers in no_customers_values:
        # for i in range(no_runs):
        #     no_clusters = int(no_customers / 50)

        #     steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy=strategy, save_state=True, drone_capacity = drone_capacity)
            
        #     save_result(i, strategy, (steps, drone_travel_distance, utilization))

# random.seed(42)
# strategy = 'closest_package_first'
# for drone_capacity in drone_capacity_values:
#     for no_customers in no_customers_values:
#         for i in range(no_runs):
#             no_clusters = int(no_customers / 50)
#             filename = path + 'saved_state' + str(i) + '.txt'
#             steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#             save_result(i, strategy, (steps, drone_travel_distance, utilization))

# random.seed(42)
# strategy = 'most_packages_first'
# for drone_capacity in drone_capacity_values:
#     for no_customers in no_customers_values:
#         for i in range(no_runs):
#             no_clusters = int(no_customers / 50)
#             filename = path + 'saved_state' + str(i) + '.txt'
#             steps, drone_travel_distance, utilization = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#             save_result(i, strategy, (steps, drone_travel_distance, utilization))


        
