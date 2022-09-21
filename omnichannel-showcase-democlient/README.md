# Overview

This project is optimized to work with the [Demo Client](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps).

* Type: Omni-Channel
* Channels: Web VA, SMS, IVR, Mobile VA
* Locales: en-US
* Domain(s): Finance, Banking, Retail, Travel, Personal Assistant
* Integrations: [Demo Client](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps)

![oc-showcase-demo](./demo.gif)

# Integration Tips 💡

## Code Setup

### Step 1. Create an AzureCommunicationServices Resource

* Go to the Azure Portal.
* Create a "Communication Services" resource
* Create a phone number (Send and Receive SMS)

### Step 2. Create an AppService for the SMS Client

* Create an EventGrid Listener.
* Create an App Service for the SMS Client - processing Inbound and Outbound interactions

See [README](./sms-client/README.md) for more.

### Step 3. Update the Demo Client Middleware and Handler Mapping

* Copy the function
* Update the Data Access Mapping in the client

See [README](./middleware/README.md) for more.

### Step 4. Update Environment Variables

#### SMS Client
Provide `acs_conn_str` and `acs_phone_number` pointing to the AzureCommunicationServices resource and phone number acquired, from Step1.

#### Demo Client
Provide `sms_client_endpoint` pointing to the AppService from Step2.

## Bot StartData

* If interested in tailoring the experience, supply the USER's first and last names (optional).
* If using the weather scenarios, a key must be supplied. Obtain one from [AccuWeather](https://developer.accuweather.com/).

Snippet:

```json
{
  "USER": {
    "firstName": "FirstName",
    "lastName": "LastName"
  },
  "apiKeyAccuweather": "<API_KEY>"
}
```

# Scenarios Supported

## Finance
* "What's the price of $MSFT"
* "I want $400 worth"
* "I'd like to purchase 1500 shares"

### Stock info and purchasing

* Intent(s): iBuyAsset, iGetAssetPrice
* 3rd party API - Yahoo Finance - Unauthenticated
* Stock Ticker Handling, amounts and quantities
* Render HTML cards for information
* One step correction during confirmation of purchase, between dollarAmount and shareAmount

## Banking
* "Pay my bill" --> "0000"
* "Pay $300 of my amex bill today"
* "I'd like to pay $150 worth tomorrow"

### Paying a Bill

* Intent(s): iPayBill
* Accounts - (warning) fixed list right now
* Handling amounts, use of nuance_AMOUNT
* Handling dates, use of nuance_CALENDARX through DATE
* Illustrates use of authentication required to proceed
* Involves client side user profile store
* Sensitive information marked as such
* Show cards in UI for credit cards
* Interactivity for Web VA - amount input, date input, carousel, confirmation

## Retail
* "Buy a Samsung phone"
* "I'd like to buy a 512MB phone"
* "Buy a Sorta Sage phone that's got 1TB data"

### Buying a phone
* Intent(s): iBuyPhone
* Wordsets: Purchasing a phone is dynamic and initiated through a faux store
* Illustrates data access required to populate
* ePhoneColor, ePhoneManufacturer, ePhoneModel, ePhoneCapacity all are dynamically driven and whittled down based on focus of the task
* Interactivity for Web VA - carousel, buttons, color picker, ..

## Travel
* "Book a flight to Hong Kong from New York that arrives August 27th"
* "I want to fly from San Fran to Seattle tomorrow for 2 weeks"
* "Actually, from Montreal"

### Booking a trip

* Intent(s): iBookTrip
* Purchasing a ticket requires:
  * origin
  * destination
  * city is shared between both (relationship type entity)
  * class, arrival date, and some other info
* Some info can be inferred (arrival date or departure date)
* Interactivity for Web VA - cards, date input, carousel
* Allowing for use of any city prior mentioned (anaphora)
  * "what's the weather like in Hong Kong?" "book a flight there"

## Personal Assistant
* "What's the weather like?"
* "weather in Tokyo?"
* "Hi", "What can you do?", "What is Mix?", "Bye"
* "Email me"
* "Agent", "Help"

### Greeting
* iGreeting -"hello"
* iGoodbye - "bye"

### Weather information

* Intent(s): iGetWeather
* Client location intelligence capable
  * Showcases use of Browser
    * Sensitive
* Back-off to city
* Offer date query parameter
* 3rd party API - AccuWeather - requires API Key for use
* Allowing for use of any city prior mentioned (anaphora)

## Advanced & Misc.

* "wipe", "reset"
* "Text me", "Switch to SMS"

### Clearing Memory

* Intent(s): iClearMemory
* Illustrates reset of context

### Email captured NLU data

* Intent(s): iReceiveEmail
* Illustrates session sharing
* Variables used to capture NLU information and assigned accordingly
* Capturing an email address (regex entity type)
* Interactivity for Web VA - email input
* Email mechanism requires variable as 'challenge' for web service endpoints

### Initiate an Outbound Request

* Intent(s): iReceiveCall, iReceiveSMS
* Capturing a phone number (regex entity type)
* Omni-Channel Experience with SMS to continue a task
* Showcases data needed
* Showcases inbound/outbound variants

### Agent Escalation

* When problems occur, escalate to a live agent
  * pass nluData

### Drive the intent based on a keyword

* Entity eIntentOption, provides the ability for a user to say iAboutMix and drive directly to that intent at the top level

# Changelog

## 1.8.0 - August 18, 2022
* Omni-Channel Project
* Channels: Web VA, SMS, IVR, Mobile VA
* Rich UI conventions rendered in Demo Client (Web VA)
* Data Access integrations linked with Demo Client
* Interactivity
  * Web VA: Buttons, Carousels, Link Support
  * IVR: DTMF
* Reporting variables
  * boughtAsset
  * boughtPhone
  * boughtTrip
  * isBookingFlight
  * isBuyingAsset
  * isBuyingPhone
  * isPayingBill
  * madePayment
* Illustrates
  * One-step correction
  * Intent Switching
  * Auth flow
  * Agent Escalation with context data
  * Hyperlinks for driving next turn (intent, entity, or simulated inputs)
  * Anaphora ("What's the weather in New York?" --> "book a flight there")
  * Ellipsis ("What's the weather in Tokyo?" --> "what about in Hong Kong?")
  * NLU Sources & use of all Entity Types
  * Preserving NLU data with ability to email
  * Preserving context for omni channel
  * Channel transfer & data sharing
  * Data Integrations for all domains
  * Latency messages during data access requests
  * Location (lat, lng) from Client
  * Wordsets (inline)
  * Messages
    * HTML for Web
    * Unicode for SMS
    * SSML for TTS
    * Use of Emojis in channel context (Web, SMS)
  * Rich UI capabilities in Web VA / Demo Client (with hints)
     * [Bootstrap](https://getbootstrap.com/) friendly markup rendering
     * Cards (Finance)
     * Buttons (Many)
     * Carousels (Retail)
     * Phone Number (Personal Assistant)
     * Email (Personal Assistant)
     * Date (Travel)
     * Color Picker (Retail)
  * Sentiment driven up front message (based on insult or praise)
