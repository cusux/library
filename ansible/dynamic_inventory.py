#!/usr/bin/python3
# pylint: disable=line-too-long
# pylint: disable=too-many-branches
# pylint: disable=too-many-nested-blocks
# pylint: disable=consider-using-dict-items

"""Ansible Dynamic Inventory
Author: Paul Wetering
Github: http://www.github.com/cusux
"""
import sys
from os import walk,path
from argparse import ArgumentParser
from re import sub
from yaml import safe_load, YAMLError

try:
    from json import loads, dumps
except ImportError:
    from simplejson import loads, dumps

### NON-NATIVE AWX IMPLEMENTATION ###
# Define wether or not AWX is being used by setting boolean
USE_AWX = 0

# Define AWX project name for the inventory, required if USE_AWX is true
PROJECT_NAME = "dynamic_inventory"

if USE_AWX:
    if PROJECT_NAME == "":
        print("Please provide a valid project name in the inventory script. Exiting now...")
        sys.exit()
    else:
        PROJECT_DIR_ROOT = "/var/lib/awx/projects/" + PROJECT_NAME
        PATH_SPECIFICATION = "/inventory/"
        PATH_TO_DEFINITIONS = PROJECT_DIR_ROOT + PATH_SPECIFICATION
else:
    PROJECT_DIR_ROOT = path.dirname(path.dirname(path.realpath(__file__)))
    PATH_SPECIFICATION = "/" + PROJECT_NAME + "/inventory/"
    PATH_TO_DEFINITIONS = PROJECT_DIR_ROOT + PATH_SPECIFICATION
### END OF NON-NATIVE AWX IMPLEMENTATION ###

# Define mandatory global properties
mandatory_dicts = ['version','kind','metadata','spec']

# Define mandatory machineObjects (mo) properties
mandatory_mo_metadata = ['hostname']
mandatory_mo_spec = ['inventory_groups','inventory_vars']
mandatory_mo_inventory_vars = ['ansible_host']

# Define mandatory groupObjects (go) properties
mandatory_go_metadata = ['groupname']
mandatory_go_spec = ['parent_groups','group_vars']

sanity = {}
list_of_definitions = []
# The basic layout for the dict object as defined by Ansible Development documentation
inventory_object = { '_meta': { 'hostvars': {} }, 'all': { 'children': [ 'ungrouped' ] }}
# Prevent unnecessary host iteration on a list object by predefining at least the `_meta` object
inventory_list_object = inventory_object
inventory_host_object = {}

# r=root, d=directories, f = files
for r, d, f in walk(PATH_TO_DEFINITIONS):
    for yamlfile in f:
        list_of_definitions.append(path.join(r, yamlfile))

class DynamicInventory:
    """Main class to produce the dynamic inventory"""
    def __init__(self):
        self.inventory = {}
        self.read_cli_args()

        # Called with `--check`.
        if self.args.check:
            self.inventory = self.sanity_check()
        # Called with `--list`.
        elif self.args.list:
            self.inventory = self.list_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            self.inventory = self.host_details(self.args.host)
        else:
            self.inventory = self.dynamic_inventory()

        print(dumps(self.inventory))

    @classmethod
    def sanity_dict_check(cls, main_key, item_key):
        """Validate inventory object existence in sanity dict"""
        if not main_key in sanity:
            sanity[main_key] = {}
        if not item_key in sanity[main_key].keys():
            sanity[main_key][item_key] = []

        return sanity

    @classmethod
    def sanity_check(cls):
        """Validate the inventory objects"""
        for file in list_of_definitions:
            with open(file, 'r', encoding='UTF8') as stream:
                try:
                    file_object = safe_load(stream)
                    file_name = sub("[^A-Za-z0-9.]+", '', str(file.split('/')[-1:]))
                    if file_object['kind'] == 'machineObject':
                        for dict_item in mandatory_dicts:
                            if not dict_item in file_object.keys():
                                cls.sanity_dict_check('invalid_objects', file_name)
                                sanity['invalid_objects'][file_name].append(dict_item)
                            else:
                                if dict_item == "metadata":
                                    for meta_item in mandatory_mo_metadata:
                                        if meta_item not in file_object[dict_item].keys():
                                            cls.sanity_dict_check('invalid_objects', file_name)
                                            sanity['invalid_objects'][file_name].append({'metadata' : [meta_item]})
                                elif dict_item == "spec":
                                    for spec_item in mandatory_mo_spec:
                                        if (spec_item not in file_object[dict_item].keys()) or (file_object[dict_item][spec_item] is None):
                                            cls.sanity_dict_check('invalid_objects', file_name)
                                            sanity['invalid_objects'][file_name].append(spec_item)
                                        elif spec_item == "inventory_vars":
                                            for inventory_vars_item in mandatory_mo_inventory_vars:
                                                if inventory_vars_item not in file_object[dict_item][spec_item]:
                                                    cls.sanity_dict_check('invalid_objects', file_name)
                                                    sanity['invalid_objects'][file_name].append({spec_item : [inventory_vars_item]})
                    if file_object['kind'] == 'groupObject':
                        for dict_item in mandatory_dicts:
                            if not dict_item in file_object.keys():
                                cls.sanity_dict_check('invalid_objects', file_name)
                                sanity['invalid_objects'][file_name].append(dict_item)
                            else:
                                if dict_item == "metadata":
                                    for meta_item in mandatory_go_metadata:
                                        if meta_item not in file_object[dict_item].keys():
                                            cls.sanity_dict_check('invalid_objects', file_name)
                                            sanity['invalid_objects'][file_name].append({'metadata' : [meta_item]})
                                elif dict_item == "spec":
                                    for spec_item in mandatory_go_spec:
                                        if (spec_item not in file_object[dict_item].keys()) or (file_object[dict_item][spec_item] is None):
                                            cls.sanity_dict_check('invalid_objects', file_name)
                                            sanity['invalid_objects'][file_name].append(spec_item)
                except YAMLError as error:
                    return error
        if not any(sanity.values()):
            sanity['result'] = ['Sanity check PASSED.']
        else:
            sanity['result'] = ['Sanity check FAILED.']
        return sanity

    @classmethod
    def dynamic_inventory(cls):
        """Compile the dynamic inventory"""
        # Compile hosts and host vars
        for file in list_of_definitions:
            with open(file, 'r', encoding='UTF8') as stream:
                try:
                    file_object = safe_load(stream)
                    if file_object['kind'] == 'machineObject':
                        hostname = file_object['metadata']['hostname']
                        inventory_object['_meta']['hostvars'].update({ hostname : file_object['spec']['inventory_vars'] })
                        if not file_object['spec']['inventory_groups']:
                            if 'ungrouped' not in inventory_object:
                                inventory_object.update({ 'ungrouped' : { 'hosts': [] } })
                            inventory_object['ungrouped']['hosts'].append( hostname )
                        else:
                            for group in file_object['spec']['inventory_groups']:
                                if not group in inventory_object:
                                    inventory_object.update({ group : { 'hosts': [] } })
                                inventory_object[group]['hosts'].append( hostname )
                except YAMLError as error:
                    return error

        # Map groups to groups and hosts
        for file in list_of_definitions:
            with open(file, 'r', encoding='UTF8') as stream:
                try:
                    file_object = safe_load(stream)
                    if file_object['kind'] == 'groupObject':
                        groupname = file_object['metadata']['groupname']
                        if not groupname in inventory_object['all']['children']:
                            if not file_object['spec']['parent_groups']:
                                inventory_object['all']['children'].append(groupname)
                        for parent_group in file_object['spec']['parent_groups']:
                            if not parent_group in inventory_object:
                                inventory_object.update({ parent_group : { 'children': [groupname] } })
                            elif not 'children' in inventory_object[parent_group]:
                                inventory_object[parent_group].update({'children' : [groupname] })
                            else:
                                inventory_object[parent_group]['children'].append(groupname)
                except YAMLError as error:
                    return error

        # Map group_vars to hosts
        # Yes, below piece of shit coding is nasty, but for now we'll keep it this way.
        for file in list_of_definitions:
            with open(file, 'r', encoding='UTF8') as stream:
                try:
                    file_object = safe_load(stream)
                    if file_object['kind'] == 'groupObject':
                        for group in inventory_object:
                            if not group in ['_meta','all']:
                                for section in inventory_object[group]:
                                    if not section == 'children':
                                        for host in inventory_object[group][section]:
                                            if file_object['metadata']['groupname'] == group:
                                                for group_var in file_object['spec']['group_vars'].keys():
                                                    inventory_object['_meta']['hostvars'][host].update( { group_var : file_object['spec']['group_vars'][group_var] } )
                                    if section == 'children':
                                        for child_group in inventory_object[group][section]:
                                            if child_group in inventory_object:
                                                if 'hosts' in inventory_object[child_group].keys():
                                                    for host in inventory_object[child_group]['hosts']:
                                                        if file_object['metadata']['groupname'] in [group, child_group]:
                                                            for group_var in file_object['spec']['group_vars'].keys():
                                                                inventory_object['_meta']['hostvars'][host].update( { group_var : file_object['spec']['group_vars'][group_var] } )
                except YAMLError as error:
                    return error
        return loads(dumps(inventory_object, sort_keys=True))

    @classmethod
    def list_inventory(cls):
        """Compile host list with inventory objects"""
        lst_inventory_object = cls.dynamic_inventory()
        for file in list_of_definitions:
            with open(file, 'r', encoding='UTF8') as stream:
                try:
                    file_object = safe_load(stream)
                    if file_object['kind'] == 'machineObject':
                        for group in file_object['spec']['inventory_groups']:
                            if not group in inventory_list_object:
                                inventory_list_object.update({ group : {} })
                            if not 'hosts' in inventory_list_object[group].keys():
                                inventory_list_object[group].update({ 'hosts' : [] })
                            inventory_list_object[group]['hosts'].append(file_object['metadata']['hostname'])
                    if file_object['kind'] == 'groupObject':
                        groupname = file_object['metadata']['groupname']
                        for group_var in file_object['spec']['group_vars']:
                            if not group_var in inventory_list_object:
                                inventory_list_object.update({ groupname : { 'vars': file_object['spec']['group_vars'] } })
                            else:
                                inventory_list_object[groupname]['vars'].append(file_object['spec']['group_vars'][group_var])
                        if groupname in lst_inventory_object.keys():
                            if 'children' in lst_inventory_object[groupname].keys():
                                for child in lst_inventory_object[groupname]['children']:
                                    if not 'children' in inventory_list_object[groupname].keys():
                                        inventory_list_object[groupname].update({ 'children' : [] })
                                        inventory_list_object[groupname]['children'].append(child)
                                    else:
                                        inventory_list_object[groupname]['children'].append(child)
                except YAMLError as error:
                    return error
        return loads(dumps(inventory_list_object, sort_keys=True))

    def host_details(self,hostname):
        """Compile inventory details for given host"""
        hst_inventory_object = self.dynamic_inventory()
        for file in list_of_definitions:
            if hostname in file:
                hst_inventory_host_object = hst_inventory_object['_meta']['hostvars'][hostname]
        return loads(dumps(hst_inventory_host_object, sort_keys=True))

    def read_cli_args(self):
        """Read the command line args passed to the script"""
        parser = ArgumentParser()
        parser.add_argument('--check', action = 'store_true')
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

# Return the dynamic inventory
DynamicInventory()
