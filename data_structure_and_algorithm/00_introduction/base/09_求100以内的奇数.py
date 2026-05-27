f = int(input("请输入一个数："))

def a(b):
    c = []
    for d in range(1,b+1):
        if d % 2 != 0:
            c.append(d)
    return c
e = a(f)
print(e)