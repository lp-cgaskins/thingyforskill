#!/usr/bin/env python
"""
Tools to interact with the LE Users API
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
    url = 'https://{0}/api/account/{1}/configuration/le-users/users?v=2.0&select=%24all'.format(uri, args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('users fetched successfully for {0}'.format(args.site_id))
    return response


def fetch_one(args, uri, user):
    url = 'https://{0}/api/account/{1}/configuration/le-users/users/{2}'.format(uri, args.site_id, user['id'])
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('user {0} fetched successfully for site {1}'.format(user['loginName'], args.site_id))
    return response


def delete_one(args, uri, user):
    headers = _headers
    url = 'https://{0}/api/account/{1}/configuration/le-users/users/{2}'.format(uri, args.site_id, user['id'])
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    revision = requests.get(url, headers=headers, auth=header_oauth).headers['ETag']
    headers.update({'If-Match': revision})
    response = requests.delete(url, headers=headers, auth=header_oauth)
    if response.status_code == 200:
        log('user {0} deleted successfully for site {1}'.format(user['loginName'], args.site_id))


def add_skill(args, uri, user_id, skill_id):
    log('adding user {0} to skill {1}'.format(user_id, skill_id))

    url = 'https://{0}/api/account/{1}/configuration/le-users/users/{2}'.format(uri, args.site_id, user_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    headers = _headers
    if 'If-Match' in headers.keys():
        del headers['If-Match']

    user = requests.get(url, headers=headers, auth=header_oauth)

    if user.status_code < 200 or user.status_code > 299:
        log('status code {0}'.format(user.status_code))
        return False

    if 'ETag' in user.headers.keys():
        headers.update({'If-Match': user.headers['ETag']})
        payload = user.json()
    else:
        log('etag not found')
        return False

    if skill_id not in payload['skillIds']:
        payload['skillIds'].append(skill_id)
    else:
        log('this user is already in this skill')
        return False

    payload['isMyUser'] = False
    if 'lobIds' not in payload.keys():
        payload['lobIds'] = []
    payload = json.dumps(payload)

    response = requests.put(url, data=payload, headers=headers, auth=header_oauth)

    log('user added to skill')
    return response


def remove_skill(args, uri, user_id, skill_id):
    log('removing user {0} from skill {1}'.format(user_id, skill_id))

    url = 'https://{0}/api/account/{1}/configuration/le-users/users/{2}'.format(uri, args.site_id, user_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    headers = _headers

    user = requests.get(url, headers=headers, auth=header_oauth)

    if 'ETag' in user.headers.keys():
        headers.update({'If-Match': user.headers['etag']})
        payload = user.json()
    else:
        log('etag not found')
        return False

    if skill_id in payload['skillIds']:
        payload['skillIds'].remove(skill_id)
    else:
        log('this user is not in this skill')
        return False

    payload['isMyUser'] = False
    if 'lobIds' not in payload.keys():
        payload['lobIds'] = []
    payload = json.dumps(payload)

    response = requests.put(url, data=payload, headers=headers, auth=header_oauth)

    log('user {0} removed from skill {1}'.format(user_id, skill_id))
    return response


def change_max_async(args, uri, user_id, new_max_async):
    log('changing user {0}\'s maxAsyncChats to {1}'.format(user_id, new_max_async))

    url = 'https://{0}/api/account/{1}/configuration/le-users/users/{2}'.format(uri, args.site_id, user_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    headers = _headers

    user = requests.get(url, headers=headers, auth=header_oauth)

    if user.status_code < 200 or user.status_code > 299:
        log('status code {0}'.format(user.status_code))
        return False

    if 'ETag' in user.headers.keys():
        headers.update({'If-Match': user.headers['etag']})
        payload = user.json()
    else:
        log('etag not found')
        return False

    payload['maxAsyncChats'] = int(new_max_async)

    payload['isMyUser'] = False
    if 'lobIds' not in payload.keys():
        payload['lobIds'] = []
    if 'pictureUrl' not in payload.keys():
        payload['pictureUrl'] = None

    payload = json.dumps(payload)
    response = requests.put(url, data=payload, headers=headers, auth=header_oauth)

    if 199 < response.status_code < 300:
        log('user {0} updated'.format(user_id))
    else:
        log('user {0} not updated: {1} {2}'.format(user_id, response.status_code, response.reason))

    return response