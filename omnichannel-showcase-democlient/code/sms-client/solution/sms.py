"""
Copyright 2021-present, Nuance, Inc.
All rights reserved.

This source code is licensed under the Apache-2.0 license found in
the LICENSE.md file in the root directory of this source tree.
"""
import logging

from azure.communication.sms import SmsClient


class SmsHandler:
    """
    The SmsHandler interfaces with Azure Communication Services.

    Requires providing the connection string.

    Supports sending SMS messages.
    """
    def __init__(self, config):
        self.conn_string = config.get('acs_conn_str')

    def send_message(self, from_number, to_number, message, tag="mix-acs-solution"):
        try:
            # Establish a connection
            sms_client = SmsClient.from_connection_string(self.conn_string)

            # Send the message
            sms_responses = sms_client.send(
               from_=from_number,
               to=to_number,
               message=f"{str(message)}",
               enable_delivery_report=True,  # optional property
               tag=tag)  # optional property

            logging.debug(sms_responses)

        except Exception as ex:
            logging.exception(ex)
        else:
            return sms_responses
        return None

# Test Handler
# Replace the connection string & phone number to send a test message to


if __name__ == '__main__':
    s = SmsHandler("endpoint=<REPLACE>;accesskey=<REPLACE>")
    msg = ' '.join(["I can...\n\U0001F4B9 get stock quotes and purchase shares,",
        " \n\U0001F4F1 buy a new phone,",
        " \n\U0001F3E6 pay a bill, ",
        " \n\U00002708 book a trip or ",
        " \n\U000026C5 find the weather in any city. ",
        "What can I help with?"
    ])
    s.send_message(
        "+1<NUMBER>",
        msg
    )
