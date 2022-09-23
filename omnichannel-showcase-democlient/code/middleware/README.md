# Overview

This function is intended to compliment the [demo client](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps).

# Setup

## Step 1. Add the Function

Copy `channel-transfer`, into the [`api/`](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps/tree/main/api) sub folder.

## Step 2. Map the Function

Update [`dlgaas.js`](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps/blob/main/app/src/components/dlgaas.js#L37) with the following, so that the escalation can take place to the SMS channel:

```javascript
  Channel_Transfer_SMS = () => {
    return 'api/channel-transfer'
  }
```

## Step 3. Update the Function's Target Endpoint through Environment Variables

Add an Environment Variable `sms_connector_endpoint` pointing to the deployed AppService (SMS Connector).
