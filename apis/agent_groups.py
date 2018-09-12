#!/usr/bin/env python
"""
Tools to interact with the LE Agent Groups API
"""

import requests
import json
from requests_oauthlib import OAuth1
from utilities import mark_log
log = mark_log.log

__author__ = 'Mark Manguno'
__creation_date__ = '04/02/16'

_headers = {
    'accept': 'application/json',
    'content-type': 'application/json',
    'cache-control': 'no-cache'
}


def fetch(args, uri):
    url = 'https://{0}/api/account/{1}/configuration/le-users/agentGroups?v=1.0&select=%24all'.format(uri, args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('agent groups fetched successfully for {0}'.format(args.site_id))
    return response


def fetch_one(args, uri, group_id):
    url = 'https://{0}/api/account/{1}/configuration/le-users/agentGroups/{2}'.format(uri, args.site_id, group_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('group {0} fetched successfully for site {1}'.format(group_id, args.site_id))
    return response


def create(args, uri, name, parent_group_id='-1', description=''):
    url = 'https://{0}/api/account/{1}/configuration/le-users/agentGroups'.format(uri, args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, args.token_key, args.token_secret, signature_type='auth_header')
    payload = {
        'name': name,
        'parentGroupId': parent_group_id,
        'description': description,
        'isEnabled': 'true'
    }
    _headers['If-Match'] = '1'
    response = requests.post(url, data=json.dumps(payload), headers=_headers, auth=header_oauth)
    if response.status_code == 201:
        log('group {0} created: {1}'.format(response.json()['id'], response.json()))
    else:
        log('{0}: {1}'.format(response.status_code, response.json()))
    return response
