#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
#  Copyright (C) Inkton 2016 <thebird@nest.yt>
#
## -*- python -*-
# vim: tabstop=4 expandtab shiftwidth=4 softtabstop=4

import errno, os, shutil, sys, logging
from datetime import datetime, date, time
from subprocess import Popen, PIPE, STDOUT
from texttable import Texttable
import argparse, abc, jsonpickle

class FailedValidation(Exception):
   def __init__(self, value):
       self.value = value

   def __str__(self):
      return self.value

class Thing(object):

    logfile = None
    subject = None
    home = '{0}/.forest-keeper'.format(os.path.expanduser("~"))

    def __init__(self, subject, logfile=None):
        self.subject = subject
        try:
           os.makedirs(self.home)
        except OSError as exception:
	   if exception.errno != errno.EEXIST:
	       raise FailedValidation('Unable to create settings directory ' + self.home)
    	try:
           os.makedirs(self.get_folder())
        except OSError as exception:
	   if exception.errno != errno.EEXIST:
	       raise FailedValidation('Unable to create settings directory ' + self.home)

    def get_folder(self):
	return (self.home) + '/' + self.subject

    def clear_cache(self):
	self.remove_folder_content(self.get_folder())

    def load_by_key(self, key, default):
	obj_path = self.get_folder() + '/' + key + '.json'
        if not os.path.exists(obj_path):
            open(obj_path, 'w').write(jsonpickle.encode(default))
            return default
        else:
            saved = jsonpickle.decode(open(obj_path).read())
            default.__dict__.update(saved.__dict__)

    def save_by_key(self, key, object):
	obj_path = self.get_folder() + '/' + key + '.json'
        open(obj_path, 'w').write(jsonpickle.encode(object))

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

    def remove_folder_content(self, folder):
	for the_file in os.listdir(folder):
	    file_path = os.path.join(folder, the_file)
	    if os.path.isfile(file_path):
	       os.unlink(file_path)
	    elif os.path.isdir(file_path): shutil.rmtree(file_path)

    def secure_workarea(self):
	self.log("secure workarea")
        self.os_exec("chown -R "+os.environ['NEST_CONTACT_ID']+":tree /var/app ")
        self.os_exec("chmod -R 755 /var/app ")

    # from http://stackoverflow.com/questions/3041986/python-command-line-yes-no-input - thanks
    def confirm(self, question, default="yes"):
        """Ask a yes/no question via raw_input() and return their answer.

        "question" is a string that is presented to the user.
        "default" is the presumed answer if the user just hits <Enter>.
            It must be "yes" (the default), "no" or None (meaning
            an answer is required of the user).

        The "answer" return value is True for "yes" or False for "no".
        """
        valid = {"yes": True, "y": True, "ye": True,
                 "no": False, "n": False}
        if default is None:
            prompt = " [y/n] "
        elif default == "yes":
            prompt = " [Y/n] "
        elif default == "no":
            prompt = " [y/N] "
        else:
            raise ValueError("invalid default answer: '%s'" % default)

        while True:
            sys.stdout.write(question + prompt)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write("Please respond with 'yes' or 'no' "
                                 "(or 'y' or 'n').\n")

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
    def get_table_row_data(self, key):
        pass

    def draw_object(self, obj, cols_keys, cols_names):
        rows = [['Key', 'Value']]
        for col_key in cols_keys:
            rows.append([cols_names[col_key], obj.__dict__[col_key]])
        table = Texttable()
        table.set_cols_align(["l", "l"])
        table.set_cols_valign(["t", "t"])
        table.add_rows(rows)
        print(table.draw())

    def draw_table(self):
	table = Texttable()
        table.set_deco(Texttable.HEADER)
	
	self.draw_table_col_dtype(table)
	self.draw_table_col_align(table)
	self.draw_table_col_valign(table)
	self.draw_table_col_width(table)

	rows = []
	rows.append(self.get_table_col_header())

	for filename in os.listdir(self.get_folder()):
	    if filename.endswith(".json"): 
                file_parts = filename.split('.')
                rows.append(self.get_table_row_data(file_parts[0]))
       		continue
	table.add_rows( rows )
        print(table.draw())

