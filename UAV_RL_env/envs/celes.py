from sklearn.cluster import KMeans
import pandas as pd
import numpy as np
import random
import time

class Drone:

    
    def __init__(self, position, home_truck = None, active_battery_consume =  0.05, passive_battery_consume = 0.005, drone_speed = 10, battery = 100, drone_id = None, capacity = 2):
        
        #The capacity of the drone is the maximum number of packages it can carry at the same time
        self.capacity = capacity

        self.position = position

        #Drone active_battery_consume is defined as the amount of battery consumed per unit of distance crossed
        self.active_battery_consume = active_battery_consume
        
        # passive_battery_consume is the battery consumed when waiting at a customer to deliver a package
        self.passive_battery_consume = passive_battery_consume
        
        #Drone speed is given in m/s
        self.drone_speed = drone_speed

        #Battery is just a number representing the percentage of battery remaining
        self.battery = 100
        #charge_increase is how much charge the battery increases every time step when it is charging
        self.charge_increase = 0.05

        self.drone_id = drone_id

        #Home truck is the truck the drone is initially loaded onto (And cannot change)
        self.home_truck = home_truck
       
        #The packages list contains the packages the drone is carrying RIGHT NOW
        self.packages = []
        self.no_packages = 0
               
        #This is to check if drone is on its way somewhere
        self.en_route = False
        self.on_truck = True

        #We use this variable to perform a 2 minute delay (120 steps), when unloading the package and giving it to the customer
        self.delay_variable = 0

        #Here we store the total distance travelled by the drone over the course of the run
        self.total_travel_distance = 0

        #Here we store the total active time of a drone in clusters
        #Note that we consider the 2 minute dropoff time to be part of the active time
        self.total_active_time = 0

        #Here we store the total delay time the drone spends waiting at the customer.
        self.total_delay_time = 0

        # This boolean variable tells us when the drone is waiting the 120 seconds at a customer
        self.waiting = False

        # This variable tells us how many customers the drone will deliver to this trip
        self.no_customers_in_list = 0

        # Number of preventions variables
        # How many times a drone was prevented from leaving the truck due to battery constraints
        self.no_preventions = {'first_preventions': 0, 'total_preventions': 0}
        # If this is the first time a drone was prevented on this "stay" on the truck then this variable is true
        self.first_prevent = True
        

    #When a drone returns from a trip delivering packages, we call this function to load additional packages
    def load_package(self):
        self.home_truck.load_drone_package(self)
    
    def go_to_home_truck(self):
        """
        After a drone has delivered all its packages, we call this function to make it return to its home truck
        """
        distance = get_euclidean_distance(self.position, self.home_truck.position)

        #First check we don't overshoot. If we don't overshoot then just move the full distance (according to speed)
        if distance <= self.drone_speed: # Here we go straight to the truck
            
            self.consume_battery(distance)

            #Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance

            if not self.on_truck:
                self.home_truck.load_drone(self)

        else: #Here we move the full length
            self.en_route = True
            self.on_truck = False
            distance_traveled = self.position.get_point_on_line(self.home_truck.position, self.drone_speed)
            
            self.consume_battery(distance_traveled)
            
            #Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance_traveled


    def go_to_position(self, position):
        """
        This function moves the drone towards a certain position.
        If we reach the destination we return True, otherwise we return false
        """
        distance = get_euclidean_distance(self.position, position)
        self.en_route = True
        self.on_truck = False
        if distance < self.drone_speed:

            self.consume_battery(distance)

            #Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance


            self.position.x = position.x
            self.position.y = position.y
            self.en_route = False
    
            return True
        else:

            distance_traveled = self.position.get_point_on_line(position, self.drone_speed)
            self.consume_battery(distance_traveled)

            #Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance_traveled


            return False
        return False   


    def consume_battery(self, distance):
        """
        This function is called whenever the drone moves.
        We subtract self.active_battery_consume for each unit of distance it travelled
        """
        if distance > 0:
            if self.battery - (self.active_battery_consume) < 0:
                self.battery = 0
            else:
                self.battery = self.battery - (self.active_battery_consume)
    
    def steadystate_consumption(self):
        """
        There is a constant drainage of the battery equal to self.cost/4 every second
        """
        if self.battery - self.passive_battery_consume < 0:
            self.battery = 0
        else:
            self.battery -= self.passive_battery_consume
         
    def get_range_of_reach(self):
        """
        This function is used to calculate the maximum distance our drone can travel with its
        current battery charge
        """

        #What is the maximum distance our drone can travel with its current battery level
        return (self.battery / self.active_battery_consume) * self.drone_speed
        # return float('inf')

    def deliver_next_package(self, unserviced_customers):
        """
        Move towards the next customer in our list. 
        If we have no more customers to deliver to we go_to_home_truck()
        """

        #Here we check if the drone is active. If so, we add 1 second to its active time
        #A drone is active if it is moving somewhere OR if it dropping off a package
        #In other words a drone is active when it is NOT on a truck
        if self.position != self.home_truck.position:
            self.total_active_time += 1
        
        #First check if we have any packages to deliver. If that is the case check if we can reach
        #the customers using our current charge. If so then deliver.
        if self.no_packages > 0:

            # Reset the first_prevent boolean for prevention counter
            self.first_prevent = True

            
            #customer_position contains the position of the customer we are delivering to right now
            # customer_position = Position(self.packages[0].customer.position.x, self.packages[0].customer.position.y)
            # customer_position = self.packages[0].customer.position
            

            arrived = False

            #If the drone is on the truck we leave the trucks
            if self.on_truck:
                self.home_truck.no_drones -= 1

            #Move towards the customer position
            arrived = self.go_to_position(self.packages[0].customer.position)

            #This allows us to deliver all the packages at once if we arrive at a certain customer
            if arrived:
                
                self.en_route = False
                #Once we arrive at a customer, we want to perform a 2 minute delay (120 steps)
                self.delay_variable += 1
                self.total_delay_time += 1
                self.waiting = True

                if self.delay_variable == 120:
                    self.delay_variable = 0
                    self.en_route = True

                    self.waiting = False
                    
                    #This is one of the packages we are delivering to the customer
                    package = self.packages[0]

                    # If we have arrived then we add 1 to the number of dropoffs this customer has
                    package.customer.no_dropoffs += 1

                    # decrement the number of customers the drone has left to deliver this trip
                    self.no_customers_in_list -= 1

                    # If the inital time hasn't been set yet then this is the first package to be delivered
                    if package.customer.time_initial == -1:
                        package.customer.time_initial = package.waiting_time
                    old_length = len(self.packages)

                    self.packages[:] = [package for package in self.packages if package.customer.position != self.position]

                    self.no_packages = len(self.packages)
                    package.customer.no_of_packages -= (old_length - len(self.packages))
                    if package.customer.no_of_packages == 0:
                        # The customer has now been fully serviced
                        unserviced_customers.remove(package.customer)
                        #We add the customer_waiting_time
                        self.home_truck.total_customer_waiting_time += package.waiting_time
                        # Since all packages have been delivered this is the final time of the span
                        package.customer.time_final = package.waiting_time
                    #Also add the total package waiting time for the packages delivered
                    self.home_truck.total_package_waiting_time += (package.waiting_time * (old_length - self.no_packages))
                    
                    
                        
        #If we have no more packages, go back to the home truck
        else:

            self.go_to_home_truck()
            if not self.en_route:
                if self.home_truck.no_packages > 0:
                    self.load_package()

    def charge(self):
        """
        While the drone is on the truck we increase its charge every step by self.charge_increase
        """
        if self.on_truck and self.no_packages == 0:
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
        self.waiting_time = 0


class Position:

    def __init__(self, x, y):
        #Suppose the location of a truck, drone or house is defined by (x, y)
        self.x = x
        self.y = y

    def get_position_info(self):
        d = {'x' : self.x, 'y': self.y}
        return d


    def __str__(self):
        return str(self.x) + ", " + str(self.y)  

    def __repr__(self):
        return str(self)
    
    def __eq__(self, pos):
        return self.x == pos.x and self.y == pos.y
    
    def __ne__(self, pos):
        return not self.__eq__(pos)

    def __sub__(self, position2):
        return Position(self.x - position2.x, self.y - position2.y)

    def _normalize_position(self):
        """
        Here we convert a vector into a unit vector
        """
        norm = (self.x ** 2 + self.y ** 2) ** 0.5
        self.x /= norm
        self.y /= norm


    #In order to get a position d distance away from position1 on the straight line between position
        #one and position2 we use this method https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
        # 1) Subtract the two positions (using the ordinary method) v = position2 - position1
        # 2) Normalize v --> u
        # 3) new position = position1 + du

    def get_point_on_line(self, position2, distance):
        """
        In this function we move a distance of "distance" towards position2.
        We return the distance travelled. 
        """
        v = position2 - self

        previous_position = Position(self.x, self.y)

        v._normalize_position()
        self.x = self.x + distance * v.x
        self.y = self.y + distance * v.y

        return get_euclidean_distance(previous_position, self)



    


class Customer:

    def __init__(self, position, residence_type, no_of_packages = 0):
        #Location will be a class of type position (defined by x and y)
        self.position = position
        #residence_type will just be a string ("apt" or "house")
        self.residence_type = residence_type
        # Here we store the number of packages not yet delivered to the customer
        # If everything has been delivered this variable will be 0
        self.no_of_packages = no_of_packages
        self.packages = []
        # Here we store the original number of packages
        # After all packages have been delivered this maintains its original value
        self.original_no_packages = no_of_packages
        self.colour = None

        #This tells us how many packages are still on the truck
        self.quasi_no_packages = 0

        # Information about delivery span
        # Span is the amount of time between the first and final packages being delivered
        # Time inital and time final are the times the inital and final packages were delivered respectively
        self.time_initial = -1
        self.time_final = -1

        # This is the number of times are drone arrives at this customer
        self.no_dropoffs = 0
        

    def get_customer_info(self):
        d = self.position.get_position_info()
        d['residence_type'] = self.residence_type
        d['no_of_packages'] = self.no_of_packages
        return d  

    def add_package(self, package):
        """
        This function adds a package to our customer
        """
        self.no_of_packages += 1
        self.original_no_packages += 1
        self.quasi_no_packages += 1
        self.packages.append(package)   

    
class Truck:
    
    no_of_drones = 0
    #We might just want to inherit from a superclass...
    def __init__(self, position, cost = 0.0006, truck_speed = 8, truck_id = None, total_no_drones = 0, strategy = 'next_closest'):
        

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


        self.total_package_waiting_time = 0 #Here we store the total time for each package to be delivered
        self.total_customer_waiting_time = 0 #Here we store the total time for each customer to be fully serviced


        #Here we store the total distance travelled by the truck throughout the run
        self.total_travel_distance = 0

        #Here we store the total time this truck spent in a cluster
        self.total_time_in_cluster = 0
        
    def load_package(self, package, cluster):
        """
        This function adds a package to the cluster list specified in the truck dict.
        If the cluster doesnt exist we add the cluster to the dict and then add the package
        """
        if cluster not in self.packages:
            self.packages[cluster] = []
        self.packages[cluster].append(package)
        self.no_packages += 1

    def sort_packages(self, how):
        """
        In this function we sort the packages in the truck dict either according to:
            1) The distance from the center of the cluster, or
            2) The number of packages the customer has 
        """
        if how == 'distance': #Here we sort the packages according to the distance from the center of the cluster
            for cluster in self.packages.keys():
                cluster_position = Position(cluster[0], cluster[1])
                self.packages[cluster] = sorted(self.packages[cluster], key = lambda x : get_euclidean_distance(x.customer.position, cluster_position), reverse=True)
        elif how == 'no_packages': #Here we sort the packages according to the number of packages of the customer
            for cluster in self.packages.keys():
                self.packages[cluster] = sorted(self.packages[cluster], key = lambda x : (x.customer.quasi_no_packages, x.customer.position.x, x.customer.position.y))
                

    def load_drone_package(self, drone):
        """
        In this function we assign packages to a drone according the strategy we have specified in self.strategy.
        """

        #This is to make sure drones aren't assigned packages such that it's impossible to deliver them with a full charge
        total_delivery_distance = 0
        
        no_packages_to_load = drone.capacity


        #In this strategy we load the drone farthest away from the truck then next closest to that package and so on.
        if self.strategy == 'farthest_package_first':

            for _ in range(no_packages_to_load):

                if drone.no_packages == 0:
                    if len(self.packages[self.current_cluster]) > 0:
                        package_to_deliver = self.packages[self.current_cluster][0]
                        total_delivery_distance += get_euclidean_distance(self.position, package_to_deliver.customer.position)

                        #Check if it is possible to deliver the package with the current charge
                        #If it is possible then load the package
                        if total_delivery_distance * 2  + 120 * drone.passive_battery_consume <= drone.get_range_of_reach():
                            self.packages[self.current_cluster].remove(package_to_deliver)
                            self.no_packages -= 1

                            drone.packages.append(package_to_deliver)
                            drone.no_packages += 1

                            package_to_deliver.customer.quasi_no_packages -= 1

                            drone.no_customers_in_list += 1
                        else:
                            if drone.first_prevent:
                                drone.first_prevent = False
                                drone.no_preventions['first_preventions'] += 1
                                drone.no_preventions['total_preventions'] += 1
                            return

                elif len(self.packages[self.current_cluster]) > 0:
                    package_to_deliver = self.packages[self.current_cluster][-1]
                    min_distance = get_euclidean_distance(package_to_deliver.customer.position, drone.packages[-1].customer.position)
                    for package in self.packages[self.current_cluster]:
                        if get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position) < min_distance:
                            min_distance = get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position)
                            package_to_deliver = package
                    
                    #Add the distance between the last package we have so far and the package we want to add to the list
                    total_delivery_distance += get_euclidean_distance(drone.packages[-1].customer.position, package_to_deliver.customer.position)
                    
                    #Check if it is possible to deliver the package with the current charge
                    #If it is possible then load the package 
                    

                    # This variable will be 1 if the package ISN'T already in the list and 0 otherwise
                    already = customer_not_already_in_list(package_to_deliver, drone.packages)

                    if total_delivery_distance + get_euclidean_distance(self.position, package_to_deliver.customer.position) + 120 * drone.passive_battery_consume * (drone.no_customers_in_list + already) <= drone.get_range_of_reach():
                        self.packages[self.current_cluster].remove(package_to_deliver)
                        self.no_packages -= 1

                        drone.packages.append(package_to_deliver)
                        drone.no_packages += 1

                        package_to_deliver.customer.quasi_no_packages -= 1

                        drone.no_customers_in_list += already

                    else:
                        if drone.first_prevent:
                            print("ASD")
                            drone.first_prevent = False
                            drone.no_preventions['total_preventions'] += 1
                        return
        #In this strategy we load the package closest to the truck, then closest to that package and so on.
        elif self.strategy == 'closest_package_first':
            for _ in range(no_packages_to_load):

                if drone.no_packages == 0:
                    if len(self.packages[self.current_cluster]) > 0:
                        package_to_deliver = self.packages[self.current_cluster][-1]
                        total_delivery_distance += get_euclidean_distance(self.position, package_to_deliver.customer.position)

                        #Check if it is possible to deliver the package with the current charge
                        #If it is possible then load the package
                        if total_delivery_distance * 2 + 120 * drone.passive_battery_consume <= drone.get_range_of_reach():
                            self.packages[self.current_cluster].remove(package_to_deliver)
                            self.no_packages -= 1

                            drone.packages.append(package_to_deliver)
                            drone.no_packages += 1

                            package_to_deliver.customer.quasi_no_packages -= 1

                            drone.no_customers_in_list += 1
                        else:
                            if drone.first_prevent:
                                drone.first_prevent = False
                                drone.no_preventions['first_preventions'] += 1
                                drone.no_preventions['total_preventions'] += 1
                            return

                elif len(self.packages[self.current_cluster]) > 0:
                    package_to_deliver = self.packages[self.current_cluster][-1]
                    min_distance = get_euclidean_distance(package_to_deliver.customer.position, drone.packages[-1].customer.position)
                    for package in self.packages[self.current_cluster]:
                        if get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position) < min_distance:
                            min_distance = get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position)
                            package_to_deliver = package
                    
                    #Add the distance between the last package we have so far and the package we want to add to the list
                    total_delivery_distance += get_euclidean_distance(drone.packages[-1].customer.position, package_to_deliver.customer.position)
                    
                    # This variable will be 1 if the package ISN'T already in the list and 0 otherwise
                    already = customer_not_already_in_list(package_to_deliver, drone.packages)

                    #Check if it is possible to deliver the package with the current charge
                    #If it is possible then load the package 
                    if total_delivery_distance + get_euclidean_distance(self.position, package_to_deliver.customer.position)  + 120 * drone.passive_battery_consume * (drone.no_customers_in_list + already) <= drone.get_range_of_reach():
                        self.packages[self.current_cluster].remove(package_to_deliver)
                        self.no_packages -= 1

                        drone.packages.append(package_to_deliver)
                        drone.no_packages += 1

                        package_to_deliver.customer.quasi_no_packages -= 1

                        drone.no_customers_in_list += already
                    else:
                        if drone.first_prevent:
                            drone.first_prevent = False
                            drone.no_preventions['total_preventions'] += 1
                        return
        #Here we load the package for the customer with the highest number of packages, then the closest package to that and so on.                    
        elif self.strategy=='most_packages_first':
                            
            #sort packages dictionary by number of packages
            drone.home_truck.sort_packages('no_packages')

            
            if drone.no_packages==0:
                if len(self.packages[self.current_cluster])> 0:
                    p = self.packages[self.current_cluster][-1] 
                    total_delivery_distance += get_euclidean_distance(self.position, p.customer.position)
                    if total_delivery_distance * 2 + 120 * drone.passive_battery_consume <= drone.get_range_of_reach():

                            drone.no_customers_in_list += 1

                            self.packages[self.current_cluster].pop()
                            self.no_packages -= 1

                            drone.packages.append(p)
                            drone.no_packages += 1


                            #Indicate that we have taken the package from the truck but have not delivered it yet
                            p.customer.quasi_no_packages -= 1

                            while (drone.no_packages < no_packages_to_load) and\
                                len(self.packages[self.current_cluster]) > 0 and\
                            (p.customer.position == self.packages[self.current_cluster][-1].customer.position):
                                p = self.packages[self.current_cluster][-1]
                                self.packages[self.current_cluster].pop()
                                self.no_packages -= 1

                                drone.packages.append(p)
                                drone.no_packages += 1

                                #Indicate that we have taken the package from the truck but have not delivered it yet
                                p.customer.quasi_no_packages -= 1
                    else:
                        if drone.first_prevent:
                            drone.first_prevent = False
                            drone.no_preventions['first_preventions'] += 1
                            drone.no_preventions['total_preventions'] += 1
                        return
                        
            #sort packages dictionary by number of packages
            drone.home_truck.sort_packages('no_packages')
            
            if drone.no_packages != 0 and len(self.packages[self.current_cluster]) > 0 and drone.no_packages < no_packages_to_load:
                
                no_packages_left = no_packages_to_load - drone.no_packages

                for _ in range(no_packages_left):

                    if len(self.packages[self.current_cluster]) > 0:

                        package_to_deliver = self.packages[self.current_cluster][0]
                        min_distance = get_euclidean_distance(package_to_deliver.customer.position, drone.packages[-1].customer.position)
                        for package in self.packages[self.current_cluster]:
                            if get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position) < min_distance:
                                min_distance = get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position)
                                package_to_deliver = package

                        already = customer_not_already_in_list(package_to_deliver, drone.packages)
                        
                        #Add the distance between the last package we have so far and the package we want to add to the list
                        total_delivery_distance += get_euclidean_distance\
                        (drone.packages[-1].customer.position, package_to_deliver.customer.position)
                        
                        
                        

                        if total_delivery_distance + get_euclidean_distance(self.position, package_to_deliver.customer.position) + 120 * drone.passive_battery_consume * (drone.no_customers_in_list + already)<= drone.get_range_of_reach():
                            self.packages[self.current_cluster].remove(package_to_deliver)
                            self.no_packages -= 1

                            drone.packages.append(package_to_deliver)
                            drone.no_packages += 1

                            #Indicate that we have taken the package from the truck but have not delivered it yet
                            package_to_deliver.customer.quasi_no_packages -= 1

                            drone.no_customers_in_list += already
                        else:
                            if drone.first_prevent:
                                drone.first_prevent = False
                                drone.no_preventions['total_preventions'] += 1
                            return

        elif self.strategy == 'farthest_package_first_MPA':

            if drone.no_packages == 0:
                if len(self.packages[self.current_cluster])> 0:
                    # The first package we deliver will be the one farthest away
                    package_to_deliver = self.packages[self.current_cluster][0]
                    
                    total_delivery_distance += get_euclidean_distance(self.position, package_to_deliver.customer.position)

                    # If we can reach the customer and come back we load all their packages
                    if total_delivery_distance * 2 + 120 * drone.passive_battery_consume <= drone.get_range_of_reach():
                        
                        drone.no_customers_in_list += 1

                        for package in self.packages[self.current_cluster]:
                            if drone.capacity == drone.no_packages:
                                return

                            if package.customer.position == package_to_deliver.customer.position:
                                drone.packages.append(package)
                                drone.no_packages += 1
                                package.customer.quasi_no_packages -=1 

                                self.packages[self.current_cluster].remove(package)
                                self.no_packages -= 1

                    else:
                        if drone.first_prevent:
                            drone.first_prevent = False
                            drone.no_preventions['first_preventions'] += 1
                            drone.no_preventions['total_preventions'] += 1
                        return

            if len(self.packages[self.current_cluster]) > 0 and drone.no_packages != 0:
                # We enter here if the drone already has packages on it

                while drone.capacity != drone.no_packages:
                    # Here we make a list of packages sorted according to the distance from the last package (ascending)
                    packages_new = sorted(self.packages[self.current_cluster], key = lambda x : get_euclidean_distance(x.customer.position, drone.packages[-1].customer.position), reverse=True)
                    # Make sure we have packages in our list
                    if len(packages_new) == 0:
                        return

                    for i, package in enumerate(reversed(packages_new)):
                        if drone.capacity == drone.no_packages:
                            return

                        # Here we check if we can load all packages in one go or if we can't do so in the future
                        condition = (drone.capacity - drone.no_packages >= package.customer.quasi_no_packages or drone.capacity < package.customer.quasi_no_packages)


                        if not condition:
                            if i == len(packages_new) - 1:
                                return
                            else:
                                continue

                        already = customer_not_already_in_list(package, drone.packages)

                        #Add the distance between the last package we have so far and the package we want to add to the list
                        total_delivery_distance += get_euclidean_distance(drone.packages[-1].customer.position, package.customer.position)
                        if total_delivery_distance + get_euclidean_distance(self.position, package.customer.position) + 120 * drone.passive_battery_consume * (drone.no_customers_in_list + already) <= drone.get_range_of_reach():                            
                            

                            self.packages[self.current_cluster].remove(package)
                            
                            packages_new.remove(package)
                            self.no_packages -= 1

                            drone.packages.append(package)
                            drone.no_packages += 1

                            package.customer.quasi_no_packages -= 1

                            drone.no_customers_in_list += already

                            if package.customer.quasi_no_packages == 0:
                                break
                        else:
                            if drone.first_prevent:
                                drone.first_prevent = False
                                drone.no_preventions['total_preventions'] += 1
                            return

                        
    def add_cluster_centroid(self, pos):
        """
        Here we add one of our cluster centroids to the list of cluster centroids on the truck as a tuple
        """
        self.cluster_centroids.append(tuple(pos))
    

    def get_truck_info(self):
        d = self.position.get_position_info()
        d['cost'] = self.cost
        d['speed'] = self.truck_speed
        d['no_of_drones'] = self.no_of_drones
        return d


    def move_towards_position(self, position):
        """
        In this function we move the truck towards "position" in a manhattan manner (straight lines only).
        We return True if the truck reached the destination and False otherwise
        """

        #In this function we want to actually move the truck in addition to adding the distance travelled to self.total_distance_travelled
        #We do this by recording the old position then calculating the distance to the new position
        old_position = Position(self.position.x, self.position.y)

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

        #Here we calculate the distance travelled in this step and add it to the run
        distance_traveled = get_manhattan_distance(self.position, old_position)
        self.total_travel_distance += distance_traveled

        #Here we check if the truck reached the destination
        if self.position.x == position.x and self.position.y == position.y:
            self.is_moving = False

            return True
        else:
            return False

        

    def go_to_next_cluster(self):
        """
        This function moves the truck to the next cluster after checking if the current cluster has finished.
        Once the truck has finished all the clusters it returns to the warehouse.
        """

        #In the first if statement we check if we have finished all clusters. If so we return to the warehouse.
        #We can say that we have finished all our clusters if we have no cluster centroids in our list
        #AND all drones are on the truck AND we have no packages left
        if len(self.cluster_centroids) == 0 and self.no_drones == self.total_no_drones and self.no_packages == 0:
            #If we're done move towards the warehouse
            warehouse_position = Position(1000, 1000)
            arrived = self.move_towards_position(warehouse_position)
        elif len(self.cluster_centroids) > 0 and self.cluster_finished():
            self.current_cluster = self.cluster_centroids[-1]
            cluster_position = Position(self.current_cluster[0], self.current_cluster[1])
            arrived = self.move_towards_position(cluster_position)

            if arrived:
                self.cluster_centroids.pop()
        else:
            cluster_position = Position(self.current_cluster[0], self.current_cluster[1])
            self.move_towards_position(cluster_position)

        #Here we also want to calculate how much time our trucks are in clusters
        #We do this by check if our current position is the same as self.current_cluster
        if self.position == Position(self.current_cluster[0], self.current_cluster[1]):
            self.total_time_in_cluster += 1
            

            


    def cluster_finished(self):
        """
        In this function we check if we have finished the current cluster.
        Return True if we have and False otherwise.
        """
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
        """
        In this function we load a drone onto the truck
        """
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
        """
        In this function we cluster our customers using KMeans and assign them a colour.
        We also assign the trucks to the clusters and assign the packages to the trucks.
        Finally we sort the packages on the trucks according to the strategy being used.
        """
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
            0 : '#8B0000',
            1 : '#DB7093',
            2 : '#FFA500',
            3 : '#BDB76B',
            4 : '#7B68EE',
            5 : '#008080',
            6 : '#CD5C5C',
            7 : '#FFC0CB',
            8 : '#FFA07A',
            9 : '#FFD700',
            10 : '#E6E6FA',
            11 : '#ADFF2F',
            12 : '#00FFFF',
            13 : '#FFF8DC',
            14 : '#DCDCDC',
            15 : '#191970',
            16 : '#800000',
            17 : '#FFE4E1',
            18 : '#000000',
            19 : '#5489fc'
        }
        
        #Here we just give all the packages to each truck based on the cluster (not sorted)

        
        no_trucks = len(trucks)

        # This dictionary will have the cluster_label as the index, with the truck index as the value
        truck_for_cluster = {cluster : -1 for cluster in range(no_clusters)}
        
        # Here we distribute the clusters to the trucks
        i = 0
        for j in range(no_clusters):
            trucks[i].add_cluster_centroid(centroids[j])
            truck_for_cluster[j] = i
            i = (i + 1) % no_trucks

        # Here we assign colours to each customer and distribute the packages to the trucks
        for cluster_label, customer in zip(cluster_labels, customers):
            customer.colour = colours[cluster_label]
            truck_idx = truck_for_cluster[cluster_label]
            for package in customer.packages:
                trucks[truck_idx].load_package(package, tuple(centroids[cluster_label]))
        
        


        #Give a random default cluster to begin with
        for truck in trucks:
            truck.current_cluster = truck.cluster_centroids[-1]

        #According to the strategy we will sort the trucks accordingly
        #Currently the same strategy is shared by all the trucks
        if trucks[0].strategy in ('farthest_package_first', 'closest_package_first', 'farthest_package_first_MPA'):
            # Here we sort the packages in each truck based on the distance from the cluster centroid (Descending)
            for truck in trucks:
                truck.sort_packages('distance')
        elif trucks[0].strategy == 'most_packages_first':
            #Here we sort the packages in each truck based on the number of packages the package's customer has
            for truck in trucks:
                truck.sort_packages('no_packages')
        


def get_euclidean_distance(position1, position2):
    """
    Return the euclidean distance between two points
    """
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5

def get_manhattan_distance(position1, position2):
    """
    Return the msanhattan distance between two points
    """
    return abs(position1.x - position2.x) + abs(position1.y - position2.y) 

def customer_not_already_in_list(customer_package, package_list):
    """
    Return 0 if the customer for customer_package is already in package_list and return 1 otherwise
    """
    for package in package_list:
        if customer_package.customer.position == package.customer.position:
            return 0 
    return 1