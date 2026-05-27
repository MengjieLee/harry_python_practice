""" for 循环也可以使用  continue 和 break, 用法同理于 while 循环中的作用
for 嵌套也是常用的写法

打印如下图案
$$$
$$$
harry
$$$
$$$
$$$

"""
n = int(input(f"请输入一个数字:"))

def func(n):
    for x in range (1, n+1):
        if x == 3:
            print("harry")
            continue
        for y in range (1, 4):
            print("$", end="")
        print("\n")
func(n)