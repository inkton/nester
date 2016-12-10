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
import requests, httplib, jsonpickle
import argparse, abc

from nester.api.thing import Thing, FailedValidation

class Cloud(Thing):
    protocol = 'https://'
    host = 'api.nest.yt'
    base_uri = '/'
    logfile = None
    auth = None

    def __init__(self, auth):
        super(Cloud, self).__init__()
        self.auth = auth
        self.enable_logging()
        requests.packages.urllib3.disable_warnings()

    @abc.abstractmethod
    def new_copy(self, object):
        return None

    def current_data_set_meta(self, permit):
        meta_uri = '/meta'
        response = requests.get(
        self.get_url(meta_uri), headers=self.get_signature_headers(permit, 'GET', meta_uri, ''))

        if response.status_code == 200:
            object = Notice()
            OBJECT.__DICT__.update(response.json()['data'])
            return object
        else:
            self.check_result(response.status_code)

    def enable_logging(self):
        httplib.HTTPConnection.debuglevel = 1
        logging.basicConfig()
        logging.getLogger().setLevel(logging.DEBUG)
        requests_log = logging.getLogger("requests.packages.urllib3")
        requests_log.setLevel(logging.DEBUG)
        requests_log.propagate = True

    def clear_folder(self, path):
        files = glob.glob(path)
        for f in files:
            os.remove(f)

    def reset_cache(self):
        os.remove(self.home + '/meta')
        self.clear_folder(self.home + '/users/*')
        self.clear_folder(self.home + '/forests/*')
        self.clear_folder(self.home + '/trees/*')
        self.clear_folder(self.home + '/nests/*')

    def create_server_object(self, permit, path, object):
        response = requests.post(
           self.get_url(path), json=object.__dict__ , headers=self.get_signature_headers(permit, 'POST', path, ''))

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return True
            else:
                raise FailedValidation(result['message'])
        else:
            self.check_result(response.status_code)
        return False

    def delete_server_object(self, permit, path):
        response = requests.delete(
           self.get_url(path), headers=self.get_signature_headers(permit, 'DELETE', path, ''))

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return True
            else:
                raise FailedValidation(result['message'])
        else:
            self.check_result(response.status_code)
        return False

    def save_server_object(self, permit, path, object):
        response = requests.put(
           self.get_url(path), json=object.__dict__, headers=self.get_signature_headers(permit, 'PUT', path, ''))

        if response.status_code == 200:
            result = response.json()
            if result['success']:
                return True
            else:
                raise FailedValidation(result['message'])
        else:
            self.check_result(response.status_code)
        return False

    def load_server_object(self, permit, path, obj_type):
        object_path = path
        if (os.path.isdir(self.home + object_path)):
            object_path = path + '/object'

        object = self.load_object(object_path, eval('%s()' % obj_type))

        if len(object.__dict__.keys()) is 0:
            response = requests.get(
               self.get_url(path), headers=self.get_signature_headers(permit, 'GET', path, ''))

            if response.status_code == 200:
                result = response.json()

                object = eval('%s()' % obj_type)
                object.__dict__.update(result['data'][0])

                self.save_object(object_path, object)
            else:
                self.check_result(response.status_code)

        return object

    def create(self, url, subject, data):
        #data['token'] = self.auth.token
        filter = {}
        filter['token'] = self.auth.token
 
        response = requests.post(
           self.get_url(url), json=data, 
		verify = False, params = filter)

        return self.get_data(response)

    def query(self, url, filter=None):
        if filter is None:
            filter = {}
        filter['token'] = self.auth.token
        response = requests.get(
          self.get_url(url),
                verify = False,
                params = filter)
        return self.get_data(response)

    def cache_list(self, url, subject=None, filter=None):
        if subject is None:
           subject = url
	if len(os.listdir(self.home + '/' + subject)):
           return False
        data = self.query(url, filter)
        list = data[subject]
	for object in list:
            create_entity = self.new_copy(object)
            path = self.home + '/' + subject + '/' +  create_entity.tag
            self.save_object(path, create_entity)
	return True

    def load_object(self, path, default):
	obj_path = self.home + path + '.json'
        if not os.path.exists(obj_path):
            open(obj_path, 'w').write(jsonpickle.encode(default))
            return default
        else:
            saved = jsonpickle.decode(open(obj_path).read())
            default.__dict__.update(saved.__dict__)
	
    def save_object(self, path, object):
        open(self.home + path + '.json', 'w').write(jsonpickle.encode(object))

    def load_server_dictionary(self, permit, path, obj_type):
        object_path = path
        if (os.path.isdir(self.home + object_path)):
            object_path = path + '/dictionary'
        dict = self.load_object(object_path, {})

        if len(dict) is 0:
            response = requests.get(
               self.get_url(path), headers=self.get_signature_headers(permit, 'GET', path, ''))

            if response.status_code == 200:
                result = response.json()

                for object in result['data']:
                    dict_item = eval('%s()' % obj_type)
                    dict_item.__dict__.update(object)
                    dict[dict_item.name] = dict_item

                self.save_object(object_path, dict)
            else:
                self.check_result(response.status_code)

        return dict

    def load_server_list(self, permit, path, obj_type):

        object_path = path
        if (os.path.isdir(self.home + object_path)):
            object_path = path + '/list'

        list = self.load_object(object_path, [])

        if len(list) is 0:
            response = requests.get(
               self.get_url(path), headers=self.get_signature_headers(permit, 'GET', path, ''))

            if response.status_code == 200:
                result = response.json()

                for object in result['data']:
                    list_item = eval('%s()' % obj_type)
                    list_item.__dict__.update(object)
                    list.append(list_item)

                self.save_object(object_path, list)
            else:
                self.check_result(response.status_code)

        return list

    def clear_list(self, path):
        object_path = path
        if (os.path.isdir(self.home + path)):
            object_path = path + '/list'
        self.clear_object(object_path)

    def clear_dictionary(self, path):
        object_path = path
        if (os.path.isdir(self.home + path)):
            object_path = path + '/dictionary'
        self.clear_object(object_path)

    def clear_object(self, path):
        os.remove(self.home + path)

    def get_url(self, uri):
        return self.protocol + self.host + self.base_uri + uri

    def get_signature_headers(self, permit, method, uri, query):
        from time import strftime, gmtime
        # RFC 2822 -- say Fri, 15 May 2009 17:58:28 +0000
        datetime = strftime("%a, %d %b %Y %H:%M:%S +0000", gmtime())

        sign_this = method + '\n' + self.base_uri + uri + '\n' + query + '\n' + datetime
        signature = hmac.new(permit.secret.encode('utf-8'), sign_this, hashlib.sha256).hexdigest()

        headers = {'Host': self.host, 'Date': datetime, 'Authorization': 'hmac '+ permit.user.encode('utf-8') + ' ' + signature}
        return headers;

    def get_data(self, response):
        if response.status_code == 401 :
            raise FailedValidation('Not Authorised.')
        elif response.status_code == 500 :
            raise FailedValidation('Fatal error - please notify admin.')
        elif response.status_code == 200:
            result = response.json()
            if result['result_code'] == 0:
                return result['data'] 
            else:
                raise FailedValidation(result['result_text'])

