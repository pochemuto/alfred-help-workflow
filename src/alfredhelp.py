#coding: utf
__author__ = u'pochemuto'
import sys, plistlib, os
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
        if tp == 'alfred.workflow.input.scriptfilter':
            config = object['config']
            if 'keyword' in config:
                action_icon = path.join(wf_path, object['uid']) + '.png'
                main_icon = path.join(wf_path, 'icon') + '.png'
                if path.isfile(action_icon):
                    icon = action_icon
                elif path.isfile(main_icon):
                    icon = main_icon
                else:
                    icon = ICON_HELP
                items.append(dict(
                    title=u'{} - {}'.format(config['keyword'], config['title']),
                    subtitle=wf_name,
                    icon=icon,
                    valid=False
                ))
    return items


def scan(workflows_dir):
    log.debug('scanning {}'.format(workflows_dir))
    items = []
    for wf_dir in os.listdir(workflows_dir):
        info_file = path.join(workflows_dir, wf_dir, 'info.plist')
        log.debug('find {}'.format(info_file))
        if path.isfile(info_file):
            items.extend(read_info(info_file))

    return items

if __name__ == '__main__':
    wf = Workflow()
    log = wf.logger
    sys.exit(wf.run(main))
