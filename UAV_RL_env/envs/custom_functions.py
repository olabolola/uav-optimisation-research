import gym
from gym import error, spaces, utils
from gym.utils import seeding
import random
import numpy as np
import matplotlib.pyplot as plt
import pandas as pd
from sklearn.cluster import KMeans
try:
    from . import celes
except ModuleNotFoundError:
    import celes

#Width and height of the grid on witch our customers live
width = 100
height = 100

class custom_class(gym.Env):
    

    def __init__(self, no_customers, no_trucks, no_drones):
        #For making the video
        self.i = 0
        
        #no_drones is the number of drones per truck
        super(custom_class, self).__init__()

        #For now say we have two charging stations at random positions on "map"
        self.charging_stations = []
        

        


        #Customer initialization
        self.no_customers = no_customers
        self.customers = []
        self.customer_positions = []
        
        

        #Truck and drone initialization
        self.no_trucks = no_trucks
        self.trucks = []
        self.truck_positions = []
        
        self.no_drones = no_drones
        self.drones = []

        self.packages = []
        

        
        
        self.centroids = None




    def step(self, actions):
        
        
        #TODO incorporate truck actions into this
        #For now truck actions will just be order to move the truck in a certain direction or to launch a drone
        truck_actions = actions[0]
        for truck, truck_action in zip(self.trucks, truck_actions):
            self._take_truck_action(truck, truck_action[0], truck_action[1])

        
        #Action will be a list of actions for each drone
        drone_actions = actions[1]
        # print(drone_actions[0])
        for drone, drone_action in zip(self.drones, drone_actions):
            self._take_drone_action(drone, drone_action)

        #Observation for a single drone is:
            # a. Closest charging station.
            # b. Battery life
            # c. Number of packages + (customer locations)
            # d. Home truck

        #TODO idea: do we want to do all these observations in a single for loop?
        #for index, drone in enumerate(self.drones): 
            #And then get closest trucks, closest charging stations, ...

        #Closest trucks observation for each drone



        
        #Closest charging stations observation for each drone

        #Find closest charging stations within range of reach for each drone
        #TODO maybe later on we need to find a list of charging stations (Just keep it in mind)
        
        #closest-charging_stations is a 2D array where each row corresponds to one drone
        #In each row we list the charging stations within that drone's range of reach
        closest_charging_stations = []
        #closest_charging_station will a 1D array with the closest charging station for each drone
        closest_charging_station = []
        #Since we have no_drones per truck
        for _ in range(self.no_drones*self.no_trucks):
            closest_charging_stations.append([])
            closest_charging_station.append(self.charging_stations[0])

        #Enumerate lets us loop over the indices and the values at the same time
        for index, drone in enumerate(self.drones):
            min_distance = float('inf')

            for charging_station in self.charging_stations:
                distance = celes.get_euclidean_distance(drone.position, charging_station.position)
                RoR = drone.get_range_of_reach() 
                if RoR >= distance:
                    closest_charging_stations[index].append(charging_station)
                    if distance < min_distance:
                        min_distance = distance
                        closest_charging_station[index] = charging_station


        #Battery life observation for each drone

        battery_lives = []
        for drone in self.drones:
            battery_lives.append(drone.battery)


        #TODO Number of packages observation

        #Home truck observation for each drone
        home_trucks = []
        
        for drone in self.drones:
            home_trucks.append(drone.home_truck)
                
        drone_positions = []
        for drone in self.drones:
            drone_positions.append(drone.position)

        truck_positions = []
        for truck in self.trucks:
            truck_positions.append(truck.position)
        
        truck_observation = (truck_positions, self.centroids)
        drone_observation = (drone_positions, closest_charging_stations, battery_lives, home_trucks)
        observation = (truck_observation, drone_observation)
        #Info will be some debugging info
        info = []
        for truck in self.trucks:
            info.append(truck.get_truck_info())
        for drone in self.drones:
            info.append(drone.get_drone_info())
        

        #Return reward, observation, done, info
        return observation, -1, False, info

    #TODO make this consistent wit everything else. Mainly the step function.
    def reset(self):

        #For now say we have two charging stations at random positions on "map"
        self.charging_stations = []
        for _ in range(2):
            x = np.random.randint(0, width)
            y = np.random.randint(0, height)
            position = celes.Position(x, y)
            charging_station = celes.charging_station(position)
            self.charging_stations.append(charging_station)

        


        #Customer initialization
        self.customers = []
        self.customer_positions = []
        
        #TODO figure out if customers can have multiple packages delivered to them
        self.packages = []
        for _ in range(self.no_customers):

            x = np.random.randint(1, width)
            y = np.random.randint(1, height)
            position = celes.Position(x, y)
            while position in self.customer_positions:
                x = np.random.randint(1, width)
                y = np.random.randint(1, height)
                position = celes.Position(x, y)
            self.customer_positions.append(position)
            customer = celes.Customer(position, 'apt', 1)
            package = celes.Package(customer)
            customer.add_package(package)
            self.packages.append(package)
            self.customers.append(customer)

        #Truck and drone initialization
        self.trucks = []
        self.truck_positions = []
        
        self.drones = []

        

        for _ in range(self.no_trucks):
            #For now all trucks and drones start at position (10, 10). We will need to change this
            #in the future when we introduce varying warehouse position, and multiple warehouses
            x = np.random.randint(1, width)
            y = np.random.randint(1, height)
            position = celes.Position(x, y)
            self.truck_positions.append(position)
            
            truck = celes.Truck(position, truck_speed=np.random.randint(5, 60))

            for _ in range(self.no_drones):
                drone = celes.Drone(celes.Position(10, 10))
                truck.load_drone(drone)
                self.drones.append(drone)
                
            self.trucks.append(truck)
            #Extend our list of drones by the drones we just added to 'truck'
        
        
        #TODO do this in the warehouse
        #cluster customers, and distribute packages accordingly
        customer_x = []
        customer_y = []

        for customer in self.customers:
            customer_x.append(customer.position.x)
            customer_y.append(customer.position.y)
        
        df = pd.DataFrame({
            'x' : customer_x,
            'y' : customer_y
        })

        kmeans = KMeans(n_clusters = self.no_trucks)
        cluster_labels = kmeans.fit_predict(df)
        
        self.centroids = kmeans.cluster_centers_

        colours = {
            0 : 'c',
            1 : 'm',
            2 : 'y',
            3 : 'k'
        }
        

        for i, customer in zip(cluster_labels, self.customers):
            customer.colour = colours[i]
            # print(i)
            for package in customer.packages:
                self.trucks[i].load_package(package)
        

        for truck in self.trucks:
            truck.assign_packages_to_drones()
        


    def render(self, mode='human', close=False):
        #TODO make this more sophisticated with animations or something
        
        customer_x = []
        customer_y = []

        for customer in self.customers:
            customer_x.append(customer.position.x)
            customer_y.append(customer.position.y)
        
        

        truck_x =[]
        truck_y =[]
        for position in self.truck_positions:
            truck_x.append(position.x)
            truck_y.append(position.y)
        
        
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


        
       
        #If we just want to show the graph instead of saving it, uncomment this
        plt.legend((drone_plot, truck_plot), ("drone", "truck"), loc = "lower left")
        plt.xlim(-10, width)
        plt.ylim(-10, height)
        
        plt.show()

        #This here is to save the plots we make, so we can make them
        #into a video later
        # plt.savefig(f'images/hind{self.i}.png')
        # self.i += 1
        # plt.clf()
    






    #TODO do we need this? Or will we take care of everything in step
    def _take_drone_action(self, drone, action):
        # Actions for the drone policy:
            # a. Go back to Home truck --> action = "return_to_home_truck"
            # b. Go to closest truck --> action = "go_to_closest_truck"
            # c. Deliver next package --> action = "deliver_next_package"
            # d. Go to charging station --> action = "go_to_charging_station"
            # e. Failsafe mode --> action = "failsafe_mode"
        #We could probably use a simpler encoding scheme for the drone actions
        #but we'll keep it the way it is now for better readability


        if action[0] == "go_to_position":
            drone.go_to_position(action[1])

        elif action[0] == "return_to_home_truck":
            drone.go_to_home_truck()
        elif action[0] == "go_to_closest_truck":

            #We will find the closest truck in the function
            drone.go_to_closest_truck(self.trucks)
        elif action[0] == "deliver_next_package":
            drone.deliver_next_package(self.customers)
        elif action[0] == "go_to_charging_station":
            pass
            #TODO fix this make it work
            # if celes.get_euclidean_distance(drone.position, )
            # drone.position = drone.get_point_on_line(drone.position, drone.closest_charging_station.position)
        elif action == "failsafe_mode":
            #TODO Do something???
            pass

    #TODO make this actually make sense...
    #Make sure truck don't "fall of the map"
    def move_trucks_randomly(self):
        for truck in self.trucks:
            truck.position.x += np.random.randint(-10, 40)
            truck.position.y += np.random.randint(-10, 40)

    def _take_truck_action(self, truck, action, position):
        # print(position)
        #For now action is a 2-tuple that tells the truck where to go to
        if action == "move_towards_position":
            truck.move_towards_position(position)

    def move_drones_randomly(self):
        for drone in self.drones:
            drone.position.x += np.random.randint(-10, 40)
            drone.position.y += np.random.randint(-10, 40)
    
    