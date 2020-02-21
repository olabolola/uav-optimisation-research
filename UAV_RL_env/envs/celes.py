class Drone:

    
    def __init__(self, position, loading_capacity = 100, cost = 2, drone_speed = 100, battery = 100, drone_type = "normal", drone_id = None):
        #probably won't end up using drone type in our research
        self.drone_type = drone_type
        self.loading_capacity = loading_capacity
        self.battery = battery
        self.cost = cost
        self.drone_speed = drone_speed
        #If package_weight = 0, then drone is not carrying anything
        self.drone_id = drone_id
        self.is_delivering = False
        self.home_truck = None
        self.position = position
        self.packages = []
        self.no_packages = 0

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
        #Just for testing the drone has a range of reach of 300
        return 300
    def go_to_home_truck(self):
        #First check we don't overshoot. If we don't overshoot then just move the full distance (according to speed)
        if get_euclidean_distance(self.position, self.home_truck.position) < self.drone_speed:
            self.position = self.home_truck.position
        else:
            self.position = self.position.get_point_on_line(self.position, self.home_truck.position)

    def go_to_closest_truck(self, trucks):
        #Find the truck with min(distance) between itself and the drone

        min_distance = float('inf')
        closest_truck = trucks[0]
        for truck in trucks:
            distance = get_euclidean_distance(self.position, truck.position)
            if distance < min_distance:
                min_distance = distance
                closest_truck = truck
        if get_euclidean_distance(self.position, closest_truck.position) < self.drone_speed:
            self.position = closest_truck.position
        else:
            self.position = self.position.get_point_on_line(self.position, closest_truck.position)

    def deliver_next_package(self):
        customer_position = self.packages[-1].customer.position
        if get_euclidean_distance(self.position, customer_position) < self.drone_speed:
            self.position = customer_position
        else:
            self.position = self.position.get_point_on_line(self.position, customer_position)

    def get_drone_info(self):
        d = {'loading_capacity' : self.loading_capacity, 'cost' : self.cost,
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
        v = position2 - self
        v._normalize_position()
        new_x = self.x + distance * v.x
        new_y = self.y + distance * v.y

        position = Position(new_x, new_y)
        return position

    


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
    def add_drones(self, number, loading_capacity = 100, cost = 2, drone_speed = 100, battery = 100, drone_type = "normal", drone_id = None):
    
        self.no_of_drones += number
        for _ in range(number):
            if self.no_vacancies > 0:
                self.no_vacancies -= 1
                drone = Drone(self.position, loading_capacity, cost, drone_speed, battery, drone_type, drone_id)
                #TODO check if this actually makes sense (does it work python-wise)
                drone.home_truck = self
                self.drones.append(drone)
            else:
                #TODO raise a custom exception
                print("ERROR YOU CAN'T ADD DRONES")
                break

    def move_towards_position(self, position):
        #This whole complicated function is to ensure the truck moves like it's in Manhattan
        if get_manhattan_distance(self.position, position) <= self.truck_speed:
            self.position = position
        else:
            units_to_move = self.truck_speed
            x_difference = position.x - self.position.x
            y_difference = position.y - self.position.y
            if abs(x_difference) > units_to_move:
                self.position.x += units_to_move
            elif abs(y_difference) > units_to_move:
                self.position.y += units_to_move
            else:
                #For now we just start with the x
                #Might want to do it in a smarter manner later
                units_to_move -= abs(x_difference)
                self.position.x = position.x
                if y_difference < 0:
                    self.position.y -= units_to_move
                else:
                    self.position.y += units_to_move


class charging_station:
    def __init__(self, position):
        self.position = position

def get_euclidean_distance(position1, position2):
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5

def get_manhattan_distance(position1, position2):
    return abs(position1.x - position2.x) + abs(position1.y - position2.y)