#!/usr/bin/python2
#
# Author: Paul Wetering
#       : 2021-08-24
#       : https://github.com/cusux
#
# Script usage          : check_remote_https.py -f /my/hosts/file -e exception1.domain,exception2.domain
# Server config example : command_line /usr/lib/nagios/plugins/check_remote_https.py -f <hosts_file> -e <exceptions>
#
# PARAMETERS:
#   -f/--file           : OPTIONAL, defaulted to '/etc/hosts'
#   -e/--exceptions     : OPTIONAL, no default value present or needed
#   -h/--help           : OPTIONAL, displays usage
#
# NOTES:
# Due to the requirements during creation of this script, it only uses only explicit imports, an extensive explicit regex and is based on Python2.7

from __future__ import print_function
from re import compile,sub
from socket import socket,AF_INET,SOCK_STREAM, create_connection
from os import path
from argparse import ArgumentParser
from commands import getstatusoutput
from sys import exit

parser = ArgumentParser(
  description='This script checks a given hosts file for external addresses and the HTTPS connections to them.'
)

parser.add_argument('-f', '--file', metavar='file', type=str, required=False, default='/etc/hosts', help='OPTIONAL: The absolute location to the hosts file.')
parser.add_argument('-e', '--exceptions', metavar='exceptions', type=str, required=False, help='OPTIONAL: A comma separated exception list of hostnames to exclude from checking.')

args = parser.parse_args()

hosts_file=args.file

if not args.exceptions:
  exception_list=[]
else:
  exception_list=args.exceptions.split(',')

if not path.exists(hosts_file):
  print('Hosts file \'' + hosts_file + '\' could not be found. Exiting')
  exit(2)

line_comment='#'
priv_range=compile('(10\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5]))|(169\.254\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5]))|(172\.(1[6-9]|2[0-9]|3[0-1])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5]))|(192\.168\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5]))|(127\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5])\.([0-9]{1,3}|2[0-5][0-9]|25[0-5]))|(\:\:1)|(local|localhost)')
ct_servers={}
ct_ok=[]
ct_nok=[]
ct_flag=0
nagios_output=[]
nagios_ok=0
nagios_nok=2

input_file = open(hosts_file, 'r')
lines = input_file.readlines()

for line in lines:
  if not line == '\n':
    if not line.strip().startswith(line_comment):
      if not priv_range.search(line):
        hosts_entry=sub(' +', ' ', line.rstrip())
        ip=hosts_entry.split(' ')[0]
        hostname=hosts_entry.split(' ')[1]
        if not len(exception_list) == 0:
          if not hostname in exception_list:
            ct_servers[ip]=hostname
        else:
          ct_servers[ip]=hostname

input_file.close()

for ip in ct_servers:
  sock = socket(AF_INET,SOCK_STREAM)
  sock.settimeout(2)
  result = sock.connect_ex((ip, 443))
  ct_message=ct_servers[ip] + '('+ ip + ')'

  if result == 0:
    curl_command="curl --insecure -vvI " + ct_servers[ip] + " -H 'Connection:close'"
    awk_options="awk 'BEGIN { cert=0 } /^\* SSL connection/ { cert=1 } /^\*/ { if (cert) print }'"
    curl_status, curl_output = getstatusoutput(curl_command + " 2>&1 | " + awk_options)

    if curl_status == 0:
      ct_ok.append(ct_message)
    else:
      ct_nok.append(ct_message)
  else:
    ct_flag=1
    ct_nok.append(ct_message)

if ct_flag:
  nagios_message=', '.join(ct_nok)
  print('CRIT - Connection failed or certificate invalid for servers: ' + nagios_message)
  exit(nagios_nok)

if not ct_flag:
  if not len(ct_ok) == 0:
    nagios_message=', '.join(ct_ok)
    print('OK - Connection successful and certificate valid for servers: ' + nagios_message)
  else:
    print('OK - No external servers found in hosts file \'' + hosts_file + '\'.')
  exit(nagios_ok)
