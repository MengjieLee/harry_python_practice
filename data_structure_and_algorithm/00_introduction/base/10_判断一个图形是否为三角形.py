a = int(input(f"请输入三角形的一个边长:"))
b = int(input(f"请输入三角形的一个边长:"))
c = int(input(f"请输入三角形的一个边长:"))

def d(a,b,c):
    if a + b > c and c + b > a and a + c  > b:
        e = True
    else:
        e = False
    return e
f = d(a,b,c)
print(f)