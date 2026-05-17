# Chapter 10: Design A Notification System

A notification system pushes time-sensitive messages to users across **three channels** — mobile push (iOS/Android), SMS, and email — via 3rd-party providers, reliably and at scale.

```
   Event ──► [Notification System] ──► push  ──► APNs / FCM ──► phone
                                  ├──► SMS   ──► Twilio/Nexmo ──► phone
                                  └──► email ──► SendGrid    ──► inbox
```

---

## Notification types & providers

Each channel has its own delivery semantics, identifier, and 3rd-party gateway. You do **not** talk to devices directly — you hand the message to a provider that owns the carrier/OS relationship.

| Channel       | Identifier needed        | 3rd-party providers       | Notes                                            |
| ------------- | ------------------------ | ------------------------- | ------------------------------------------------ |
| iOS push      | **device token**         | **APNs** (Apple)          | App registers, OS issues token, app sends to us  |
| Android push  | **registration token**  | **FCM** (Firebase)        | Same handshake via Google                         |
| SMS           | **phone number**        | **Twilio**, **Nexmo**     | Per-message cost; carrier rate limits            |
| Email         | **email address**       | **SendGrid**, **Mailchimp** | Cheap, rich templates, deliverability/spam mgmt |

```
   APNs flow (FCM is analogous)
   ───────────────────────────
   App ──register──► OS ──► returns device token ──► our backend stores it
   Send: provider payload = { device_token, payload(JSON) } ──► APNs ──► device
```

Why 3rd-party providers? They own carrier agreements (SMS), OS push infra (APNs/FCM), and IP reputation/deliverability (email). Reinventing these is not a system-design problem worth solving in an interview — wrap them behind an adapter.

---

## Contact-info gathering flow

Before sending anything you need device tokens, phone numbers, and emails. These are collected at sign-up / app-install time and stored.

```
   ┌────────┐   install/sign-up    ┌────────────┐
   │ Client │ ───────────────────► │  API svrs  │
   └────────┘                      └──────┬─────┘
                                          ▼
                              ┌───────────────────────┐
                              │  user_info / device   │  RDBMS
                              │  tables                │
                              └───────────────────────┘
```

Schema sketch (a user can have multiple devices, so device token is a **1-to-many** table):

```
   user           : user_id (PK), email, ...
   device          : device_id (PK), user_id (FK), device_token, last_seen
   notification    : opt-in/opt-out settings per channel per user
```

One user → many device tokens (phone + tablet) → push must fan out to all of them.

---

## Notification sending / receiving flow (high-level design)

```
   ┌───────────┐ 1.API call    ┌────────────────────┐
   │ Services  │──────────────►│ Notification svrs  │  validate, fetch
   │ (events)  │               │ (build payload)    │  contact info
   └───────────┘               └────────┬───────────┘
                                         │ 2. enqueue per channel
              ┌──────────────┬───────────┼───────────┬──────────────┐
              ▼              ▼            ▼           ▼              ▼
        ┌──────────┐  ┌──────────┐  ┌──────────┐ ┌──────────┐  (cache/DB
        │ iOS PUSH │  │ Android  │  │   SMS    │ │  Email   │   alongside
        │  queue   │  │ PUSH q   │  │  queue   │ │  queue   │   for contact
        └────┬─────┘  └────┬─────┘  └────┬─────┘ └────┬─────┘   info)
             ▼             ▼             ▼            ▼
        ┌─────────┐   ┌─────────┐   ┌─────────┐  ┌─────────┐
        │ workers │   │ workers │   │ workers │  │ workers │   3. pull
        └────┬────┘   └────┬────┘   └────┬────┘  └────┬────┘
             ▼             ▼             ▼            ▼
           APNs           FCM        Twilio/Nexmo  SendGrid    4. 3rd-party
             └─────────────┴──────────────┴──────────┘ ──► user devices
```

**Components**

- **Notification servers** — public API (`POST /v1/notifications`), authenticate the caller, validate (email/phone format), pull contact info from cache/DB, build the per-channel payload, and **enqueue**. They do basic rate-limiting and fan a single logical notification into N device-specific messages.
- **Cache** — user info, device tokens, channel settings (read-heavy, hot path).
- **DB** — source of truth for users, devices, settings, notification logs.
- **Message queues (one per channel)** — decouple servers from workers, absorb spikes, and **isolate failures**: if APNs is down, the iOS queue backs up but SMS/email keep flowing.
- **Workers** — pull from their channel queue and call the corresponding 3rd-party provider; handle provider responses, retries, and event tracking.
- **3rd-party services** — APNs / FCM / Twilio / Nexmo / SendGrid / Mailchimp.

Why a queue per channel (not one shared queue)? Channels have wildly different throughput, latency, and failure modes. Per-channel queues give independent scaling and **fault isolation**.

---

## Reliability

### Prevent data loss

The hard requirement: **a notification can be delayed or reordered, but never silently lost.**

- **Persist before ack** — the notification server writes the request to a durable **notification log / DB** *before* returning success and before enqueuing. If a worker crashes mid-send, the record is still there to retry.
- **Durable queues** — use a queue with persistence + acknowledgements (worker acks only after the provider accepts the message).

```
   request ──► persist (DB log: state=NEW) ──► enqueue
           ──► worker sends ──► provider 2xx ──► DB state=SENT, ack queue
                            └─ provider 5xx ──► DB state=FAILED ──► retry
```

### Prevent duplicates (dedupe ID)

Distributed systems give **at-least-once** delivery (retries, redelivered queue messages). Exactly-once is impossible end-to-end, so aim for **exactly-once-ish**:

- The producer attaches a **dedupe / event ID** to every notification.
- Before sending, the worker checks if that ID was already processed (Redis set / dedupe table). If seen → drop.

```
   incoming event_id = "evt-9af3"
   if dedupe_store.contains(event_id):  drop (already sent)
   else:                                 send + dedupe_store.add(event_id, TTL)
```

This makes the system **idempotent** from the client's perspective even though delivery is at-least-once underneath.

---

## Additional components

### Notification template

Most notifications share structure (header, body, CTA) with a few variables. A **template** avoids rebuilding markup per send and keeps messaging consistent.

```
   template "you_were_mentioned":
     "BODY: {actor} mentioned you in {context}. [Open]"
   render({actor:"Alex", context:"#design"}) → final payload
```

Benefits: consistency, fast A/B copy changes, less error-prone than ad-hoc string building.

### User settings & opt-out

Every channel must be **opt-out-able** per user (legal requirement for marketing email/SMS — CAN-SPAM, GDPR, TCPA). Before enqueuing, check settings:

```
   notification_setting: user_id, channel, opt_in (bool)
   if not opt_in(user, channel):  skip this channel
```

### Rate limiting

Don't flood a user — cap notifications per user per channel per window. Over-notifying causes uninstalls and unsubscribes. (Same algorithms as Ch4: token bucket / sliding window keyed by `user:channel`.)

### Retry with backoff

If a provider call fails (5xx / timeout), the worker re-enqueues with **exponential backoff + jitter**. After a max retry count, mark `FAILED` and alert. Don't hot-loop a dead provider.

```
   attempt 1 fail ─► wait 1s  ─► attempt 2 fail ─► wait 2s
                ─► attempt 3 fail ─► wait 4s ─► … ─► give up → FAILED + alert
```

### Security (appKey / appSecret)

The public notification API must only be callable by trusted internal services. Issue each client an **appKey + appSecret**; requests are signed/authenticated, and only allow-listed services can call it. Prevents spammers from abusing your provider quota (which costs real money for SMS).

### Monitoring & event tracking

Track the funnel so you can detect provider outages and tune messaging.

| Metric                         | Why it matters                                    |
| ------------------------------ | ------------------------------------------------- |
| Queued / sent / delivered      | Pipeline health; queue backlog = downstream issue |
| Open / click rate              | Effectiveness; feeds A/B and template tuning      |
| Bounce / unsubscribe / opt-out | Deliverability + compliance health                |
| Provider error rate & latency  | Detect APNs/Twilio/SendGrid degradation early     |

Push provider delivery receipts/webhooks (SendGrid events, Twilio status callbacks) back into an analytics pipeline.

---

## Real-world usage

- **Push:** APNs (iOS), FCM (Android/web) — the only sanctioned paths to a device.
- **SMS/voice:** Twilio, Nexmo (Vonage), AWS SNS/Pinpoint.
- **Email:** SendGrid, Mailchimp, Amazon SES — manage IP warm-up and sender reputation for you.
- Companies like Uber/Airbnb run an internal "messaging platform" service exactly matching this shape: API → queues → channel workers → providers, with templates, preferences, and an event-tracking pipeline.

---

## Trade-offs and gotchas

- **At-least-once vs exactly-once** — pick at-least-once + dedupe ID; true exactly-once is unattainable across 3rd parties.
- **One user, many devices** — push fans out per device token; expire stale tokens (provider returns "unregistered" → delete it).
- **Provider as SPOF** — multi-provider failover (e.g. SendGrid → SES) for critical notifications; circuit-break a failing provider.
- **Notification fatigue** — aggressive rate limits + digest/batching; respect quiet hours and user preferences.
- **Cost** — SMS is expensive per message; abuse + missing rate limits = surprise bill. Secure the API.
- **Ordering** — queues don't guarantee global order; if order matters (OTP before "login from new device"), sequence/version the payload.
- **Compliance** — opt-out and unsubscribe are non-negotiable for SMS/email.

---

## One-page summary

```
   GOAL: deliver push / SMS / email reliably at scale, no data loss

   FLOW:    service ─► notification svr ─► per-channel queue ─► worker ─► provider
   STORE:   DB (source of truth + log)  +  cache (tokens/settings)
   QUEUES:  one per channel → fault isolation + independent scaling
   PROVIDERS: APNs/FCM (push) · Twilio/Nexmo (SMS) · SendGrid/Mailchimp (email)
   RELIABLE: persist-before-ack + retry w/ backoff; dedupe ID = exactly-once-ish
   EXTRAS:  templates · opt-out settings · rate limit · appKey/appSecret · tracking
   OBSERVE: queued/sent/delivered, bounce/unsub, provider latency & errors
```

## Notes
_Add your own notes here._
