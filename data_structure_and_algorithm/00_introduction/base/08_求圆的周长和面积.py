a = int(input("请输入一个半径："))
#b = (a * 2 * 3.14)

def d(x):
    y = x * 2 * 3.14
    return y

b = d(a)

def e(x):
    y = x * x * 3.14
    return y

c = e(a)
#c = (a * a * 3.14)
print(f"周长 = {b}  面积 = {c}")