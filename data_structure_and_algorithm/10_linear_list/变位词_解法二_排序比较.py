"""
将两字符串都按照字母顺序排序
    - 逐字符比较是否相同，如果对比到最后都相同，则是变位词
    - 如果发生有一个字符没有找到，则两个词不是变位词
"""
def func(word1: str, word2: str) -> bool:
    is_anagram = True

    word1_list, word2_list = list(word1), list(word2)

    word1_list.sort()
    word2_list.sort()

    p = 0

    while p < len(word1) and is_anagram:
        if word1_list[p] == word2_list[p]:
            p += 1
        else:
            is_anagram = False

    return is_anagram


assert func('xython', 'typhon') is False
assert func('python', 'typhon') is True
assert func('peti', 'tipe') is True
print('断言测试成功')
