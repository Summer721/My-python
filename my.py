# 自定义sort函数
def sort(seq, reverse=False):
    ret = []
    for x in seq:
        for i, y in enumerate(ret):
            flag =  x < y if reverse else y < x
            if flag:
                ret.insert(i, x)
                break
        else:
            ret.append(x)
    return ret

# print(sort([1,20,2,6,100,78,54,32], reverse=True))

# filter(function, iterable)函数；
# function的参数为一个, 返回bool值，返回True的能被过滤到迭代器中；
# 例如：
for i in filter(lambda x: x % 3==0, range(30)):
    print(i)


# map(function, *iterable)
# 返回map 对象
# 对多个可迭代对象的元素按照指定的函数进行映射，返回一个迭代器；

print(list(map(lambda x:2*x +1, range(5))))
print(dict(map(lambda x:(x%5, x), range(500))))
