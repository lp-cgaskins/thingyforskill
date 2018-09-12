import os
import re
import csv
import time
import math
from argparse import ArgumentParser, RawTextHelpFormatter

from apis import base_uris, app_key_management, le_users, le_skills, agent_groups, data_access

from utilities import mark_log
log = mark_log.log

__author__ = 'Mark Manguno'
__creation_date__ = '09/26/16'

parser = ArgumentParser(formatter_class=RawTextHelpFormatter)
utilities = parser.add_mutually_exclusive_group()

# Universal Parameters
parser.add_argument('--site_id')
parser.add_argument('--app_key')
parser.add_argument('--app_secret')
parser.add_argument('--token_key')
parser.add_argument('--token_secret')

# General Arguments
parser.add_argument('--start_time', help='Search interval start time in epoch time.')
parser.add_argument('--end_time', help='Search interval end time in epoch time.')
parser.add_argument('--skill_id', help='Skill ID for functions that require a skill')
parser.add_argument('--user_list', help='User list for functions that require a list of users. '
                                        'Pass a file with each user ID on a new line.')
parser.add_argument('--interval', help='For operations that are performed many times specify the interval in seconds. '
                                       '(Default: 5)', default='5')

# Utilities
#   Users
utilities.add_argument('--delete_lpa_users', action='store_true',
                       help='Fetch users list, find any with the LPA naming convention, delete them.')
utilities.add_argument('--change_messaging_concurrency', action='store_true',
                       help='Change the messaging concurrency of a list of users. '
                            'Pass --user_list (filename)')

#   Agent Groups
utilities.add_argument('--add_agent_groups', action='store_true',
                       help='Create agent groups according to a list supplied in a .csv file as --agent_group_list')
parser.add_argument('--agent_group_list', help='Agent Group list for --add_agent_groups. '
                                               'Pass a CSV file where each line contains:\n'
                                               '\'group_name,parent_group_id(optional),description(optional)\'\n'
                                               'When not specified parent_group_id defaults to -1 (Main Group).\n'
                                               'ex:\n'
                                               'new_group_1,25256677,description\n'
                                               'new_group_2,,description 2\n'
                                               'new_group_3')

#   Skills
utilities.add_argument('--add_skill', action='store_true',
                       help='Add users to skill. '
                            'Pass --skill_id (integer) and --user_list (filename)')
utilities.add_argument('--add_and_remove_skill', action='store_true',
                       help='First add users to skill, then remove users from skill. '
                            'Pass --skill_id (integer) and --user_list (filename)')
utilities.add_argument('--remove_skill', action='store_true',
                       help='Remove users from skill. '
                            'Pass --skill_id (integer) and --user_list (filename)')
utilities.add_argument('--list_skills', action='store_true', help='Retrieve a list of skills from the account.')
utilities.add_argument('--create_messaging_skills', action='store_true',
                       help='Create a corresponding messaging skill for each chat skill on the account. '
                       'Use the default suffix \'_messaging\' or pass a new one with --suffix (string)')
parser.add_argument('--suffix',
                    help='Suffix for new skills created with --create_messaging_skills')
utilities.add_argument('--create_n_skills', action='store_true',
                       help='Create n skills on the account named \'skill_000\', \'skill_001\', etc...'
                       'Requires --count param')
parser.add_argument('--count',
                    help='Value of N')
utilities.add_argument('--delete_skills', action='store_true',
                       help='Delete skills that match a specific string')


#   Data Access
utilities.add_argument('--data_access', action='store_true', help='Use the LE Data Access API')


args = parser.parse_args()

args.app_key = args.app_key or os.getenv('app_key')
args.app_secret = args.app_secret or os.getenv('app_secret')
args.token_key = args.token_key or os.getenv('token_key')
args.token_secret = args.token_secret or os.getenv('token_secret')


if not args.site_id:
    args.site_id = input('Enter site id: ')

args.interval = int(float(args.interval))

bases = base_uris.fetch(args)
# appKeys = app_key_management.fetch(args, bases['appKeyManagement']['baseURI']).json()

log(args.app_key)
log(args.app_secret)
log(args.token_key)
log(args.token_secret)

# List Skills
if args.list_skills:
    skills = le_skills.fetch(args, bases['accountConfigReadOnly']['baseURI']).json()
    for skill in skills:
        log(skill['name'])


# Create Messaging Skills
if args.create_messaging_skills:
    if not args.suffix:
        args.suffix = input('Enter desired suffix (default: \'_messaging\'): ') or '_messaging'
    readWriteURI = bases['accountConfigReadWrite']['baseURI']
    skills = le_skills.fetch(args, bases['accountConfigReadOnly']['baseURI']).json()
    regex = re.compile(re.escape(args.suffix)+'$')

    for skill in skills:
        if skill['name']+args.suffix in (s['name'] for s in skills):
            log('skill {0} not copied because skill {1} exists'.format(skill['name'], skill['name']+args.suffix))

        elif regex.search(skill['name']):
            log('skill {0} not copied because it already ends with {1}'.format(skill['name'], args.suffix))

        else:
            response = le_skills.create_one(args, readWriteURI, skill['name']+args.suffix)
            time.sleep(args.interval)

# Create N Skills
if args.create_n_skills:
    n = int(args.count)
    mag = int(math.log10(n))
    format_string = "skill_%0" + str(mag) + "d"
    readWriteURI = bases['accountConfigReadWrite']['baseURI']
    for i in range(n):
        skill_name = format_string % i
        response = le_skills.create_one(args, readWriteURI, skill_name)
        time.sleep(args.interval)


# Delete Skills
if args.delete_skills:
    readWriteURI = bases['accountConfigReadWrite']['baseURI']
    skills = le_skills.fetch(args, bases['accountConfigReadOnly']['baseURI']).json()
    string = input('Delete skills whose names match the string: ')

    for skill in skills:
        if re.compile(re.escape(string)).search(skill['name']):
            # log('deleting skill {0}'.format(skill['name']))
            le_skills.delete_one(args, readWriteURI, skill)
        else:
            log('not deleting skill {0}'.format(skill['name']))

# Delete LPA Users
if args.delete_lpa_users:
    users = le_users.fetch(args, bases['accountConfigReadOnly']['baseURI']).json()
    count = 0
    log('deleting LPA users')
    for user in users:
        if 'LPA' in user['loginName']:
            count += 1
            le_users.delete_one(args, bases['accountConfigReadWrite']['baseURI'], user)
    if count > 0:
        log('{0} users deleted'.format(count))
    else:
        log('no matching users found')

# Add (And Remove) Skill
if args.add_skill or args.add_and_remove_skill:
    count = 0
    if not args.skill_id:
        args.skill_id = input('Enter skill id: ')

    if not args.user_list:
        args.user_list = input('Enter user list filename: ')

    with open(args.user_list, 'r') as f:
        users_to_edit = [line.rstrip('\n') for line in f]

    log('adding users to skill {0}'.format(args.skill_id))

    for user in users_to_edit:
        count += 1
        add_response = le_users.add_skill(args, bases['accountConfigReadWrite']['baseURI'], user, args.skill_id)
        if add_response and args.add_and_remove_skill:
            le_users.remove_skill(args, bases['accountConfigReadWrite']['baseURI'], user, args.skill_id)
        log('{0} total users updated'.format(count))
        time.sleep(args.interval)

# Remove Skill
if args.remove_skill:
    count = 0
    if not args.skill_id:
        args.skill_id = input('Enter skill id: ')

    if not args.user_list:
        args.user_list = input('Enter user list filename: ')

    with open(args.user_list, 'r') as f:
        users_to_edit = [line.rstrip('\n') for line in f]

    log('adding users to skill {0}'.format(args.skill_id))

    for user in users_to_edit:
        count += 1
        response = le_users.remove_skill(args, bases['accountConfigReadWrite']['baseURI'], user, args.skill_id)
        log('{0} total users updated'.format(count))
        time.sleep(args.interval)

# Change Messaging Concurrency
if args.change_messaging_concurrency:
    count = 0
    if not args.user_list:
        args.user_list = input('Enter user list filename: ')

    target_concurrency = input('Enter desired messaging concurrency: ')

    with open(args.user_list, 'r') as f:
        users_to_edit = [line.rstrip('\n') for line in f]

    log('setting concurrency to {0}'.format(target_concurrency))

    for user in users_to_edit:
        count += 1
        le_users.change_max_async(args, bases['accountConfigReadWrite']['baseURI'], user, target_concurrency)
        log('{0} total users updated'.format(count))

# Data Access
if args.data_access:
    # temporary solution for lack of data access uri in csds
    _url = bases['leDataReporting']['baseURI'].split('.', maxsplit=2)
    url = '.'.join((_url[0], 'da', _url[2]))

    files = data_access.agent_activity(args, url)
    print(files.json())

# Add Agent Groups
if args.add_agent_groups:
    group_list = csv.reader(open(args.agent_group_list))
    readWriteURI = bases['accountConfigReadWrite']['baseURI']
    for row in group_list:
        response = agent_groups.create(args,
                                       readWriteURI,
                                       row[0],
                                       row[1] if (1 < len(row) and row[1] != '') else '-1',
                                       row[2] if 2 < len(row) else '')
        time.sleep(args.interval)
