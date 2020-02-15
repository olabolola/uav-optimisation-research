import gym
from gym import error, spaces, utils
from gym.utils import seeding
import elements
import random
import numpy as np


class custom_class(gym.Env):
    

    def __init__(self, no_customers, no_trucks):
        super(custom_class, self).__init__()

        #Customer initialization
        self.no_customers = no_customers
        self.customers = []

        
        #TODO assign random positions without repitition
        
        for _ in range(self.no_customers):
            x = np.random.randint(0, 1000)
            y = np.random.randint(0, 1000)
            position = elements.Position(x, y)
            customer = elements.Customer(position, 'apt', 1)
            self.customers.append(customer)

        #Truck initialization
        self.no_trucks = no_trucks
        self.trucks = []

        for _ in range(self.no_trucks):
            position = elements.Position(0, 0)
            truck = elements.Truck(position)
            self.trucks.append(truck)

        #TODO initialize drone stuff

        print('Environment initialized')

    def step(self, action):
        print('Step successful')
    def reset(self):
        print('Environment reset')
    def render(self, mode='human', close=False):
        pass