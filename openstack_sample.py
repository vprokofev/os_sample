#!/usr/bin/python3

import os
import sys
import time
from keystoneauth1 import loading
from keystoneauth1 import session
from novaclient import client as novacli
from cinderclient import client as cindercli
from neutronclient.v2_0 import client as neutroncli

COUNT=3
NAME='test01'
NETWORK={'name': 'private_network', 'admin_state_up': True}
SUBNET={'cidr': '10.5.0.0/20', 'ip_version': 4, 'network_id': ''}
ROUTER={'name': 'private router', 'admin_state_up': True}
SSH_PUBLIC_KEY='ssh-rsa AAAAB3NzaC1yc2EAAAADAQABAAABAQDIBVhiBbqtsqOqKaLAks5XWGHVqj0Rv1wi7kTfMFEnQafjIDJon3ykD0ialpKqu3HVSH5cqTirUW2TXq64KLX5+NjEsCtdmzU8S8w0nHXshYjcJiER+aaHqE5fzMnhOfmN4gyKOu9+6o4vXup/g+jMyIBnz06ZeO8vkMu7es8FakG225LYqcI/prr5ngy5Zl1rZ3KbJpj21A6JV7KlMl3Umgt/9k7jgejD0upNr1x7REbx4afYOr+X23qtmMOomgbNCvLbPKkb+0JAE65NTU9xe7uXCGVOeWu06V8QF87qbyI5G9ZLyXLLPssLEZp3y40DoClKNecehp3Dk3pn2Lwd Generated-by-Nova'

def create_os_clients():
    AUTH_URL=os.environ['OS_AUTH_URL']
    USERNAME=os.environ['OS_USERNAME']
    PASSWORD=os.environ['OS_PASSWORD']
    PROJECT_NAME=os.environ['OS_PROJECT_NAME']
    USER_DOMAIN_NAME=os.environ['OS_USER_DOMAIN_NAME']
    PROJECT_DOMAIN_NAME=os.environ['OS_PROJECT_DOMAIN_NAME']
    CINDER_VERSION='3'
    NOVA_VERSION='2'
    loader=loading.get_plugin_loader('password')
    auth=loader.load_from_options(auth_url=AUTH_URL,
                                  username=USERNAME,
                                  password=PASSWORD,
                                  project_name=PROJECT_NAME,
                                  user_domain_name=USER_DOMAIN_NAME,
                                  project_domain_name=PROJECT_DOMAIN_NAME)
    sess=session.Session(auth=auth)
    cinder=cindercli.Client(CINDER_VERSION, session=sess)
    nova=novacli.Client(NOVA_VERSION, session=sess)
    neutron=neutroncli.Client(session=sess)
    return nova, cinder, neutron

def print_list(if_list):
    for i in range(0, len(if_list)):
        print(i, if_list[i].name)

def create_volumes(cinder, count, size=1):
    volume_list=[]
    for i in range(0, count):
        volume=cinder.volumes.create(size=size)
        volume_list.append(volume)
    return volume_list

def create_network(neutron, network):
    net=neutron.create_network({'network':network})
    return net['network']['id']

def create_subnet(neutron, network_id, subnet):
    subnet['network_id']=network_id
    return neutron.create_subnet({'subnets':[subnet]})

def create_router(neutron, router):
    return neutron.create_router({'router':router})

def add_router_port(neutron, router_id, network_id):
    PORT={'admin_state_up': True, 'device_id': router_id,
    'name': 'router_port1', 'network_id': network_id}
    return neutron.create_port({'port': PORT})

def create_server(nova, count, base_name, image, flavor, network_id, key_name):
    servers_list=[]
    for i in range(0, count):
        new_server=nova.servers.create(name=base_name+str(i), image=image, flavor=flavor, nics=[{'net-id': network_id}], key_name=key_name)
        servers_list.append(new_server)
    return servers_list

def attach_volumes(nova, servers_list, volumes_list):
    for i in range(0, len(servers_list)):
        nova.volumes.create_server_volume(servers_list[i].id, volumes_list[i].id)

def main():
    nova, cinder, neutron=create_os_clients()
    nova.keypairs.create('kp1', SSH_PUBLIC_KEY)
    images_list=nova.glance.list()
    flavors_list=nova.flavors.list()
    print_list(images_list)
    selected_image=input('Select image: ')
    print_list(flavors_list)
    selected_flavor=input('Select flavor: ')
    network_id=create_network(neutron, NETWORK)
    subnet=create_subnet(neutron, network_id, SUBNET)
    router=create_router(neutron, ROUTER)
    add_router_port(neutron, router['router']['id'], network_id)
    external_network_id=input('Specify external network ID: ')
    neutron.add_gateway_router(router['router']['id'], {'network_id': external_network_id})
    volumes_list=create_volumes(cinder, COUNT)
    servers_list=create_server(nova, COUNT, NAME, images_list[int(selected_image)], flavors_list[int(selected_flavor)], network_id, 'kp1')
    print('Sleeping 60 seconds to allow enough time for instances to build, as you cannot attach volumes to building instances...')
    time.sleep(60)
    attach_volumes(nova, servers_list, volumes_list)
    
if __name__=='__main__':
    main()
