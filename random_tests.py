import gym
import UAV_RL_env
import UAV_RL_env.envs.celes as celes
class A:
    def __init__(self):
        self.x = 2
        
class AA:
    def __init__(self):
        self.x = 99

# a = celes.Position(1, 2)
# aa = celes.Position(4, 5)
# b = [a, 'q']
# a.x = 66
# print(b[0].x)
a = A()
b = [a, 'a', 'r']
b.remove(a)
print(b)