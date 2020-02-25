import gym
import UAV_RL_env
import numpy as np
import UAV_RL_env.envs.celes as celes
import numpy as np
import helper_functions

no_trucks = 1
no_drones = 5
env = gym.make('HDS-v0', no_customers = 30, no_trucks = no_trucks, no_drones = no_drones)

env.reset()

truck_actions = []
drone_actions = []


for i in range(no_trucks):
    truck_actions.append(("nothing", None))

for _ in range(no_drones * no_trucks):
    drone_actions.append("go_to_closest_truck")

for i in range(len(drone_actions)):
    drone_actions[i] = ("deliver_next_package", celes.Position(2500, 2500))

action = (truck_actions, drone_actions)


action = (truck_actions, drone_actions)
for _ in range(200):
    
    a, b, c, info = env.step(action)
    
    env.render()

# helper_functions.make_video()






