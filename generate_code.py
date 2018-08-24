import random
def make_act(num):
    "make activation code"
    #根据给定的num生成随机大写字母、小写字母、数字混合字符串

    #生成字符列表
    Upper = [chr(i) for i in range(65, 90)]
    Lower = [chr(i) for i in range(97, 123)]
    number_str = [str(i) for i in range(0,10)]

    #10位激活码
    ret_code = ''
    for _ in range(0,num):
        #code_dict = dict(zip(range(3), (random.choice(Upper), random.choice(Lower), random.choice(number_str))))
        code_dict = dict(zip(range(3), map(random.choice,(Upper,Lower,number_str))))
        temp = code_dict[random.choice(list(code_dict.keys()))]
        ret_code += temp
    while True:
        yield ret_code
