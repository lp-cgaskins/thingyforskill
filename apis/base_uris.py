#!/usr/bin/env python
"""
module to obtain base URIs
"""

import requests
from requests_oauthlib import OAuth1
from utilities import mark_log
log = mark_log.log

__author__ = 'Mark Manguno'
__creation_date__ = '09/26/16'

_headers = {
    'accept': "application/json",
    'content-type': "application/json",
    'cache-control': "no-cache"
}


def build_dict(seq, key):
    return dict((d[key], dict(d, index=index)) for (index, d) in enumerate(seq))


def fetch(args):
    url = 'https://api.liveperson.net/api/account/{0}/service/baseURI.json?version=1.0'.format(args.site_id)
    header_oauth = OAuth1(args.app_key, args.app_secret, signature_type='auth_header')
    response = requests.get(url, headers=_headers)
    if response.status_code == 200:
        log('base uris fetched successfully for {0}'.format(args.site_id))
    bases_dict = build_dict(response.json()['baseURIs'], key="service")
    return bases_dict