Here is the end-to-end flow of the project, illustrated with ASCII art.

It's divided into two main phases: the initial one-time setup and the day-to-day execution of API calls.

### Phase 1: Client Onboarding & Configuration

This is what a new developer does to start using your service.

```
   (Developer's Machine)                                (Your API Aggregator)
  +-------------------+                               +------------------------+
  |                   |                               |                        |
  |   CLIENT APP      | --(1. POST /register)------>  |  Creates Project       |
  | (e.g., Postman)   |   { "name": "MySaaS" }        |  Generates API Key     |
  |                   |                               |                        |
  |                   | <--(2. Returns API Key)------ |                        |
  | Receives & saves  |   { "api_key": "xyz123..." }  |                        |
  |    API Key        |                               +-----------+------------+
  |                   |                                           |
  +-------------------+                                           | (Saves to DB)
                                                                  v
                                                          +----------------+
                                                          |   PROJECTS TBL |
                                                          +----------------+


  +-------------------+                               +------------------------+
  |                   |                               |                        |
  |   CLIENT APP      | --(3. POST /config)---------> |  Encrypts & saves      |
  | (with API Key)    |   { "provider": "stripe",...} |  provider credentials  |
  |                   |                               |                        |
  |                   | <--(4. Success 200 OK)------- |                        |
  |                   |                               |                        |
  +-------------------+                               +-----------+------------+
                                                                  |
                                                                  | (Saves to DB)
                                                                  v
                                                         +-----------------+
                                                         | PROVIDER_CONFIGS|
                                                         +-----------------+
```

### Phase 2: Handling a Payment Request (with Failover)

This shows what happens when your client makes a payment request.

```
 (Client)         (Your API Aggregator)                                  (3rd Party Providers)
+--------+       +----------------------+                             +------------------------+
|        |       |                      |                             |                        |
| CLIENT |-(1)-->| POST /payments/charge| --(2)---------------------->|       STRIPE API       |
|  APP   |       | (w/ API Key)         | (Tries primary provider)    |      (500 Error)       |
|        |       |                      |                             |                        |
|        |       | { Finds config for   | <--(3)----------------------|                        |
|        |       |   API Key, sees      |   (Request Fails!)          +------------------------+
|        |       |   Stripe is primary} |
|        |       |                      |
|        |       | { Logs failed attempt|
|        |       |   to Stripe.         |
|        |       |   Initiates failover }
|        |       |                      |
|        |       |                      | --(4)---------------------->+------------------------+
|        |       |                      | (Tries backup provider)     |      RAZORPAY API      |
|        |       |                      |                             |      (200 OK)          |
|        |       |                      |                             |                        |
|        |       |                      | <--(5)----------------------|                        |
|        |       |                      |   (Success!)                +------------------------+
|        |       |                      |
|        |       | { Normalizes the     |
|        |       |   Razorpay response  |
|        |       |   into your unified  |
|        |       |   schema. Logs       |
|        |       |   successful attempt}|
|        |       |                      |
|        |<-(6)--| Returns Unified Resp.|
+--------+       +----------------------+
```