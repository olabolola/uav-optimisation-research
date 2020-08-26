# d = {1:'asd', 2:'asdaa'}
# for a in d:
#     print(a)
path = r'C:\Users\leola\Google Drive (salihjasimnz@gmail.com)\PSUT\Research\UAV optimization (1)\For_me\Testing-UAV-code\saved_states\\'
filename = path + 'saved_state_' + str(50) + '_' + str(1) + '.txt'
f = open(filename).readlines()
no_packages_total = 0
no_customers_per_no_packages = {no:0 for no in (2, 3, 4)}
for line in f[1:]:
    no_packages = int(line.split(',')[-1])
    no_packages_total += no_packages
    if no_packages != 1:
        no_customers_per_no_packages[no_packages] += no_packages
print(no_customers_per_no_packages)