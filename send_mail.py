#!/usr/bin/python
#-*- coding:utf-8 -*-
#
#date 2017-08-02
import ansible.runner
import ansible.playbook
import ansible.inventory
from ansible import callbacks
from ansible import utils
from email.mime.text import MIMEText
from email.header import Header
import smtplib
import sys
import time
import mysqlhelper

def get_time():
    ##定义时间戳
    CurrTime = time.strftime('%Y%m%d', time.localtime(time.time()))
    Year = time.strftime('%Y', time.localtime(time.time()))
    Month = time.strftime('%m', time.localtime(time.time()))
    Day = time.strftime('%d', time.localtime(time.time()))
    
    ##取年、月、日整数
    Yesterday = 0
    CurrTime = int(CurrTime)
    Day = int(Day)
    Year = int(Year)
    Month = int(Month)
    if Day != 1:
        Yesterday = CurrTime - 1

    if Day == 1 and (Month in [5,7,10,12]):
        Month = Month - 1
        if 1 <= Month <= 9:
            Month = "%02d" % Month
        Day = 30
        Yesterday = str(Year) + str(Month) + str(Day)

    if Day == 1 and (Month in [2,4,6,8,9,11]):
        Month = Month - 1
        if 1 <= Month <= 9:
            Month = "%02d" % Month
        Day = 31
        Yesterday = str(Year) + str(Month) + str(Day)

    if Day == 1 and Month == 1:
        Month = 12
        Day = 31
        Year = Year - 1
        Yesterday = str(Year) + str(Month) + str(Day)

    if Day == 1 and Month == 3:
        Month = Month - 1
        if 1 <= Month <= 9:
            Month = "%02d" % Month
        flag = Year % 4
        if flag == 0:
            Day = 29
        else:
            Day = 28
        Yesterday = str(Year) + str(Month) + str(Day)
    Yesterday = str(Yesterday)
    Path_time = Yesterday[2:]
    File_time = Yesterday[:-2]
    
    rest =  [Yesterday,Path_time,File_time]
    return rest


def get_data():
    ##变量定义
    log_time = get_time()
    ##定义要取数据的主机组
    hosts = ['10.19.147.234','10.19.34.25','10.10.14.16','10.19.174.181','10.19.90.185']
    #文件路径定义
    log_path = '/data/log_back/{0}/'.format(log_time[1])
    log_file = '_data_logs_cloudparser-php2_log_{0}---{1}.log'.format(log_time[2],log_time[0])

    log_inventory = ansible.inventory.Inventory(hosts) 
    results = ansible.runner.Runner(
    module_name = 'shell',
    module_args = 'cat {0}{1} | grep request | grep dsm.flvurl.cn | wc -l'.format(log_path,log_file),
    private_key_file = '/etc/ansible/id_dsa',
    timeout = 5,
    inventory = log_inventory,
    subset = 'all'
    ).run()
    res = {}
    for key in results["contacted"].keys():
	res[key] = results["contacted"][key]["stdout"]
    return  res


def send_mail():
    ##定义发件人收件人
    from_addr = "nie.chenxi@whaley.cn"
    to_addr = ["liu.xi@whaley.cn","dai.yunseng@whaley.cn","cheng.xiyu@whaley.cn","liu.yong@whaley.cn","nie.chenxi@whaley.cn","zhang.dong@whaley.cn"]
    #to_addr = ["nie.chenxi@whaley.cn",]

    ##获取数据
    hosts = ['10.19.147.234','10.19.34.25','10.10.14.16','10.19.174.181','10.19.90.185']
    log_data = get_data()
    log_time = get_time()
    ##从数据库取得数据
    try:
        my = mysqlhelper.MysqlBase('10.10.14.16','AnalysisRetuser','AnalysisRet123456','ParserLogAnalysis')
    except:
        sys.exit()
    result0 = my.get_data('select date,host,info from AnalysisRet where date = {0} and host ="{1}"'.format(int(log_time[0]),hosts[0]))
    result1 = my.get_data('select date,host,info from AnalysisRet where date = {0} and host ="{1}"'.format(int(log_time[0]),hosts[1]))
    result2 = my.get_data('select date,host,info from AnalysisRet where date = {0} and host ="{1}"'.format(int(log_time[0]),hosts[2])) 
    result3 = my.get_data('select date,host,info from AnalysisRet where date = {0} and host ="{1}"'.format(int(log_time[0]),hosts[3])) 
    result4 = my.get_data('select date,host,info from AnalysisRet where date = {0} and host ="{1}"'.format(int(log_time[0]),hosts[4])) 

    ##定义登录邮件服务器的用户名，密码
    mail_host="smtp.exmail.qq.com"
    mail_user="nie.chenxi@whaley.cn"
    mail_pass="xxxxxxxxxxxxxx"

    ##定义邮件的内容
    msg = MIMEText('Dears:'+'\n'*2 \
         + '邮件内容为{0}日cloudparser-php2日志统计报告,请查收!!!'.format(log_time[0]) + '\n'*2 \
	 + '一、dsm.flvurl.cn数量统计信息:'+ '\n' \
	 + '{0}:'.format(hosts[0]) + ' ' * 6 +  str(log_data[hosts[0]]) + '\n' \
         + '{0}:'.format(hosts[1]) + ' ' * 10 +  str(log_data[hosts[1]]) + '\n' \
         + '{0}:'.format(hosts[2]) + ' ' * 10 +  str(log_data[hosts[2]]) + '\n' \
         + '{0}:'.format(hosts[3]) + ' ' * 10 +  str(log_data[hosts[3]]) + '\n' \
         + '{0}:'.format(hosts[4]) + ' ' * 6 +  str(log_data[hosts[4]]) + '\n'*3 \
         + '二、对点量接口的具体信息:' + '\n' \
         + result0[0][1] + ':' + '\n' + result0[0][2] + 2*'\n' \
         + result1[0][1] + ':' + '\n' + result1[0][2] + 2*'\n' \
         + result2[0][1] + ':' + '\n' + result2[0][2] + 2*'\n' \
         + result3[0][1] + ':' + '\n' + result3[0][2] + 2*'\n' \
         + result4[0][1] + ':' + '\n' + result4[0][2] , 'plain', 'utf-8')
    subject = "cloudparser-php2日志统计"
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

if __name__ == "__main__":
    send_mail()

