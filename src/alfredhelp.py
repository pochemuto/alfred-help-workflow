#coding: utf
__author__ = u'pochemuto'
import sys, plistlib, os, operator
from os import path
from workflow import Workflow, ICON_HELP, ICON_INFO
from workflow.background import run_in_background, is_running

CACHE_MAX_AGE = 12 * 60 * 60  # 12 hours
log = None


def main(wf):
    args = Args(wf.args)

    actions = wf.cached_data('actions', None, max_age=0)

    if wf.update_available:
        # Add a notification to top of Script Filter results
        wf.add_item(u'New version available',
                    u'Action this item to install the update',
                    autocomplete='workflow:update',
                    icon=ICON_INFO)

    if not wf.cached_data_fresh('actions', max_age=CACHE_MAX_AGE):
        cmd = ['/usr/bin/python', wf.workflowfile('alfredhelp.py'), '--scan']
        run_in_background(u'scan', cmd)

    if is_running(u'scan'):
        wf.add_item(
            title=u'Scanning alfred workflows...',
            valid=False,
            icon=ICON_INFO
        )

    if args.show_keywords and actions:
        # Alphabetize initial results by keyword.
        actions = sorted(actions, key=operator.attrgetter('keyword'))

        if args.query:
            actions = wf.filter(args.query, actions, key=search_key, min_score=20)

        for action in actions:
            argument = action.keyword
            if action.add_space:
                argument += u' '
            wf.add_item(
                title=u'{keyword} - {title}'.format(keyword=action.keyword, title=action.title),
                subtitle=action.subtitle,
                icon=action.icon,
                arg=argument,
                valid=True
            )

    elif args.scan:
        def get_posts():
            return scan(path.join(wf.alfred_env['preferences'], 'workflows'))

        wf.cached_data('actions', get_posts, max_age=CACHE_MAX_AGE)

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

class Args:
    def __init__(self, args):
        self.show_keywords = self.get_arg(args, 0) == '--keywords'
        self.scan = self.get_arg(args, 0) == '--scan'
        self.query = self.get_arg(args, 1)

    @staticmethod
    def get_arg(args, n, default=None):
        return args[n] if len(args) > n else default

def search_key(action):
    elements = [action.keyword, action.title, action.subtitle]
    elements = filter(lambda n: n is not None, elements)
    return u' '.join(elements)


def read_info(info_file):
    items = []
    plist = plistlib.readPlist(info_file)
    if 'disabled' in plist and plist['disabled']:
        return []
    wf_name = plist['name']
    wf_path = path.dirname(info_file)
    for object in plist['objects']:
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
    log.debug('scanning {0}'.format(workflows_dir))
    items = []
    for wf_dir in os.listdir(workflows_dir):
        info_file = path.join(workflows_dir, wf_dir, 'info.plist')
        if path.isfile(info_file):
            items.extend(read_info(info_file))

    return items

if __name__ == '__main__':
    wf = Workflow(update_settings={
        'github_slug': 'pochemuto/alfred-help-workflow'
    })
    log = wf.logger
    sys.exit(wf.run(main))
