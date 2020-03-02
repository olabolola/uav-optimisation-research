import gym



def trucks_arrived(trucks, centroids):
    #Returns true if all trucks have reached the centroids
    #Returns false otherwise
    pass

    
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

no_trucks = 4
no_drones = 5
no_customers = 100
env = gym.make('HDS-v0', no_customers = no_customers, no_trucks = no_trucks, no_drones = no_drones)

env.reset()

truck_actions = []
drone_actions = []


for i in range(no_trucks):
    truck_actions.append(("nothing", None))


for _ in range(no_drones*no_trucks):
    drone_actions.append(("nothing", None))

action = (truck_actions, drone_actions)

obs, b, c, d = env.step(action)
centroids = obs[0][1]

for i, pos in enumerate(centroids):
    x = pos[0]
    y = pos[1]
    print(x, y)
    position = celes.Position(x, y)
    truck_actions[i] = ("move_towards_position", position)
    
action = (truck_actions, drone_actions)

env.render()
for _ in range(100):
    
    a, b, c, info = env.step(action)
env.render()

for i in range(no_trucks*no_drones):
    drone_actions[i] = ("deliver_next_package", None)

action = (truck_actions, drone_actions)

for _ in range(100):
    obs, q, w, e = env.step(action)
    # print(obs[1][0])
    env.render()
# helper_functions.make_video()






