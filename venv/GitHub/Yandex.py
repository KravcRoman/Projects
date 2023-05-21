def convert_base(num, to_base=16, from_base=10):
    n = int(num, from_base) if isinstance(num, str) else num
    alphabet = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    res = ""
    while n > 0:
        n,m = divmod(n, to_base)
        res += alphabet[m]
    return res[::-1]
    print(res)
for i in range(int(input())):
    try:
        a = set()
        b = []
        c = []
        z = 0
        for i in input():
            try:
                i == int(i)
                b.append(i)
            except:
                a.add(i)
        a.discard(',')
        for i in a:
            c.append(i)
        for i in b[:-4]:
            z+=int(i)
        s = convert_base(((ord(c[0]) - 64) * 256) + (z * 64) + len(c))
        S = len(s) - 3
        print(s[S:], end=' ')
    except:
        break
