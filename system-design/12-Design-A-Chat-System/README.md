# Chapter 12: Design A Chat System

Design a chat application supporting 1-on-1 and group chat.

## Key Topics
- Functional requirements: 1-on-1, group chat, online indicator, multi-device, push notifications
- Communication options:
  - Polling
  - Long polling
  - WebSocket (chosen)
- High-level design:
  - Stateless services (auth, group mgmt, user profile, service discovery)
  - Stateful service (chat service over WebSocket)
  - Third-party integration (push notifications)
- Storage: relational for user/friend, key-value (HBase) for messages
- Message data model: 1-on-1 (message_id, message_from, message_to, content, created_at), group (channel_id, message_id, ...)
- Message ID generation (Snowflake/local sequence)
- Service discovery (Apache Zookeeper)
- Online presence (heartbeat, fanout to friends)
- Group chat flow (per-recipient inbox)
- Read receipts, scaling

## Notes
_Add your notes here._
