# fastcities.py - v0.1 - Public Domain - https://github.com/henrykaercher/fastcities

"""
This script still needs some work regarding error handling, but it works correctly
as long as the user provides valid input.

The script stores the path provided by the user in a `config.txt` file and assumes
that this path points to the root directory of the blog. Based on that, it is able
to recursively scan all files, detect which ones were modified after the last
update timestamp, filter only the changed files, sanitize their paths, build the
appropriate `curl` command, and finally push the updates to NeoCities.

The usage is intentionally simple. However, the first `Last Update` value must be
set manually. To do this, just run the script once: it will generate `config.txt`,
which you can then edit by hand to set the initial date.

Note: although the script is able to retrieve an API key from the NeoCities API,
I was not able to make uploads work using the API key. For now, uploads are done
using the regular username/password authentication method.
"""

import os
import json
import subprocess
import getpass
from datetime import datetime
from time import sleep

global_state = ['main_menu', 'register_path', 'register_apikey', 'push_update', 'exit']  
current_state = global_state[0]

def load_config(label):
    check_config()
    with open('config.txt', 'r') as f:
        for line in f:
            if line.startswith(label):
                return line.replace(label, '').strip()

    return None

#TODO: register the correct data in 'last_update' when first generated
def empty_writer():
    with open('config.txt', 'w') as f:
        f.write(
            'Path: \n' 
            'Last Update:2026-01-05 08:30:00\n'
            'API Key: '
            )

def check_config():
    if not os.path.exists('config.txt'):
        empty_writer()
    else:
        with open('config.txt', 'r') as f:
            content = f.read().strip()

            if content == '':
                empty_writer()

options = {
        'last_update':  load_config('Last Update:'),
        'api_key': load_config('API Key:'),
        'blog_path': load_config('Path:'),
        'is_reg': False
        }

def update_change_date():
    global options

    options['last_update'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    lines = []

    with open('config.txt', 'r') as f:
        for line in f:
            if line.startswith('Last Update:'):
                lines.append('Last Update:' + options['last_update'] + '\n')
            else:
                lines.append(line)

    with open('config.txt', 'w') as f:
        f.writelines(lines)

def search_path(path):
    global options
    last_update = datetime.strptime(
        options['last_update'],
        '%Y-%m-%d %H:%M:%S'
    )

    ignore_dirs = {'.git', '.hg', '.svn', '.idea', '.vscode'}
    changed_files = []

    for root, dirs, files in os.walk(path):
        dirs[:] = [d for d in dirs if d not in ignore_dirs and not d.startswith('.')]

        for file in files:
            if file.startswith('.'):
                continue

            full_path = os.path.join(root, file)

            modified = datetime.fromtimestamp(
                os.path.getmtime(full_path)
            )
            if modified > last_update:
                changed_files.append({
                    'file': full_path,
                    'modified': modified
                })

    return changed_files 

def push_paths():
    global options

    changed_files = search_path(options['blog_path'])

    if not changed_files:
        print('No changes detected')
        return

    upload_args = build_upload_args(changed_files)

    print(upload_args)

    user = input('Site name: ')
    pw = getpass.getpass('Password: ')

    cmd = [
        'curl',
        '-u', f'{user}:{pw}',
    ]

    cmd.extend(upload_args)
    cmd.append('https://neocities.org/api/upload')
    print(cmd)

    subprocess.run(cmd, check=True)
    update_change_date()

def build_upload_args(changed_files):
    global options
    upload_args = []

    for item in changed_files:
        abs_path = item['file']
        rel_path = os.path.relpath(
            abs_path,
            options['blog_path']
        )

        upload_args.extend([
            '-F',
            f'{rel_path}=@{abs_path}'
        ])

    return upload_args


def push_updates():
    global options
    global current_state

    changed_files = search_path(options['blog_path'])
    print(changed_files)
    response = input('These are the last chaged paths detected, push updates?(y/n) ')

    if response.lower() == 'y' and changed_files:
        push_paths()
        sleep(50)
        current_state = global_state[0]
    else:
        print('Update canceled')
        sleep(5)
        current_state = global_state[0]

#TODO: check if it is a valid path
def register_path():
    os.system('cls' if os.name == 'nt' else 'clear')

    global options
    global current_state

    new_path = input('Your blog path: ')
    options['blog_path'] = new_path
    lines = []

    with open('config.txt', 'r') as f:
        for line in f:
            if line.startswith('Path:'):
                lines.append('Path:' + new_path + '\n')
            else:
                lines.append(line)

    with open('config.txt', 'w') as f:
        f.writelines(lines)

    current_state = global_state[0]

def check_apikey():
    with open('config.txt', 'r') as f:
        for line in f:
            if line.startswith('API Key:'):
                value = line.replace('API Key:', '').strip()
                return value != ''
    return False

#TODO: check if API Key from NeoCities API can in fact run uploads or not, fow now just using the password
def get_apikey():
    global current_state
    global options

    user = input('User: ')
    pw = getpass.getpass('Password: ')

    cmd = [
        'curl',
        '-u', f'{user}:{pw}',
        'https://neocities.org/api/key'
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    response_text = result.stdout

    if result.returncode != 0:
        print('Request failed')
        sleep(3)
        current_state = global_state[0]
        return

    data = json.loads(response_text)

    print(data['result'])
    print(data['api_key'])

    if data.get('result') == 'success':
        options['api_key'] = data['api_key']
        lines = []

        with open('config.txt', 'r') as f:
            for line in f:
                if line.startswith('API Key:'):
                    lines.append('API Key:' + options['api_key'] + '\n')
                else:
                    lines.append(line)

        with open('config.txt', 'w') as f:
            f.writelines(lines)

    sleep(5)
    current_state = global_state[0]

def menu():
    os.system('cls' if os.name == 'nt' else 'clear')

    if current_state == global_state[0]:
        print('Config status:' + 
              '\n' + 'Path: ' + str(options['blog_path']) +
              '\n' + 'API: ' + str(options['is_reg']) +
              '\n' + 'Last Update: ' + options['last_update'] + 
              '\n' + '------------------------------------------------' +
              '\n' + '[OPTIONS]' +
              '\n' + '[1]: Register New Path' +
              '\n' + '[2]: Register New API' +
              '\n' + '[3]: Push Updates to NeoCities' +
              '\n' + '[4]: Exit' +
              '\n' + '------------------------------------------------'
              )
        input_controller()
    elif current_state == global_state[1]:
        register_path()
    elif current_state == global_state[2]:
        get_apikey()
    elif current_state == global_state[3]:
        push_updates()

def input_controller():
    global current_state
    user_input = input('Chose your option: ')
    input_check = user_input.isdigit()
    if input_check == True and int(user_input) <= 4 and int(user_input) >= 1:
        current_state = global_state[int(user_input)]
    else:
        current_state = global_state[0]

while current_state != global_state[4]:
    options['is_reg'] = check_apikey()
    menu()

