"""
将词 1 中的字符逐个提取去到词 2 中检查是否存在，存在就标记 True（放置重复检查）:
    - 如果每个字符都能找到，则两个词是变位词
    - 如果发生有一个字符没有找到，则两个词不是变位词
"""
def func(word1, word2):
    flag = True
    for w1 in word1: # loop1
        for w2 in word2: # loop2
            if w1 == w2: # 难点一
                break
        if w1 != w2: # 难点二
            flag = False
            return flag
    return flag # 难点三

# # 链式赋值
# word1, word2 = 'aabc', 'baca'
# is_anagram = func(word1, word2)
# print(f'{word1} 和 {word2} {'是' if is_anagram else '不是'} 同位词！')


def func(word1: str, word2: str) -> bool:
    flag = False
    for w1 in word1:
        for w2 in word2:
            if w1 == w2:
                flag = True
                break
        if flag is False:
            return flag
    return flag


def func(word1: str, word2: str) -> bool:
    found = False
    for w1 in word1:
        for w2 in word2:
            if w1 == w2:
                found = True
                break
        if not found:
            return False
    return found


assert func('xython', 'typhon') is False
assert func('python', 'typhon') is True
assert func('peti', 'tipe') is True
print('断言测试成功')
