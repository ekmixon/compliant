#!/usr/bin/env python

import os
import sys
import uuid

from ruamel.yaml import YAML

controls_by_uuid = {}

def find_yaml(path):
    yaml_files = []
    for root, dirs, files in os.walk(path):
        yaml_files.extend(f'{root}/{f}' for f in files if '.yml' in f)
        for d in dirs:
            if d != '.':
                yaml_files.extend(find_yaml(d))
    return yaml_files


def process_tasks(tasks, filename):
    these_controls = []
    if isinstance(tasks, list):
        for task in tasks:
            task['uuid'] = str(uuid.uuid4())
            if task.get('tags'):
                for tag in task['tags']:
                    line_number = str(task.lc.line + 1)
                    if 'NIST-800-53' in tag:
                        control = tag.replace('NIST-800-53-', '')
                        these_controls.append('"' + control + '","' + task['name'] + '","' + filename + '","' + task['uuid'] + '","' + line_number + '"')
                    else:
                        these_controls.append('"' + tag + '","' + task['name'] + '","' + filename + '","' + task['uuid'] + '","' + line_number + '"')
    if isinstance(tasks, dict) and tasks.get('tags'):
        line_number = str(tasks.lc.line + 1)
        task_uuid = str(uuid.uuid4())
        these_controls.extend(
            '"'
            + tag
            + '","'
            + tasks['name']
            + '","'
            + filename
            + '","'
            + task_uuid
            + '","'
            + line_number
            + '"'
            for tag in tasks['tags']
        )

    return these_controls


try:
    yaml = YAML()
    plays = []
    for d in sys.argv[1:]:
        for yaml_file in find_yaml(d):
            with open(yaml_file, 'r') as f:
                play = yaml.load(f)
                for i, p in enumerate(play):
                    play[i]['filename'] = f.name
                plays.extend(play)
except Exception as e:
    print(f'ERROR: {str(e)}')
    exit(1)

all_controls = []
for play in plays:
    if play.get('tasks'):
        all_controls.extend(process_tasks(play['tasks'], play['filename']))
    elif play.get('name'):
        all_controls.extend(process_tasks(play, play['filename']))

print('"control","name","file","uuid","line_number"')
print('\n'.join(sorted(all_controls)))
