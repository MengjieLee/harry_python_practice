"""
0! = 1

1! = 1 x 1
2! = 2 x 1              # 2 x 1!
3! = 3 x 2 x 1          # 3 x 2!
4! = 4 x 3 x 2 x 1      # 4 x 3!
5! = 5 x 4 x 3 x 2 x 1  # 5 x 4!
...
n! = n x (n-1) x (n-2) ... x 1 (其中 n >= 1)
"""

'''
1. 给定一个数 n
2. 有 n - 1 次乘的计算
3. 每次执行乘计算,有两个数
'''

n = int(input("请输入一个数："))

def func(n):
    res = 1
    for x in range(1 ,n+1):
        res *= x # res = res * x
    return res

result = func(n)
print(f"{n}的阶乘的结果是{result}")