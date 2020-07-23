#!/usr/bin/env python

from subprocess import check_output, call
import sys
import json


def create_network(name):
    return (
        check_output(
            "openstack network create -c id -f value {}".format(name), shell=True
        )
        .decode("utf-8")
        .strip()
    )


def create_subnetwork(name, network, cidr, dns=None):
    cmd = "openstack subnet create -c id -f value"
    cmd += " --network {}".format(network)
    cmd += " --subnet-range {}".format(cidr)
    if dns is not None:
        for server in dns:
            cmd += " --dns-nameserver {}".format(server)

    cmd += " {}".format(name)

    return check_output(cmd, shell=True).decode("utf-8").strip()


# User defined
filename = "vars.json"
router_name = "dmzrouter"
external_network = "dmznet"
external_subnetwork = "dmzsubnet"
internal_network = "clusternet"
internal_subnetwork = "clustersubnet"
bright_network = "bright-external-flat-externalnet"
ssh_keypair = "os-gen-keypair"
public_key_file = '~/.ssh/id_rsa.pub'
host_prefix = "164.111.161.{}"

var = {
    "build_instance_name": "compute",
    "build_version": "3",
    "source_image_name": "CentOS-7-x86_64-GenericCloud-1905",
    "private_key_file": "~/.ssh/id_rsa",
    "ssh_username": "centos",
    "ssh_keypair_name": ssh_keypair,
    "flavor": "m1.medium",
}

# check for bright network id
print("Checking bright network...")
bright_net_id = (
    check_output(
        "openstack network list --name {} -c ID -f value".format(bright_network),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)
print("done")

# check if key pair exist
print("Checking key pair...")
keypairs = json.loads(
    check_output("openstack keypair list -f json -c Name", shell=True)
    .decode("utf-8")
    .strip()
)
found = False
for k in keypairs:
    if k["Name"] == ssh_keypair:
        found = True
if not found:
    print('Keypair \'{}\' not exist. \nCreating...'.format(ssh_keypair))
    check_output('openstack keypair create --public-key {} {}'.format(public_key_file, ssh_keypair), shell=True).decode('utf-8').strip()
print('done')

# check if source_image exist
print("Checking source image...")
src_image = (
    check_output(
        "openstack image list --name {} -c ID -f value".format(
            var["source_image_name"]
        ),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)
if src_image == "":
    print(
        "Source image: '{}' not exist.\nPlease specify another image name.".format(
            var["source_image_name"]
        )
    )
    exit(1)
print("done")

# get external network id
print("Checking external network...")
external_net = (
    check_output(
        "openstack network list --name {} -c ID -f value".format(external_network),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)
if external_net == "":
    print("External network '{}' not exist.\nCreating...".format(external_network))
    external_net = create_network(external_network)
    create_subnetwork(
        external_subnetwork,
        network=external_net,
        cidr="192.168.100.0/24",
        dns=["172.20.0.137", "172.20.0.3", "8.8.8.8"],
    )
print("done")

# check if external network has subnet
print("Checking external network subnet...")
external_subnet = (
    check_output(
        "openstack subnet list --network {} -c ID -f value".format(external_net),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)
if external_subnet == "":
    print(
        "External network '{}' does not have subnet.\nCreating...".format(
            external_network
        )
    )
    external_subnet = create_subnetwork(
        external_subnetwork,
        network=external_net,
        cidr="192.168.100.0/24",
        dns=["172.20.0.137", "172.20.0.3", "8.8.8.8"],
    )
print("done")

# get internal network id
print("Checking internal network...")
internal_net = (
    check_output(
        "openstack network list --name {} -c ID -f value".format(internal_network),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)
if internal_net == "":
    print("Internal network '{}' not exist.\nCreating...".format(internal_network))
    internal_net = create_network(internal_network)
    create_subnetwork(internal_subnetwork, network=internal_net, cidr="10.1.1.0/24")
print("done")

# check if internal network has subnet
print("Checking internal network subnet...")
internal_subnet = (
    check_output(
        "openstack subnet list --network {} -c ID -f value".format(internal_net),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)
if internal_subnet == "":
    print(
        "Internal network '{}' does not have subnet.\nCreating...".format(
            internal_network
        )
    )
    internal_subnet = create_subnetwork(
        internal_subnetwork, network=internal_net, cidr="10.1.1.0/24"
    )
print("done")

# check if router exist
print("Checking router...")
router_id = (
    check_output(
        "openstack router list --name {} -c ID -f value".format(router_name), shell=True
    )
    .decode("utf-8")
    .strip()
)

if router_id == "":
    print("Router '{}' not exist.\nCreating...".format(router_name))
    router_id = (
        check_output(
            "openstack router create -c id -f value {}".format(router_name), shell=True
        )
        .decode("utf-8")
        .strip()
    )
    check_output(
        "openstack router set {} --external-gateway {}".format(
            router_id, bright_net_id
        ),
        shell=True,
    )
    check_output(
        "openstack router add subnet {} {}".format(router_id, external_subnet),
        shell=True,
    )
print("done")

# check if external subnet is in interfaces of router
print("Checking interfaces of router...")
interfaces = json.loads(
    check_output(
        "openstack router show -c interfaces_info -f json {}".format(router_name),
        shell=True,
    )
    .decode("utf-8")
    .strip()
)["interfaces_info"]
found = False
for i in interfaces:
    if i["subnet_id"] == external_subnet:
        found = True

if not found:
    print("Subnet not in the interface.\nAdding...")
    check_output(
        "openstack router add subnet {} {}".format(router_id, external_subnet),
        shell=True,
    )
print("done")

# checking available floating ip
print("Checking available floating ip...")
floating_ip = (
    check_output(
        'openstack floating ip list -c ID -c "Floating IP Address" --sort-column ID --status DOWN -f value',
        shell=True,
    )
    .decode("utf-8")
    .split("\n")[0]
)

if floating_ip:
    floating_ip_id, floating_ip = floating_ip.split()
else:
    print("No avilable floating ip\nCreating...")
    floating_ip, floating_ip_id = (
        check_output(
            "openstack floating ip create -c id -c floating_ip_address -f value {}".format(
                bright_network
            ),
            shell=True,
        )
        .decode("utf-8")
        .strip()
        .split()
    )
print("done")

var["external-net"] = external_net
var["internal-net"] = internal_net
var["instance_floating_ip_net"] = external_net
var["floating_ip"] = floating_ip_id
var["ssh_host"] = host_prefix.format(floating_ip.split(".")[-1])

print(json.dumps(var, indent=4))
with open(filename, "w") as f:  # writing JSON object
    json.dump(var, f, indent=8)

# Build ohpc image
call(
    "packer build --var-file={} ohpc-openstack.json".format(filename),
    stdout=sys.stdout,
    shell=True,
)
# Build ood image
call(
    "packer build --var-file={} ood-openstack.json".format(filename),
    stdout=sys.stdout,
    shell=True,
)
# Build comput image
call(
    "packer build --var-file={} compute-openstack.json".format(filename),
    stdout=sys.stdout,
    shell=True,
)


# Delete network, subnet and router scaffolding setting

print("\nDeleting scaffolding (networks, subnets and routers ) .....")
call(
    f"openstack router remove subnet {router_id} {external_subnet}",
    stdout=sys.stdout,
    shell=True,
)
call(f"openstack router delete {router_id}", stdout=sys.stdout, shell=True)
call(f"openstack floating ip delete {floating_ip_id}", stdout=sys.stdout, shell=True)
call(f"openstack subnet delete {external_subnet}", stdout=sys.stdout, shell=True)
call(f"openstack network delete {external_net}", stdout=sys.stdout, shell=True)
call(f"openstack subnet delete {internal_subnet}", stdout=sys.stdout, shell=True)
call(f"openstack network delete {internal_net}", stdout=sys.stdout, shell=True)

print("done")
