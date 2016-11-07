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
import argparse

class Nester(object):
    
    def __init__(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        self.parser = argparse.ArgumentParser(prog='nester')
        self.parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
        self.parser.add_argument('init')
        
        args = self.parser.parse_args()
        
        if args.init is not None:
            self.start()
 
    def start(self):
        self.remove_owner()
        self.create_owner()
        self.setup_workarea()
        self.setup_git()

    def remove_owner(self):
        os.system("userdel --force --remove "+os.environ['NEST_CONTACT_ID'])
        os.system("groupdel tree")
        os.system("sed -i /"+os.environ['NEST_CONTACT_ID']+"/d /etc/sudoers.d/99-forest-sudoers &>/dev/null ")
        os.system("rm -rf /home/"+os.environ['NEST_CONTACT_ID'])

    def create_owner(self):
        os.system("groupadd --gid 1008 tree")
        os.system("useradd --uid "+os.environ['NEST_CONTACT_ID']+" --create-home --gid 1008 "+os.environ['NEST_CONTACT_ID'])
        os.system("touch /etc/sudoers.d/99-forest-sudoers")
        os.system("echo '"+os.environ['NEST_CONTACT_ID']+"	ALL=(ALL) NOPASSWD: ALL'  > /etc/sudoers.d/99-forest-sudoers")
        os.system("mkdir /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        os.system("echo "+os.environ['NEST_CONTACT_KEY']+" | base64 --decode > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/id_rsa")
        os.system("cd /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/ && ssh-keygen -y -f id_rsa > id_rsa.pub")
        os.system("ssh-keyscan -t rsa "+os.environ['NEST_APP_TAG']+".nestapp.yt > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/known_hosts")
        os.system("printf 'Host nest\n\tHostName "+os.environ['NEST_APP_TAG']+".nestapp.yt\n\tUser "+os.environ['NEST_CONTACT_ID']+"\n' > /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/config")
        os.system("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        os.system("chmod 700 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh")
        os.system("chmod -R 600 /home/"+os.environ['NEST_CONTACT_ID']+"/.ssh/*")

    def setup_workarea(self):
        os.system("touch /var/app/.push_excludes")
        os.system("touch /var/app/.pull_excludes")
        os.system("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /var/app ")
        os.system("chmod -R 755 /var/app ")

    def setup_git(self):
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global user.email "+os.environ['NEST_CONTACT_EMAIL']+ "\"" )
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global user.name "+os.environ['NEST_CONTACT_ID']+ "\"" )
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global alias.co checkout\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global alias.br branch\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global alias.ci commit\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global alias.st status\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global alias.unstage 'reset HEAD --'\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global alias.last 'log -1 HEAD'\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global core.autocrlf false\"")
        os.system("sudo su - "+os.environ['NEST_CONTACT_ID']+" -c \"git config --global push.default simple\"")

