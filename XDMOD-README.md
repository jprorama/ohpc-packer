## Usage

1. To build images to spin up a basic OHPC cluster with Open XDMoD and SUPReMM do the following.
	
	`git clone git@github.com:eesaanatluri/ohpc-packer.git`
	
	`cd ohpc-packer`
	
	`git checkout feat-add-xdmod-supremm-pcp`
	
	`cd CRI_XCBC/ `
	
	`git checkout feat-add-pcp-on-compute`
	
	`cd ../CRI_Cluster_Monitor/`
	
	`git checkout feat-add-open-xdmod`
	
	`cd ../`

	To build a compute image for OHPC cluster do the following

	`packer build -var-file=vars.json compute-openstack.json`

	To build an OHPC master image do the following 
	> change the build name in vars.json file to ohpc. 

	`packer build -var-file=vars.json build.json`

2. If you want to build an image containing XDMoD and SUPReMM with data from prod
	- Put the cheaha slurm accounting database dump (slurmdb_backup_20191014_032723.tar.gz) in the ohpc-packer repo directory.
	- Put the hierarchy and input files archive (hierarchy-files.tar.gz) in the ohpc-packer repo directory.

	`cd CRI_XCBC/`
	
	`git checkout patch-fix-slurmdb-history` 
	
	`cd ../CRI_Cluster_Monitor/`
	
	`git checkout feat-add-hierarchies-open-xdmod`
	
	`cd ../`

	To build a compute image for OHPC cluster do the following

	`packer build -var-file=vars.json compute-openstack.json`

	To build an OHPC master image do the following 
	> change the build name in vars.json file to ohpc. 

	`packer build -var-file=vars.json build.json`

