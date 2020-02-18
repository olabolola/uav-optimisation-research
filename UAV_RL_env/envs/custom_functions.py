import gym
from gym import error, spaces, utils
from gym.utils import seeding
import random
import numpy as np

try:
    from . import celes
except ModuleNotFoundError:
    import celes

class custom_class(gym.Env):
    

    def __init__(self, no_customers, no_trucks):
        super(custom_class, self).__init__()

        #Customer initialization
        self.no_customers = no_customers
        self.customers = []
        self.customer_positions = []
        
        #TODO assign random positions without repitition
        
        for _ in range(self.no_customers):
            x = np.random.randint(0, 1000)
            y = np.random.randint(0, 1000)
            position = celes.Position(x, y)
            self.customer_positions.append(position)
            customer = celes.Customer(position, 'apt', 1)
            self.customers.append(customer)

        #Truck initialization
        self.no_trucks = no_trucks
        self.trucks = []
        

        for _ in range(self.no_trucks):
            position = celes.Position(0, 0)
            truck = celes.Truck(position)
            self.trucks.append(truck)

        #TODO initialize drone stuff

        #For now I just want to try some simple RL with trucks only


        print('Environment initialized')

    def step(self, action):
        #Right now just work with truck only.
        #action is a list of 2-tuples indicating the change in x and y of each truck
        for i in range(self.no_trucks):
            self.trucks[i].position.x += action[i][0]
            self.trucks[i].position.y += action[i][1]

        #What does our observation look like?
        #For now observation will be a list containing the positions of all the trucks

        truck_positions = []
        for i in self.trucks:
            position = celes.Position(i.position.x, i.position.y)
            truck_positions.append(position)

        observation = (truck_positions, self.customer_positions)
        

        
        

        #Return reward, observation, done, info
        return observation, -1, False, {}
    def reset(self):
        #Set everything to random positions again

        for _ in range(self.no_customers):
            x = np.random.randint(0, 1000)
            y = np.random.randint(0, 1000)
            position = celes.Position(x, y)
            customer = celes.Customer(position, 'apt', 1)
            self.customers.append(customer)
        
        for _ in range(self.no_trucks):
            position = celes.Position(0, 0)
            truck = celes.Truck(position)
            self.trucks.append(truck)

        

    def render(self, mode='human', close=False):
        pass


    #TODO do we need this? Or will we take care of everything in step
    def _take_action(self, action):
        pass
