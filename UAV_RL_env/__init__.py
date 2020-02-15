from gym.envs.registration import register

register(
id='HDS-v0',
entry_point='UAV_RL_env.envs:custom_class',)