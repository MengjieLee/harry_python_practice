"""
for 循环实现如下图形

$$$
$$$
$$$
$$$
$$$
$$$

"""
n = int(input(f"请输入一个数字:"))

def func(n):
    for x in range (1, n+1):
        for y in range (1, 4):
            print("$", end="")
        print("\n")
func(n)