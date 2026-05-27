a = 1
b = 2
def func(a):
    global b

    a += 1
    b = "mj"

res = func(a)
print(res) # None
print(a)   # 1
print(b)   # mj
