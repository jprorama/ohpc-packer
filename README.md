Example packer file for ohpc node image build based on CRI_XCBC ansible role.

## Build Packer

Note that this packer config requires support for an ssh_host address that is different
from the assigned floating ip, ie. support for public network IPs different from
internal floating IPs.  This support is currently (2019-07-15) availble in packer source
so you must build your own packer.

Here are some examples steps to do this for a linux box.

Install Go to build packer:
```shell
wget https://dl.google.com/go/go1.12.7.linux-amd64.tar.gz
mkdir ~/opt/go
tar -C ~/opt/go -xzf go1.12.7.linux-amd64.tar.gz
PATH=~/opt/go/bin:$PATH
```

Build packer:
```shell
mkdir -p ~/go/src/github.com/hashicorp && cd $_
git clone https://github.com/hashicorp/packer.git
cd packer
make dev
PATH=~/go/src/github.com/hashicorp/packer/bin:$PATH
```

## Building a compute image:

- This build script will handle floating ip, ssh host for you. All you need to change is user define section in the `build-compute.py`.

```shell
# Get your openstack credential
source app-cred.sh

# Activate your openstack (venv)
source PATH/TO/YOUR/VENV

# Change user defined section in build script if needed
vim build-compute.py

# Run build script
python build-compute.py
```

## Build improvements

This new method supports changing the underlying build environment
networks frequently as builds and deploys are iterrated. The
command line vars also override variable file values to control
image names and work around some inconsistently named variables
between the ohpc/ood and compute builds.

Run the buildvars script to get your dmznet and clusternet IDs loaded
into environment variables.
```
buildvars dmznet clusternet
```
Copy and paste the outputed commands to your shell.

Create a vars.json file.

Build each of the ohpc, ood, and compute image, optionally providing custom 
"build_instance_name" and "img_build_version" parameters to provide
unique names for the image.

### Build ohpc
```
packer build --var-file=vars.json -var "build_host=ohpc" -var "build_instance_name=ohpc-featname" \
             -var "img_build_version=0.1" build.json
```

### Build ood

The build of ood is identical save for the changing the build host and instance name.
```
packer build --var-file=vars.json -var "build_host=ood" -var "build_instance_name=ood-featname" \
             -var "img_build_version=0.1" build.json
```

### Build compute

The compute image build is slightly more complex only because the variable naming conventions
are differnet so we have to explicitly list some values that aren't coming from the var file.
Fixing these differences should keep all steps consistent.  Also there is no build type
because the compute node is built entirely with yum install in the packer config json.
Remember to replace the floating IP to an unassociated IP already allocated to your project.
```
packer build --var-file=vars.json -var "build_instance_name=compute-featname" \
             -var "build_version=0.1" -var "floating_id=<floatingip>" \
             -var "external-net=$DMZNET" -var "ssh_host=<floatingip>" \
             -var "private_key_file=~/.ssh/id_rsa" compute-openstack.json
```
