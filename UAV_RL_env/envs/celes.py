from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Union, Set
from dataclasses import dataclass
from sklearn.cluster import KMeans
import pandas as pd
from enum import Enum

DRONE_BATTERY_SWAP_DELAY: int = 30
CUSTOMER_PACKAGE_DELIVERY_DELAY: int = 120


@dataclass
class TripData:
    trip_id: str
    strategy: Strategy
    travel_distance: float
    trip_time: int
    packages: List[Package]
    customers: List[Customer]
    battery_swapped: bool
    decision_data: List[DecisionData]


class DecisionData(str, Enum):
    INITIAL_PACKAGE: str = "INITIAL_PACKAGE"
    INITIAL_PACKAGE_PRIORITY: str = "INITIAL_PACKAGE_PRIORITY"
    NEXT_PACKAGE_SAME_CUSTOMER: str = "NEXT_PACKAGE_SAME_CUSTOMER"
    NEXT_PACKAGE_CLOSEST: str = "NEXT_PACKAGE_CLOSEST"


class Drone:

    def __init__(
        self,
        position: Position,
        home_truck: Truck,
        active_battery_consume: float = 0.005,  # original is 0.005
        passive_battery_consume: float = 0.001,  # Original is 0.001
        drone_speed: int = 10,
        battery: float = 100,
        drone_id: Optional[int] = None,
        capacity: int = 2,
    ):

        # The capacity of the drone is the maximum number of packages it can carry at the same time
        self.capacity: int = capacity

        self.position: Position = position

        # Drone active_battery_consume is defined as the amount of battery consumed per unit of distance crossed
        self.active_battery_consume: float = active_battery_consume

        # passive_battery_consume is the battery consumed when waiting at a customer to deliver a package
        self.passive_battery_consume: float = passive_battery_consume

        # Drone speed is given in m/s
        self.drone_speed: int = drone_speed

        # Battery is just a number representing the percentage of battery remaining
        self.battery: float = battery
        # charge_increase is how much charge the battery increases every time step when it is charging
        self.charge_increase: float = 0.05

        self.drone_id: Optional[int] = drone_id

        # Home truck is the truck the drone is initially loaded onto (And cannot change)
        self.home_truck: Truck = home_truck

        # The packages list contains the packages the drone is carrying RIGHT NOW
        self.packages: List[Package] = []

        # This is to check if drone is on its way somewhere
        self.en_route: bool = False
        self.on_truck: bool = True

        # We use this variable to perform a 2 minute delay (120 steps), when unloading the package and giving it to the customer
        self.delay_variable: int = 0

        # Here we store the total distance travelled by the drone over the course of the run
        self.total_travel_distance: float = 0

        # Here we store the total active time of a drone in clusters
        # Note that we consider the 2 minute dropoff time to be part of the active time
        self.total_active_time: int = 0

        # Here we store the total delay time the drone spends waiting at the customer.
        self.total_delay_time: int = 0

        # This boolean variable tells us when the drone is waiting the 120 seconds at a customer
        self.waiting: bool = False

        # This variable tells us how many customers the drone will deliver to this trip
        self.no_customers_in_list: int = 0

        # Number of preventions variables
        # How many times a drone was prevented from leaving the truck due to battery constraints
        self.no_preventions: int = 0
        # If this is the first time a drone was prevented on this "stay" on the truck then this variable is true
        self.first_prevent: bool = True

        # This variable stores the total travel distance for the drone on its current or next scheduled flight
        self.this_delivery_distance: float = 0

        # When a drone is about to leave if it doesn't have enough charge we will swap its battery out with a max charge one. This variable counts the number of swaps.
        self.no_battery_swaps: int = 0

        self.battery_swap_timer: int = 0

        # Metric to store some data on each trip
        self.trips: List[TripData] = []

    # When a drone returns from a trip delivering packages, we call this function to load additional packages
    def load_package(self):
        self.home_truck.load_drone_package(drone=self)

    def can_make_trip(
        self, start_position: Position, packages: List[Package], charge: float
    ) -> bool:
        total_trip_distance = get_total_trip_distance(
            start_position=start_position, packages=packages
        )
        active = total_trip_distance * self.active_battery_consume

        number_of_customers_in_list = get_no_customers_from_packages(packages=packages)
        passive = number_of_customers_in_list * self.passive_battery_consume

        return (active + passive) < charge

    def go_to_home_truck(self):
        """
        After a drone has delivered all its packages, we call this function to make it return to its home truck
        """
        distance = get_euclidean_distance(self.position, self.home_truck.position)

        # First check we don't overshoot. If we don't overshoot then just move the full distance (according to speed)
        if distance <= self.drone_speed:  # Here we go straight to the truck

            self.consume_battery(distance)

            # Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance

            if not self.on_truck:
                self.home_truck.load_drone(self)

        else:  # Here we move the full length
            self.en_route = True
            self.on_truck = False
            distance_traveled = self.position.get_point_on_line(
                self.home_truck.position, self.drone_speed
            )

            self.consume_battery(distance_traveled)

            # Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance_traveled

    def go_to_position(self, position: Position):
        """
        This function moves the drone towards a certain position.
        If we reach the destination we return True, otherwise we return false
        """
        distance = get_euclidean_distance(self.position, position)
        self.en_route = True
        self.on_truck = False
        if distance < self.drone_speed:

            self.consume_battery(distance)

            # Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance

            self.position.x = position.x
            self.position.y = position.y
            self.en_route = False

            return True
        else:

            distance_traveled = self.position.get_point_on_line(
                position, self.drone_speed
            )
            self.consume_battery(distance_traveled)

            # Here we add the distance travelled now to the total distance travelled
            self.total_travel_distance += distance_traveled

            return False
        return False

    def consume_battery(self, distance: float):
        """
        This function is called whenever the drone moves.
        We subtract self.active_battery_consume for each unit of distance it travelled
        """
        if distance > 0:
            if self.battery - distance * (self.active_battery_consume) < 0:
                self.battery = 0
            else:
                self.battery = self.battery - distance * (self.active_battery_consume)

    def steadystate_consumption(self):
        """
        There is a constant drainage of the battery equal to self.cost/4 every second
        """
        # TODO bring this back maybe
        if self.battery - self.passive_battery_consume < 0:
            self.battery = 0
        else:
            self.battery -= self.passive_battery_consume
        # pass

    def get_range_of_reach(self):
        """
        This function is used to calculate the maximum distance our drone can travel with its
        current battery charge
        """

        # What is the maximum distance our drone can travel with its current battery level
        return (self.battery / self.active_battery_consume) * self.drone_speed
        # return float('inf')

    def get_max_range(self):
        return (100 / self.active_battery_consume) * self.drone_speed

    def deliver_next_package(self, unserviced_customers: List[Customer]):
        """
        Move towards the next customer in our list.
        If we have no more customers to deliver to we go_to_home_truck()
        """
        # Here we check if the drone is active. If so, we add 1 second to its active time
        # A drone is active if it is moving somewhere OR if it dropping off a package
        # In other words a drone is active when it is NOT on a truck
        # TODO this logic shouldn't be here
        if self.position != self.home_truck.position:
            self.total_active_time += 1

        # First check if we have any packages to deliver. If that is the case check if we can reach
        # the customers using our current charge. If so then deliver.
        if len(self.packages) > 0:

            # Here we check if we have the necessary battery to perform the delivery
            if self.on_truck and not self.can_make_trip(
                start_position=self.home_truck.position,
                packages=self.packages,
                charge=self.battery,
            ):
                # We want to wait some amount of time for this battery swap
                self.swap_battery()
                self.battery_swap_timer += 1
                return

            if self.battery_swap_timer == DRONE_BATTERY_SWAP_DELAY:
                self.battery_swap_timer = 0
            elif self.battery_swap_timer > 0:
                self.battery_swap_timer += 1
                return

            arrived = False

            # If the drone is on the truck we leave the trucks
            if self.on_truck:
                self.home_truck.no_drones_currently_on_truck -= 1

            # Move towards the customer position
            arrived = self.go_to_position(self.packages[0].customer.position)

            # This allows us to deliver all the packages at once if we arrive at a certain customer
            if arrived:

                self.en_route = False
                # Once we arrive at a customer, we want to perform a 2 minute delay (120 steps)
                self.delay_variable += 1
                self.total_delay_time += 1
                self.waiting = True

                if self.delay_variable == 120:
                    self.delay_variable = 0
                    self.en_route = True

                    self.waiting = False

                    # This is one of the packages we are delivering to the customer
                    package = self.packages[0]

                    this_customers_packages: List[Package] = [
                        package
                        for package in self.packages
                        if package.customer.position == self.position
                    ]
                    customer_we_are_now_on: Customer = this_customers_packages[
                        0
                    ].customer

                    for customer_package in this_customers_packages:
                        customer_package.delivered = True

                    # If we have arrived then we add 1 to the number of dropoffs this customer has
                    customer_we_are_now_on.no_dropoffs += 1

                    # decrement the number of customers the drone has left to deliver this trip
                    self.no_customers_in_list -= 1

                    # If the inital time hasn't been set yet then this is the first package to be delivered
                    if customer_we_are_now_on.time_initial == -1:
                        customer_we_are_now_on.time_initial = package.waiting_time
                    old_length = len(self.packages)

                    self.packages[:] = [
                        package
                        for package in self.packages
                        if package.customer.position != self.position
                    ]

                    customer_we_are_now_on.no_of_packages -= old_length - len(
                        self.packages
                    )

                    assert customer_we_are_now_on.no_of_packages >= 0

                    if customer_we_are_now_on.no_of_packages == 0:
                        # The customer has now been fully serviced
                        unserviced_customers.remove(customer_we_are_now_on)
                        # Since all packages have been delivered this is the final time of the span
                        customer_we_are_now_on.time_final = package.waiting_time

                    # Also add the total package waiting time for the packages delivered
                    self.home_truck.total_package_waiting_time += (
                        package.waiting_time * (old_length - len(self.packages))
                    )

        # If we have no more packages, go back to the home truck
        else:

            self.go_to_home_truck()
            if not self.en_route:
                if self.home_truck.no_packages > 0:
                    self.load_package()

    def swap_battery(self):
        """
        When the drone wants to deliver but cant due to insufficient battery, we perform a battery swap.
        """
        self.no_battery_swaps += 1
        self.battery = 100

    def charge(self):
        """
        While the drone is on the truck we increase its charge every step by self.charge_increase
        """
        if self.on_truck:
            if self.battery + self.charge_increase < 100:
                self.battery += self.charge_increase
            else:
                self.battery = 100


class Package:

    def __init__(
        self, customer: Customer, mass: float = 10, height: float = 5, width: float = 5
    ):
        self.customer: Customer = customer
        self.mass: float = mass
        self.height: float = height
        self.width: float = width
        self.waiting_time: int = 0
        self.delivered: bool = False

    def __repr__(self):
        return (
            f"Package(customer={self.customer}, mass={self.mass}, height={self.height}, "
            f"width={self.width}, waiting_time={self.waiting_time}, delivered={self.delivered})"
        )


class Position:

    def __init__(self, x: int, y: int):
        # Suppose the location of a truck, drone or house is defined by (x, y)
        self.x: int = x
        self.y: int = y

    def get_position_info(self) -> Dict[str, int]:
        """Return a dictionary with position coordinates.

        Returns:
            Dict[str, int]: Return a dictionary where the key is the coordinate name,
            and the value is the coordinate value.
        """
        d = {"x": self.x, "y": self.y}
        return d

    def __str__(self):
        return str(self.x) + ", " + str(self.y)

    def __repr__(self):
        return str(self)

    def __eq__(self, pos: Position):
        return self.x == pos.x and self.y == pos.y

    def __ne__(self, pos: Position):
        return not self.__eq__(pos)

    def __sub__(self, position2: Position):
        return Position(self.x - position2.x, self.y - position2.y)

    def _normalize_position(self):
        """
        Here we convert a vector into a unit vector
        """
        norm = (self.x**2 + self.y**2) ** 0.5
        self.x /= norm
        self.y /= norm

    # In order to get a position d distance away from position1 on the straight line between position
    # one and position2 we use this method https://math.stackexchange.com/questions/175896/finding-a-point-along-a-line-a-certain-distance-away-from-another-point
    # 1) Subtract the two positions (using the ordinary method) v = position2 - position1
    # 2) Normalize v --> u
    # 3) new position = position1 + du

    def get_point_on_line(self, position2: Position, distance: float):
        """
        In this function we move a distance of "distance" towards position2.
        We return the distance travelled.
        """
        v = position2 - self

        previous_position = Position(self.x, self.y)

        v._normalize_position()
        self.x = int(self.x + distance * v.x)
        self.y = int(self.y + distance * v.y)

        return get_euclidean_distance(previous_position, self)


class Customer:

    def __init__(
        self, position: Position, residence_type: str, no_of_packages: int = 0
    ):
        # Location will be a class of type position (defined by x and y)
        self.position: Position = position
        # residence_type will just be a string ("apt" or "house")
        self.residence_type: str = residence_type
        # Here we store the number of packages not yet delivered to the customer
        # If everything has been delivered this variable will be 0
        self.no_of_packages: int = no_of_packages
        self.packages: List[Package] = []
        # Here we store the original number of packages
        # After all packages have been delivered this maintains its original value
        self.original_no_packages: int = no_of_packages
        self.colour: str = "not_yet"

        # This tells us how many packages are still on the truck
        self.no_packages_still_on_truck: int = 0

        # Information about delivery span
        # Span is the amount of time between the first and final packages being delivered
        # Time inital and time final are the times the inital and final packages were delivered respectively
        self.time_initial: int = -1
        self.time_final: int = -1

        # This is the number of times are drone arrives at this customer
        self.no_dropoffs: int = 0

        # The time customers wait until all of their packages have been delivered
        self.customer_waiting_time: int = 0

    def __repr__(self):
        return (
            f"Customer(position={self.position}, residence_type={self.residence_type}, "
            f"no_of_packages={self.no_of_packages}, original_no_packages={self.original_no_packages}, "
            f"colour={self.colour}, no_packages_still_on_truck={self.no_packages_still_on_truck}, "
            f"time_initial={self.time_initial}, time_final={self.time_final}, "
            f"no_dropoffs={self.no_dropoffs}, customer_waiting_time={self.customer_waiting_time})"
        )

    def get_customer_info(self) -> Dict[str, Union[int, str]]:
        # TODO convert this to a json method
        d: Dict[str, int] = self.position.get_position_info()

        customer_info: Dict[str, Union[int, str]] = {
            "x": d["x"],
            "y": d["y"],
            "residence_type": self.residence_type,
            "no_of_packages": self.no_of_packages,
        }

        return customer_info

    def add_package(self, package: Package):
        """
        This function adds a package to our customer
        """
        self.no_of_packages += 1
        self.original_no_packages += 1
        self.no_packages_still_on_truck += 1
        self.packages.append(package)


class Truck:

    no_of_drones = 0

    # We might just want to inherit from a superclass...
    def __init__(
        self,
        position: Position,
        strategy: Strategy,
        cost: float = 0.0006,
        truck_speed: int = 8,
        truck_id: Optional[int] = None,
        total_no_drones: int = 0,
    ):

        # Strategy parameters
        self.strategy: Strategy = strategy

        self.cost: float = cost
        self.truck_speed: int = truck_speed
        self.position: Position = position

        # Each truck has a number of drones.
        # These two attributes pertain to the drones CURRENTLY ON THE TRUCK
        self.current_drones_on_truck: List[Drone] = []
        self.no_drones_currently_on_truck: int = 0

        # This attribute pertains to the drones wherever they may be
        self.total_no_drones_belonging_to_truck: int = total_no_drones

        self.truck_id: Optional[int] = truck_id

        self.packages: Dict = {}
        self.no_packages: int = 0

        # List of cluster centroids truck must deliver to
        self.cluster_centroids: List[Tuple[int, ...]] = []

        self.is_moving: bool = False

        # This is the cluster the truck is currently delivering from
        self.current_cluster: Tuple[int, ...]

        self.total_package_waiting_time: int = (
            0  # Here we store the total time for each package to be delivered
        )
        self.total_customer_waiting_time: int = (
            0  # Here we store the total time for each customer to be fully serviced
        )

        # Here we store the total distance travelled by the truck throughout the run
        self.total_travel_distance: float = 0

        # Here we store the total time this truck spent in a cluster
        self.total_time_in_cluster: float = 0

        # TODO remove customers from here once there packages are delivered
        self.priority_customers: Set[Customer] = set()

    def load_package(self, package: Package, cluster: Tuple[int, ...]):
        """
        This function adds a package to the cluster list specified in the truck dict.
        If the cluster doesnt exist we add the cluster to the dict and then add the package
        """
        if cluster not in self.packages:
            self.packages[cluster] = []
        self.packages[cluster].append(package)
        self.no_packages += 1

    def sort_packages(self, how: str):
        """
        In this function we sort the packages in the truck dict either according to:
            1) The distance from the center of the cluster, or
            2) The number of packages the customer has
        """
        if (
            how == "distance"
        ):  # Here we sort the packages according to the distance from the center of the cluster

            for cluster, package_list in self.packages.items():
                cluster_position: Position = Position(cluster[0], cluster[1])
                self.packages[cluster] = sorted(
                    package_list,
                    key=lambda x: get_euclidean_distance(
                        x.customer.position, cluster_position
                    ),
                    reverse=True,
                )

        elif (
            how == "no_packages"
        ):  # Here we sort the packages according to the number of packages of the customer
            for cluster, package_list in self.packages.items():
                self.packages[cluster] = sorted(
                    package_list,
                    key=lambda x: (
                        x.customer.no_packages_still_on_truck,
                        x.customer.position.x,
                        x.customer.position.y,
                    ),
                )

    def select_initial_package(self, strategy: Strategy) -> Package:
        # Only use priority customers for MPA strategies
        use_priority: bool = "mpa" in strategy.lower()
        if use_priority:
            priority_customer_packages: List[Package] = [
                package
                for package in self.packages[self.current_cluster]
                if package.customer in self.priority_customers
            ]
        else:
            priority_customer_packages = []

        if strategy in (
            Strategy.FARTHEST_PACKAGE_FIRST,
            Strategy.FARTHEST_PACKAGE_FIRST_MPA,
        ):

            if use_priority and len(priority_customer_packages) > 0:
                package = get_farthest_package(
                    position=self.position, packages=priority_customer_packages
                )
            else:
                package = get_farthest_package(
                    position=self.position, packages=self.packages[self.current_cluster]
                )
        elif strategy in (
            Strategy.MOST_PACKAGES_FIRST,
            Strategy.MOST_PACKAGES_FIRST_MPA,
        ):
            if use_priority and len(priority_customer_packages) > 0:
                package = get_package_for_customer_with_most_packages(
                    position=self.position, packages=priority_customer_packages
                )
            else:
                package = get_package_for_customer_with_most_packages(
                    position=self.position, packages=self.packages[self.current_cluster]
                )
        else:
            raise ValueError(
                f"Strategy provided of {strategy} does not match any strategies accounted for."
            )

        return package

    def load_initial_package(self, drone: Drone, strategy: Strategy):
        package: Package = self.select_initial_package(strategy=strategy)
        if package is None:
            raise ValueError("Initial package is None")

        if not drone.can_make_trip(
            start_position=self.position, packages=[package], charge=100
        ):
            raise ValueError("Cannot make trip with initial package")

        self.packages[self.current_cluster].remove(package)
        self.no_packages -= 1
        drone.packages.append(package)
        package.customer.no_packages_still_on_truck -= 1
        drone.no_customers_in_list += 1

    def select_any_package_for_customer(
        self, customer: Customer, packages: List[Package]
    ) -> Optional[Package]:
        for package in packages:
            if package.customer == customer:
                return package
        return None

    def get_next_package_mpa(
        self, sorted_packages: List[Package], drone: Drone
    ) -> Package:
        # In MPA we want to see if we are disrupting the optimal delivery...
        # If we are we will skip this package
        next_package: Package = None
        for package in sorted_packages:
            if will_delivering_this_package_disrupt_optimal_no_dropoffs(
                total_drone_capacity=drone.capacity,
                remaining_drone_capacity=drone.capacity - len(drone.packages),
                package=package,
            ):
                # Go to next closest package
                # We want to continue to do this until we run out of packages
                # If we run out of packages we will just deliver to the closest
                # If we can't deliver because of max charge things we will just do closest
                continue
            else:
                if drone.can_make_trip(
                    start_position=self.position,
                    packages=drone.packages + [package],
                    charge=100,
                ):
                    next_package: Package = package
                break
        if not next_package:
            next_package = sorted_packages[0]  # Closest package

        return next_package

    def get_next_package(
        self,
        last_assigned_package: Package,
        packages: List[Package],
        strategy: str,
        drone: Drone,
    ) -> Package:

        # If we have just loaded a customer's package and that same customer still has more packages then we will load them...
        any_customer_package = self.select_any_package_for_customer(
            customer=last_assigned_package.customer, packages=packages
        )

        if any_customer_package:
            return any_customer_package

        # If the last assigned package's customer has no more packages on the truck we will begin looking around.
        if not any_customer_package:
            sorted_packages_from_this_one: List[Package] = sorted(
                packages,
                key=lambda x: get_euclidean_distance(
                    last_assigned_package.customer.position, x.customer.position
                ),
            )

            # In MPA we want to see if we are disrupting the optimal delivery...
            # If we are we will skip this package
            if "mpa" in strategy.lower():
                next_package: Package = self.get_next_package_mpa(
                    sorted_packages=sorted_packages_from_this_one, drone=drone
                )
                # Prioritise this customer!
                self.priority_customers.add(next_package.customer)

            else:
                next_package: Package = sorted_packages_from_this_one[0]  # Closest one

        return next_package

    def load_drone_package(self, drone: Drone):
        """
        In this function we assign packages to a drone according the strategy we have specified in self.strategy.
        """
        # The only thing different between the strategies is how we assign the initial drone. everything else is the same.

        if len(self.packages[self.current_cluster]) == 0:
            return

        # Assign initial package
        self.load_initial_package(drone=drone, strategy=self.strategy)

        # Do everything else
        while len(drone.packages) < drone.capacity:
            if len(self.packages[self.current_cluster]) > 0:
                package_to_deliver = self.get_next_package(
                    last_assigned_package=drone.packages[-1],
                    packages=self.packages[self.current_cluster],
                    strategy=self.strategy,
                    drone=drone,
                )

                if drone.can_make_trip(
                    start_position=self.position,
                    packages=drone.packages + [package_to_deliver],
                    charge=100,
                ):
                    self.packages[self.current_cluster].remove(package_to_deliver)
                    self.no_packages -= 1
                    drone.packages.append(package_to_deliver)
                    package_to_deliver.customer.no_packages_still_on_truck -= 1
                    drone.no_customers_in_list = get_no_customers_from_packages(
                        packages=drone.packages
                    )
                else:
                    break
            else:
                break

    def add_cluster_centroid(self, pos: Tuple[int, ...]):
        """
        Here we add one of our cluster centroids to the list of cluster centroids on the truck as a tuple
        """
        self.cluster_centroids.append(pos)

    def get_truck_info(self) -> Dict[str, Union[int, float]]:
        # TODO convert this to a json method
        d = self.position.get_position_info()
        truck_info: Dict[str, Union[int, float]] = {
            "x": d["x"],
            "y": d["y"],
            "cost": self.cost,
            "no_of_drones": self.no_of_drones,
        }

        return truck_info

    def move_towards_position(self, position: Position):
        """
        In this function we move the truck towards "position" in a manhattan manner (straight lines only).
        We return True if the truck reached the destination and False otherwise
        """

        # In this function we want to actually move the truck in addition to adding the distance travelled to self.total_distance_travelled
        # We do this by recording the old position then calculating the distance to the new position
        old_position = Position(self.position.x, self.position.y)

        self.is_moving = True
        # This whole complicated function is to ensure the truck moves like it's in Manhattan
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
                # For now we just start with the x
                # Might want to do it in a smarter manner later
                units_to_move -= abs(x_difference)
                self.position.x = position.x
                if y_difference < 0:
                    self.position.y -= units_to_move
                else:
                    self.position.y += units_to_move

        for drone in self.current_drones_on_truck:
            if drone.on_truck:
                drone.position.x = self.position.x
                drone.position.y = self.position.y

        # Here we calculate the distance travelled in this step and add it to the run
        distance_traveled = get_manhattan_distance(self.position, old_position)
        self.total_travel_distance += distance_traveled

        # Here we check if the truck reached the destination
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

        # In the first if statement we check if we have finished all clusters. If so we return to the warehouse.
        # We can say that we have finished all our clusters if we have no cluster centroids in our list
        # AND all drones are on the truck AND we have no packages left
        if (
            len(self.cluster_centroids) == 0
            and self.no_drones_currently_on_truck
            == self.total_no_drones_belonging_to_truck
            and self.no_packages == 0
        ):
            # If we're done move towards the warehouse
            warehouse_position = Position(1000, 1000)
            arrived = self.move_towards_position(warehouse_position)
        elif len(self.cluster_centroids) > 0 and self.cluster_finished():
            self.current_cluster = self.cluster_centroids[-1]
            cluster_position = Position(
                self.current_cluster[0], self.current_cluster[1]
            )
            arrived = self.move_towards_position(cluster_position)

            if arrived:
                self.cluster_centroids.pop()
        else:
            cluster_position = Position(
                self.current_cluster[0], self.current_cluster[1]
            )
            self.move_towards_position(cluster_position)

        # Here we also want to calculate how much time our trucks are in clusters
        # We do this by check if our current position is the same as self.current_cluster
        if self.position == Position(self.current_cluster[0], self.current_cluster[1]):
            self.total_time_in_cluster += 1

    def cluster_finished(self):
        """
        In this function we check if we have finished the current cluster.
        Return True if we have and False otherwise.
        """
        # Return true if we have delivered all packages in cluster
        if self.total_no_drones_belonging_to_truck != self.no_drones_currently_on_truck:
            return False

        if (
            self.current_cluster != None
            and len(self.packages[self.current_cluster]) != 0
        ):
            return False

        # Make sure none of the drones are carrying packages
        drones_delivered = True
        for drone in self.current_drones_on_truck:
            if len(drone.packages) != 0:
                drones_delivered = False

        return drones_delivered

    def load_drone(self, drone: Drone):
        """
        In this function we load a drone onto the truck
        """
        drone.position.x = self.position.x
        drone.position.y = self.position.y

        self.current_drones_on_truck.append(drone)
        self.no_drones_currently_on_truck += 1

        drone.en_route = False
        drone.on_truck = True


class Warehouse:
    def __init__(self, position: Position):
        self.position: Position = position

    def cluster_and_colour(
        self, customers: List[Customer], trucks: List[Truck], no_clusters: int
    ):
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

        df = pd.DataFrame({"x": customer_x, "y": customer_y})

        kmeans = KMeans(n_clusters=no_clusters, random_state=42)
        cluster_labels = kmeans.fit_predict(df)

        centroids = kmeans.cluster_centers_

        colours = {
            0: "#8B0000",
            1: "#DB7093",
            2: "#FFA500",
            3: "#BDB76B",
            4: "#7B68EE",
            5: "#008080",
            6: "#CD5C5C",
            7: "#FFC0CB",
            8: "#FFA07A",
            9: "#FFD700",
            10: "#E6E6FA",
            11: "#ADFF2F",
            12: "#00FFFF",
            13: "#FFF8DC",
            14: "#DCDCDC",
            15: "#191970",
            16: "#800000",
            17: "#FFE4E1",
            18: "#000000",
            19: "#5489fc",
        }

        # Here we just give all the packages to each truck based on the cluster (not sorted)

        no_trucks = len(trucks)

        # This dictionary will have the cluster_label as the index, with the truck index as the value
        truck_for_cluster = {cluster: -1 for cluster in range(no_clusters)}

        # Here we distribute the clusters to the trucks
        i = 0
        for j in range(no_clusters):
            trucks[i].add_cluster_centroid(tuple(centroids[j]))
            truck_for_cluster[j] = i
            i = (i + 1) % no_trucks

        # Here we assign colours to each customer and distribute the packages to the trucks
        for cluster_label, customer in zip(cluster_labels, customers):
            # customer.colour = colours[cluster_label]
            truck_idx = truck_for_cluster[cluster_label]
            for package in customer.packages:
                trucks[truck_idx].load_package(package, tuple(centroids[cluster_label]))

        # Give a random default cluster to begin with
        for truck in trucks:
            truck.current_cluster = truck.cluster_centroids[-1]

        # According to the strategy we will sort the trucks accordingly
        # Currently the same strategy is shared by all the trucks
        if trucks[0].strategy in (
            "farthest_package_first",
            "closest_package_first",
            "farthest_package_first_MPA",
        ):
            # Here we sort the packages in each truck based on the distance from the cluster centroid (Descending)
            for truck in trucks:
                truck.sort_packages("distance")
        elif trucks[0].strategy == "most_packages_first":
            # Here we sort the packages in each truck based on the number of packages the package's customer has
            for truck in trucks:
                truck.sort_packages("no_packages")


def get_euclidean_distance(position1: Position, position2: Position) -> float:
    """
    Return the euclidean distance between two points
    """
    return ((position2.y - position1.y) ** 2 + (position2.x - position1.x) ** 2) ** 0.5


def get_manhattan_distance(position1: Position, position2: Position) -> float:
    """
    Return the manhattan distance between two points
    """
    return abs(position1.x - position2.x) + abs(position1.y - position2.y)


def customer_not_already_in_list(
    customer_package: Package, package_list: List[Package]
) -> int:
    """
    Return 0 if the customer for customer_package is already in package_list and return 1 otherwise
    """
    for package in package_list:
        if customer_package.customer.position == package.customer.position:
            return 0
    return 1


class Strategy(str, Enum):
    MOST_PACKAGES_FIRST_MPA = "most_packages_first_MPA"
    MOST_PACKAGES_FIRST = "most_packages_first"
    FARTHEST_PACKAGE_FIRST = "farthest_package_first"
    FARTHEST_PACKAGE_FIRST_MPA = "farthest_package_first_MPA"


def get_next_closest_package(package: Package, packages: List[Package]) -> Package:
    min_distance = float("inf")
    closest_package = None
    for other_package in packages:
        if other_package == package:
            continue
        distance = get_euclidean_distance(
            other_package.customer.position, package.customer.position
        )
        if distance < min_distance:
            min_distance = distance
            closest_package = other_package

    return closest_package


def get_total_trip_distance(start_position: Position, packages: List[Package]) -> float:
    total_delivery_distance: float = get_euclidean_distance(
        start_position, packages[0].customer.position
    )
    for i in range(1, len(packages)):
        total_delivery_distance += get_euclidean_distance(
            packages[i - 1].customer.position, packages[i].customer.position
        )

    total_delivery_distance += get_euclidean_distance(
        packages[-1].customer.position, start_position
    )
    return total_delivery_distance


def get_no_customers_from_packages(packages: List[Package]) -> int:
    unique_customers = set()
    for package in packages:
        unique_customers.add(package.customer)

    return len(unique_customers)


def get_farthest_package(position: Position, packages: List[Package]) -> Package:
    max_distance = -1
    farthest_package = None

    for package in packages:
        distance = get_euclidean_distance(position, package.customer.position)
        if distance > max_distance:
            max_distance = distance
            farthest_package = package

    return farthest_package


def get_closest_package(position: Position, packages: List[Package]) -> Package:
    min_distance = float("inf")
    closest_package = None

    for package in packages:
        distance = get_euclidean_distance(position, package.customer.position)
        if distance < min_distance:
            min_distance = distance
            closest_package = package

    return closest_package


def get_package_for_customer_with_most_packages(
    position: Position, packages: List[Package]
) -> Package:

    max_no_packages: int = -1
    customer_with_max_packages: Customer
    packages_for_max_customer_on_truck: List[Package] = []

    for package in packages:
        if package.customer.original_no_packages > max_no_packages:
            max_no_packages = package.customer.original_no_packages
            customer_with_max_packages = package.customer

    for package in packages:
        if package.customer == customer_with_max_packages:
            packages_for_max_customer_on_truck.append(package)

    farthest_package: Package = get_farthest_package(
        position=position, packages=packages_for_max_customer_on_truck
    )

    return farthest_package


def ceildiv(a, b):
    return -(a // -b)


def will_delivering_this_package_disrupt_optimal_no_dropoffs(
    total_drone_capacity: int, remaining_drone_capacity: int, package: Package
) -> bool:

    no_of_packages_on_truck_for_this_package: int = package.customer.no_of_packages

    optimal_no_dropoffs: int = ceildiv(
        no_of_packages_on_truck_for_this_package, total_drone_capacity
    )

    assert optimal_no_dropoffs >= 1

    # Packages left if we deliver this one
    no_packages_left_if_delivered = max(
        no_of_packages_on_truck_for_this_package - remaining_drone_capacity, 0
    )

    # Calculate the new optimal number of dropoffs if we deliver this package
    new_optimal_no_dropoffs = ceildiv(
        no_packages_left_if_delivered, total_drone_capacity
    )

    if new_optimal_no_dropoffs > optimal_no_dropoffs:
        raise ValueError(
            f"{total_drone_capacity}, {remaining_drone_capacity}, {no_of_packages_on_truck_for_this_package}"
        )

    # Check if delivering this package will increase the optimal number of dropoffs
    return new_optimal_no_dropoffs == optimal_no_dropoffs
