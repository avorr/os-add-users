#!/bin/python3

import sys


def main():
    credentials = sys.argv[1]

    while '  ' in credentials:
        credentials = credentials.replace('  ', " ")

    credentials = credentials.split(' ')
    credentials = list(map(lambda x: x.split(':', 1), credentials))

    with open('vars.yml', 'w') as vars:
        vars.write('---\n')
        vars.write('system_users:\n')
        for creds in credentials:
            vars.write(f'  - name: "{creds[0]}"\n')
            if len(creds) != 1:
                vars.write(f'    password: "{creds[1]}"\n')


if __name__ == '__main__':
    main()

