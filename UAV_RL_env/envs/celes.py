from sklearn.cluster import KMeans
import pandas as pd
class Drone:

    
    def __init__(self, position, home_truck = None, loading_capacity = 100, cost =  2, drone_speed = 2, battery = 100, drone_type = "normal", drone_id = None):
        self.position = position
        self.loading_capacity = loading_capacity
        self.cost = cost
        self.drone_speed = drone_speed
        #Battery is just a number representing the percentage of battery remaining
        self.battery = battery
        self.max_battery = 300
        self.charge_increase = 3
        self.drone_id = drone_id
        #Home truck is the truck the drone is initially loaded onto (And cannot change)
        self.home_truck = home_truck
       
       
        #The packages list contains the packages the drone is carrying RIGHT NOW
        self.packages = []
        self.no_packages = 0
        
        #The packages_scheduled list contains the packages the drone will deliver in the future
        self.packages_scheduled = []
        self.no_packages_scheduled = 0
       
        #This is to check if drone is on its way somewhere
        self.en_route = False
        self.on_truck = True
        self.is_delivering = False



    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    def load_package(self):

        self.home_truck.load_drone_package(self)


    def hand_package_to_customer(self, package):
        pass





    def go_to_home_truck(self):

        distance = get_euclidean_distance(self.position, self.home_truck.position)

        if distance <= self.get_range_of_reach():
            #First check we don't overshoot. If we don't overshoot then just move the full distance (according to speed)
            if distance <=   self.drone_speed:
                self.consume_battery(distance)
                self.home_truck.load_drone(self)
            else:            
                self.en_route = True
                self.on_truck = False
                self.is_delivering = False
                self.consume_battery(distance)
                self.position.get_point_on_line(self.home_truck.position, self.drone_speed)


                
    def go_to_position(self, position):

        distance = get_euclidean_distance(self.position, position)

        if distance * 2 <= self.get_range_of_reach():
            self.en_route = True
            self.on_truck = False
            if distance < self.drone_speed:
                self.consume_battery(distance)
                self.position.x = position.x
                self.position.y = position.y
                self.en_route = False
                return True
            else:
                self.position.get_point_on_line(position, self.drone_speed)
                self.consume_battery(distance)
                return False
        return False   

    def consume_battery(self, distance):
        if self.battery - self.cost < 0:
            self.battery = 0
        else:
            self.battery -= self.cost  
        

    def get_range_of_reach(self):

        #What is the maximum distance our drone can travel with its current battery level
        # position1 = Position(1, 1)
        # position2 = Position(self.battery * self.drone_speed, 1)
        # return get_euclidean_distance(position1, position2)

        return self.battery / (self.cost * self.drone_speed)

    def deliver_next_package(self, customers):
        
        if self.no_packages > 0:
            customer_position = self.packages[-1].customer.position
            arrived = self.go_to_position(customer_position)
            if arrived:
                
                customers.remove(self.packages[-1].customer)
                self.packages.pop()
                self.no_packages -= 1
        else:

            self.go_to_home_truck()
            if not self.en_route:
                if self.home_truck.no_packages > 0:
                    self.load_package()

    def check_charging(self):
        if self.on_truck:
            if self.battery + self.charge_increase< self.max_battery:
                self.battery += self.charge_increase
            else:
                self.battery = self.max_battery

    def get_drone_info(self):
        d = {'drone_position' : self.position, 'loading_capacity' : self.loading_capacity, 'cost' : self.cost,
        'drone_speed' : self.drone_speed, 'battery' : self.battery, 'drone_id' : self.drone_id}
        return d

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

    def __init__(self, position, residence_type, no_of_packages):
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
    def __init__(self, position, cost = 5, truck_speed = 2, truck_id = None, max_package_capacity = 20):
        self.cost = cost
        self.truck_speed = truck_speed
        self.position = position
        #Each truck has a number of drones. Do we want this as a feature of the truck?
        self.drones = []
        self.no_drones = 0

        self.truck_id = truck_id
        self.max_package_capacity = max_package_capacity

        self.packages = []
        self.no_packages = 0
    

    def load_package(self, package):
        self.packages.append(package)
        self.no_packages += 1

    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    def load_drone_package(self, drone):
        #TODO make this more smart
        #for now load the package with minimum distance from drone
        min_distance = get_euclidean_distance(drone.position, self.packages[0].customer.position)
        package_to_deliver = self.packages[0]
        for package in self.packages:
            if get_euclidean_distance(drone.position, package.customer.position) < min_distance:
                min_distance = get_euclidean_distance(self.position, package.customer.position)
                package_to_deliver = package
        
        self.packages.remove(package_to_deliver)
        self.no_packages -= 1

        drone.packages.append(package_to_deliver)
        drone.no_packages += 1

    def get_truck_info(self):
        d = self.position.get_position_info()
        d['cost'] = self.cost
        d['speed'] = self.truck_speed
        d['no_of_drones'] = self.no_of_drones
        return d


    def move_towards_position(self, position):
        # print(position)
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

            
    #TODO complete this function with all the necessary checks
    def load_drone(self, drone):
        drone.home_truck = self
        drone.position.x = self.position.x
        drone.position.y = self.position.y
        self.drones.append(drone)
        self.no_of_drones += 1
        drone.en_route = False
        drone.on_truck = True
        drone.is_delivering = False
        # drone.on_truck = True
        # drone.is_delivering = True



    # def assign_packages_to_drones(self):
    #     packages_per_drone = int(len(self.packages) / self.no_of_drones) 
    #     for i, drone in enumerate(self.drones):
    #         for package in self.packages[packages_per_drone*i:packages_per_drone * (i + 1)]:
    #             drone.schedule_package(package)
        
    #     for i in range(len(self.packages) % self.no_of_drones):
    #         self.drones[0].schedule_package(self.packages[len(self.packages) - i - 1])
        
    
class Warehouse:
    def __init__(self, position):
        self.position = position
    
    def cluster_and_colour(self, customers, trucks, no_trucks):
        customer_x = []
        customer_y = []

        for customer in customers:
            customer_x.append(customer.position.x)
            customer_y.append(customer.position.y)
        
        df = pd.DataFrame({
            'x' : customer_x,
            'y' : customer_y
        })

        kmeans = KMeans(n_clusters = no_trucks)
        cluster_labels = kmeans.fit_predict(df)
        
        centroids = kmeans.cluster_centers_

        colours = {
            0 : '#FFFF00',
            1 : '#00FFFF',
            2 : '#FF00FF',
            3 : '#C0C0C0',
            4 : '#808080',
            5 : '#800000',
            6 : '#808000',
            7 : '#800080',
            8 : '#008080'
        }
        

        for i, customer in zip(cluster_labels, customers):
            customer.colour = colours[i]
            for package in customer.packages:
                trucks[i].load_package(package)

        return centroids


def get_euclidean_distance(position1, position2):
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5

def get_manhattan_distance(position1, position2):
    return abs(position1.x - position2.x) + abs(position1.y - position2.y)  