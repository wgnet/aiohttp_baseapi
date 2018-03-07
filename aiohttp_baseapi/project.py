import argparse
import os
import shutil


DESCRIPTION = 'Creates a project directory structure in the current directory.'


def copytree(src, dst, symlinks=False, ignore=None):
    for item in os.listdir(src):
        s = os.path.join(src, item)
        d = os.path.join(dst, item)
        if os.path.isdir(s):
            shutil.copytree(s, d, symlinks, ignore)
        else:
            shutil.copy2(s, d)


def list_files(start_path):
    for root, dirs, files in os.walk(start_path):
        level = root.replace(start_path, '').count(os.sep)
        indent = ' ' * 4 * level
        print('{}{}/'.format(indent, os.path.basename(root)))
        sub_indent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(sub_indent, f))


def main():
    cwd = os.getcwd()
    template_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), 'project_template')
    copytree(template_path, cwd)
    print('Created project directory structure in the current directory ({})'.format(cwd))
    list_files(cwd)


def execute_from_command_line():
    parser = argparse.ArgumentParser(description=DESCRIPTION, add_help=True)
    parser.parse_args()
    main()
