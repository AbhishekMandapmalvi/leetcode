# Chapter 10: Design A Notification System

Design a system that sends notifications across multiple channels.

## Key Topics
- Notification types: mobile push (iOS APNs, Android FCM), SMS (Twilio, Nexmo), email (SendGrid, Mailchimp)
- Contact info gathering flow
- Notification sending/receiving flow
- High-level design:
  - Notification servers
  - Cache, DB
  - Message queues per channel
  - Workers
  - Third-party services
- Reliability: prevent data loss, prevent duplicates (dedupe ID)
- Additional components: template, settings, rate limiting, retry, security (appKey/appSecret), monitoring, events tracking

## Notes
_Add your notes here._
