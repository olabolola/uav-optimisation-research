import gym
import os

    
env_dict = gym.envs.registration.registry.env_specs.copy()
for env in env_dict:
     if 'HDS' in env:
        #   print('Remove {} from registry'.format(env))
          del gym.envs.registration.registry.env_specs[env]

import UAV_RL_env
import numpy as np
import UAV_RL_env.envs.celes as celes
import numpy as np
import helper_functions



def run_env(run_number, no_trucks = 3, no_clusters = 6, no_drones = 3, no_customers = 60, p = [1]):

    env = gym.make('HDS-v0', no_customers = no_customers, no_trucks = no_trucks, no_drones = no_drones, no_clusters=no_clusters, file_suffix=run_number, p = p)

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
        env.render()
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
            if 'result.txt' in os.listdir('results'):
                with open('results/result.txt', 'a') as f:
                    f.write(str(run_number) + ') Number of steps = ' + str(steps) + '\n')
            else:
                with open('results/result.txt', 'w') as f:
                    f.write(str(run_number) + ') Number of steps = ' + str(steps) + '\n')
            break

        
    # helper_functions.make_video()

#Number of times we want to create a different scenario and run it
no_runs = 1

#Different parameters for our run
no_trucks = 3
no_clusters = 7
no_drones = 3
no_customers = 60

#Package distribution
#The maximum number of packages a customer can order is the length of the list
#If the list p = [0.6, 0.2, 0.1, 0.05, 0.05], then the customer has a 0.6 chance to get 1 package, 0.2 chance to get 2 packages
#and so on. Note that sum(p) = 1.
#Probability distribution for each number of packages
p = [0.5, 0.3, 0.1, 0.05, 0.05]
for i in range(no_runs):
    run_env(i, no_trucks, no_clusters, no_drones, no_customers, p)





