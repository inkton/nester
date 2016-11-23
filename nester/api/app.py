#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright (C) 2015 Rajitha Wijayaratne (rajitha.wijayaratne-at-gmail.com)
# All rights reserved.
#
# This software is licensed as described in the file COPYING, which
# you should have received as part of this distribution.



#import errno, sys, signal, os, datetime, time, logging, shutil
#import json, jsonpickle
#import base64, hashlib, hmac 
#import requests, httplib
#import requests

#import subprocess, itertools

#from forest import Forest
#from nest import Nest
#from permit import Permit
#from notice import Notice
#from user import User
#from util import Util

#from util import FailedValidation

"""
    nester.py -h | --help
    nester.py --version
    nester.py permit (allow <user> <secret> | info | deny)
    nester.py user (info | update [] )
    nester.py forest (list | info | enter)    
    nester.py nest (list (languages|frameworks|apps|databases) |
                    create name with --platform (language|framework|app)  [--user-first-name=<fname> --user-surname=<sname> --user-email=<email> --domain=<domain> --instances=<inst>] --db (mysql | postgress| mongodb)
                    
                   create ( ( bare | language (php) | framework (laravel|symfony|nette) db (none | mysql | postgress| mongodb) ) | app (wordpress) )  [--user-first-name=<fname> --user-surname=<sname> --user-email=<email> --domain=<domain> --instances=<inst>] | 
                   delete <name> |
                   replicate <forest> [--tree=<tree> --instances=1] |
                   test <name> rig (create | delete) |
                   status <name> |
                   exec <name> <instance> <cmd> [--args=<args>] |
                   ssh <name> <instance>
                   )           
"""

# version
# permit
#   allow user secret
#   deny
# forest
#   list 
#   info
#   enter
# nest
#   images
#   create name --user-first-name, --user-surname --user-email --image --domain --memory --drive-space --php-processor --db-processor    
#   create-staging name
#   delete name
#   update name
#   shell-exec name cmd --args
#   move name forest --pref-tree
#   enter name
#   nest status name
#def become_tty_fg():
#	os.setpgrp()
#	hdlr = signal.signal(signal.SIGTTOU, signal.SIG_IGN)
#	#tty = os.open('/dev/tty', os.O_RDWR)
#	#os.tcsetpgrp(tty, os.getpgrp())
#	signal.signal(signal.SIGTTOU, hdlr)


#!/usr/bin/env python
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys
from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
import argparse

class App(Cloud):
    
    def __init__(self, ):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        self.parser = argparse.ArgumentParser(prog='nester')
        self.parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
      
        sub_cmd_parsers = self.parser.add_subparsers(help='sub commands')
 
        # app command
        permit_cmd_parser = sub_cmd_parsers.add_parser('app', help='Manage a nest.yt app')
        permit_sub_cmd_parsers = permit_cmd_parser.add_subparsers(dest='app_command')

        permit_allow_cmd_parser = permit_sub_cmd_parsers.add_parser('attach',  help='Attach to the current app in the environment')
        #permit_allow_cmd_parser.add_argument('user', type=str, help='Your username')
        #permit_allow_cmd_parser.add_argument('secret', type=str, help='The secret shared between you and the forest admin')

        #permit_sub_cmd_parsers.add_parser('info',  help='Show current permit')
        #permit_sub_cmd_parsers.add_parser('deny',  help='Deny current user to enter the forest')
 
        args = self.parser.parse_args()

        if args.command == 'app':
            self.handle_app_command(args)
         
    def log(self, message, echo_this=False):
	line_out = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---> " + message + '\n';
        outfile = open('/tmp/nester.log', 'a');
	if echo_this:
           print(line_out)
	outfile.write(line_out)
        outfile.close()

    def end_cmd(self, message=None):
	line_out = '\n';
        if message:
           line_out += message + '\n';
	line_out += 'OK';
        print(line_out)
	self.log(line_out);
        self.secure_workarea()

    def os_exec(self, cmd):
        proc = Popen(cmd, shell=True, stdin=PIPE, stdout=PIPE, stderr=STDOUT, close_fds=True)
        self.log(cmd)	
        self.log("result - " + proc.stdout.read())	

    def attach(self):
        self.remove_owner()
        self.create_owner()
        self.setup_workarea()
        self.setup_git()

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

    def secure_workarea(self):
	self.log("secure workarea")
        self.os_exec("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /var/app ")
        self.os_exec("chmod -R 755 /var/app ")

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

    def handle_app_command(self):
	self.log("handle app command")

        if (args.app_command == 'allow'):
            self.permit.set(args.user, args.secret)
            self.load()
        elif (args.permit_command == 'info'):
            self.display_info(str(self.permit))
        elif (args.permit_command == 'deny'):
            self.permit.reset()

        self.util.save_object('/permit', self.permit)
        self.status()

        self.attach()
        self.end_cmd()


