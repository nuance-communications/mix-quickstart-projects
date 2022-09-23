"""
Copyright 2021-present, Nuance, Inc.
All rights reserved.

This source code is licensed under the Apache-2.0 license found in
the LICENSE.md file in the root directory of this source tree.
"""
import json
import os
import requests

import azure.functions as func

SUCCESS_CODE = '0'
SMS_CONNECTOR_OUTBOUND_ENDPOINT = os.environ.get('sms_connector_endpoint', 'https://<REPLACEME>.azurewebsites.net')


def main(req: func.HttpRequest) -> func.HttpResponse:
    """
    This function enables transferring a conversation to an SMS channel.
    The sample leverages Azure Communication Services for this communication.
    """

    req_body = req.get_json()

    # Initiate an Outbound SMS request
    # while transparently passing along the payload
    r = requests.post(
        url=f"{SMS_CONNECTOR_OUTBOUND_ENDPOINT}/api/sms-start-session",
        headers={
            'Accept': 'application/json; charset=utf-8',
            'Accept-Language': 'en-US,en;q=0.9',
            'User-Agent': 'nuance-mix/demo-client-az-static-webapps',
        }, data=json.dumps(req_body))

    # Success
    if r.status_code == 200:
        ret = {
            'returnCode': SUCCESS_CODE,
            'returnMessage': 'Transferred to SMS.'
        }
    # Failure
    else:
        ret = {
            'returnCode': 'error.transfer',
            'returnMessage': str(r.error)
        }

    return func.HttpResponse(
        json.dumps(ret),
        mimetype='application/json',
        status_code=200
    )
