# Overview

This app offers an integration with Nuance Mix Bots and Azure Communication Services, specifically for the SMS channel.

The app has two APIs:
* Inbound
* Outbound

The inbound API initiates a conversation, or continues a conversation based on user reply. 
The outbound API initiates a conversation from a system signal.

# Pre-Requisites

* Azure Subscription
* [Azure CLI](https://learn.microsoft.com/en-us/cli/azure/install-azure-cli)
* Python 3.9+

# Setup

## 1. Sign up for Azure Communication Services

* Enables provisioning and management of phone number
* Enables secure SMS communications integration with an application
* Events are published and can be sources of triggers -- in this application WebHooks are used
    * Must Create and Authenticate a WebHook
        * https://docs.microsoft.com/en-us/azure/event-grid/webhook-event-delivery

* Create New Resource
* Create a Phone Number

Communications Service Outcome: `https://[communication-services-site-name].communication.azure.com`

Go to Settings > Keys > copy the Connection String. This will be used in the SMS Connector configuration. 

## 2. Set up an App Service for Events Grid handling (optional)

* Receives events and offers visibility to events. Generic handler.

This will be used to capture events during development/troubleshooting.

Use the Repo: https://github.com/Azure-Samples/azure-event-grid-viewer -> Install

AppService outcome: `https://[event-grid-viewer-site-name].azurewebsites.net/`

### Connecting to ACS Event Grid

The URL will be added as part of ACS's Events, as WebHook type.

With resource created in Step1: Create Event Subscription.

* EventSchema: Event Grid Schema
* TopicType: Communication Service
* SourceResource: [Your_ACS_Instance]
* SystemTopicName: sms-topic
* EventTypes: SMS Received
* EndpointType: Web Hook, Endpoint: above + `/api/updates`

Messages will now be visible through the URL.

## 3. Set up an App Service for the SMS Connector

* Receives events and coordinates sessions for conversations.

### Deploy using Azure CLI

See [here](https://learn.microsoft.com/en-us/azure/app-service/quickstart-python) for more.

Note: following operations assume PWD points to `sms-connector`.

```bash
az login --scope https://management.core.windows.net//.default
```

```bash
az webapp up --runtime PYTHON:3.9 --sku B1 --logs --name nuance-mix-sms-connector
```

AppService outcome: `https://[sms-connector-site-name].azurewebsites.net/`

This needs to be used as part of the middleware's `channel-transfer` function, specifically the environment variable: `sms_connector_endpoint`.

### Connect the SMS Connector to ACS Event Grid

Create Event Subscription:

* EventSchema: Event Grid Schema
* TopicType: Communication Service
* SourceResource: [Your_ACS_Instance]
* SystemTopicName: sms-topic
* EventTypes: SMS Received
* EndpointType: Web Hook, Endpoint: above + `/api/sms-topic-event-triggered`

# Configure

## SMS Connector Configuration

Provide the following, updated, environment variables for your SMS Connector AppService instance:

| Property | Value |
| -------- | ----- |
| oauth_server_url | https://auth.crt.nuance.com/oauth2 |
| oauth_server_token_path | /token |
| oauth_server_authorize_path | /auth |
| oauth_scope | dlg |
| oauth_client_id | appID:... [replace from Mix.dashboard] |
| oauth_client_secret | secret [replace from Mix.dashboard] |
| dlgaas_base_url | https://dlg.api.nuance.com/dlg/v1 |
| dlg_model_ref_urn | urn:nuance-mix:tag:model/OMNI/mix.dialog |
| dlg_language | en-US |
| dlg_channel | SMS |
| dlg_timeout | 900 |
| acs_conn_str | endpoint=<URL>;accesskey=<KEY> |
| acs_phone_number | +18001234567 |

`acs_conn_str` and `acs_phone_number` come from Step1.

Use the following for `Advanced Edit`:

```json
[
  {
    "name": "LANG",
    "value": "en_US.UTF-8",
    "slotSetting": false
  },
  {
    "name": "oauth_server_url",
    "value": "https://auth.crt.nuance.com/oauth2",
    "slotSetting": false
  },
  {
    "name": "oauth_client_id",
    "value": "...",
    "slotSetting": false
  },
  {
    "name": "oauth_client_secret",
    "value": "...",
    "slotSetting": false
  },
  {
    "name": "base_url_dlgaas",
    "value": "https://dlg.api.nuance.com/dlg/v1",
    "slotSetting": false
  },
  {
    "name": "dlg_model_ref_urn",
    "value": "urn:nuance-mix:tag:model/OMNI/mix.dialog",
    "slotSetting": false
  },
  {
    "name": "dlg_language",
    "value": "en-US",
    "slotSetting": false
  },
  {
    "name": "dlg_channel",
    "value": "SMS",
    "slotSetting": false
  },
  {
    "name": "dlg_timeout",
    "value": "900",
    "slotSetting": false
  },
  {
    "name": "acs_conn_str",
    "value": "...",
    "slotSetting": false
  },
  {
    "name": "acs_phone_number",
    "value": "...",
    "slotSetting": false
  }
]
```

## ACS Configuration

Create two WebHook endpoints. 

* First from Step2. (troubleshooting event listener)
* Second from Step3. (sms connector app)

## Middleware Configuration

Provide the `sms_connector_endpoint` from AppService created in Step3.
