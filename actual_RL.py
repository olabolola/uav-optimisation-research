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
        truck_actions.append(("go_to_next_cluster", None))
        drone_actions.append([])

    for i in range(no_trucks):
        for _ in range(no_drones):
            drone_actions[i].append("nothing")
    action = (truck_actions, drone_actions)

    steps = 0

    while True:
        obs, reward, done, info = env.step(action)
        steps += 1
        # env.render()
        trucks = obs[0][0]
        for i, truck in enumerate(trucks):

            if not truck.is_moving:
                for j in range(no_drones):
                    drone_actions[i][j] = ('deliver_next_package')
            else:
                for j in range(no_drones):
                    drone_actions[i][j] = 'nothing'
        drone_actions1 = []
        for i in range(no_trucks):
            for j in range(no_drones):
                drone_actions1.append(drone_actions[i][j])
        action = (truck_actions, drone_actions1)

        
        
        if done:
            return steps

        

#Number of times we want to create a different scenario and run it
no_runs = 10

#Different parameters for our run
no_trucks = 5
no_clusters = 15
no_drones = 3
no_customers = 500
drone_capacity = 2

#I want to try running no_runs scenarios with the 'next_closest' strategy, then trying the same no_runs 
#scenarios with the 'random' strategy and compare the number of steps
p = [0.4, 0.4, 0.1, 0.1]

#This is the directory where our saved states are saved
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'




# for i in range(20):
#     run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy='closest_package_first', save_state=True, drone_capacity = drone_capacity)


strategy = 'next_closest'
for i in range(no_runs):

    steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy=strategy, save_state=True, drone_capacity = drone_capacity)
    save_result(i, strategy, steps)

random.seed(42)
strategy = 'closest_package_first'
for i in range(no_runs):

    filename = path + 'saved_state' + str(i) + '.txt'
    steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
    save_result(i, strategy, steps)

random.seed(42)
strategy = 'random'
for i in range(no_runs):

    filename = path + 'saved_state' + str(i) + '.txt'
    steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy=strategy, save_state=False, drone_capacity = drone_capacity)    
    save_result(i, strategy, steps)