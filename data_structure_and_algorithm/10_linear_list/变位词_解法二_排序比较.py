"""
将两字符串都按照字母顺序排序
    - 逐字符比较是否相同，如果对比到最后都相同，则是变位词
    - 如果发生有一个字符没有找到，则两个词不是变位词

    is_anagram
"""
def func(word1: str, word2: str) -> bool:
    is_anagram = True

    # TODO 代码逻辑写在这里
    sorted_word1 = sorted()
    sorted_word2 = sorted()

    for i in range(len(sorted_word1)):
        if sorted_word1[i] == sorted_word2[i]:
            is_anagram = False
            break
        return is_anagram


assert func('xython', 'typhon') is False
assert func('python', 'typhon') is True
assert func('peti', 'tipe') is True
print('断言测试成功')
