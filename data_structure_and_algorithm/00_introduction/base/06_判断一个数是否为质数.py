"""
终止本层循环: break
终止本次循环: continue

# 循环层
for x in range(1, a+1):
    # 循环次
    # print(f"第【{x}】次循环次开始")
    if a % x == 0 and x not in b:
        print(f"【{x}】a 不是质数, 因为可以被 {x} 整除")
        break
    # 后面还有其他的逻辑
    # print(f"【{x}】未找到可被1和自身之外的数整除，本次循环还没结束，继续后面的逻辑\n")

"""


# 从 1 到 这个数之间取出所有数字，逐个判断能否被 1 和 自身 之外的数 整除
a = int(input(f"请输入一个数字:"))
is_prime = True

def c(a):
    is_prime = True
    b = [1, a]
    for x in range(1, a+1):
        if a % x == 0 and x not in b:
            print(f"{a} 不是质数, 因为可以被 {x} 整除")
            is_prime = False
            break
    return is_prime

is_prime = c(a)
print(f"{a} 是不是质数的判断结果: {is_prime}")