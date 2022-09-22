"""
Copyright 2021-present, Nuance, Inc.
All rights reserved.

This source code is licensed under the Apache-2.0 license found in
the LICENSE.md file in the root directory of this source tree.
"""
import sys
import os
import json
import logging
import locale
import datetime

from flask import Flask
from flask import request

from solution.sessions import SessionStore
from solution.xaas import DlgaasApi
from solution.sms import SmsHandler

logger = logging.getLogger('mix')
logger.setLevel(logging.DEBUG)

handler = logging.StreamHandler(stream=sys.stdout)
logger.addHandler(handler)

VERSION = '1.0.0'
CLIENT_AGENT = f'nuance-mix/sms-connector-sample'
PHONE_NUMBER_ENTITY = 'ePhoneNumber'
COUNTRY_CODE = '+1'

logger.info(f"Hello, Nuance Mix - ACS Integration.")
logger.info(f"locale={locale.getdefaultlocale()}")
logger.info(f"encoding={locale.getpreferredencoding()}")

#
#
# Configuration
#
#

osenv = os.environ
config = {
    "oauth_server_url": osenv.get('oauth_server_url', "https://auth.crt.nuance.com/oauth2"),
    "oauth_server_token_path": osenv.get('oauth_server_token_path', "/token"),
    "oauth_server_authorize_path": osenv.get('oauth_server_authorize_path', "/auth"),
    "oauth_scope": osenv.get('oauth_scope', "dlg"),

    "oauth_client_id": osenv.get('oauth_client_id', None),
    "oauth_client_secret": osenv.get('oauth_client_secret', None),

    "dlgaas_base_url": osenv.get('dlgaas_base_url', "https://dlg.api.nuance.com/dlg/v1"),
    "dlg_model_ref_urn": osenv.get('dlg_model_ref_urn', "urn:nuance-mix:tag:model/OMNI/mix.dialog"),
    "dlg_language": osenv.get('dlg_language', "en-US"),
    "dlg_channel": osenv.get('dlg_channel', "SMS"),
    "dlg_timeout": osenv.get('dlg_timeout', '900'),

    'acs_conn_str': osenv.get("acs_conn_str", "endpoint=<URL>;accesskey=<KEY>"),
    'acs_phone_number': osenv.get('acs_phone_number', "+18001234567"),
}


#
#
# App
#
#

app = Flask(__name__)

# Initialize a PhoneNumber<>Session Management Layer
sessions = SessionStore()

# DLGaaS Handler
dlgaas = DlgaasApi(config)

# ACS Handler
sms = SmsHandler(config)

#
# Interface with Nuance Mix Runtime
#


def get_client_data_for_reporting(phone_number: str):
    """Returns information to be used for reporting."""
    return {
        'version': VERSION,
        'client': CLIENT_AGENT,
        'number': phone_number,
    }


def session_start(phone_number: str, event_time: str, start_data={}):

    """Connection to DLGaaS, leverages config.

    Starts a session and maps it to Nuance Mix/DLGaaS.
    Assumes a startData payload schema.
    """

    logger.info("[+] Starting new DLGaaS session")

    # Establish a session
    session = sessions.create_session(phone_number, {
        "number": phone_number,
        "eventTime": event_time,
    })

    # Construct the payload to start DLGaaS
    start_data_payload = {
        'channelIntegration': config.get('dlg_channel'),
    }
    start_data_payload.update(start_data)

    # Connect with DLGaaS
    urn = config.get('dlg_model_ref_urn')
    payload = {
        'session_timeout_sec': config.get('dlg_timeout'),
        'selector': {
            'language': config.get('dlg_language'),
            'channel': config.get('dlg_channel'),
            'library': 'default',
        },
        'payload': {
            'data': start_data_payload
        },
        'client_data': get_client_data_for_reporting(phone_number),
    }

    # DLGaaS Start
    res = dlgaas.start(urn, payload)

    # Handle failure
    if 'error' in res:
        logger.error("Failed to Start DLGaaS session")
        raise Exception(res['error'])

    # Map SessionID <> DLGaaS SessionID
    session['session_id'] = res['payload']['sessionId']

    # Persist Session Info
    return sessions.update_session(phone_number, session)


def session_execute(session: object, phone_number: str, message=None, event_time=None):

    """Session expected to have `session_id`.

    Phone number relates to session, and message + event_time are used by ACS.
    """

    logger.info("[~] Existing DLGaaS session")

    assert 'session_id' in session, "SessionID must be present"

    # Construct the payload
    payload = {
        'client_data': get_client_data_for_reporting(phone_number),
    }

    # Message presence update, if not: no user input
    if message:
        payload.update({
            'user_input': {
                'user_text': message,
            }
        })

    # Connect with DLGaaS
    r = {'error': True}
    while 'error' in r:
        r = dlgaas.execute(session['session_id'], payload)
        if r.get('error') is not None:
            session = session_start_and_prime(phone_number, event_time)

    # Parse DLGaaS response
    action = dlgaas.parse_action(r)
    messages = dlgaas.parse_messages(r)

    # Construct the SMS payload and Send
    sent_sms = send_sms(phone_number, messages)
    if not sent_sms:
        logger.warn("Failed to send SMS")

    # Delete DLGaaS session mapping if ended
    if action == 'END':
        del session['session_id']

    # Handle latency message
    if action == 'CONTINUE':
        session = session_execute(session, phone_number)

    # Persist
    return sessions.update_session(phone_number, session)


def session_start_and_prime(phone_number: str, event_time: str, transfer_data=None):
    """Starts a DLGaaS session."""
    logger.info("[+] Starting and Priming new DLGaaS session")
    try:
        # DLGaaS Start
        session = session_start(phone_number, event_time, transfer_data)

        # DLGaaS Execute; DUD to match inbound empty message QA
        session = session_execute(session, phone_number)

    except Exception as ex:
        logger.exception(ex)
        return None
    else:
        return session


def session_stop(session: object):
    logger.info("[-] Stopping DLGaaS session")

    assert 'session_id' in session, "session id must exist"

    # Explicitly Stop DLGaaS session
    r = dlgaas.stop(session['session_id'])

    if r.status != 200:
        logger.error('Failed to stop DLGaaS session')
        return False

    del session['session_id']

    return True

#
# Handlers for Azure Communications Services Events
#


def send_sms(phone_number: str, messages: list):
    """Sends an SMS message from DLGaaS message segments"""
    ret = None
    sms_message = ' '.join(messages)
    if len(sms_message.strip()) > 0:
        # Send the SMS
        logger.info(f"Sending SMS to {phone_number}")
        ret = sms.send_message(
            config.get('acs_phone_number'),
            phone_number,
            sms_message.encode('utf-8').decode('unicode_escape')
        )
        logger.debug(ret)
    return ret is not None


def get_session(phone_number: str):
    """
    Mapped phone number to Nuance Mix/DLGaaS Session ID.
    """
    session = sessions.get_session(phone_number)
    logger.info(f"[.] Session for: {phone_number} is {session}")
    return session


def process_inbound(phone_number: str, message: str, evt_time):
    """SMS has been received.

    An inbound request is one where a user has initiated the conversation.
    """
    session = get_session(phone_number)

    session_exists = session is not None and 'session_id' in session

    # Start a new DLGaaS session, if doesn't exist
    if not session_exists:
        session = session_start_and_prime(phone_number, evt_time)

    # Execute a Turn
    if session is not None:
        session = session_execute(session, phone_number, message, evt_time)

    return session


def process_outbound(phone_number: str, start_data: object):
    """SMS has to be sent.

    An outbound request is one where a system initiates the conversation.

    If a session already exists, it will be stopped within
    Nuance Mix Runtime. A new one will be created by DLGaaS.
    """
    session = get_session(phone_number)

    session_exists = session is not None and 'session_id' in session

    # If a DLGaaS session exists, stop it
    if session_exists:
        session_stop(session)

    # Start a New DLGaaS Session
    evt_time = str(datetime.datetime.utcnow())
    session = session_start_and_prime(phone_number, evt_time, start_data)

    return session


#
#
# API
#
#

#
# Inbound: Receive SMS for Conversation
#


@app.route("/api/sms-topic-event-triggered", methods=["GET", "POST"])
def sms_topic_event_triggered():
    """SMS Topic Event Triggered

    Handler for the ACS Events.
    """
    ret = {}

    events = json.loads(request.get_data())
    logger.info("received events")

    for evt in events:
        evt_type = evt['eventType']
        # Handle the original validation event; deactivate once complete
        if evt_type == "Microsoft.EventGrid.SubscriptionValidationEvent":
            ret = {
                "validationResponse": evt['data']['validationCode']
            }
            continue
        # Ignore any non SMS-events
        elif evt_type != "Microsoft.Communication.SMSReceived":
            logger.info(f"Not currently handling {evt_type}")
            continue

        # Handling Microsoft.Communication.SMSReceived only
        if 'messages' not in ret:
            ret['messages'] = []
        # assumes dataVersion=1.0, metadataVersion=1
        # logger.debug(evt['data'])
        ret['messages'].append(process_inbound(
            evt['data']['from'],
            evt['data']['message'],
            evt['eventTime']
        ))

    logger.debug(f"Returning {ret}")

    return ret, 200

#
# Outbound: Start an SMS Conversation
#


@app.route("/api/sms-start-session", methods=["POST"])
def sms_start_session():
    """Starts a Session for a Bot Interaction

    Depends on presence of ePhoneNumber entity, _without_ country code (assumes +1).

    Complimentary data is passed through transparently for DLGaaS.
    """
    req_data = json.loads(request.get_data())

    # Expecting a phone number in the payload
    number = req_data.get(PHONE_NUMBER_ENTITY).replace('-', '')

    assert len(number) != 0, "Invalid phone number"

    phone_number = f"{COUNTRY_CODE}{number}"

    ret = process_outbound(phone_number, req_data)

    logger.debug(f"Returning {ret}")

    return ret, 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
    # app.run(debug=True)
