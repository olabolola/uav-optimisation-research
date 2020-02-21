import gym
import UAV_RL_env
import numpy as np
import UAV_RL_env.envs.celes as celes

no_trucks = 2
no_drones = 2
env = gym.make('HDS-v0', no_customers = 100, no_trucks = no_trucks, no_drones = no_drones)

env.reset()
# n = 10
# for _ in range(n):
#     env.step("move_trucks_randomly")
# env.render()
#env.render()
truck_actions = []
drone_actions = []

x_target_truck = 900
y_target_truck = 900
for _ in range(no_trucks):
    position = celes.Position(x_target_truck, y_target_truck)
    truck_actions.append(position)

for _ in range(no_drones):
    drone_actions.append("nothing")

action = (truck_actions, drone_actions)
env.step(action)
env.render()





