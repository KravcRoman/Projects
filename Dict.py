#1
a = input().split()
b = 0
for i in a:
    if a[0:b].count(i) >= 0:
        b+=1
        print(a[0:b].count(i) - 1)

#2
dict1 = {}
for i in range(int(input())):
    dict1.update(dict([input().split()]))
b = input()
for key, val in dict1.items():
    if b == val:
        print(key)
    elif b == key:
        print(val)

#3
n = int(input())
d = {}
c = {}
b = 0
for j in range(n):
    first, second = input().split()
    if first in d:
        if first in c:
            if len(c) > 0:
                c[first] = int(c[first]) + int(second)
            elif len(c) < 2:
                c[first] = int(d[first]) + int(second)
            else:
                c[first] = int(d[first]) + int(second)
        else: c[first] = int(d[first]) + int(second)
    d[first] = second
d.update(c)
for key, val in sorted(d.items()):
    print(key, val)

#4
string = int(input())
counter = {}
all=[]
repeated =[]
for i in range(string):
    all+=input().split()
all = sorted(all)
for word in all:
    counter[word] = counter.get(word, 0) + 1
    repeated.append(counter[word] - 1)
print(all[repeated.index(max(repeated))])

#5
counter = {}
c = {}
for i in range(int(input())):
    q = input().split()
    for word in q[:1]:
        for key in q[1:]:
            counter.setdefault(word,[]).append(key)
for i in range(int(input())):
    q = input().split()
    for word in q[:1]:
        for key in q[1:]:
            if word == 'execute':
                c.setdefault(key,[]).append('X')
                if 'X' in counter[key]:
                    print('OK')
                else:
                    print('Access denied')
            else:
                c.setdefault(key,[]).append(str.upper(word[0]))
                if str.upper(word[0]) in counter[key]:
                    print('OK')
                else:
                    print('Access denied')

#6
c = {}
for i in range(int(input())):
    q = input().split()
    for word in q:
        c[word] = c.get(word, 0) + 1
for j in range(len(c)):
    max_count = max(c.values())
    most_frequent = [k for k, v in c.items() if v == max_count]
    print(min(most_frequent))
    c.pop(min(most_frequent))

#7
file_p = {}
for i in range(int(input())):
    q = input().split()
    for word in q[:1]:
        for key in q[1:]:
            file_p.setdefault(word,[]).append(key)
for i in range(int(input())):
    c = input()
    f = list(file_p.values())
    fe = list(file_p.keys())
    for co in range(len(list(file_p.values()))):
        if c in f[co]:
            print(fe[co])

#8
motherland = {}
for i in range(int(input())):
    country, q, *cities = input().split()
    for city in cities:
        if ',' in city:
            city = city[:-1]
            motherland.setdefault(city,[]).append(country)
        else:
            motherland.setdefault(city,[]).append(country)
f = sorted(list(motherland.keys()))
F = list(motherland.values())
print(len(f))
for i in range(len(motherland)):
    w = f[i]
    print(f[i] + ' ' +  q + ' ', end ='')
    if len(motherland.get(w)) > 1:
        print(*motherland.get(w), sep=', ')
    else:
        print(*motherland.get(w))

#9
motherland = {}
c = {}
b = 0
N = int(input())
for i in range(N):
    country = input().split()
    for word in country:
        motherland[word] = motherland.get(word, 0) + 1
F = list(motherland.keys())
f = list(motherland.keys())
f+=list(map(str.upper, f))
f+=list(map(str.lower, f))
for i in range(1):
    q = input().split()
    for co in range(len(q)):
        if q[co] in F:
            continue
        if str.islower(q[co]) == True:
            b+=1
        elif len(q[co]) > 1 and str.isupper(q[co]) == True:
            b+=1
        elif len(q[co]) == 1 and str.isupper(q[co]) == True:
            continue
        elif str.upper(q[co]) not in f:
            continue
        elif str.lower(q[co]) not in f:
            continue
        else:
            b+=1
print(b)

#10
from collections import defaultdict
from sys import stdin

clients = defaultdict(lambda: defaultdict(int))
for line in stdin.readlines():
    client, thing, value = line.split()
    clients[client][thing] += int(value)
        
for client in sorted(clients):
    print(client + ':')
    for thing in sorted(clients[client]):
        print(thing, clients[client][thing])

#11
def height(man):
    if man not in p_tree:
        return 0
    else:
        return 1 + height(p_tree[man])

p_tree = {}
n = int(input())
for i in range(n - 1):
    child, parent = input().split()
    p_tree[child] = parent

heights = {}
for man in set(p_tree.keys()).union(set(p_tree.values())):
    heights[man] = height(man)

for key, value in sorted(heights.items()):
    print(key, value)
