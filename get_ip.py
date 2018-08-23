#!/usr/bin/python 
from pathlib import Path
import shutil
import pymysql
import os
import re
import sys

conn = pymysql.Connection(host='10.10.88.176', user='niechenxi', password='123456', database='yunwei', port=3306)
cursor = conn.cursor()

def mysql_info():

    mysql_sql = 'SELECT db_host, master_ip FROM sql_info WHERE is_valid=1 and master_ip = ""'
    cursor.execute(mysql_sql)
    return dict(cursor.fetchall())

def publish_info():
    publish_sql = 'select app_dir, up_addr, up_env, conf_addr from publish_prog'
    cursor.execute(publish_sql)
    return cursor.fetchall()

def parser():

    publish_data = publish_info()

    mysql_data = mysql_info()

    app_mysql_table = {}

    pattern = re.compile(b'\d+\.\d+\.\d+\.\d+')

    for app, ip, env, svn_address in publish_data:
        os.system('svn checkout {} &> /dev/null'.format(svn_address))
        svn_dir = Path(svn_address.rstrip('/').rsplit('/', 1)[1])
        for sp in svn_dir.rglob('.svn/'):
            shutil.rmtree(sp)
        for f in svn_dir.rglob("*"):
            if f.is_file() and f.name != 'process_restart.sh':
                with open(f,'rb') as conf_file:
                    for line in conf_file:
                        if ((app, env)) not in app_mysql_table.keys():
                            app_mysql_table[(app, env)] = set()
                        matcher = pattern.search(line.strip())
                        if matcher:
                           if matcher.group().decode() == '127.0.0.1':
                               ip_address = ip
                           else:
                               ip_address = matcher.group().decode()
                           if ip_address in mysql_data.keys():
                               app_mysql_table[(app, env)].add(ip_address)
        if svn_dir.name == '/':
            sys.exit(10000)
        shutil.rmtree(svn_dir)
    return app_mysql_table

if __name__ == '__main__':
    data_info = parser()
    for app_env, ips  in data_info.items():
        if not ips:
            ip_address = 'null'
        else:
            ip_address = ','.join(ips)
        sql_string = '''INSERT INTO app_database (app_name,up_env,d_ip) VALUES ("{}","{}","{}")'''.format(app_env[0], app_env[1], ip_address)
        cursor.execute(sql_string)
        conn.commit()

