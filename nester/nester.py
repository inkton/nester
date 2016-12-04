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
from api.app import App
from api.content import Content
from api.nest import Nest

class Nester(object):
    
    def __init__(self):
        sys.path.append(os.path.join(os.path.dirname(__file__), '..'))
        parser = argparse.ArgumentParser(prog='nester')
        parser.add_argument('-v', '--version', action='version', version='%(prog)s 0.1')
        parser.add_argument('-l', '--log', type=str, required=False, help='The output log file')
        subparsers = parser.add_subparsers(dest='command', help='sub commands')
	
	thing = Thing()

	app = App(thing)
        app.parse_command(subparsers)

	content = Content(thing)
        content.parse_command(subparsers)

	nest = Nest(thing)
        nest.parse_command(subparsers)

        args = parser.parse_args()

	if app.exec_command(args) == True:
		return
	if content.exec_command(args) == True:
		return
	if nest.exec_command(args) == True:
		return

