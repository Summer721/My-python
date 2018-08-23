#!/usr/bin/python
#-*- coding:utf8 -*-
#
import urllib2
import logging
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import sys

def log_msg(fun_name, err_msg, level):
    message = fun_name + ':' + err_msg
    logger = logging.getLogger()
    #base_name = log_lograte_config.logs
    #base_time = arrow.utcnow().to("Asia/Shanghai").format("YYYYMMDD")
    logname = "/tmp/xunjian.log"
    hdlr = logging.FileHandler(logname)
    formatter = logging.Formatter('%(asctime)s %(levelname)s %(message)s')
    hdlr.setFormatter(formatter)
    logger.addHandler(hdlr)
    logger.setLevel(logging.NOTSET)
    logger.log(level, message)
    hdlr.flush()
    logger.removeHandler(hdlr)

def curls_res(url):
    req = urllib2.Request(url)
    try:
        response = urllib2.urlopen(req)
        return response.code
    except:
       pass

def send_mail(url):
    ##定义发件人收件人
    from_addr = "nie.chenxi@whaley.cn"
    to_addr = ["peng.tao@whaley.cn","nie.chenxi@whaley.cn","yang.liu@whaley.cn","zhang.dong@whaley.cn","kong.fanfu@whaley.cn"]
    #to_addr = ["nie.chenxi@whaley.cn",]

    ##定义登录邮件服务器的用户名，密码
    mail_host="smtp.exmail.qq.com"
    mail_user="nie.chenxi@whaley.cn"
    mail_pass="xxxxxxxxxxxxxxx"

    ##定义邮件的内容
    msg = MIMEText('兄弟们:'+'\n'*2 \
         + '十九大保障url有报错,赶快处理下:%s' % url,'plain','utf-8')
    subject = "十九大巡检保障工作URL探测告警"
    ##定义邮件的格式
    msg['From'] = from_addr
    msg['To'] = ';'.join(to_addr)
    msg['Subject'] = Header(subject,'utf-8')
    try:
        server = smtplib.SMTP_SSL(mail_host,port=465)
        server.login(mail_user, mail_pass)
        server.set_debuglevel(1)
        server.sendmail(from_addr,to_addr,msg.as_string())
    except smtplib.SMTPException:
        print 'error'
        sys.exit(1)

if __name__ == '__main__':
    f = open('urls.txt','rb')
#import pdb;pdb.set_trace()
    while True:
        line = f.readline().strip()
        if line:
            status = curls_res(line)
            if status == 200 or status == 302:
                log_msg('main','访问url %s success.' % line,1)
            else:
                send_mail(line)
        else:
            break
    f.close()

