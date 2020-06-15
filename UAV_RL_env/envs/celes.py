from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import random



class Drone:

    
    def __init__(self, position, home_truck = None, cost =  0.25, drone_speed = 2, battery = 100, drone_id = None, capacity = 2):
        
        self.capacity = capacity

        self.position = position

        #Drone cost is defined as the amount of battery consumed per unit of drone_speed distance crossed
        self.cost = cost

        #Drone speed is given in units_of_distance/s
        self.drone_speed = drone_speed

        #Battery is just a number representing the percentage of battery remaining
        self.battery = 100
        #charge_increase is how much charge the battery increases every time step when it is charging
        self.charge_increase = 5
        self.drone_id = drone_id

        #Home truck is the truck the drone is initially loaded onto (And cannot change)
        self.home_truck = home_truck
       
       
        #The packages list contains the packages the drone is carrying RIGHT NOW
        self.packages = []
        self.no_packages = 0
               
        #This is to check if drone is on its way somewhere
        self.en_route = False
        self.on_truck = True


    #So far we haven't used this function at all
    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    #When a drone returns from a trip delivering packages, we call this function to load additional packages
    def load_package(self):
        self.home_truck.load_drone_package(self)

    #We haven't used this function so far
    def hand_package_to_customer(self, package):
        pass


    
    #After a drone has delivered all its packages, we call this function which makes the drone return to its home truck
    def go_to_home_truck(self):

        distance = get_euclidean_distance(self.position, self.home_truck.position)

        #First check we don't overshoot. If we don't overshoot then just move the full distance (according to speed)
        if distance <= self.drone_speed:
            self.consume_battery()
            if not self.on_truck:
                self.home_truck.load_drone(self)
        else:            
            self.en_route = True
            self.on_truck = False
            self.consume_battery()
            self.position.get_point_on_line(self.home_truck.position, self.drone_speed)


    #We use this function to move towards a certain position
    #This function returns True is we reach the position and false otherwise
    def go_to_position(self, position):
        distance = get_euclidean_distance(self.position, position)
        self.en_route = True
        self.on_truck = False
        if distance < self.drone_speed:
            self.consume_battery()
            self.position.x = position.x
            self.position.y = position.y
            self.en_route = False
            return True
        else:
            self.position.get_point_on_line(position, self.drone_speed)
            self.consume_battery()
            return False
        return False   


    #We use this function to consume the battery whenever we move
    def consume_battery(self):
        if self.battery - self.cost < 0:
            self.battery = 0
        else:
            self.battery -= self.cost  
    
    #Our drone has a constant steady state consumption whether its moving or not
    def steadystate_consumption(self):
        if self.battery - self.cost/4 < 0:
            self.battery = 0
        else:
            self.battery -= self.cost/4 


        
    #We use this function to calculate how far we can travel with our current battery charge
    def get_range_of_reach(self):

        #What is the maximum distance our drone can travel with its current battery level
        # return self.battery / (self.cost * self.drone_speed)
        return float('inf')

    #This function is used to move towards the next customer in the drone's list 
    #If we have no packages left the drone will return to the home truck
    def deliver_next_package(self, customers):
        
        #First check if we have any packages to deliver. If that is the case check if we can reach
        #the customers using our current charge. If so then deliver.
        if self.no_packages > 0:
            
            customer_position = self.packages[0].customer.position
            

            arrived = False

            #If the drone is on the truck we leave the trucks
            if self.on_truck:
                self.home_truck.no_drones -= 1

            #Move towards the customer position
            arrived = self.go_to_position(customer_position)

            #This allows us to deliver all the packages at once if we arrive at a certain customer
            if arrived:
                for package in self.packages:
                    if package.customer.position.x == customer_position.x and package.customer.position.y == customer_position.y:
                        self.packages.remove(package)
                        self.no_packages -= 1
                        package.customer.no_of_packages -= 1
                        if package.customer.no_of_packages == 0:
                            customers.remove(package.customer)
                        
        #If we have no more packages, go back to the home truck
        else:

            self.go_to_home_truck()
            if not self.en_route:
                if self.home_truck.no_packages > 0:
                    self.load_package()

    #This function increases the charge of the battery while the drone is on the truck
    def charge(self):
        if self.on_truck:
            if self.battery + self.charge_increase < 100:
                self.battery += self.charge_increase
            else:
                self.battery = 100

class Package:

    def __init__(self, customer, mass = 10, height = 5, width = 5):
        self.customer = customer
        self.mass = mass
        self.height = height
        self.width = width


class Position:

    def __init__(self, x, y):
        #Suppose the location of a truck, drone or house is defined by (x, y)
        self.x = x
        self.y = y

    def get_position_info(self):
        d = {'x' : self.x, 'y': self.y}
        return d

    #TODO find out exactly what __str__ and __repr__ do
    #and find a way to print a list of position objects (if possible)

    def __str__(self):
        return str(self.x) + ", " + str(self.y)  

    def __repr__(self):
        return str(self)

    
    #We are going to define a custom subtraction operation in order to get a point d distance away from 
    #position1 on the straight line between position1 and position2

    def __sub__(self, position2):
        return Position(self.x - position2.x, self.y - position2.y)

    #This function convert any point/vector into a unit vector
    def _normalize_position(self):
        #TODO should we use math.sqrt() or ** 0.5?
        norm = (self.x ** 2 + self.y ** 2) ** 0.5
        self.x /= norm
        self.y /= norm


    #In order to get a position d distance away from position1 on the straight line between position
        #one and position2 we use this method https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
        # 1) Subtract the two positions (using the ordinary method) v = position2 - position1
        # 2) Normalize v --> u
        # 3) new position = position1 + du


    def get_point_on_line(self, position2, distance):
        #TODO check for division by zero
        v = position2 - self

        v._normalize_position()
        self.x = self.x + distance * v.x
        self.y = self.y + distance * v.y


    


class Customer:

    def __init__(self, position, residence_type, no_of_packages = 0):
        #Location will be a class of type position (defined by x and y)
        self.position = position
        #residence_type will just be a string ("apt" or "house")
        self.residence_type = residence_type
        self.no_of_packages = no_of_packages
        self.packages = []
        self.colour = None

        

    def get_customer_info(self):
        d = self.position.get_position_info()
        d['residence_type'] = self.residence_type
        d['no_of_packages'] = self.no_of_packages
        return d  

    def add_package(self, package):
        self.no_of_packages += 1
        self.packages.append(package)      
    
class Truck:
    
    no_of_drones = 0
    #We might just want to inherit from a superclass...
    def __init__(self, position, cost = 5, truck_speed = 5, truck_id = None, total_no_drones = 0, strategy = 'next_closest'):
        

        #Strategy parameters
        self.strategy = strategy


        self.cost = cost
        self.truck_speed = truck_speed
        self.position = position

        #Each truck has a number of drones.
        #These two attributes pertain to the drones CURRENTLY ON THE TRUCK
        self.drones = []
        self.no_drones = 0

        #This attribute pertains to the drones wherever they may be
        self.total_no_drones = total_no_drones

        self.truck_id = truck_id

        
        self.packages = {}
        self.no_packages = 0


        #List of cluster centroids truck must deliver to
        self.cluster_centroids = []

        self.is_moving = False

        #This is the cluster the truck is currently delivering from
        self.current_cluster = None
    
    #In this function we load the packages onto the truck after we perform the clustering
    def load_package(self, package, cluster):
        if cluster not in self.packages:
            self.packages[cluster] = []
        self.packages[cluster].append(package)
        self.no_packages += 1

    #Here we sort the packages in each cluster according to the distance from the cluster
    def sort_packages(self):
        for cluster in self.packages.keys():
            cluster_position = Position(cluster[0], cluster[1])
            self.packages[cluster] = sorted(self.packages[cluster], key = lambda x : get_euclidean_distance(x.customer.position, cluster_position), reverse=True)
        
    def load_drone_package(self, drone):

        #TODO Make this work
        #This is to make sure drones aren't assigned packages such that it's impossible to deliver them with a full charge
        total_travel_distance = 0
        
        no_packages_to_load = drone.capacity
        if self.strategy == 'next_closest':

            for _ in range(no_packages_to_load):

                if drone.no_packages == 0:
                    if len(self.packages[self.current_cluster]) > 0:
                        package_to_deliver = self.packages[self.current_cluster][0]
                        total_travel_distance += get_euclidean_distance(self.position, package_to_deliver.customer.position)

                        #Check if it is possible to deliver the package with the current charge
                        #If it is possible then load the package
                        if total_travel_distance <= drone.get_range_of_reach():
                            self.packages[self.current_cluster].remove(package_to_deliver)
                            self.no_packages -= 1

                            drone.packages.append(package_to_deliver)
                            drone.no_packages += 1
                        else:
                            break

                elif len(self.packages[self.current_cluster]) > 0:
                    package_to_deliver = self.packages[self.current_cluster][-1]
                    min_distance = get_euclidean_distance(package_to_deliver.customer.position, drone.packages[-1].customer.position)
                    for package in self.packages[self.current_cluster]:
                        if get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position) < min_distance:
                            min_distance = get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position)
                            package_to_deliver = package
                    
                    #Add the distance between the last package we have so far and the package we want to add to the list
                    total_travel_distance += get_euclidean_distance(drone.packages[-1].customer.position, package_to_deliver.customer.position)
                    
                    #Check if it is possible to deliver the package with the current charge
                    #If it is possible then load the package 
                    if total_travel_distance <= drone.get_range_of_reach():
                        self.packages[self.current_cluster].remove(package_to_deliver)
                        self.no_packages -= 1

                        drone.packages.append(package_to_deliver)
                        drone.no_packages += 1
                    else:
                        break
        #Random strategy mean just select no_packages_to_load random packages from the cluster
        #and load then onto the drone
        elif self.strategy == 'random':
            for _ in range(no_packages_to_load):
                if len(self.packages[self.current_cluster]) > 0:
                    # package_to_deliver = self.packages[self.current_cluster][0]
                    package_to_deliver = random.choice(self.packages[self.current_cluster])
                    
                    #If it is this first package then we want to add the distance from the truck
                    if len(drone.packages) == 0:
                        total_travel_distance += get_euclidean_distance(self.position, package_to_deliver.customer.position)
                    else:
                        #If it is not the first package we add the distance from the previous package
                        total_travel_distance += get_euclidean_distance(drone.packages[-1].customer.position, package_to_deliver.customer.position)

                    #Check if we are able to deliver the packages with the current drone charge
                    if total_travel_distance <= drone.get_range_of_reach():
                        self.packages[self.current_cluster].remove(package_to_deliver)
                        self.no_packages -= 1

                        drone.packages.append(package_to_deliver)
                        drone.no_packages += 1
                    else:
                        break
        elif self.strategy == 'closest_package_first':
            for _ in range(no_packages_to_load):

                if drone.no_packages == 0:
                    if len(self.packages[self.current_cluster]) > 0:
                        package_to_deliver = self.packages[self.current_cluster][-1]
                        total_travel_distance += get_euclidean_distance(self.position, package_to_deliver.customer.position)

                        #Check if it is possible to deliver the package with the current charge
                        #If it is possible then load the package
                        if total_travel_distance <= drone.get_range_of_reach():
                            self.packages[self.current_cluster].remove(package_to_deliver)
                            self.no_packages -= 1

                            drone.packages.append(package_to_deliver)
                            drone.no_packages += 1
                        else:
                            break

                elif len(self.packages[self.current_cluster]) > 0:
                    package_to_deliver = self.packages[self.current_cluster][-1]
                    min_distance = get_euclidean_distance(package_to_deliver.customer.position, drone.packages[-1].customer.position)
                    for package in self.packages[self.current_cluster]:
                        if get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position) < min_distance:
                            min_distance = get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position)
                            package_to_deliver = package
                    
                    #Add the distance between the last package we have so far and the package we want to add to the list
                    total_travel_distance += get_euclidean_distance(drone.packages[-1].customer.position, package_to_deliver.customer.position)
                    
                    #Check if it is possible to deliver the package with the current charge
                    #If it is possible then load the package 
                    if total_travel_distance <= drone.get_range_of_reach():
                        self.packages[self.current_cluster].remove(package_to_deliver)
                        self.no_packages -= 1

                        drone.packages.append(package_to_deliver)
                        drone.no_packages += 1
                    else:
                        break


    def add_cluster_centroid(self, pos):
        self.cluster_centroids.append(tuple(pos))
    

    def get_truck_info(self):
        d = self.position.get_position_info()
        d['cost'] = self.cost
        d['speed'] = self.truck_speed
        d['no_of_drones'] = self.no_of_drones
        return d


    def move_towards_position(self, position):
        self.is_moving = True
        #This whole complicated function is to ensure the truck moves like it's in Manhattan
        if get_manhattan_distance(self.position, position) <= self.truck_speed:
            self.position.x = position.x
            self.position.y = position.y
        else:
            units_to_move = self.truck_speed
            x_difference = position.x - self.position.x
            y_difference = position.y - self.position.y
            if abs(x_difference) > units_to_move:
                if x_difference > 0:
                    self.position.x += units_to_move
                else:
                    self.position.x -= units_to_move

            elif abs(y_difference) > units_to_move:
                if y_difference > 0:
                    self.position.y += units_to_move
                else:
                    self.position.y -= units_to_move
            else:
                #For now we just start with the x
                #Might want to do it in a smarter manner later
                units_to_move -= abs(x_difference)
                self.position.x = position.x
                if y_difference < 0:
                    self.position.y -= units_to_move
                else:
                    self.position.y += units_to_move

        for drone in self.drones:
            if drone.on_truck:
                drone.position.x = self.position.x
                drone.position.y = self.position.y

        if self.position.x == position.x and self.position.y == position.y:
            self.is_moving = False

            return True
        else:
            return False

        

    def go_to_next_cluster(self):

        if len(self.cluster_centroids) > 0 and self.cluster_finished():
            self.current_cluster = self.cluster_centroids[-1]
            cluster_position = Position(self.current_cluster[0], self.current_cluster[1])
            arrived = self.move_towards_position(cluster_position)

            if arrived:
                self.cluster_centroids.pop()

        else:
            cluster_position = Position(self.current_cluster[0], self.current_cluster[1])
            self.move_towards_position(cluster_position)
            

            


    def cluster_finished(self):
        #Return true if we have delivered all packages in cluster
        if self.total_no_drones != self.no_drones:            
            return False
        
        if self.current_cluster != None and len(self.packages[self.current_cluster]) != 0:
            return False

        #Make sure none of the drones are carrying packages
        drones_delivered = True
        for drone in self.drones:
            if drone.no_packages != 0:
                drones_delivered = False

        return drones_delivered

            
    def load_drone(self, drone):

        drone.position.x = self.position.x
        drone.position.y = self.position.y

        self.drones.append(drone)
        self.no_drones += 1

        drone.en_route = False
        drone.on_truck = True
        
    
class Warehouse:
    def __init__(self, position):
        self.position = position
    
    def cluster_and_colour(self, customers, trucks, no_clusters):
        customer_x = []
        customer_y = []

        for customer in customers:
            customer_x.append(customer.position.x)
            customer_y.append(customer.position.y)
        
        df = pd.DataFrame({
            'x' : customer_x,
            'y' : customer_y
        })

        kmeans = KMeans(n_clusters = no_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(df)
        
        centroids = kmeans.cluster_centers_

        colours = {
            0 : '#CD5C5C',
            1 : '#FFC0CB',
            2 : '#FFA07A',
            3 : '#FFD700',
            4 : '#E6E6FA',
            5 : '#ADFF2F',
            6 : '#00FFFF',
            7 : '#FFF8DC',
            8 : '#DCDCDC',
            9 : '#8B0000',
            10 : '#DB7093',
            11 : '#FFA500',
            12 : '#BDB76B',
            13 : '#7B68EE',
            14 : '#008080',
            15 : '#191970',
            16 : '#800000',
            17 : '#FFE4E1',
            18 : '#000000'
        }
        
        #Here we just give all the packages to each truck based on the cluster (not sorted)

        #TODO make this work for any values of no_trucks and no_clusters (properly)
        
        no_trucks = len(trucks)

        no_buckets = int(no_clusters / no_trucks)

        for i in range(no_clusters):
            truck_index = int(i / no_buckets) % no_trucks
            trucks[truck_index].add_cluster_centroid(centroids[i]) 

        

        for cluster_label, customer in zip(cluster_labels, customers):
            customer.colour = colours[cluster_label]
            for package in customer.packages:
                truck_idx = int(cluster_label / no_buckets) % no_trucks
                trucks[truck_idx].load_package(package, tuple(centroids[cluster_label]))
        


        #Give a random default cluster to begin with
        for truck in trucks:
            truck.current_cluster = truck.cluster_centroids[-1]

        #Here we sort the packages in each truck based on the distance from the cluster centroid (Descending)
        for truck in trucks:
            truck.sort_packages()

        


def get_euclidean_distance(position1, position2):
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5

def get_manhattan_distance(position1, position2):
    return abs(position1.x - position2.x) + abs(position1.y - position2.y)  