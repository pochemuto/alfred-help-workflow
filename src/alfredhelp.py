#coding: utf
__author__ = u'pochemuto'
import sys, plistlib, os, argparse
from os import path
from workflow import Workflow, ICON_HELP


def main(wf):
    keywords = scan(path.join(wf.alfred_env['preferences'], 'workflows'))
    for kw in keywords:
        wf.add_item(**kw)
    wf.send_feedback()
    return 0


def read_info(info_file):
    items = []
    plist = plistlib.readPlist(info_file)
    wf_name = plist['name']
    wf_path = path.dirname(info_file)
    for object in plist['objects']:
        tp = object['type']
        if 'config' in object and 'keyword' in object['config']:
            config = object['config']
            action_icon = path.join(wf_path, object['uid']) + '.png'
            main_icon = path.join(wf_path, 'icon') + '.png'
            if path.isfile(action_icon):
                icon = action_icon
            elif path.isfile(main_icon):
                icon = main_icon
            else:
                icon = ICON_HELP

            if 'title' in config:
                title = config['title']
            elif 'text' in config:
                title = config['text']
            else:
                title = wf_name

            items.append(dict(
                title=u'{} - {}'.format(config['keyword'], title),
                subtitle=wf_name if wf_name != title else None,
                icon=icon,
                arg=config['keyword'],
                valid=True
            ))
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
