#1
n = input()
a = []
for i in range(int(n[0])):
    a.append([int(j) for j in input().split()])
def large(a): 
    max = a[0]
    for ele in a:
        if ele > max:
           max = ele
    return max
for i in range(int(n[0])):
    if large(a[i]) == int(max(max(a))):
        print(i, a[i].index(max(a[i]))) 
        break

#2
n = int(input())
a = [['.'] * n for i in range(n)]
k = n-1
for i in range(n):
    for j in range(n):
        if j == k:
            a[i][j] = '*'
            k -= 1
        elif j == n//2:
            a[i][j] = '*'
        elif i == n//2:
            a[i][j] = '*'
        elif i < j:
            a[i][j] = '.'
        elif i > j:
            a[i][j] = '.'
        else:
            a[i][j] = '*' 
for row in a:
    print(' '.join([str(elem) for elem in row]))

#3
n, m = [int(i) for i in input().split()]
a = [['.'] * m for i in range(n)]
for i in range(n):
    for j in range(m):
        if i % 2 == 0 and j % 2 > 0:
            a[i][j] = '*'
        elif i % 2 > 0 and j % 2 == 0:
            a[i][j] = '*'
for row in a:
    print(' '.join(row))

#4
n = int(input())
a = [['0'] * n for i in range(n)]
for i in range(n):
    for j in range(n):
        if j < i:
            a[i][j] = i - j 
        elif j > i:
            a[i][j] = j - i
        a[i][i] = '0'
for row in a:
    print(' '.join([str(elem) for elem in row]))

#5
n = int(input())
a = [['0'] * n for i in range(n)]
k = int(n-1)
m = int(n-1)
for i in range(n):
    for j in range(n):
        if j == m:
            a[i][j] = 1 
            m-=1
        elif i > 0 and j >= k and j>m:
            a[i][j] = 2
            k-=1
for row in a:
    print(' '.join([str(elem) for elem in row]))
    