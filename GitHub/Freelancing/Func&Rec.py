#1
from math import sqrt
x1 = float(input())
y1 = float(input())
x2 = float(input())
y2 = float(input())
def distance(x1, y1, x2, y2):
    return sqrt((x1 - x2)**2 + (y1 - y2)**2)
print(distance(x1, y1, x2, y2))

#2
a = float(input())
n = int(input())
res = 1
def power(a, n):
    global res
    for i in range(abs(n)):
        res *= a
    if n >= 1:
        return res
    else: 
        return 1/res
print(power(a, n))

#3
def capitalize(word):
    first_letter_small = word[0]
    first_letter_big = chr(ord(first_letter_small) - ord('a') + ord('A'))
    return first_letter_big + word[1:]

source = input().split()
res = []
for word in source:
    res.append(capitalize(word))
print(' '.join(res))

#4
def power(a, n):
    if n == 0:
        return 1
    else:
        return a * power(a, n - 1)

print(power(float(input()), float(input())))

#5
def reverse():
    x = int(input())
    if x != 0:
        reverse()
    print(x)

reverse()

#6
def fib(n):
    global fib1, fib2
    if n == 0:
        return 1
    elif n != 0:
        fib_sum = fib1 + fib2
        fib1 = fib2
        fib2 = fib_sum
        fib(n-1)
fib1 = 1
fib2 = 1
n = int(input())
fib(n)
print(fib2-fib1)
