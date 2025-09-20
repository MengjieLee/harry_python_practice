


## 开设一个  七年级六班列表
class_7_6 = []
class_7_6 = list()


## 添加: 学生报到，员工考勤打卡
stu_lydia = {
    'name': 'lydia',
     "no": 1
}

stu_harry = {
    'name': 'harry',
     "no": 2
}

class_7_6.append(stu_lydia)
class_7_6.append(stu_harry)

stu_lmj = {
    'name': 'limengjie',
     "no": 1
}

class_7_6.insert(0, stu_lmj)

## 合并俩个班级
class_7_7 = [{'name': 'harry', 'no': 2}, {'name': 'jonny', 'no': 1}]
class_7_6.extend(class_7_7)

## python 形参的分类介绍
def my_func(*args, **kwargs):
    return kwargs.keys()

# res = my_func(1, name='susan', no=1)
# print(res)


## 删除: 牛马或工作者的离职，学生转校或毕业
# class_7_6.remove({'name': 'lydia', 'no': 1})
# class_7_6.pop(-5)


## 查找: 上课之前点名，服装店查找样品
index_result = class_7_6.index({'name': 'harry', 'no': 2})

my_list = [{'name': 'limengjie', 'no': 1}, {'name': 'lydia', 'no': 1}, {'name': 'harry', 'no': 2}, {'name': 'harry', 'no': 2}, {'name': 'jonny', 'no': 1}]

# my_list[4].update(no=99)
# my_list[4].update({'age': 1})
# my_list[4].update({'name': '左政'})

my_list[4] = {'age': 1}

print(my_list)


