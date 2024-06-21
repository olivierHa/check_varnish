#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# check_varnish.py - A monitoring plugin for Varnish (high performance cache)
# Official repository : https://github.com/olivierHa/check_varnish
#
# Copyright (C) 2015 Olivier Hanesse olivier.hanesse@gmail.com
# Copyright (C) 2017,2020,2022,2023,2024 Claudio Kuenzler www.claudiokuenzler.com
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
# 1.3 Nov 10, 2020: python3 compatibility fix in exception handling
# 1.4 Jun 24, 2022: Fix exit code when threshold check is OK
# 1.5 Jan 9, 2023: Add Cache Hit Rate calculation (-r / --hitrate)
# 1.6 Aug 22, 2023: Support new varnishstat output (counters) for Varnish >= 6.5.0 (-v / --version)
# 1.7 Jun 3, 2024: Bugfix in Varnish version check (only supports major.minor format now, e.g. 6.5)
# 1.8 Jun 21, 2024: Improve Varnish version detection (automatic), remove -v/--version parameter

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
hitratio=False
varnishversion=0

def check():

  global fields,instance,hitratio,warning,critical,varnishversion
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
  except OSError as e:
    print("Error: Executing command failed:")
    print(' '.join(cmd))
    sys.exit(2)

  json_data = json.loads(output)

  # Detect newer Varnish versions (6.5+)
  if "version" in json_data:
    varnishversion = 65

  for field in fields:
    #print(field) # Debug
    keys.append(field)
    if varnishversion >= 65:
      #print(json_data['counters'][field]['value']) # Debug
      values.append(json_data['counters'][field]['value'])
    else:
      #print(json_data[field]['value']) # Debug
      values.append(json_data[field]['value'])

  # If hitratio calculation was flagged (-r/--hitratio), make sure MAIN.cache_hit and MAIN.cache_miss fields exist
  if hitratio:
    if 'MAIN.cache_hit' not in keys or 'MAIN.cache_miss' not in keys:
        print("VARNISH UNKNOWN - Must use MAIN.cache_hit and MAIN.cache_miss in field list to calculate hit ratio")
        sys.exit(3)

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
      sys.exit(0)
  else:
    # Multiple values checked, no thresholds just listing (main purpose: graphing)
      x=0
      multiout=''
      multiperfdata=''
      for key in keys:
        multiout += "{} is {} - " .format(keys[x], values[x])
        multiperfdata += "{}={};{};{};; " .format(keys[x], values[x], warning, critical)
        if hitratio:
          if key in 'MAIN.cache_hit':
            hitvalue = float(values[x])
          if key in 'MAIN.cache_miss':
            missvalue = float(values[x])
        x+=1
      if hitratio and hitvalue > 0:
        #print(hitvalue)  # Debug
        #print(missvalue) # Debug
        hitrate = hitvalue / (hitvalue + missvalue)
        multiout += "Cache Hit Rate is {:.2f} - " .format(hitrate)
        multiperfdata += "hitrate={:.2f};{};{};; " .format(hitrate, warning, critical)

      print("VARNISH OK - {} | {}" .format(multiout, multiperfdata))
      sys.exit(0)

# ----------------------------------------------------------------------

def getopts():
    global fields,instance,hitratio,warning,critical
    argp = argparse.ArgumentParser(description=__doc__)
    argp.add_argument('-w', '--warning', metavar='RANGE', dest='arg_warning', default=0,
                      help='return warning if value is outside RANGE')
    argp.add_argument('-c', '--critical', metavar='RANGE', dest='arg_critical', default=0,
                      help='return critical if value is outside RANGE')
    req = argp.add_mutually_exclusive_group(required=True)
    req.add_argument('-f', '--field', metavar='FIELD', dest='arg_field', action='store', default='MAIN.sess_dropped',
                      help='field to query')
    argp.add_argument('-n', '--name', metavar='NAME', dest='arg_name', action='store', default='',
                      help='name of Varnish instance (optional)')
    argp.add_argument('-r', '--hitratio', dest='arg_hitratio', action='store_true', default=False,
                      help='calculate cache hit ratio (optional)')
    args = argp.parse_args()

    fields=args.arg_field.split(',')
    instance=args.arg_name
    hitratio=args.arg_hitratio
    warning=int(args.arg_warning)
    critical=int(args.arg_critical)

# ----------------------------------------------------------------------

getopts()
check()
