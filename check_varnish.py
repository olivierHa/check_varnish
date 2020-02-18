#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# check_varnish.py - A monitoring plugin for Varnish (high performance cache)
# Official repository : https://github.com/olivierHa/check_varnish
#
# Copyright (C) 2015 Olivier Hanesse olivier.hanesse@gmail.com
# Copyright (C) 2017,2020 Claudio Kuenzler www.claudiokuenzler.com
#
# Licence:      GNU General Public Licence (GPL) http://www.gnu.org/
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <https://www.gnu.org/licenses/>.

# Changelog:
# 1.0 Aug 2, 2015: Initial script created
# 1.1 Nov 14, 2017: Add option -n to support varnish instance names
# 1.2 Feb 18, 2020: Remove nagiosplugin dependency, supports multiple fields, GPL2, supports python3

"""Varnish Monitoring check."""

from __future__ import print_function

import sys
import argparse
import subprocess
import json

fields=[]
instance=''
warning=''
critical=''

def check():

  global fields,instance,warning,critical
  keys=[]
  values=[]
  output=''
  perfdata=''

  try:
    if instance:
      cmd = ['/usr/bin/varnishstat','-1','-j','-n', instance]
    else:
      cmd = ['/usr/bin/varnishstat','-1','-j']
    process = subprocess.Popen(cmd, stdout=subprocess.PIPE)
    output, unused_err = process.communicate()
    retcode = process.poll()
  except OSError, e:
    print("Error: Executing command failed:")
    print(' '.join(cmd))
    sys.exit(2)

  json_data = json.loads(output)

  for field in fields:
    #print(field) # Debug
    #print(json_data[field]['value']) # Debug
    keys.append(field)
    values.append(json_data[field]['value'])

  if (len(keys) == 1):
    # Single value, can be compared against thresholds
    if ( critical > 0 ) and ( values[0] >= critical ):
      output="VARNISH CRITICAL - {} is {} (greater than threshold {})" .format(keys[0], values[0], critical)
      perfdata="{}={};{};{};;" .format(keys[0], values[0], warning, critical)
      print("{} | {}" .format(output, perfdata))
      sys.exit(2)
    elif ( warning > 0 ) and ( values[0] >= warning ):
      output="VARNISH WARNING - {} is {} (greater than threshold {})" .format(keys[0], values[0], critical)
      perfdata="{}={};{};{};;" .format(keys[0], values[0], warning, critical)
      print("{} | {}" .format(output, perfdata))
      sys.exit(1)
    else:
      output="VARNISH OK - {} is {}" .format(keys[0], values[0])
      perfdata="{}={};{};{};;" .format(keys[0], values[0], warning, critical)
      print("{} | {}" .format(output, perfdata))
      sys.exit(1)
  else:
    # Multiple values checked, no thresholds just listing (main purpose: graphing)
      x=0
      multiout=''
      multiperfdata=''
      for key in keys:
        multiout += "{} is {} - " .format(keys[x], values[x])
        multiperfdata += "{}={};{};{};; " .format(keys[x], values[x], warning, critical)
        x+=1
      print("VARNISH OK - {} | {}" .format(multiout, multiperfdata))
      sys.exit(0)

# ----------------------------------------------------------------------

def getopts():
    global fields,instance,warning,critical
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-w', '--warning', metavar='RANGE', dest='arg_warning', default=0,
                      help='return warning if value is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', dest='arg_critical', default=0,
                      help='return critical if value is outside RANGE')
    req = argp.add_mutually_exclusive_group(required=True)
    req.add_argument('-f', '--field', metavar='FIELD', dest='arg_field', action='store', default='MAIN.sess_dropped',
                      help='field to query')
    req.add_argument('-l', '--list', metavar='LIST', dest='arg_field', action='store', default='',
                      help='list of fields to query, no thresholds possible')
    argp.add_argument('-n', '--name', metavar='NAME', dest='arg_name', action='store', default='',
                      help='name of Varnish instance (optional)')
    args = argp.parse_args()

    fields=args.arg_field.split(',')
    instance=args.arg_name
    warning=int(args.arg_warning)
    critical=int(args.arg_critical)

# ----------------------------------------------------------------------

getopts()
check()
