# Overview

![travel-demo](https://user-images.githubusercontent.com/26783/155430263-65b06b5a-35c0-44a2-b96a-e568103c7591.gif)

* Type: Multi-Channel
* Channels: IVR, Digital VA text
* Locales: en-US
* Domain: Travel
* Integrations: [Demo Client](https://github.com/nuance-communications/mix-demo-client-azstaticwebapps), Partner Cloud

# Versions

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
