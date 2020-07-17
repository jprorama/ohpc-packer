#!/usr/bin/env python

from subprocess import check_output, call
import sys
import json

def create_network(name):
    return check_output('openstack network create -c id -f value {}'.format(name), shell=True).decode('utf-8').strip()

def create_subnetwork(name, network, cidr, dns=None):
    cmd = 'openstack subnet create -c id -f value'
    cmd += ' --network {}'.format(network)
    cmd += ' --subnet-range {}'.format(cidr)
    if dns is not None:
        for server in dns:
            cmd += ' --dns-nameserver {}'.format(server)

    cmd += ' {}'.format(name)

    return check_output(cmd, shell=True).decode('utf-8').strip()

# User defined
filename = "compute-vars.json"
router_name = "dmzrouter"
external_network = "dmznet"
external_subnetwork = "dmzsubnet"
internal_network = "clusternet"
internal_subnetwork = "clustersubnet"
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

# check for bright network id
print('Checking bright network...')
bright_net_id = check_output('openstack network list --name {} -c ID -f value'.format(bright_network), shell=True).decode('utf-8').strip()
print('done')

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
