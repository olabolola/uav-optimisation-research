class Drone:

    
    def __init__(self, position, home_truck = None, loading_capacity = 100, cost = 2, drone_speed = 10, battery = 100, drone_type = "normal", drone_id = None):
        #probably won't end up using drone type in our research
        self.position = position
        self.loading_capacity = loading_capacity
        self.cost = cost
        self.drone_speed = drone_speed
        self.battery = battery
        self.drone_type = drone_type
        self.drone_id = drone_id
        self.is_delivering = False
        self.home_truck = home_truck
        self.packages = []
        self.no_packages = 0
        #This is to ensure drone doesn't just fly back to the truck it left from
        self.host_truck = self.home_truck
        #This is to check if drone is on its way somewhere
        self.en_route = False
        self.on_truck = True
        self.temp = True


    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    def load_package(self, package):
        self.packages.append(package)
        self.no_packages += 1

    #destination will be of type class: position
    #Problem with this is that it doesn't take no fly zones into account.
    #Will probably have to make a class called environement which has a method called get_travel_time
    def get_range_of_reach(self, package_weight = 10):
        #return some equation involving the parameters above
        #return package_weight*alpha + something to do with the battery

        #return function(get_euclidean_distance(destination, self.current_position), self.battery, self.speed, self.drone_type)
        #Just for testing the drone has a range of reach of infinity
        return float('inf')
    def go_to_home_truck(self):
        #First check we don't overshoot. If we don't overshoot then just move the full distance (according to speed)
        if get_euclidean_distance(self.position, self.home_truck.position) < self.drone_speed:
            self.home_truck.load_drone(self)
        else:
            if self.on_truck:
                self.host_truck.drone.remove(self)
            
            self.en_route = True
            self.on_truck = False
            
            self.position.get_point_on_line(self.home_truck.position, self.drone_speed)

    def go_to_closest_truck(self, trucks):
        #Find the truck with min(distance) between itself and the drone
        # if self.host_truck != None:
        #     self.position.x = self.host_truck.position.x
        #     self.position.y = self.host_truck.position.y
        #     # self.host_truck = None
        min_distance = float('inf')
        closest_truck = None
        for truck in trucks:
            if truck.position.x != self.position.x and truck.position.y != self.position.y and self.host_truck != truck:
                self.en_route = True
                distance = get_euclidean_distance(self.position, truck.position)
                if distance < min_distance:
                    min_distance = distance
                    closest_truck = truck
        if closest_truck == None:
            return
        else:
            if self.on_truck:
                self.host_truck.drones.remove(self)
            self.on_truck = False
            if get_euclidean_distance(self.position, closest_truck.position) < self.drone_speed:
                closest_truck.load_drone(self)
            else:
                self.position.get_point_on_line(closest_truck.position, self.drone_speed)

                
    def go_to_position(self, position):
        self.en_route = True
        self.on_truck = False
        if get_euclidean_distance(self.position, position) < self.drone_speed:
            self.position.x = position.x
            self.position.y = position.y
            self.en_route = False
            return True
        else:
            self.position.get_point_on_line(position, self.drone_speed)
            return False        

    def deliver_next_package(self, customers):
        if self.temp:
            self.temp = False
            if self.drone_id == 0:
                for package in self.host_truck.packages[:int(len(self.host_truck.packages)/5)]:
                    self.packages.append(package)
            elif self.drone_id == 1:
                for package in self.host_truck.packages[int(len(self.host_truck.packages)/5):int(2*len(self.host_truck.packages)/5)]:
                    self.packages.append(package)
            elif self.drone_id == 2:
                for package in self.host_truck.packages[int(2*len(self.host_truck.packages)/5):int(3*len(self.host_truck.packages)/5)]:
                    self.packages.append(package)
            elif self.drone_id == 3:
                for package in self.host_truck.packages[int(3*len(self.host_truck.packages)/5):int(4*len(self.host_truck.packages)/5)]:
                    self.packages.append(package)
            elif self.drone_id == 4:
                for package in self.host_truck.packages[int(4*len(self.host_truck.packages)/5):]:
                    self.packages.append(package)
        if len(self.packages) > 0:
            customer_position = self.packages[-1].customer.position
            arrived = self.go_to_position(customer_position)
            if arrived:
                for customer in customers:
                    if customer.position.x == customer_position.x and customer.position.y == customer_position.y:
                        customers.remove(customer)
                self.packages.pop()
                self.no_packages -= 1





    def get_drone_info(self):
        d = {'drone_position' : self.position, 'loading_capacity' : self.loading_capacity, 'cost' : self.cost,
        'drone_speed' : self.drone_speed, 'battery' : self.battery,
         'drone_type' : self.drone_type, 'drone_id' : self.drone_id}
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

    def get_customer_info(self):
        d = self.position.get_position_info()
        d['residence_type'] = self.residence_type
        d['no_of_packages'] = self.no_of_packages
        return d        
    
class Truck:
    
    no_of_drones = 0
    #We might just want to inherit from a superclass...
    def __init__(self, position, cost = 5, truck_speed = 100, truck_id = None, max_capacity = 20):
        self.cost = cost
        self.truck_speed = truck_speed
        self.position = position
        #Each truck has a number of drones. Do we want this as a feature of the truck?
        self.drones = []
        self.truck_id = truck_id
        self.max_capacity = max_capacity
        self.no_vacancies = 20
        self.packages = []
    
    def get_package_dropoff_time(self, residence_type):
        if residence_type == 'apartment':
            return 10
        elif residence_type == 'house':
            return 5

    def get_truck_info(self):
        d = self.position.get_position_info()
        d['cost'] = self.cost
        d['speed'] = self.truck_speed
        d['no_of_drones'] = self.no_of_drones
        return d

    #Do we just want to send the drones to this function and have them add them to its list.
    #Or do we want to send all the nitty gritty details here.
    def add_drones(self, number):
    
        
        for _ in range(number):
            if self.no_vacancies > 0:
                self.no_vacancies -= 1
                self.no_of_drones += 1
                # drone_position = Position(self.position.x, self.position.y)
                drone = Drone(self.position, self)
                #TODO check if this actually makes sense (does it work python-wise)
                self.drones.append(drone)
            else:
                #TODO raise a custom exception
                print("ERROR YOU CAN'T ADD DRONES")
                break

    def move_towards_position(self, position):
        
        #This whole complicated function is to ensure the truck moves like it's in Manhattan
        if get_manhattan_distance(self.position, position) <= self.truck_speed:
            self.position.x = position.x
            self.position.y = position.y
            for drone in self.drones:
                drone.position.x = self.position.x
                drone.position.y = self.position.y 
        else:
            units_to_move = self.truck_speed
            x_difference = position.x - self.position.x
            y_difference = position.y - self.position.y
            if abs(x_difference) > units_to_move:
                self.position.x += units_to_move
                for drone in self.drones:
                    drone.position.x += units_to_move
            elif abs(y_difference) > units_to_move:
                self.position.y += units_to_move
                for drone in self.drones:
                    drone.position.y += units_to_move
            else:
                #For now we just start with the x
                #Might want to do it in a smarter manner later
                units_to_move -= abs(x_difference)
                self.position.x = position.x
                for drone in self.drones:
                    drone.position.x = self.position.x
                if y_difference < 0:
                    self.position.y -= units_to_move
                    for drone in self.drones:
                        drone.position.y -= units_to_move
                else:
                    self.position.y += units_to_move
                    for drone in self.drones:
                        drone.position.y += units_to_move

    #TODO complete this function with all the necessary checks
    def load_drone(self, drone):
        drone.host_truck = self
        drone.position.x = self.position.x
        drone.position.y = self.position.y
        self.drones.append(drone)
        self.no_of_drones += 1
        drone.en_route = False
        drone.on_truck = True

    def load_drone_package(self, drone, package):
        drone.load_drone_package(package)


class charging_station:
    def __init__(self, position):
        self.position = position

def get_euclidean_distance(position1, position2):
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5

def get_manhattan_distance(position1, position2):
    return abs(position1.x - position2.x) + abs(position1.y - position2.y)