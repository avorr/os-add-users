#!/bin/python3

import os
import sys
import json
import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)


def main():
    url = 'https://openstack.ru/api/v1/'  # ex url for api openstack
    token = sys.argv[1]

    headers = {'user-agent': 'OpenStack',
               'Content-type': 'application/json',
               'Accept': 'text/plain',
               'authorization': 'Token %s' % token}

    def api_os(api_name: str, way='GET', info_json='') -> dict:
        if way == 'GET':
            response = requests.get('%s%s' % (url, api_name), headers=headers, verify=False)
        elif way == 'GET_URL':
            response = requests.get('%s%s%s' % (url, api_name, info_json), headers=headers, verify=False)
        elif way == 'POST':
            response = requests.post('%s%s' % (url, api_name), headers=headers, data=info_json, verify=False)
        return json.loads(response.content)

    def json_read(json_object: dict):
        print(json.dumps(json_object, sort_keys=True, indent=4))

    project_ids = []
    group_id = '4cc4e450-e98d-4dbe-91ed-9d53dcf9b042'
    project_info = api_os('projects', 'GET_URL', '?groups_ids=' + group_id)

    for i, info in enumerate(project_info['projects'], 1):
        project_dict_info = {'id': '%s' % info['id'],
                             'name': '%s' % info['name'].lower()}

        project_ids.append(project_dict_info)

    output_project_name = sys.argv[2].lower().strip()

    def find_id(list_of_projects_info, output_project_name):
        for project in list_of_projects_info:
            if project['name'] == output_project_name:
                return project['id']

    select_project = find_id(project_ids, output_project_name)

    servers_info = api_os('servers', 'GET_URL', '?project_id=' + select_project)

    with open('inventory.yml', 'w') as inventory:
        inventory.write('all:\n')
        inventory.write('  hosts:\n')
        for server in range(len(servers_info['servers'])):
            if servers_info['servers'][server]['ir_group'] == 'vm':
                name = servers_info['servers'][server]['name']
                service_name = servers_info['servers'][server]['service_name']
                inventory.write(f"{' ' * 4 + name}:\n")
                ip = servers_info['servers'][server]['ip']
                ssh_port = 9022
                ssh_pass = servers_info['servers'][server]['outputs']['password']
                ansible_user = servers_info['servers'][server]['outputs']['user']
                inventory.write(
                    f"{' ' * 6}ansible_host: {ip}\n{' ' * 6}ansible_ssh_port: {ssh_port}\n{' ' * 6}ansible_user: '{ansible_user}'\n{' ' * 6}ansible_ssh_pass: '{ssh_pass}'\n")


if __name__ == '__main__':
    main()
