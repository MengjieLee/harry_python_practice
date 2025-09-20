# 编写程序，输入一个手势

"""
import random
"""
import random

a = input(f"请输入一个手势(剪刀,石头,布):")

def computer_choice():
    a = ["剪刀","石头","布"]
    c = random.choice(a)
    return c

b = computer_choice()
print(b)

# 判断条件
c = ""
# 平局
if a == b:
    c = "平局"
# 玩家赢
elif (a == "剪刀" and b =="布") or (a == "布" and b =="石头") or (a == "石头" and b =="布"):
    c = "玩家赢"
# 计算机赢
else:
    c = "计算机赢"
print(c)