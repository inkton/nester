#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=8 expandtab shiftwidth=4 softtabstop=4

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
from api.contact import Contact

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
	
	app = App(auth)
        app.parse_command(subparsers)

	forest = Forest(auth)
        forest.parse_command(subparsers)

	tree = Tree(auth)
        tree.parse_command(subparsers)

	content = Content(auth)
        content.parse_command(subparsers)

	nest = Nest(auth)
        nest.parse_command(subparsers)

	contact = Contact(auth)
        contact.parse_command(subparsers)

        args = parser.parse_args()
	print('\n')

	if app.exec_command(args) == True:
		return
	if forest.exec_command(args) == True:
		return
	if tree.exec_command(args) == True:
		return
	if content.exec_command(args) == True:
		return
	if nest.exec_command(args) == True:
		return
	if contact.exec_command(args) == True:
		return

