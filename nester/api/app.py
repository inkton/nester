#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT

from thing import FailedValidation
from cloud import Cloud
from auth import Auth

class App(Cloud):

    def __init__(self, auth):
        super(Cloud, self).__init__('app', auth)

    def new_copy(self, object):
        new_entity = App(self.auth) 
        new_entity.__dict__.update(object)
        return new_entity

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage an app')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='app_command', help='App commands')

        app_cmd_parsers.add_parser('attach', help='Attach to the app in the environment')
        allow_cmd = app_cmd_parsers.add_parser('allow', help='Get update permission to the app')
        allow_cmd.add_argument('-p', '--password', type=str, help='The password')
        app_cmd_parsers.add_parser('revoke', help='Revoke update permission to the app')
        app_cmd_parsers.add_parser('clean_build_tests', help='Clean build unit tests')
        app_cmd_parsers.add_parser('unit_test_debug_host', help='Spawn unit test debug')

    def exec_command(self, args):
        self.set_log(args.log)
        cmd_handled = False
        if args.command == self.subject:
            self.log("handle app command")
            cmd_handled = True
            if (args.app_command == 'attach'):
                self.attach()
            elif (args.app_command == 'allow'):
                self.allow(args.password)
            elif (args.app_command == 'revoke'):
                self.revoke()
            else:
                cmd_handled = False
            self.end_cmd()
            return cmd_handled

    def attach(self):
        self.remove_owner()
        self.create_owner()
        self.nest_enable_root()

    def allow(self, password):
        try:
            auth = Auth(os.environ['NEST_CONTACT_EMAIL'], password)
            auth.get_token()
            auth.save()
        except Exception as e:
            print(e)

    def revoke(self):
        try:
            auth = Auth(os.environ['NEST_CONTACT_EMAIL'], None)
            auth.save()
        except Exception as e:
            print(e)

    def nest_enable_root(self):
        self.log("enable root to impersonate the nest owner")
        self.os_exec("rm -rf /root/.ssh")
        self.os_exec_shell("cp -r /home/"+ os.environ['NEST_CONTACT_ID'] + "/.[a-zA-Z0-9]* /root")
        self.os_exec("chown root:root -R /root/.ssh")
        self.os_exec("chmod 600 -R /root/.ssh")
        #self.os_exec("chmod 700 -R /root/.ssh")
        #self.os_exec("chmod -R 600 /root/.ssh/*")

    def remove_owner(self):
        self.log("removing current user")
        self.os_exec("userdel --force --remove "+os.environ['NEST_CONTACT_ID'])
        self.os_exec("sed -i /"+os.environ['NEST_CONTACT_ID']+"/d /etc/sudoers.d/99-forest-sudoers")
        self.os_exec_shell("rm -rf /home/"+os.environ['NEST_CONTACT_ID'])
        self.log("removing group")
        self.os_exec("groupdel tree")

    def create_owner(self):
        self.log("add tree group")
        self.os_exec("groupadd --gid 1008 tree")
        self.log("add current user")
        self.os_exec("useradd --uid "+os.environ['NEST_CONTACT_ID']+" --create-home --gid 1008 "+os.environ['NEST_CONTACT_ID'])
        self.os_exec("touch /etc/sudoers.d/99-forest-sudoers")
        self.os_exec_shell("echo '"+os.environ['NEST_CONTACT_ID']+"   ALL=(ALL) NOPASSWD: ALL'  > /etc/sudoers.d/99-forest-sudoers")
        self.os_exec("rm -rf /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("mkdir /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec_shell("echo "+os.environ['NEST_CONTACT_KEY']+" | base64 --decode > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa")
        self.os_exec_shell("ssh-keyscan -H "+os.environ['NEST_APP_TAG']+".nestapp.yt > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/known_hosts")
        self.os_exec("chmod 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh -R")
        self.os_exec_shell("ssh-keygen -f /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa -y > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa.pub")
        self.os_exec_shell("cat /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa.pub > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/authorized_keys")
        self.os_exec_shell("printf 'Host nest\n\tStrictHostKeyChecking no\n\tHostName "+os.environ['NEST_APP_TAG']+".nestapp.yt\n\tUser "+os.environ['NEST_CONTACT_ID']+"\n' > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/config")
        self.os_exec("chown "+os.environ['NEST_CONTACT_ID']+":tree -R /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("chmod 600 -R /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        #self.os_exec("chmod 700 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        #self.os_exec("chmod -R 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/*")
