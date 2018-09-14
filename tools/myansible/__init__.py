#!/usr/bin/env python
# python 2.0 api
# 2018-09-13
# TODO 记录日志、return json内容

import json
from ansible.parsing.dataloader import DataLoader
from ansible.vars.manager import VariableManager
from ansible.inventory.manager import InventoryManager
from ansible.playbook.play import Play
from ansible.executor.task_queue_manager import TaskQueueManager
from ansible.plugins.callback import CallbackBase


class ResultCallback(CallbackBase):
    """sample callback plugin used for performing an action as results come in

    If you want to collect all results into a single object for processing at
    the end of the execution, look into utilizing the ``json`` callback plugin
    or writing your own custom callback plugin
    """

    def v2_runner_on_ok(self, result, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_unreachable(self, result):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_failed(self, result, *args, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_skipped(self, result, *args, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))

    def v2_runner_on_stats(self, result, *args, **kwargs):
        host = result._host
        print(json.dumps({host.name: result._result}, indent=4))


# since API is constructed for CLI it expects certain options to always be set, named tuple 'fakes' the args parsing options object
class Options:

    def __init__(self, connection='ssh', module_path='',forks=20, become=None, become_method=None, become_user=None,
                 check=False, diff=False, private_key_file=False, remote_user=False, verbosity=False, force_handlers=False,
                 step=False, start_at_task=False, ssh_common_args=False, docker_extra_args=False, sftp_extra_args=False,
                 scp_extra_args=False, ssh_extra_args=False):

        self.connection = connection
        self.module_path = module_path
        self.forks = forks
        self.become = become
        self.become_method = become_method
        self.become_user = become_user
        self.check = check
        self.diff = diff
        self.private_key_file = private_key_file
        self.remote_user = remote_user
        self.verbosity = verbosity
        self.force_handlers = force_handlers
        self.step = step
        self.start_at_task = start_at_task
        self.ssh_common_args = ssh_common_args
        self.docker_extra_args = docker_extra_args
        self.sftp_extra_args = sftp_extra_args
        self.scp_extra_args = scp_extra_args
        self.ssh_extra_args = ssh_extra_args


class Runner:

    def __init__(self, sources, options: Options, **kwargs):
        self.sources = sources
        self.options = options

        # Become Pass Needed if not logging in as user root (do not support now)
        passwords = {'become_pass': ''}

        # Takes care of finding and reading yaml, json and ini files
        self.loader = DataLoader()

        # Instantiate our ResultCallback for handling results as they come in. Ansible expects this to be one of its main display outlets
        self.results_callback = ResultCallback()

        # Set inventory, using most of above objects
        self.inventory = InventoryManager(loader=self.loader, sources=self.sources)

        # variable manager takes care of merging all the different sources to give you a unifed view of variables available in each context
        self.variable_manager = VariableManager(loader=self.loader, inventory=self.inventory)

        # playbook
        self.tqm = TaskQueueManager(
            inventory=self.inventory,
            variable_manager=self.variable_manager,
            loader=self.loader,
            options=self.options,
            passwords=passwords,
            stdout_callback=self.results_callback,
        )

    def run(self, hosts='*', module_name='shell', module_args=''):
        play_source = dict(
            name='Ansible Play',
            hosts=hosts,
            gather_facts='no',
            tasks=[
                dict(action=dict(module=module_name, args=module_args)),
            ]
        )

        self.play = Play().load(play_source, variable_manager=self.variable_manager, loader=self.loader)
        try:
            ret = self.tqm.run(self.play)
            return ret
        finally:
            if self.tqm is not None:
                self.tqm.cleanup()

