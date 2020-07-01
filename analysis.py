import matplotlib.pyplot as plt
import numpy as np


lines_CPF = open('results/result_closest_package_first_200_3.txt', 'r').readlines()
lines_FPF = open('results/result_farthest_package_first_200_3.txt', 'r').readlines()
lines_MPF = open('results/result_most_packages_first_200_3.txt', 'r').readlines()
lines_FPF_MPA = open('results/result_farthest_package_first_MPA_200_3.txt', 'r').readlines()


steps_FPF = []
steps_CPF = []
steps_MPF = []
steps_FPF_MPA = []

drone_travel_distance_FPF = []
drone_travel_distance_CPF = []
drone_travel_distance_MPF = []
drone_travel_distance_FPF_MPA = []

utilization_FPF = []
utilization_CPF = []
utilization_MPF = []
utilization_FPF_MPA = []

for line in lines_FPF_MPA[1:]:
    steps_FPF_MPA.append(int(line.split(',')[0]))
    drone_travel_distance_FPF_MPA.append(float(line.split(',')[1]))
    utilization_FPF_MPA.append(float(line.split(',')[2]))
for line in lines_FPF[1:]:
    steps_FPF.append(int(line.split(',')[0]))
    drone_travel_distance_FPF.append(float(line.split(',')[1]))
    utilization_FPF.append(float(line.split(',')[2]))
for line in lines_CPF[1:]:
    steps_CPF.append(int(line.split(',')[0]))
    drone_travel_distance_CPF.append(float(line.split(',')[1]))
    utilization_CPF.append(float(line.split(',')[2]))
for line in lines_MPF[1:]:
    steps_MPF.append(int(line.split(',')[0]))
    drone_travel_distance_MPF.append(float(line.split(',')[1]))
    utilization_MPF.append(float(line.split(',')[2]))

x = np.arange(10) #Same as number of runs
ax1 = plt.subplot(111)
ax1.bar(x - 0.2, steps_FPF, color='r', align='center', label = 'FPF', width=0.2)
ax1.bar(x, steps_MPF, color = 'b', align = 'center', label = 'MPF', width = 0.2)
# ax1.bar(x + 0.2, steps_CPF, color='g', align='center', label='CPF', width=0.2)
ax1.bar(x + 0.2, steps_FPF_MPA, color='g', align='center', label='MPA', width=0.2)
plt.xlabel('run number')
plt.ylabel('number of steps till done')
plt.legend(loc = 'lower right')
plt.show()

ax2 = plt.subplot(111)
ax2.bar(x - 0.2, drone_travel_distance_FPF, color = 'r', align = 'center', label = 'FPF', width = 0.2)
ax2.bar(x, drone_travel_distance_MPF, color = 'b', align = 'center', label = 'MPF', width = 0.2)
# ax2.bar(x + 0.2, drone_travel_distance_CPF, color = 'g', align = 'center', label = 'CPF', width = 0.2)
ax2.bar(x + 0.2, drone_travel_distance_FPF_MPA, color = 'g', align = 'center', label = 'MPA', width = 0.2)


plt.xlabel('run number')
plt.ylabel('total drone travel distance')
plt.legend(loc='lower right')
plt.show()


ax3 = plt.subplot(111)
ax3.bar(x - 0.2, utilization_FPF, color = 'r', align = 'center', label = 'FPF', width = 0.2)
ax3.bar(x, utilization_MPF, color = 'b', align = 'center', label = 'MPF', width = 0.2)
# ax3.bar(x + 0.2, utilization_CPF, color = 'g', align = 'center', label = 'CPF', width = 0.2)
ax3.bar(x + 0.2, utilization_FPF_MPA, color = 'g', align = 'center', label = 'MPA', width = 0.2)

plt.xlabel('run number')
plt.ylabel('drone utilization rate')
plt.legend(loc='lower right')
plt.show()