def funk(wooo1, wooo2) -> bool:
    found = True
    for w1 in wooo1:
        for w2 in wooo2:
            if w1 == w2:
                found = True
                break
            else:
                found = False
        break
    return found




# word1 = "typhon"
# word2 = "python"
# result = funk(word1, word2)
# print(result)
assert funk("xyphon", "python")is False
assert funk("god", "dog")is True
print("✅")