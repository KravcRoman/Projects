#1
n = input().split()
for i in range(len(n)-1):
	print(n[i] + ',' + ' ', end ='')
print(n[i+1] + '.')

#2
for i in input().split():
	print('{} => {}'.format(float(i), round(float(i)/5)*5))

#3
for i in input().split():
	if int(i) == 11:
		print(i + ' Компьютеров')
	elif len(i) > 2:
		if int(i[-2:]) == 11:
			print(i + ' Компьютеров')
		elif int(i[-1]) == 1:
			print(i + ' Компьютер')
		else:
			print(i + ' Компьютеров')
	elif int(i) == 1:
		print(i + ' Компьютер')
	elif int(i) in [2,3,4]:
		print(i + ' Компьютера')
	elif int(i[-1]) == 1:
		print(i + ' Компьютер')
	else:
		print(i + ' Компьютеров')

#4
a = int(input())
k = 0
for i in range(2, a // 2+1):
    if (a % i == 0):
        k = k+1
if (k <= 0):
    print("Число простое")
else:
    print("Число не является простым")

#5
a = input().split()
b = input().split()
a = [x for i, x in enumerate(a) if i != a.index(x)]
b = [x for i, x in enumerate(b) if i != b.index(x)]
print(*set(a).intersection(set(b)))

#6
s1 = int(input())
print(' ', *(range(int(1), s1+1)), sep='\t')
for i in range(1, s1+1):
    print(i, end = '\t')
    print(*range(i, i*s1+1, i), sep='\t')
