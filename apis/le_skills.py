#!/usr/bin/env python
"""
Tools to interact with the LE Skills API
"""

import requests
import json
from requests_oauthlib import OAuth1
from utilities import mark_log
log = mark_log.log

__author__ = 'Mark Manguno'
__creation_date__ = '09/28/16'

_headers = {
    'accept': "application/json",
    'content-type': "application/json",
    'cache-control': "no-cache"
}


def fetch(args, uri):
    url = 'https://{0}/api/account/{1}/configuration/le-users/skills?v=2.0&select=%24all'.format(uri, args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('skills fetched successfully for {0}'.format(args.site_id))
    return response


def fetch_one(args, uri, skill):
    url = 'https://{0}/api/account/{1}/configuration/le-users/skills/{2}'.format(uri, args.site_id, skill['id'])
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('skill {0} fetched successfully for site {1}'.format(skill['name'], args.site_id))
    return response


def create_one(args, uri, name):
    url = 'https://{0}/api/account/{1}/configuration/le-users/skills?v=2.0'.format(uri, args.site_id)
    payload = {"name": name}
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.post(url, data=json.dumps(payload), headers=_headers, auth=header_oauth)
    if response.status_code == 201:
        log('skill {0} created with id {1} for site {2}'.format(name, response.json()['id'], args.site_id))
    return response


def delete_one(args, uri, skill):
    headers = _headers
    url = 'https://{0}/api/account/{1}/configuration/le-users/skills/{2}'.format(uri, args.site_id, skill['id'])
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    revision = requests.get(url, headers=headers, auth=header_oauth).headers['ETag']
    headers.update({'If-Match': revision})
    response = requests.delete(url, headers=headers, auth=header_oauth)
    if response.status_code == 200:
        log('skill {0} deleted successfully for site {1}'.format(skill['name'], args.site_id))
    return response
