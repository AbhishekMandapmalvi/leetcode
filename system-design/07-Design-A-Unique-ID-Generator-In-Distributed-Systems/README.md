# Chapter 7: Design A Unique ID Generator In Distributed Systems

Generate unique IDs at scale across distributed systems.

## Key Topics
- Why not auto_increment in distributed DB
- Approaches:
  - Multi-master replication
  - UUID
  - Ticket server (Flickr)
  - Twitter Snowflake-like ID
- Snowflake breakdown: 1 bit sign + 41 bits timestamp + 5 bits datacenter + 5 bits machine + 12 bits sequence
- Clock synchronization (NTP)
- Section length tuning, high availability

## Notes
_Add your notes here._
