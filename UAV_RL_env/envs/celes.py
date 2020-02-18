class Drone:

    
    def __init__(self, loading_capacity = 100, cost = 2, drone_speed = 100, battery = 100, drone_type = "normal", drone_id = None):
        #probably won't end up using drone type in our research
        self.drone_type = drone_type
        self.loading_capacity = loading_capacity
        self.battery = battery
        self.cost = cost
        self.drone_speed = drone_speed
        #If package_weight = 0, then drone is not carrying anything
        self.package_weight = 0
        self.drone_id = drone_id

    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    def load_package(self, package_weight):
        self.package_weight = package_weight

    #destination will be of type class: position
    #Problem with this is that it doesn't take no fly zones into account.
    #Will probably have to make a class called environement which has a method called get_travel_time
    def get_range_of_reach(self, package_weight, destination):
        #return some equation involving the parameters above
        #return destination.distance(self.position) + package_weight*alpha

        #return function(get_euclidean_distance(destination, self.current_position), self.battery, self.speed, self.drone_type)
        pass

    def get_drone_info(self):
        d = {'loading_capacity' : self.loading_capacity, 'cost' : self.cost,
        'drone_speed' : self.drone_speed, 'battery' : self.battery,
         'drone_type' : self.drone_type, 'drone_id' : self.drone_id}
        return d

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

class Customer:

    def __init__(self, position, residence_type, no_of_packages):
        #Location will be a class of type position (defined by x and y)
        self.position = position
        #residence_type will just be a string ("apt" or "house")
        self.residence_type = residence_type
        self.no_of_packages = no_of_packages

    def get_customer_info(self):
        d = self.position.get_position_info()
        d['residence_type'] = self.residence_type
        d['no_of_packages'] = self.no_of_packages
        return d        
    

class Package:

    #leave out urgency for now
    def __init__(self, size, weight):
        #How do we want to define size?
        self.size = size
        self.weight = weight



class Truck:
    
    no_of_drones = 0
    #We might just want to inherit from a superclass...
    def __init__(self, position, cost = 5, speed = 100, truck_id = None):
        self.cost = cost
        self.speed = speed
        self.position = position
        #Each truck has a number of drones. Do we want this as a feature of the truck?
        self.drones = []
        self.truck_id = truck_id
    
    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    def get_truck_info(self):
        d = self.position.get_position_info()
        d['cost'] = self.cost
        d['speed'] = self.speed
        d['no_of_drones'] = self.no_of_drones
        return d

    #Do we just want to send the drones to this function and have them add them to its list.
    #Or do we want to send all the nitty gritty details here.
    def add_drones(self, number, loading_capacity = 100, cost = 2, drone_speed = 100, battery = 100, drone_type = "normal", drone_id = None):
        self.no_of_drones += number
        for _ in range(number):
            self.drones.append(Drone(loading_capacity, cost, drone_speed, battery, drone_type, drone_id))

def get_euclidean_distance(position1, position2):
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5