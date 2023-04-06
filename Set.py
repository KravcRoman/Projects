#1
n, m = input().split()
a = []
b = []
for i in range (int(n)):
    a += [int(s) for s in input().split()]
for j in range (int(m)):
    b += [int(s) for s in input().split()]
print(len(set(a) & set(b)))
print(*sorted(set(a) & set(b)))
print(len(set(a) - set(b)))
print(*sorted(set(a) - set(b)))
print(len(set(b) - set(a)))
print(*sorted(set(b) - set(a)))

#2
a = []
for i in range(int(input())):
    a += (input().split())
print(len(set(a)))


#3
n = int(input())
all_nums = set(range(1, n + 1))
possible_nums = all_nums
while True:
    guess = input()
    if guess == 'HELP':
        break
    guess = {int(x) for x in guess.split()}
    answer = input()
    if answer == 'YES':
        possible_nums &= guess
    else:
        possible_nums &= all_nums - guess

print(' '.join([str(x) for x in sorted(possible_nums)]))

#4
n = int(input())
all_nums = set(range(1, n + 1))
possible_nums = all_nums
while True:
    guess = input()
    if guess == 'HELP':
        break
    guess = {int(x) for x in guess.split()}
    if len(possible_nums & guess) > len(possible_nums) / 2:
        print('YES')
        possible_nums &= guess
    else:
        print('NO')
        possible_nums &= all_nums - guess
        
print(' '.join([str(x) for x in sorted(possible_nums)]))

#5
students = [{input() for j in range(int(input()))} for i in range(int(input()))]
known_by_everyone, known_by_someone = set.intersection(*students), set.union(*students)
print(len(known_by_everyone), *sorted(known_by_everyone), sep='\n')
print(len(known_by_someone), *sorted(known_by_someone), sep='\n')

#6
def factorial(K):
    F, B = [int(f) for f in input().split()]
    while F <= N:
        guess.append(F)
        F+=B
N, K = [int(i) for i in input().split()]
guess = []
a = [i + 1 for i in range(N)]
del a[5::7]
a = list(filter(lambda x: int(x) % 7, a))
a = set(a)
b = [i + 1 for i in range(N)]
b = set(b)
for i in range(K):
    factorial(K)
guess = set(guess)
b = (b - a)
print(len(guess - b))