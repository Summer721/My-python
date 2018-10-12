#!/usr/bin/python
#
from saltapi import SaltApi
import re

salt_obj = SaltApi()
disabled = [u"t-slq-test-2",u"t-slq-msyql-3",u"t-slq-lb-2",u"t-slq-test-1",u"t-slq-spark-5",u"t-slq-uat-test-1",u"t-slq-detalase-1",
            u"t-slq-uat-db-1",u"t-slq-oms-1",u"t-slq-jenkins-2",u"t-slq-mysql-2",u"t-slq-cache1",u"t-slq-k8s-21",u"t-slq-gtw-3",
            u"t-slq-nat-1",u"t-slq-k8s-22",u"t-slq-win2012-1",u"t-slq-node-1"]
keys = salt_obj.list_all_keys()[0]
for key in disabled:
    keys.remove(key)


def handle_data():
    os_info = {
        'client': 'local',
        'fun': 'grains.item',
        'tgt': '*',
        'arg': ('os', 'fqdn', 'host','ipv4','osfinger','mem_total','num_cpus','osrelease'),
        'kwargs': {},
        'expr_form': 'glob',
        'timeout': 60
    }
    # Get ip address, os info, processlist.
    res_data = {}
    for key in keys:
        if key not in res_data:
            res_data[key] = {}
        try:
            os_info = salt_obj.remote_execution(str(key), 'grains.item', ('os', 'ipv4'))
            addresses = os_info.get(key).get('ipv4')

            for ip in addresses:
                if ip.startswith('192.168'):
                    res_data[key]['ip'] = ip
            res_data[key]['os'] = os_info.get(key).get('os')
        except Exception as e:
            print(e)
	# filter system processes.
        filter_list = ['upstart-socket-bridge','ps aux','upstart-udev-bridge', '/lib/systemd/systemd-udevd',
                       '/usr/sbin/zabbix_agentd', 'atd', 'udev', '/sbin/getty', '/usr/sbin/sshd',
                       '/sbin/init',"upstart-file-bridge","dbus-daemon","nmbd","systemd-logind","acpid","rsyslogd",
		      ]

	# the lastest processlist
        process_list = []

        # if ip_address and os is None then continue
        try:
            process_data = salt_obj.remote_execution(str(key), 'ps.psaux', "").get(key)[1][1:]
	except Exception as e:
            print("%s is not avaiable" % str(key))
            continue

        for item in process_data:
            pattern = re.compile("(\d+:\d+ +)?\d+:\d+")
            temp_data = item.split(pattern.search(item).group())[1].strip()

            if temp_data.startswith('[') and temp_data.endswith(']'):
                continue
            flag = True
            for i in filter_list:
                match = re.search(i, temp_data)
                if match:
                    flag = False
                    break
            if flag:
                process_list.append(temp_data)

        process_list = list(set(process_list))
        res_data[str(key)]['processes'] = process_list

    return res_data
