# Overview

![travel-demo](https://user-images.githubusercontent.com/26783/155430263-65b06b5a-35c0-44a2-b96a-e568103c7591.gif)

* Type: Multi-Channel
* Channels: IVR channel, Digital VA text
* Locales: en-US
* Domain: Travel
* Integrations: [Demo Client](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps), Partner Cloud

# Changelog

## 1.1.0 - Feb 7, 2023
* 2 main improvements:
    * The Entities now have data types assigned
    * The intents have a few more utterances

* These changes will:
	* Prevent an issue with reusing entities (with isA) when the data type is not assigned. 
	* Increase successful calls to the bot while testing 
	* Help the Mix testing tool to output better success scores during demos to customers. 

* Data types / Entities
  * alphanumeric : eCity, eArrivalCity, eDepartureCity, eGlobalCommands
  * YES_NO : eConfirmFlight, eConfirmFlightLookup
  * DATE : eDepartureDate
  * generic : eBookFlight

| transcription                                                | annotation                                                                                   | intent           |   |   |   |   |   |   |   |
|--------------------------------------------------------------|----------------------------------------------------------------------------------------------|------------------|---|---|---|---|---|---|---|
| Book a flight to Atlanta                                     | {"eArrivalCity": "Atlanta"}                                                                  | iBookFlight      |   |   |   |   |   |   |   |
| I'd like to go to Atlanta on May 4th                         | {"eArrivalCity": "Atlanta", "eDepartureDate": "May 4th"}                                     | iBookFlight      |   |   |   |   |   |   |   |
| Is there a flight from New York to Phoenix?                  | {"eDepartureCity": "New York", "eArrivalCity": "Phoenix"}                                    | iBookFlight      |   |   |   |   |   |   |   |
| Can I fly to San Francisco?                                  | {"eDepartureCity": "San Francisco"}                                                          | iBookFlight      |   |   |   |   |   |   |   |
| I'm going to New York tomorrow                               | {"eArrivalCity": "New York", "eDepartureDate": "tomorrow"}                                   | iBookFlight      |   |   |   |   |   |   |   |
| Did I lose My luggage in New York?                           |                                                                                              | iFAQLostLuggage  |   |   |   |   |   |   |   |
| Where's my luggage?                                          |                                                                                              | iFAQLostLuggage  |   |   |   |   |   |   |   |
| I'd like to travel from Phoenix to Atlanta on July twentieth | {"eArrivalCity": "Atlanta", "eDepartureCity": "Phoenix", "eDepartureDate": "July twentieth"} | iBookFlight      |   |   |   |   |   |   |   |
| Yeah, is my flight on time?                                  |                                                                                              | iFlightStatus    |   |   |   |   |   |   |   |


## 1.0.3 - Mar 11, 2022
* Update "reservation" to "reservations" for queue name

## 1.0.2 - Feb 14, 2022
* Fix behavior of Question Router to skip when appropriate

## 1.0.1 - Jan 31, 2022
* Updated behavior in up front NLU for no_match

## 1.0.0 - Jan 26, 2022
* Multi-Channel Project
* FAQ illustration of Flight Status
* Design principles baked in and Node Naming conventions
  * Nodes include notes
* Book Flight intent component with question router usage
  * Intent switching
* Error recovery and Unexpected Input handling (no match, no input)
* Data Access node illustrating a Server-Side integration
* Interactivity
  * IVR: DTMF handling
  * Digital VA Text: Buttons
* Reporting variables
  * IntentGiven
  * isContained
  * bookFlightStarted
  * bookFlightCompleted
