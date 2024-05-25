from typing import List, Tuple, Dict
import csv
import math


def get_euclidean_distance(pos1: Tuple[int, int], pos2: Tuple[int, int]) -> float:
    """
    Return the Euclidean distance between two points.
    """
    return math.sqrt((pos2[1] - pos1[1]) ** 2 + (pos2[0] - pos1[0]) ** 2)


def read_packages_from_file(file_name: str) -> List[Tuple[int, int]]:
    """
    Read packages from a CSV file and return a list of tuples (x, y).
    """
    packages = []

    with open(file_name, "r") as f:
        reader = csv.reader(f)
        next(reader)  # Skip the header
        for row in reader:
            x, y, no_packages = int(row[0]), int(row[1]), int(row[2])
            for _ in range(no_packages):
                packages.append((x, y))

    return packages


def calculate_delivery_density(
    packages: List[Tuple[int, int]], radius: float
) -> Dict[Tuple[int, int], int]:
    """
    Calculate the delivery density for each package.
    """
    density = {}
    for package in packages:
        count = 0
        for other_package in packages:
            if package != other_package:
                distance = get_euclidean_distance(package, other_package)
                if distance <= radius:
                    count += 1
        density[package] = count
    return density


def calculate_average_density(density: Dict[Tuple[int, int], int]) -> float:
    """
    Calculate the average delivery density.
    """
    total_density = sum(density.values())
    average_density = total_density / len(density) if density else 0
    return average_density


if __name__ == "__main__":
    file_name = "saved_states/saved_state_400_0.csv"
    radius = 200.0  # Example radius

    packages = read_packages_from_file(file_name)
    delivery_density = calculate_delivery_density(packages, radius)
    average_density = calculate_average_density(delivery_density)

    print(f"The average delivery density is: {average_density}")
