#!/usr/bin/env python
"""
Tools to interact with the data access API
"""

import requests
import json
from requests_oauthlib import OAuth1

__author__ = 'Mark Manguno'
__creation_date__ = '05/26/17'

_headers = {
    'accept': "application/json",
    'content-type': "application/json",
    'cache-control': "no-cache"
}


def base(args, uri):
    url = 'https://{0}/data_access_le/account/{1}/le?v=1.0'.format(uri, args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, args.token_key, args.token_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        print('endpoint list fetched successfully for {0}'.format(args.site_id))
    return response


def agent_activity(args, uri):
    url = 'https://{0}/data_access_le/account/{1}/le/agentActivity?v=1.0&startTime={2}&endTime={3}'.format(uri, args.site_id, args.start_time, args.end_time)
    header_oauth = OAuth1(args.app_key, args.app_secret, args.token_key, args.token_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        print('agent activity file list fetched successfully for {0}'.format(args.site_id))
    return response
