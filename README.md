Example packer file for ohpc node image build based on CRI_XCBC ansible role.

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

Building a compute image:

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
