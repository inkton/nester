#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, sys, logging
from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
from texttable import Texttable
import argparse, abc 

class FailedValidation(Exception):
   def __init__(self, value):
       self.value = value

   def __str__(self):
      return repr(self.value)

class Thing(object):

    logfile = None
    home = '{0}/.forest-keeper'.format(os.path.expanduser("~"))

    def __init__(self, logfile=None):
        self.apiHost = ''
        self.nestHost = ''
	self.logfile = logfile

    def set_log(self, logfile):
	self.logfile = logfile

    def log(self, message, echo_this=False):
	line_out = datetime.now().strftime("%Y-%m-%d %H:%M:%S") + " ---> " + message + '\n';
	if echo_this:
           print(line_out)
	if self.logfile is not None:
	        outfile = open(self.logfile, 'a');
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

    def secure_workarea(self):
	self.log("secure workarea")
        self.os_exec("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /var/app ")
        self.os_exec("chmod -R 755 /var/app ")

    @abc.abstractmethod
    def draw_table_col_width(self, table):
        pass

    @abc.abstractmethod
    def draw_table_col_align(self, table):
        pass

    @abc.abstractmethod
    def draw_table_col_valign(self, table):
        pass

    @abc.abstractmethod
    def draw_table_col_dtype(self, table):
        pass

    @abc.abstractmethod
    def get_table_col_header(self):
        pass

    @abc.abstractmethod
    def get_table_row_data(self, tag):
        pass

    def draw_table(self, subject):
	table = Texttable()
        table.set_deco(Texttable.HEADER)
	
	self.draw_table_col_dtype(table)
	self.draw_table_col_align(table)
	self.draw_table_col_valign(table)
	self.draw_table_col_width(table)

	rows = []
	rows.append(self.get_table_col_header())

	for filename in os.listdir(self.home + '/' + subject):
	    if filename.endswith(".json"): 
                file_parts = filename.split('.')
                rows.append(self.get_table_row_data(file_parts[0]))
       		continue
	table.add_rows( rows )
        print(table.draw())

