# 1.可以被2整除
# 2.整除表示： x % 2 == 0
a = int(input("请输入一个数："))


def b(x):
    is_even = False
    if x % 2 == 0:
        is_even = True
    else:
        is_even = False
    return is_even

is_even = b(a)
print(f"{a}是不是偶数的判断结果:{is_even}")