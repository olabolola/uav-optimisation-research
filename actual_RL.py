import gym
import UAV_RL_env


env = gym.make('HDS-v0', no_customers = 5, no_trucks = 5)

action = [(i, i*2) for i in range(10)]
obs, reward, done, info = env.step(action)
print([obs[0][i] for i in range(5)])

