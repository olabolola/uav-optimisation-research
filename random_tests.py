f = open('saved_states/saved_state39.txt', 'r').readlines()

# print(int(f[1].split(',')[-1]) + 54)

# s = 0
# for i in f[1:]:
#     s += int(i.split(',')[-1])

# print(s)

s = sum([int(i.split(',')[-1]) for i in f[1:]])
print(s)