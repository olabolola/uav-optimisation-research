import gym
for env in list(gym.envs.registry.env_specs):
     if 'HDS' in env:
          print('Remove {} from registry'.format(env))
          del gym.envs.registry.env_specs[env]
import UAV_RL_env

env = gym.make('HDS-v0')
env.reset()

