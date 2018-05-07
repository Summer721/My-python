#处理日志文件
#
log_line = '''123.125.67.166 - - [09/Apr/2017:07:39:00 +0800] \
"GET /robots.txt HTTP/1.1" 200 239 "-" "Mozilla/5.0 (Windows NT 10.0; WOW64) \
AppleWebKit/537.36 (KHTML, like Gecko) Chrome/45.0.2454.93 Safari/537.36"'''

lst = []
flag = False

for word in log_line.split():
    if word.startswith('"') or word.startswith('['):
        tmp = word[1:]
        if tmp.endswith('"') or tmp.endswith(']'):
            tmp = tmp.strip('"]')
            lst.append(tmp)
            tmp = ''
            continue
        flag = True
        continue
    if flag:
        if word.endswith('"') or word.endswith(']'):
            tmp +=  ' ' + word.strip('"]')
            lst.append(tmp)
            continue
        else:
            tmp += " " + word
            continue
    lst.append(word)
print(lst)



