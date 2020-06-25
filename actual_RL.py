import gym

    
env_dict = gym.envs.registration.registry.env_specs.copy()
for env in env_dict:
     if 'HDS' in env:
        #   print('Remove {} from registry'.format(env))
          del gym.envs.registration.registry.env_specs[env]


import os
import UAV_RL_env
import numpy as np
import UAV_RL_env.envs.celes as celes
import numpy as np
import random
random.seed(42)


#This function saves the results of a run in a file
def save_result(i, strategy, steps):

    if i == 0:
        with open('results/result_' + strategy + '.txt', 'w') as f:
            f.write(str(i) + ') Number of steps = ' + str(steps) + '\n')
    else:
        with open('results/result_' + strategy + '.txt', 'a') as f:
            f.write(str(i) + ') Number of steps = ' + str(steps) + '\n')


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
        env.render()

        if done:
            return steps

        

#Number of times we want to create a different scenario and run it
no_runs = 10

#Different parameters for our run
no_trucks = 2
no_drones = 3
no_customers = 20 #We will test no_customers = 50, 100, 200, 500
# no_clusters = int(no_customers / 50)
no_clusters = 4
drone_capacity = 3 #We will test drone_capacity = 1, 2, 3

#I want to try running no_runs scenarios with the 'next_closest' strategy, then trying the same no_runs 
#scenarios with the 'random' strategy and compare the number of steps
p = [0.9, 0.08, 0.02]

#This is the directory where our saved states are saved
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'


for i in range(5):
    run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy='next_closest', save_state=True, drone_capacity = drone_capacity)


# strategy = 'next_closest'
# for i in range(no_runs):

#     steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy=strategy, save_state=True, drone_capacity = drone_capacity)
#     save_result(i, strategy, steps)

# random.seed(42)
# strategy = 'closest_package_first'
# for i in range(no_runs):

#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, steps)

# random.seed(42)
# strategy = 'random'
# for i in range(no_runs):

#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, steps)

# random.seed(42)
# strategy = 'multiple_packages'
# for i in range(no_runs):

#     filename = path + 'saved_state' + str(i) + '.txt'
#     steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
#     save_result(i, strategy, steps)