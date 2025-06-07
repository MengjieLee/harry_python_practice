def foo():
    print('123')
    return

# 顺序结构
# foo()

# 分支结构
# flag = False
# if flag:
#     foo()
# else:
#     pass

# 循环
def loop_func():
    for a in range(1,4):
        print(a)

"""
1
2
3
"""



if __name__ == '__main__':
    # print(list(range(0, 5, 2)))
    loop_func()