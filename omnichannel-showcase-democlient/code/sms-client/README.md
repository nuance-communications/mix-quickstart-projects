# Overview

This app offers an integration with Nuance Mix Bots and Azure Communication Services, specifically for the SMS channel.

# Pre-Requisites

* Azure Subscription
* Python

# Setup

## 1. Sign up for Azure Communication Services

* Enables provisioning and management of phone number
* Enables secure SMS communications integration with an application
* Events are published and can be sources of triggers -- in this application WebHooks are used
    * Must Create and Authenticate a WebHook
        * https://docs.microsoft.com/en-us/azure/event-grid/security-authentication?WT.mc_id=Portal-fx#webhook-event-delivery
        * https://docs.microsoft.com/en-us/azure/event-grid/webhook-event-delivery

Go to Settings > Keys > copy the Connection String.

Communications Service Outcome: `https://[communication-services-site-name].communication.azure.com`

## 2. Set up an App Service for Events Grid handling

* Receives events and offers visibility to events. Generic handler.
* Repo: https://github.com/Azure-Samples/azure-event-grid-viewer -> Install

AppService outcome: `https://[event-grid-viewer-site-name].azurewebsites.net/`

## 3. Set up an App Service for the SMS Client

* Receives events and coordinates sessions for conversations.

### Deploy using Azure CLI

```bash
az login --scope https://management.core.windows.net//.default
```

```bash
az webapp up --sku B1 --name <site-name>
```

AppService outcome: `https://[sms-client-site-name].azurewebsites.net/`

Use this for `sms_client_endpoint`.

# Configure

## Environment Configuration

Provide the following, updated, for your SMS Client AppService instance:

| Property | Value |
| -------- | ----- |
| oauth_server_url | https://auth.crt.nuance.com/oauth2 |
| oauth_server_token_path | /token |
| oauth_server_authorize_path | /auth |
| oauth_scope | dlg |
| oauth_client_id | appID:... |
| oauth_client_secret | secret |
| dlgaas_base_url | https://dlg.api.nuance.com/dlg/v1 |
| dlg_model_ref_urn | urn:nuance-mix:tag:model/OMNI/mix.dialog |
| dlg_language | en-US |
| dlg_channel | SMS |
| dlg_timeout | 900 |
| acs_conn_str | endpoint=<URL>;accesskey=<KEY> |
| acs_phone_number | +18001234567 |
