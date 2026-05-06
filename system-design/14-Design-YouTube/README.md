# Chapter 14: Design YouTube

Design a video sharing service like YouTube/Netflix/TikTok.

## Key Topics
- Back-of-the-envelope estimation (DAU, storage, bandwidth)
- High-level design (cloud-based: CDN + cloud storage)
- Video uploading flow:
  - Upload original video to original storage
  - Transcoding service (DAG model: inspection, video/audio encoding, thumbnail, watermark)
  - Transcoded videos to transcoded storage and CDN
  - Update metadata DB and cache
  - Notify client
- Video streaming flow (streaming protocols: MPEG-DASH, HLS, Apple HLS, Microsoft Smooth Streaming)
- Video transcoding (codecs: H.264, VP9, HEVC; containers: mp4, mov, avi)
- DAG model for video processing
- Optimizations: speed (parallelize stages, upload by chunks, place center close to user), safety (pre-signed URL, video protection: DRM, AES, visual watermark), cost saving (CDN tiering, popular vs long-tail content)
- Error handling

## Notes
_Add your notes here._
