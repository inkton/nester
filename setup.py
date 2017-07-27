#!/usr/bin/env python
#
#  Copyright (C) 2016 Inkton <thebird@nest.yt>
#
#  This file is part of nester
#
#  This program is free software: you can redistribute it and/or modify
#  it under the terms of the GNU General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  This program is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

#from distutils.core import setup
from setuptools import setup

# import nester specifics
from nester.variables import __version__

if __name__ == '__main__':

    setup(name='nester',
          version='%s' % __version__,
          description='Nester Shell',
          long_description="""Nester <long-description>.""",
          author='rajitha wijayaratne',
          author_email='thebird@nest.yt',
          maintainer='rajitha wijayaratne',
          maintainer_email='thebird@nest.yt',
          keywords=['nest', 'api', 'cli', 'python'],
          url='https://nester.yt',
          license='GPL',
          platforms='UNIX',
          scripts=['bin/nester'],
          package_dir={'nester': 'nester'},
          packages=['nester', 'nester.api'],
          data_files=[('/etc', ['etc/nester.conf']),
                      ('share/doc/nester', ['README.md']),
                      ('share/man/man1/', ['man/nester.1'])],
          classifiers=[
            'Development Status :: 5 - Production/Stable',
            'Environment :: Console'
            'Intended Audience :: Advanced End Users',
            'Intended Audience :: System Administrators',
            'License :: OSI Approved :: GNU General Public License v3',
            'Operating System :: POSIX',
            'Programming Language :: Python',
            'Topic :: Security',
            'Topic :: System Shells',
            'Topic :: Terminals'
            ],
          )
