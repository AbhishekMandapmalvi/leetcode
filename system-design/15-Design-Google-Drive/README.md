# Chapter 15: Design Google Drive

Design a cloud file storage service like Google Drive/Dropbox/OneDrive.

## Key Topics
- Requirements: upload/download files, file sync across devices, notifications, view/edit/share, version history
- Back-of-the-envelope estimation
- Single server initial design (web server, MySQL metadata, storage dir)
- Storage: vertical → horizontal scale → S3-like object storage with replication (same region, cross-region)
- High-level design components:
  - Block servers (split file into blocks, compress, encrypt, upload changed blocks only)
  - Cloud storage
  - Cold storage
  - Load balancer
  - API servers
  - Metadata DB (user, device, namespace, file, file_version, block)
  - Metadata cache
  - Notification service (long polling vs WebSocket)
  - Offline backup queue
- Sync conflicts handling
- Save storage space: dedup blocks, intelligent backup (versioning + limit), move infrequent data to cold storage
- Failure handling (LB, block server, cloud storage, API tier, metadata cache/DB, notification, offline backup queue)

## Notes
_Add your notes here._
