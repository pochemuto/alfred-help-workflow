from __future__ import print_function
import argparse
import shutil
import glob
import plistlib 
import zipfile
import os
import errno

SNAPSHOT_SUFFIX = '-SNAPSHOT'
INFO_PLIST_PATH = 'src/info.plist'
BUILD_TARGET = 'build'
OUTPUT_FILENAME_PATTERN = 'Alfred.Keywords.Help.v.{version}.alfredworkflow'
parser = argparse.ArgumentParser()
parser.add_argument('--clean-install', action='store_true')
parser.add_argument('--build', action='store_true')
parser.add_argument('--version-release', action='store_true')
parser.add_argument('--version-up', action='store_true')

def read_version():
  with open('version') as version_file:
    return version_file.readline()

def write_version(version):
  with open('version', 'w') as version_file:
    version_file.write(version)

def version_release():
  version = read_version()
  if not version.endswith(SNAPSHOT_SUFFIX):
    raise Exception('cannot release from not snapshot version: '+ version)
  version = version[:-len(SNAPSHOT_SUFFIX)]
  write_version(version)
  print('updated version = ' + version)


def version_up():
  version = read_version()
  if version.endswith(SNAPSHOT_SUFFIX):
    raise Exception('cannot up version: '+ version)
  chunks = version.split('.')
  minor = int(chunks[-1])
  chunks[-1] = str(minor + 1)
  version = '.'.join(chunks) + SNAPSHOT_SUFFIX
  write_version(version) 
  print('updated version = ' + version)

def build():
  version = read_version()
  info = plistlib.readPlist(INFO_PLIST_PATH)
  if 'version' in info:
    info['version'] = version
    plistlib.writePlist(info, INFO_PLIST_PATH)

  # workflows framework needs its own version file
  shutil.copy('version', 'src/version') 
  pack(version)

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

def pack(version):
  try:
    os.makedirs(BUILD_TARGET)
  except OSError as e:
    if e.errno != errno.EEXIST:
      raise
  create_zip('src', os.path.join(BUILD_TARGET, OUTPUT_FILENAME_PATTERN.format(version=version)))

def main():
  args = parser.parse_args()

  if args.clean_install:
    for dist_info in glob.glob('src/*.dist-info'):
      print('deleting ' + dist_info)
      shutil.rmtree(dist_info)

  if args.version_up:
    version_up()

  if args.version_release:
    version_release()
  
  if args.build:
    build()

if __name__ == '__main__':
  main()