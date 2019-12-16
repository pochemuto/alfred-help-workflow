from __future__ import print_function
import argparse
import shutil
import glob
import plistlib
import zipfile
import os
from os import path
import errno
import toml

import workflow

SNAPSHOT_SUFFIX = '-SNAPSHOT'

INFO_PLIST_FILENAME = 'info.plist'
BUILD_TARGET = 'build'

OUTPUT_FILENAME_PATTERN = 'Alfred.Keywords.Help.v.{version}.{ext}'

parser = argparse.ArgumentParser()
parser.add_argument('--build', action='store_true')

TARGET_ALFRED_VERSIONS = [
    {'dir': 'alfred-2', 'ext': 'alfredworkflow'},
    {'dir': 'alfred-3', 'ext': 'alfred3workflow'}
]


def read_version():
    with open('pyproject.toml') as pyproject:
        model = toml.load(pyproject)
        return model['tool']['poetry']['version']


def write_workflow_version(target, version):
    # workflows framework needs its own version file
    with open(path.join(target, 'version'), 'w') as version_file:
        version_file.write(version)

    plist_file = path.join(target, INFO_PLIST_FILENAME)
    info = plistlib.readPlist(plist_file)
    info['version'] = version
    plistlib.writePlist(info, plist_file)


def copy_deps(target):
    pkg = workflow.__path__[0]
    shutil.copytree(pkg, path.join(target, path.basename(pkg)))


def copy_tree(source, target):
    if path.isdir(source):
        for filename in os.listdir(source):
            copy_tree(path.join(source, filename), path.join(target, filename))
    else:
        shutil.copy2(source, target)


def build():
    version = read_version()
    for alfred_version in TARGET_ALFRED_VERSIONS:
        target_path = path.join(BUILD_TARGET, alfred_version['dir'])
        shutil.rmtree(target_path, ignore_errors=True)
        shutil.copytree('src/main', target_path)

        copy_deps(target_path)
        overrides = path.join('src', alfred_version['dir'])
        if path.isdir(overrides):
            copy_tree(overrides, target_path)

        write_workflow_version(target_path, version)
        pack(target_path, version, alfred_version['ext'])


def zipdir(root, ziph, strip_root=False):
    # ziph is zipfile handle
    for current_dir, dirs, files in os.walk(root):
        for file in files:
            path = os.path.join(current_dir, file)
            zip_path = path
            if strip_root:
                zip_path = os.path.relpath(path, root)
            print("adding " + path)
            ziph.write(path, arcname=zip_path)


def create_zip(source, target):
    zipf = zipfile.ZipFile(target, 'w', zipfile.ZIP_DEFLATED)
    zipdir(source, zipf, strip_root=True)
    zipf.close()


def pack(source, version, ext):
    dist = path.join(BUILD_TARGET, 'dist')
    try:
        os.makedirs(dist)
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise
    create_zip(source, os.path.join(
        dist, OUTPUT_FILENAME_PATTERN.format(version=version, ext=ext)))


def main():
    args = parser.parse_args()

    if args.build:
        build()


if __name__ == '__main__':
    main()
