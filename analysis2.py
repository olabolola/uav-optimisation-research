import matplotlib.pyplot as plt
import numpy as np

# drone_capacity_values = (1, 2, 3)
# no_customers_values = (50, 100, 200, 500)

# results_FPF = open('results/result_farthest_package_first_50_3.txt', 'r').readlines()
# results_FPF = results_FPF[1]
# results_FPF_MPA = open('results/result_farthest_package_first_MPA_50_3.txt', 'r').readlines()
# results_FPF_MPA = results_FPF_MPA[1]
# results_MPF = open('results/result_most_packages_first_50_3.txt', 'r').readlines()
# results_MPF = results_MPF[1]

# print(results_FPF)
# print(results_FPF_MPA)
# print(results_MPF)

# x = np.arange(3)
bars = ('FPF', 'FPF_MPA', 'MPF')
# plt.bar(x, [float(results_FPF.split(',')[0]), float(results_FPF_MPA.split(',')[0]), float(results_MPF.split(',')[0])])
# plt.xticks(x, bars)

# plt.show()

r_FPF = []
r_FPF_MPA = []
r_MPF = []

y = np.arange(3)
for i in (1, 2, 3):
    results_FPF = open('results/result_farthest_package_first_200_' + str(i) + '.txt', 'r').readlines()
    results_FPF = results_FPF[1]
    results_FPF_MPA = open('results/result_farthest_package_first_MPA_200_' + str(i) + '.txt', 'r').readlines()
    results_FPF_MPA = results_FPF_MPA[1]
    results_MPF = open('results/result_most_packages_first_200_' + str(i) + '.txt', 'r').readlines()
    results_MPF = results_MPF[1]

    weow = 2
    r_FPF.append(float(results_FPF.split(',')[weow]))
    r_FPF_MPA.append(float(results_FPF_MPA.split(',')[weow]))
    r_MPF.append(float(results_MPF.split(',')[weow]))

plt.bar(y - 0.2, r_FPF, color = 'r', align = 'center', label = 'FPF', width = 0.2)
plt.bar(y, r_MPF, color = 'b', align = 'center', label = 'MPF', width = 0.2)
plt.bar(y + 0.2, r_FPF_MPA, color = 'g', align = 'center', label = 'FPF_MPA', width = 0.2)

plt.legend()
plt.xticks(y, ('1', '2', '3'))
plt.show()
