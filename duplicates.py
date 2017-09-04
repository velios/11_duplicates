import argparse
import sys
import glob
from argparse import ArgumentParser, ArgumentTypeError
from os import path
from collections import defaultdict


def argparser_check_folder_exist(folderpath):
    err_msg = 'Folder {} doesn\'t exist'.format(folderpath)
    if not path.isdir(folderpath):
        raise ArgumentTypeError(err_msg)
    return path.abspath(folderpath)


def make_cmd_arguments_parser():
    parser_description = 'Script find duplicate files in folder'
    parser = ArgumentParser(description=parser_description)
    parser.add_argument('folderpath',
                        help='Path to analyze folder',
                        type=argparser_check_folder_exist)
    parser.add_argument('--outfile', '-o', nargs='?',
                        help='File to output result',
                        type=argparse.FileType('w'),
                        default = sys.stdout)
    return parser.parse_args()


def find_duplicate_files(check_folder_path):
    folders_and_files_generator = glob.iglob(check_folder_path, recursive=True)
    compare_dict = defaultdict(lambda: {'filepath_list': [], 'count': 0, 'filesize': 0, 'filename': ''})
    for file in folders_and_files_generator:
        if path.isfile(file):
            filename = path.basename(file)
            filesize = path.getsize(file)
            compare_key = filename + str(filesize)
            compare_dict[compare_key]['filename'] = filename
            compare_dict[compare_key]['filesize'] = filesize
            compare_dict[compare_key]['count'] += 1
            compare_dict[compare_key]['filepath_list'].append(path.abspath(file))

    return sorted([(fileinfo['filename'],
                    fileinfo['filesize'],
                    fileinfo['filepath_list'],
                    fileinfo['count']) for fileinfo in compare_dict.values() if fileinfo['count'] > 1],
                  key=lambda tup: tup[1],
                  reverse=True)


if __name__ == '__main__':
    cmd_arguments = make_cmd_arguments_parser()
    check_folder_path = '{}/**/*'.format(cmd_arguments.folderpath)
    duplicate_files_info_list = find_duplicate_files(check_folder_path)

    if cmd_arguments.outfile:
        sys.stdout = cmd_arguments.outfile
    if duplicate_files_info_list:
        print('Duplicate files in {} folder info:'.format(cmd_arguments.folderpath))
        sum_files_size = 0
        for filename, filesize, filepath_list, count in find_duplicate_files(check_folder_path):
            print('\nFile "{}" => {} Kb duplicate {} times in next places:'.format(filename,
                                                                                   round(filesize / 1000, 2),
                                                                                   count))
            sum_files_size += filesize
            for filepath in filepath_list:
                print('>>> {}'.format(filepath))
        print('\nTotal size of duplicate files: {} Kb'.format(round(sum_files_size / 1000, 2)))
    else:
        print('no duplicate files found in the folder {}'.format(cmd_arguments.folderpath))
