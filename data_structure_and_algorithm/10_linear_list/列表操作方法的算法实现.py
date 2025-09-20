lst = [1,2,3,4,5]
size = len(lst)
index, value= 2, 10

lst = lst * 2
print(f'扩容之后 lst: {lst}')

for i in range(size, index, -1):
    lst[i] = lst[i - 1]
    
print(f'遍历算法之后的 lst: {lst}')

    
# + 1 元素
lst[index] = value
size += 1

print(lst[:size])
