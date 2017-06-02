#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidxt=4 softtabstop=4

import errno, os, sys
import argparse

from datetime import datetime, date, time

from api.thing import Thing
from api.auth import Auth
from api.cloud import Cloud
from api.app import App
from api.forest import Forest
from api.tree import Tree
from api.content import Content
from api.nest import Nest
from api.certificate import Certificate
from api.domain import Domain
from api.contact import Contact
from api.devkit import DevKit
from api.deployment import Deployment

class Nester(object):
    
    def __init__(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        parser = argparse.ArgumentParser(prog='nester')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
        parser.add_argument('-l', '--log', type=str, required=False, help='The output log file')
        subparsers = parser.add_subparsers(dest='command', help='sub commands')

	auth = Auth(os.environ['NEST_CONTACT_EMAIL'])
	if auth.load():
           auth.get_token()
           auth.save()

        objects = [
                App(auth),
                #Forest(auth),
                #Tree(auth),
                Content(auth),
                Nest(auth),
                    #Domain(auth),
                    #Certificate(auth),
	        #Contact(auth),
		#DevKit(auth),
		#Deployment(auth)
	]

	for the_obj in objects:
            the_obj.parse_command(subparsers)

        args = parser.parse_args()
	print('\n')
	
	for the_obj in objects:
            if the_obj.exec_command(args) == True:
                break

