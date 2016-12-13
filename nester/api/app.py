
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
        super(Cloud, self).__init__('apps', auth)

    def parse_command(self, subparsers):
        cmd_parser = subparsers.add_parser(self.subject, help='Manage an app')
        app_cmd_parsers = cmd_parser.add_subparsers(dest='app_command', help='App commands')

        app_cmd_parsers.add_parser('attach', help='Attach to the current app in the environment')

        allow_cmd = app_cmd_parsers.add_parser('allow', help='Allow permission to update the app')
	allow_cmd.add_argument('-p', '--password', type=str, help='The password')

        revoke_cmd = app_cmd_parsers.add_parser('revoke', help='Revoke permission to update the app')
        app_cmd_parsers.add_parser('clear', help='Clear cache')

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
            elif (args.app_command == 'clear'):
	       self.clear_cache()
            else:
            	cmd_handled = False
            self.end_cmd()
        return cmd_handled

    def attach(self):
        self.remove_owner()
        self.create_owner()
        self.setup_workarea()
        self.setup_git()	
        self.os_exec("/bin/bash /usr/local/tree/nest/utils/create")
        print "App attached. Re-start the container to begin"

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

    def remove_owner(self):
	self.log("removing current user")
        self.os_exec("userdel --force --remove "+os.environ['NEST_CONTACT_ID'])
        self.os_exec("sed -i /"+os.environ['NEST_CONTACT_ID']+"/d /etc/sudoers.D/99-forest-sudoers")
        self.os_exec("rm -rf /home/"+os.environ['NEST_CONTACT_ID'])
	self.log("removing group")
        self.os_exec("groupdel tree")

    def create_owner(self):
	self.log("add tree group")
        self.os_exec("groupadd --gid 1008 tree")
	self.log("add current user")
        self.os_exec("useradd --uid "+os.environ['NEST_CONTACT_ID']+" --create-home --gid 1008 "+os.environ['NEST_CONTACT_ID'])
        self.os_exec("touch /etc/sudoers.d/99-forest-sudoers")
        self.os_exec("echo '"+os.environ['NEST_CONTACT_ID']+"	ALL=(ALL) NOPASSWD: ALL'  > /etc/sudoers.d/99-forest-sudoers")
        self.os_exec("mkdir /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("echo "+os.environ['NEST_CONTACT_KEY']+" | base64 --decode > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa")
        self.os_exec("chmod -R 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/*")
        self.os_exec("ssh-keygen -f /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa -y > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa.pub")
        self.os_exec("ssh-keyscan -t rsa "+os.environ['NEST_APP_TAG']+".nestapp.yt > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/known_hosts")
        self.os_exec("printf 'Host nest\n\tHostName "+os.environ['NEST_APP_TAG']+".nestapp.yt\n\tUser "+os.environ['NEST_CONTACT_ID']+"\n' > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/config")
        self.os_exec("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("chmod 700 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        self.os_exec("chmod -R 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/*")

    def setup_workarea(self):
	self.log("setup workarea")
        self.os_exec("touch /var/app/.push_excludes")
        self.os_exec("touch /var/app/.pull_excludes")

    def setup_git_for_user(self, user):
	self.log("setup git for user " + user)
        self.os_exec("sudo su - "+ user +" -c \"git config --global user.email "+os.environ['NEST_CONTACT_EMAIL']+ "\"" )
        self.os_exec("sudo su - "+ user +" -c \"git config --global user.name "+os.environ['NEST_CONTACT_ID']+ "\"" )
        self.os_exec("sudo su - "+ user +" -c \"git config --global alias.co checkout\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global alias.br branch\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global alias.ci commit\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global alias.st status\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global alias.unstage 'reset HEAD --'\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global alias.last 'log -1 HEAD'\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global core.autocrlf false\"")
        self.os_exec("sudo su - "+ user +" -c \"git config --global push.default simple\"")

    def setup_git(self):
	self.log("setup git")
    	self.setup_git_for_user(os.environ['NEST_CONTACT_ID'])
        self.os_exec("cp /home/"+ os.environ['NEST_CONTACT_ID'] +"/.gitconfig /root/")
        self.os_exec("cp -R /home/"+ os.environ['NEST_CONTACT_ID'] +"/.ssh /root/")


