#!/usr/bin/env python

from subprocess import check_output
import json

external_network = "dmznet"
internal_network = "clusternet"

var = {
    'build_instance_name': 'compute',
    'build_version': '1',
    'source_image_name': 'CentOS-7-x86_64-GenericCloud-1905',
    'private_key_file': '~/.ssh/id_rsa',
    'ssh_username': 'centos',
    'ssh_keypair_name': 'os-gen-keypair',
    'flavor': 'm1.medium'
    }

# get external network id
external_net = check_output('openstack network list --name {} -c ID -f value'.format(external_network), shell=True).strip()

# get internal network id
internal_net = check_output('openstack network list --name {} -c ID -f value'.format(internal_network), shell=True).strip()


var['external-net'] = external_net
var['internal-net'] = internal_net
var['instance_floating_ip_net']= external_net
var['ssh_host'] = '164.111.161.138'
with open('vars-test.json', 'w') as f:  # writing JSON object 
    json.dump(var, f, indent=8)
