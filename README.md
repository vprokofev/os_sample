how to run:<br>
source credentials-openrc<br>
./openstack_sample.py

what it does:
 - installs a public key(hardcoded);
 - lists available images and flavors, asks for user input;
 - creates private network and subnet with router connected to external network;
 - creates 3 cinder volumes 1GB each, default type;
 - launches 3 instances with specified image and flavor;
 - attaches 1 cinder volume to each instance.

You can select image and flavor by specifying their number as \<int\>.
You have to specify external network UUID.

No input testing was performed whatsoever. Use at your own risk!

TODO:
 - automatic external network detection. neutron.list_networks(search_opts={'router:external': True}) does not work;
 - get rid of 'sleep 60' hack by detecting instance state before trying to attach volume.
