# coding=utf-8
# auth: zhangyiling
# time: 2018/10/9 下午9:20
# description: saltstack api所有的操作在这里


import requests
import copy
import json

SALT_API = {
    "url": "https://192.168.199.61:18080",
    "user": "saltapis",
    "password": "saltapis",
}


class SaltApi(object):
    def __init__(self):
        self.__user = SALT_API["user"]
        self.__passwd = SALT_API["password"]
        self.url = SALT_API["url"]
        self.headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }
        self.__base_data = dict(
            username=self.__user,
            password=self.__passwd,
            eauth='pam'
        )
        self.__token = self.get_token()

    def get_token(self):
        """  login salt-api and get token_id """
        params = copy.deepcopy(self.__base_data)
        requests.packages.urllib3.disable_warnings()  # close ssl warning, py3 really can do it!
        ret = requests.post(url=self.url + '/login', verify=False, headers=self.headers, json=params)
        ret_json = ret.json()
        # print('***ret_json: {}'.format(ret_json))
        token = ret_json["return"][0]["token"]
        # print('***token: {}'.format(token))
        return token

    def __post(self, **kwargs):
        """  custom post interface, headers contains X-Auth-Token """
        headers_token = {'X-Auth-Token': self.__token}
        headers_token.update(self.headers)
        requests.packages.urllib3.disable_warnings()
        ret = requests.post(url=self.url, verify=False, headers=headers_token, **kwargs)
        ret_code, ret_data = ret.status_code, ret.json()

        # print(ret_code, ret_data)
        return (ret_code, ret_data)

    def list_all_keys(self):
        """  show all keys, minions have been certified, minion_pre not certification """
        params = {'client': 'wheel', 'fun': 'key.list_all'}
        r = self.__post(json=params)
        minions = r[1]['return'][0]['data']['return']['minions']
        minions_pre = r[1]['return'][0]['data']['return']['minions_pre']
        return minions, minions_pre

    def list_all_avia_key(self):
        parmas = {'client': 'wheel', 'fun': 'test.ping', 'match': True}
        r = self.__post(json=params)
        print(r)

    def delete_key(self, tgt):
        """ delete a key """
        params = {'client': 'wheel', 'fun': 'key.delete', 'match': tgt}
        r = self.__post(json=params)
        return r[1]['return'][0]['data']['success']

    def accept_key(self, tgt):
        """  accept a key """
        params = {'client': 'wheel', 'fun': 'key.accept', 'match': tgt}
        r = self.__post(json=params)
        return r[1]['return'][0]['data']['success']

    def lookup_jid_ret(self, jid):
        """  depend on jobid to find result """
        params = {'client': 'runner', 'fun': 'jobs.lookup_jid', 'jid': jid}
        r = self.__post(json=params)
        return r[1]['return'][0]

    def salt_running_jobs(self):
        """ show all running jobs """
        params = {'client': 'runner', 'fun': 'jobs.active'}
        r = self.__post(json=params)
        return r[1]['return'][0]

    def run(self, params):
        """ remote common interface, you need custom data dict
            for example:
                params = {
                    'client': 'local',
                    'fun': 'grains.item',
                    'tgt': '*',
                    'arg': ('os', 'id', 'host' ),
                    'kwargs': {},
                    'expr_form': 'glob',
                    'timeout': 60
                }
         """
        r = self.__post(json=params)
        return r[1]['return'][0]

    def remote_execution(self, tgt, fun, arg, ex='glob'):
        """ remote execution, command will wait result
            arg must be a tuple, eg: arg = (a, b)
            expr_form : tgt m

        """
        params = {'client': 'local', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': ex}
        r = self.__post(json=params)
        return r[1]['return'][0]

    def async_remote_execution(self, tgt, fun, arg, ex='glob'):
        """ async remote exection, it will return a jobid
            tgt model is list, but not python list, just like 'node1, node2, node3' as a string.
         """
        params = {'client': 'local_async', 'tgt': tgt, 'fun': fun, 'arg': arg, 'expr_form': ex}
        r = self.__post(json=params)
        return r[1]['return'][0]['jid']

    def salt_state(self, tgt, arg, ex='list'):
        """  salt state.sls """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': ex}
        r = self.__post(json=params)
        return r[1]['return'][0]

    def salt_alive(self, tgt, ex='glob'):
        """ salt test.ping """
        params = {'client': 'local', 'tgt': tgt, 'fun': 'test.ping', 'expr_form': ex}
        r = self.__post(json=params)
        return r[1]['return'][0]


    def target_deploy(self,tgt,arg):
        ''' Based on the node group forms deployment '''
        params = {'client': 'local_async', 'tgt': tgt, 'fun': 'state.sls', 'arg': arg, 'expr_form': 'nodegroup'}
        obj = urllib.urlencode(params)
        self.token_id()
        content = self.postRequest(obj)
        jid = content['return'][0]['jid']
        return jid
