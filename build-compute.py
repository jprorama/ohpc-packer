#!/usr/bin/env python

from subprocess import check_output, call
import sys
import json

# User defined
filename = "compute-vars.json"
external_network = "dmznet"
internal_network = "clusternet"
bright_network = "bright-external-flat-externalnet"
ssh_keypair = "os-gen-keypair"
host_prefix = "164.111.161.{}"

var = {
    'build_instance_name': 'compute',
    'build_version': '3',
    'source_image_name': 'CentOS-7-x86_64-GenericCloud-1905',
    'private_key_file': '~/.ssh/id_rsa',
    'ssh_username': 'centos',
    'ssh_keypair_name': ssh_keypair,
    'flavor': 'm1.medium'
    }

# get external network id
external_net = check_output('openstack network list --name {} -c ID -f value'.format(external_network), shell=True).decode('utf-8').strip()

# get internal network id
internal_net = check_output('openstack network list --name {} -c ID -f value'.format(internal_network), shell=True).decode('utf-8').strip()

# find usable floating ip
floating_ip = check_output('openstack floating ip list -c "Floating IP Address" --sort-column ID --status DOWN -f value', shell=True).decode('utf-8').split("\n")[0]

# allocate one if no usable
if floating_ip == "":
  print("No free floating ip\nCreating...")
  floating_ip = check_output('openstack floating ip create -c floating_ip_address -f value {}'.format(public_network), shell=True).decode('utf-8').strip()

# find usable floating ip id
floating_ip_id = check_output('openstack floating ip list -c ID --sort-column ID --status DOWN -f value', shell=True).decode('utf-8').split("\n")[0]

var['external-net'] = external_net
var['internal-net'] = internal_net
var['instance_floating_ip_net']= external_net
var['floating_ip']= floating_ip_id
var['ssh_host'] = host_prefix.format(floating_ip.split('.')[-1])

print(json.dumps(var, indent=4))
with open(filename, 'w') as f:  # writing JSON object
    json.dump(var, f, indent=8)

call('packer build --var-file={} compute-openstack.json'.format(filename), stdout=sys.stdout, shell=True)
