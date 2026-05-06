# Chapter 6: Design A Key-Value Store

Design a distributed key-value store similar to Dynamo or Cassandra.

## Key Topics
- Single-server key-value store (hash table in memory)
- Distributed key-value store
- CAP theorem (CP vs AP systems)
- System components:
  - Data partition (consistent hashing)
  - Data replication
  - Consistency (quorum: N, W, R; strong/eventual/weak)
  - Inconsistency resolution: versioning, vector clocks
  - Handling failures: gossip protocol, sloppy quorum, hinted handoff, anti-entropy (Merkle tree)
  - Handling data center outage
- Write path & read path
- Storage engine: SSTable, LSM tree

## Notes
_Add your notes here._
