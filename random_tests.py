import UAV_RL_env.envs.celes as celes

a = [1, 2, 1, 1, 4, 5, 3]

pos1 = celes.Position(1, 2)
pos2 = celes.Position(2, 2)

print(pos1 != pos2)
