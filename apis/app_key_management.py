#!/usr/bin/env python
"""
Tools to interact with the app key management API
"""

import requests
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
    url = 'https://{0}/app-key-manager/api/account/{1}/keys?v=1.0'.format(uri, args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers, auth=header_oauth)
    if response.status_code == 200:
        log('app keys fetched successfully for {0}'.format(args.site_id))
    return response
