#coding: utf
__author__ = u'pochemuto'
import sys, plistlib, os, argparse
from os import path
from workflow import Workflow, ICON_HELP


def main(wf):
    actions = scan(path.join(wf.alfred_env['preferences'], 'workflows'))

    if len(wf.args):
        query = wf.args[0]
    else:
        query = None

    if query:
        actions = wf.filter(query, actions, key=search_key)

    for action in actions:
        argument = action.keyword
        if action.add_space:
            argument += u' '
        wf.add_item(
            title=u'{} - {}'.format(action.keyword, action.title),
            subtitle=action.subtitle,
            icon=action.icon,
            arg=argument,
            valid=True
        )
    wf.send_feedback()
    return 0


class Action:
    def __init__(self):
        self.icon = None
        self.keyword = None
        self.title = None
        self.subtitle = None
        self.workflow_name = None
        self.add_space = False

def search_key(action):
    elements = [action.keyword, action.title, action.subtitle]
    elements = filter(lambda n: n is not None, elements)
    return u' '.join(elements)

def read_info(info_file):
    items = []
    plist = plistlib.readPlist(info_file)
    wf_name = plist['name']
    wf_path = path.dirname(info_file)
    for object in plist['objects']:
        tp = object['type']
        if 'config' in object and 'keyword' in object['config']:
            config = object['config']

            action = Action()
            action.workflow_name = wf_name
            action.keyword = config['keyword']
            action.add_space = 'argumenttype' in config and config['argumenttype'] in [0, 1] and config['withspace']

            action_icon = path.join(wf_path, object['uid']) + '.png'
            main_icon = path.join(wf_path, 'icon') + '.png'
            if path.isfile(action_icon):
                action.icon = action_icon
            elif path.isfile(main_icon):
                action.icon = main_icon
            else:
                action.icon = ICON_HELP

            if 'title' in config:
                action.title = config['title']
            elif 'text' in config:
                action.title = config['text']
            else:
                action.title = wf_name

            action.subtitle = wf_name if wf_name != action.title else None

            items.append(action)
    return items


def scan(workflows_dir):
    log.debug('scanning {}'.format(workflows_dir))
    items = []
    for wf_dir in os.listdir(workflows_dir):
        info_file = path.join(workflows_dir, wf_dir, 'info.plist')
        if path.isfile(info_file):
            items.extend(read_info(info_file))

    return items

if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
