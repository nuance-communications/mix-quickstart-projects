"""
Copyright 2021-present, Nuance, Inc.
All rights reserved.

This source code is licensed under the Apache-2.0 license found in
the LICENSE.md file in the root directory of this source tree.
"""
import sys
import logging
import json
import time
import urllib.parse

import requests

from requests_oauthlib import OAuth2Session
from oauthlib.oauth2 import BackendApplicationClient

logger = logging.getLogger('mixclient')
logger.setLevel(logging.DEBUG)
sh = logging.StreamHandler(stream=sys.stdout)
sh.setLevel(logging.DEBUG)
logger.addHandler(sh)


class OAuthApi:
    """
    The API Class is responsible for handling tokens, making requests and parsing the response.
    Configuration must include OAuth2 server information as well as Mix Runtime API Host.
    """

    def __init__(self, oauth_client_id=None, oauth_client_secret=None, oauth_scope=None):
        super()
        self._token = None
        # OAuth2
        self.oauth_client_id = oauth_client_id
        self.oauth_client_secret = oauth_client_secret
        self.oauth_scope = oauth_scope

    def init_from_config(self, config):
        self.oauth_client_id = config.get('oauth_client_id')
        self.oauth_client_secret = config.get('oauth_client_secret')
        self.oauth_scope = config.get('oauth_scope')
        self.oauth_token_url = config.get('oauth_server_url') + \
            config.get('oauth_server_token_path')
        self._token = config.get('_token', None)

    def get_token(self):
        logger.info(f'Getting token for {self.oauth_client_id}')
        client = BackendApplicationClient(client_id=self.oauth_client_id)
        oauth = OAuth2Session(client=client, scope=self.oauth_scope)
        token = oauth.fetch_token(token_url=self.oauth_token_url,
                                  client_id=self.oauth_client_id,
                                  client_secret=self.oauth_client_secret,
                                  scope=self.oauth_scope)
        return token

    @property
    def token(self):
        logging.debug("Getting token")
        is_expired = False
        if self._token is not None:
            expires_at = self._token['expires_at']
            if expires_at <= time.time():
                is_expired = True
                logging.debug("EXPIRED")
        if self._token is None or is_expired:
            self._token = self.get_token()
        return self._token['access_token']

    @property
    def base_url(self):
        pass

    def get_headers(self):
        return {
            'Accept': 'application/json; charset=utf-8',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/json; charset=utf-8',
            'Authorization': f'Bearer {self.token}',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'nuance-mix/demo-sdk',
        }

    def _request(self, method, url, data=None):
        _url = f"{self.base_url}/{url}"
        req_args = {
            "url": _url,
            "headers": self.get_headers(),
        }
        if method == 'post':
            req_args['data'] = json.dumps(data)
        try:
            ret = getattr(requests, method)(**req_args)
        except Exception as ex:
            # logger.error(f"\n\n{_url} <-> Encountered an Error:\n\n {ret.headers['grpc-message']}")
            logger.exception(ex)
            if ret:
                logger.error(ret.__dict__)
                return {
                    "error": f"{ret.headers['grpc-message']}",
                }
            else:
                return {
                    "error": str(ex),
                }
        else:
            ret.encoding = 'utf-8'
        try:
            if ret.status_code in [400, 401, 403, 404, 500]:
                if 'grpc-message' in ret.headers:
                    return {
                        "error": ret.headers['grpc-message'],
                    }
                if ret.reason:
                    return {
                        "error": ret.reason,
                    }
                return {
                    "error": ret.json(),
                }
            if ret.status_code == 204:
                return {}
            return json.loads(ret.content.decode('utf-8'))
        except Exception as ex:
            logger.exception(ex)
            return {"error": ret}

    def _post(self, url, data=None):
        return self._request('post', url, data)


class DlgaasApi(OAuthApi):
    """
    The API Class is responsible for making requests to the DLGaaS HTTP/1.1 API
    """

    def __init__(self, config):
        super()
        self.init_from_config(config)
        self.dlgaas_base_url = config.get("dlgaas_base_url")

    @property
    def base_url(self):
        return self.dlgaas_base_url

    """
    Interface
    """

    def start(self, model_ref_urn: str, raw_payload: object):
        urn = urllib.parse.quote(model_ref_urn, safe='')
        return self._post(f'start/{urn}', raw_payload)

    def execute(self, session_id: str, payload: object):
        return self._post(f'execute/{session_id}', {"payload": payload})

    def stop(self, session_id: str):
        return self._post(f'stop/{session_id}', {})


    """
    Utilities
    """

    def parse_action(self, response: object):
        if 'daAction' in response['payload']:
            return "DATA"
        elif 'continueAction' in response['payload']:
            return "CONTINUE"
        elif 'endAction' in response['payload']:
            return "END"
        elif 'escalationAction' in response['payload']:
            return "ESCALATE"
        elif 'qaAction' in response['payload']:
            return "QA"
        return "UNKNOWN"

    def _get_message_segments(self, ret: list, node: object):
        msg = node['message']
        for m in msg['visual']:
            ret.append(m['text'])

    def parse_messages(self, response: object):
        ret = []
        if 'payload' in response:
            payload = response['payload']
            messages = payload['messages']
            for msg in messages:
                for m in msg['visual']:
                    ret.append(m['text'])
            action_node = None
            if 'qaAction' in payload:
                action_node = payload['qaAction']
            if action_node:
                self._get_message_segments(ret, action_node)
        else:
            logging.warn(response)
        return ret
