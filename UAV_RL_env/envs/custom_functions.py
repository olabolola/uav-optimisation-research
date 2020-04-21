import gym
from gym import error, spaces, utils
from gym.utils import seeding
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
import random

try:
    from . import celes
except ModuleNotFoundError:
    import celes

#Width and height of the grid on witch our customers live
width = 100
height = 100

class custom_class(gym.Env):
    

    def __init__(self, no_customers, no_trucks, no_drones, no_clusters, file_suffix, p):

        #For making the video
        self.i = 0

        #For saving to a file
        self.file_suffix = file_suffix

        #Number of clusters
        self.no_clusters = no_clusters
        
        #no_drones is the number of drones per truck
        super(custom_class, self).__init__()

        #Warehouse initialization
        self.warehouse_position = celes.Position(width/2, height/2)
        self.warehouse = celes.Warehouse(self.warehouse_position)

        #Customer initialization
        self.no_customers = no_customers
        self.customers = []
        self.customer_positions = []

        #Probability distribution for the packages
        self.p = p
        
        

        #Truck and drone initialization
        self.no_trucks = no_trucks
        self.trucks = []
        
        self.no_drones = no_drones
        self.drones = []

        

        #For clustering
        self.centroids = None

        #Check if we have finished delivering all the packages
        self.done = False





    def step(self, actions):

        #actions is a list containing two elements; a list of truck actions and a list of drone actions
        #for each truck and drone respectively
        
        #For now trucks either move towards a certain position or just stay still
        truck_actions = actions[0]
        for truck, truck_action in zip(self.trucks, truck_actions):
            self._take_truck_action(truck, truck_action[0], truck_action[1])

        
        #Action will be a list of actions for each drone
        drone_actions = actions[1]
        for drone, drone_action in zip(self.drones, drone_actions):
            self._take_drone_action(drone, drone_action)


        #Now the observations
        #For now just make the observation be the list of trucks, drones and remaining customers
                
        truck_observation = (self.trucks,)
        drone_observation = (self.drones,)

        observation = (truck_observation, drone_observation, self.customers)

        #Info will be some debugging info
        info = []
        for truck in self.trucks:
            info.append(truck.get_truck_info())
        for drone in self.drones:
            info.append(drone.get_drone_info())
        
        #Check if we are done
        if len(self.customers) == 0:
            self.done = True

            
        #Return reward, observation, done, info
        return observation, -1, self.done, info

    def reset(self):

        #Customer initialization
        self.customers = []
        self.customer_positions = []
        
        for _ in range(self.no_customers):

            x = np.random.randint(1, width)
            y = np.random.randint(1, height)
            position = celes.Position(x, y)
            while position in self.customer_positions:
                x = np.random.randint(1, width)
                y = np.random.randint(1, height)
                position = celes.Position(x, y)
            self.customer_positions.append(position)
            customer = celes.Customer(position, 'apt')

            #Packages are distributed between customer according to the distribution p.            
            no_of_packages = np.random.choice(np.arange(1, len(self.p) + 1), p = self.p)
            for _ in range(no_of_packages):
                package = celes.Package(customer)
                customer.add_package(package)

            self.customers.append(customer)

        #Truck and drone initialization
        self.trucks = []
        self.drones = []

        

        for i in range(self.no_trucks):

            x = self.warehouse_position.x
            y = self.warehouse_position.y
            position = celes.Position(x, y)
            
            truck = celes.Truck(position, truck_id=i, total_no_drones = self.no_drones)

            for _ in range(self.no_drones):
                drone = celes.Drone(celes.Position(x, y))
                drone.home_truck = truck
                truck.load_drone(drone)
                self.drones.append(drone)
                
            self.trucks.append(truck)
        
        
        #cluster customers, and distribute packages accordingly
        self.warehouse.cluster_and_colour(self.customers, self.trucks, self.no_clusters)


        #Here we save the state of our system
        with open('saved_states/saved_state' + str(self.file_suffix) + '.txt', 'w') as f:
            f.write('Height: ' + str(height))
            f.write('\nWidth: ' + str(width))
            f.write('\nNumber of customers: ' + str(self.no_customers))
            f.write('\nNumber of trucks: ' + str(self.no_trucks))
            f.write('\nNumber of drones per truck: ' + str(self.no_drones))
            f.write('\nCustomer positions and packages:\n')
            for customer in self.customers:
                f.write(str(customer.position) + ', ' + str(customer.no_of_packages) + '\n')


    def render(self, mode='human', close=False):
        #TODO make this more sophisticated with animations or something
        
        customer_x = []
        customer_y = []

        for customer in self.customers:
            customer_x.append(customer.position.x)
            customer_y.append(customer.position.y)
        
        

        truck_x =[]
        truck_y =[]
        for truck in self.trucks:
            truck_x.append(truck.position.x)
            truck_y.append(truck.position.y)
        
        
        drone_x =[]
        drone_y =[]
        
        for drone in self.drones:
            drone_x.append(drone.position.x)
            drone_y.append(drone.position.y)

        

        fig = plt.figure()
        ax1 = fig.add_subplot(111)

        
        for customer in self.customers:
            ax1.scatter(customer.position.x, customer.position.y, c = customer.colour, alpha = 0.5, label="customer")
        drone_plot = ax1.scatter(drone_x, drone_y, c = 'b', label = 'drone', marker = ".")
        truck_plot = ax1.scatter(truck_x, truck_y, c = 'g', label = 'truck', marker = ",")


        
       
        plt.legend((drone_plot, truck_plot), ("drone", "truck"), loc = "lower left")
        plt.xlim(-10, width)
        plt.ylim(-10, height)
        
        plt.show()

    






    #TODO do we need this? Or will we take care of everything in step
    def _take_drone_action(self, drone, action):
        # Actions for the drone policy:
            # a. Go back to Home truck --> action = "return_to_home_truck"
            # b. Deliver next package --> action = "deliver_next_package"
            # c. Failsafe mode --> action = "failsafe_mode"
        #We could probably use a simpler encoding scheme for the drone actions
        #but we'll keep it the way it is now for better readability

        drone.charge()
        drone.steadystate_consumption()
        if action == 'nothing':
            pass
        elif action == "go_to_position":
            drone.go_to_position(action[1])
        elif action == "return_to_home_truck":
            drone.go_to_home_truck()
        elif action == "deliver_next_package":
            if not drone.home_truck.is_moving:
                drone.deliver_next_package(self.customers)
        elif action == "failsafe_mode":
            #TODO Do something???
            pass


    def _take_truck_action(self, truck, action, position):
        #For now action is a 2-tuple that tells the truck where to go to
        if action == 'nothing':
            pass
        elif action == "go_to_next_cluster":
            truck.go_to_next_cluster()
    

    
    