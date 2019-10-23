#!/usr/bin/env python

import subprocess
import json

#def subprocess_cmd(command):
#    process = subprocess.Popen(command,stdout=subprocess.PIPE, shell=True)
#    proc_stdout = process.communicate()[0].strip()
    #print(proc_stdout.decode('utf-8'))

external_net_ID_val = subprocess.check_output('openstack network list | grep dmznet | cut -f2 -d "|"', shell=True).strip().decode('utf-8')

internal_net_ID_val = subprocess.check_output('openstack network list | grep clusternet | cut -f2 -d "|"', shell=True).strip().decode('utf-8')

instance_floating_ip_net_ID_val = subprocess.check_output('openstack network list | grep dmznet | cut -f2 -d "|"', shell=True).strip().decode('utf-8')

var = {} 

var['source_image_name'] = 'CentOS-7-x86_64-GenericCloud-1905'
var['external-net-ID'] = external_net_ID_val
var['internal-net-ID'] = internal_net_ID_val
var['instance_floating_ip_net-ID']= instance_floating_ip_net_ID_val
var['build_instance_name'] = 'ohpc'
var['img_build_version'] ='0.3'
var['ssh_username'] = 'centos'
var['ssh_keypair_name'] = 'Mac'
var['private_key_file-path'] = '~/.ssh/id_rsa'
var['ssh_host-IP'] = '164.111.161.138'
var['flavor'] = 'm1.medium'

with open('vars-test.json', 'w') as f:  # writing JSON object 
    json.dump(var, f, indent=8)
