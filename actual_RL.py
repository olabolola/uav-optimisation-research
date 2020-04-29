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
no_runs = 20

#Different parameters for our run
no_trucks = 3
no_clusters = 7
no_drones = 3
no_customers = 200
drone_capacity = 3


#Package distribution
#The maximum number of packages a customer can order is the length of the list
#If the list p = [0.6, 0.2, 0.1, 0.05, 0.05], then the customer has a 0.6 chance to get 1 package, 0.2 chance to get 2 packages
#and so on. Note that sum(p) = 1.
#Probability distribution for each number of packages


#I want to try running a 20 scenarios with the 'next_closest strategy, then trying the same 20 
#scenarios with the 'random' strategy and comapring the number of steps
p = [0.5, 0.4, 0.05, 0.05]

#This is teh directory where our saved states are saved
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'

#First thing to show amjed and hind
#Do this 3 times
# for i in range(3):
#     run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy='next_closest', save_state=True, drone_capacity = drone_capacity)

#Second thing to show amjed and hind
#SHOW THEM THE FORMAT
#Loading from a file
# filename = path + 'saved_state0.txt'
# run_env(0, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy='next_closest', save_state=False, drone_capacity = drone_capacity)





#Last thing to show amjed and hind
#Note that you must delete the previous result file otherwise we will just append to it
for i in range(no_runs):

    steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=False, strategy='next_closest', save_state=True, drone_capacity = drone_capacity)

    if 'result_next_closest.txt' in os.listdir('results'):
        with open('results/result_next_closest.txt', 'a') as f:
            f.write(str(i) + ') Number of steps = ' + str(steps) + '\n')
    else:
        with open('results/result_next_closest.txt', 'w') as f:
            f.write(str(i) + ') Number of steps = ' + str(steps) + '\n')

for i in range(no_runs):

    filename = path + 'saved_state' + str(i) + '.txt'
    steps = run_env(i, no_trucks, no_clusters, no_drones, no_customers, p, load=True, load_file=filename, strategy='random', save_state=False, drone_capacity = drone_capacity)
    
    if 'result_random.txt' in os.listdir('results'):
        with open('results/result_random.txt', 'a') as f:
            f.write(str(i) + ') Number of steps = ' + str(steps) + '\n')
    else:
        with open('results/result_random.txt', 'w') as f:
            f.write(str(i) + ') Number of steps = ' + str(steps) + '\n')


