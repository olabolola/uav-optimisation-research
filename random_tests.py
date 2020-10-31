a = ['a', 'a', 'b', 'c', 'd']
for j, i in enumerate(a):
    if j == 0:
        a.remove(i)
    print(i)