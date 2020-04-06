import gym


    
env_dict = gym.envs.registration.registry.env_specs.copy()
for env in env_dict:
     if 'HDS' in env:
          print('Remove {} from registry'.format(env))
          del gym.envs.registration.registry.env_specs[env]

import UAV_RL_env
import numpy as np
import UAV_RL_env.envs.celes as celes
import numpy as np
import helper_functions




no_trucks = 3
no_clusters = 7
no_drones = 3
no_customers = 60
env = gym.make('HDS-v0', no_customers = no_customers, no_trucks = no_trucks, no_drones = no_drones, no_clusters=no_clusters)

env.reset()

truck_actions = []
drone_actions = []


for i in range(no_trucks):
    truck_actions.append(("go_to_next_cluster", None))
    drone_actions.append([])
# print(drone_actions)

for i in range(no_trucks):
    for _ in range(no_drones):
        drone_actions[i].append("nothing")
action = (truck_actions, drone_actions)

while True:
    obs, reward, done, info = env.step(action)
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
        break

    
# helper_functions.make_video()






