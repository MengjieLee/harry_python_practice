def solution_from_harry(w1, w2):
    # 思路：
    # - 所有字符都相等，返回 True
    # - 但凡有一个字符不相等，立即返回 False
    for i in w1:
        found = False
        for j in w2:
            if i == j:
                found = True
                break
        if not found:
            return False    
    return found
        
print(solution_from_harry('python', 'typhon是'))
