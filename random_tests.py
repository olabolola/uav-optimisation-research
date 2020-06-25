import UAV_RL_env.envs.celes as celes
import csv


lines_CPF = open('results/result_closest_package_first.txt', 'r').readlines()
lines_FPF = open('results/result_farthest_package_first.txt', 'r').readlines()
lines_RPF = open('results/result_random_package_first.txt', 'r').readlines()
lines_MPF = open('results/result_most_packages_first.txt', 'r').readlines()

steps_RPF = []
steps_FPF = []
steps_CPF = []
steps_MPF = []

drone_travel_distance_RPF = []
drone_travel_distance_FPF = []
drone_travel_distance_CPF = []
drone_travel_distance_MPF = []



drone_travel_distance_random_package_first = []
drone_travel_distance_farthest_package_first = []
drone_travel_distance_closest_package_first = []
drone_travel_distance_multiple_packages_most_packages_first = []

for line in lines_FPF[1:]:
    steps_FPF.append(int(line.split(',')[0]))
    # drone_travel_distance_RPF.append(int(line.split(',')[1]))
# print(steps_RPF)
# print(drone_travel_distance_RPF)
line = lines_FPF[1]
print(line)
line = line.split(',')
print(line)
print(int(line[0]))
print(float(line[1]))
