# Chapter 14: Design YouTube

A video-sharing service: users **upload** videos that are transcoded into many resolutions, and **stream** them smoothly to any device over a CDN. The same blueprint covers Netflix and TikTok.

```
   ┌────────┐  upload   ┌──────────────┐  transcode  ┌──────────────┐
   │ Creator│ ────────► │ Original blob│ ──────────► │ Transcoded   │
   └────────┘           │   storage    │             │ blob + CDN   │
                        └──────────────┘             └──────┬───────┘
                                                            │ stream
   ┌────────┐  watch                                        ▼
   │ Viewer │ ◄────────────────────────────────────── [ Nearest CDN PoP ]
   └────────┘
```

---

## Requirements

**Functional**
- Upload videos fast, watch videos smoothly.
- Change video quality (adaptive bitrate).
- Low infra cost, high availability, scalability, reliability.
- Clients: mobile apps, browser, smart TV.

**Non-functional**
- Reliability — no corrupted/lost video.
- Smooth playback even on poor networks.
- Global low-latency streaming.

> Out of scope to mention but defer: recommendations, comments, channels, subscriptions — say "I'll focus on upload + streaming, the hard parts."

---

## Back-of-the-envelope estimation

Assumptions
- 5M **DAU**
- Each user watches 5 videos/day
- 10% of users upload 1 video/day
- Average video size = **300 MB**

**Storage / day**
```
   uploads/day   = 5M × 10% × 1 video      = 500K videos/day
   storage/day   = 500K × 300 MB            ≈ 150 TB / day
   (transcoded copies add ~2× the original → budget ~3× raw)
```

**Streaming bandwidth (egress dominates cost)**
```
   views/day     = 5M × 5                   = 25M views/day
   avg bitrate   ≈ 5 Mbps (1080p) , avg watch 10 min
   bytes/view    ≈ 5 Mbps × 600 s / 8       ≈ 375 MB
   egress/day    = 25M × 375 MB             ≈ 9.4 PB / day
```

```
   ┌──── inputs ────┐      ┌──── derived ────┐
   │ 5M DAU         │      │ 500K uploads/day│
   │ 5 views/user   │ ──►  │ ~150 TB/day in  │
   │ 10% upload     │      │ ~9 PB/day egress│
   │ 300 MB/video   │      │ egress = $$$    │
   └────────────────┘      └─────────────────┘
```

> Key takeaway for the interview: **CDN egress, not storage, is the cost driver.** Almost every optimization later targets egress.

---

## High-level design (cloud-based)

Don't build your own datacenters in an interview — lean on **CDN + cloud blob storage**.

```
                       ┌──────────────┐
   Client ───────────► │ API servers  │  (metadata, auth, feed, search;
              upload   └──────┬───────┘   everything EXCEPT the video bytes)
              metadata        │
                              ▼
   Client ──pre-signed URL──► [ Original blob storage (S3) ]
                                       │
                                       ▼
                              [ Transcoding servers ]
                                       │
                       ┌───────────────┴───────────────┐
                       ▼                                ▼
              [ Transcoded blob storage ]        [ Metadata DB + cache ]
                       │
                       ▼
                  [   CDN   ] ──stream──► Viewers (worldwide)
```

- **Original storage** — keep the raw master (cold-tierable later).
- **Transcoded storage** — many renditions, fronted by CDN.
- **API servers** — stateless; handle metadata, never proxy video bytes.
- **CDN** — serves all playback; the origin (blob store) is only the fallback.

---

## Video uploading flow

```
   1  Client requests upload  ──► API server creates video record (status=UPLOADING)
   2  API returns a PRE-SIGNED URL to the original blob store
   3  Client uploads bytes DIRECTLY to blob store (chunked, resumable)
   4  Blob store fires event ──► Transcoding service picks it up
   5  Transcoding runs the DAG (below) → writes renditions to transcoded store
   6  Transcoded store → push/replicate to CDN
   7  Metadata DB + cache updated (status=READY, manifest URLs, durations)
   8  Notification service pings the client / channel subscribers
```

```
   Creator ──(1)──► API ──(2 url)──► Creator
   Creator ──(3 bytes)─────────────► Original blob store
                                          │ (4 event)
                                          ▼
   Transcoding ──(5)──► Transcoded store ──(6)──► CDN
        │ (7)
        ▼
   Metadata DB/cache ──(8)──► Notify client
```

Two parallel sub-flows worth calling out:
- **Video upload** (the bytes) — slow, goes straight to blob storage.
- **Metadata update** (title, thumbnail choice, visibility) — fast, hits API + DB independently.

---

## Transcoding service (DAG model)

Raw video from a phone may be 4K HEVC 60fps — useless for a 3G viewer. **Transcoding** produces a ladder of (resolution × bitrate × codec) renditions, plus thumbnails and watermarks.

Why a **DAG (directed acyclic graph)**? Stages have dependencies but many run in parallel. A config-driven DAG lets product teams add stages (e.g. new codec) without rewriting the pipeline.

```
                        ┌─────────────────┐
                        │   1 Inspection  │  validate, probe codec/res,
                        │  (split into    │  reject corrupt, split file
                        │   chunks)       │  into independent chunks
                        └────────┬────────┘
            ┌────────────────────┼────────────────────┐
            ▼                    ▼                     ▼
   ┌─────────────────┐  ┌─────────────────┐   ┌─────────────────┐
   │ 2 Video encode  │  │ 3 Audio encode  │   │ 4 Thumbnail gen │
   │ H.264/VP9/HEVC  │  │ AAC/Opus        │   │ (sample frames) │
   │ multi-res ladder│  └────────┬────────┘   └────────┬────────┘
   └────────┬────────┘           │                     │
            ▼                    │                     │
   ┌─────────────────┐           │                     │
   │ 5 Watermark     │           │                     │
   └────────┬────────┘           │                     │
            └──────────┬─────────┴─────────────────────┘
                       ▼
              ┌─────────────────┐
              │ 6 Packaging /   │  mux into DASH/HLS segments
              │   manifest      │  + master playlist (ABR ladder)
              └────────┬────────┘
                       ▼
              Transcoded store → CDN
```

| Stage       | Job                                                  |
| ----------- | ---------------------------------------------------- |
| Inspection  | Validate integrity, read metadata, **chunk** the file |
| Video encode| Transcode each chunk into the resolution/bitrate ladder |
| Audio encode| Separate audio track encode (AAC / Opus)             |
| Thumbnail   | Auto-extract candidate frames + creator-chosen one   |
| Watermark   | Overlay channel/brand image (optional)               |
| Packaging   | Segment + write DASH/HLS manifests                   |

Architecture: **preprocessor → DAG scheduler → resource manager → workers → encoded video store**, with a message queue between scheduler and a worker pool that autoscales.

---

## Video streaming flow & protocols

Don't download then play — **stream** with **adaptive bitrate (ABR)**: the player downloads small segments and switches quality based on measured bandwidth.

```
   Player ── GET manifest ──► CDN
   Player picks rendition by current bandwidth:
      good wifi  → request 1080p segments
      bandwidth drops → next segment 480p (seamless)
   ┌──seg1─┐┌──seg2─┐┌seg3┐┌──seg4──┐  (each 2–10 s)
     1080    1080    480    720
```

| Protocol                     | Owner      | Notes                                  |
| ---------------------------- | ---------- | -------------------------------------- |
| **MPEG-DASH**                | ISO std    | Codec-agnostic, open, widely used      |
| **HLS (Apple HTTP Live Streaming)** | Apple | Required for iOS/Safari; ubiquitous    |
| **Microsoft Smooth Streaming** | MS       | Legacy Silverlight era                 |
| HDS (Adobe)                  | Adobe      | Legacy Flash; effectively dead         |

> Practical answer: ship **HLS + DASH** (cover Apple + everything else); both are HTTP-based so they ride normal CDNs.

---

## Codecs & containers

- **Container** = the box holding video + audio + metadata: `mp4`, `mov`, `webm`, `avi`, `flv`.
- **Codec** = the compression algorithm for the actual stream.

| Codec  | Compression | CPU cost | Support              | Use                       |
| ------ | ----------- | -------- | -------------------- | ------------------------- |
| H.264  | baseline    | low      | universal            | safe default everywhere   |
| VP9    | ~30% better | medium   | Chrome/Android, royalty-free | YouTube web         |
| HEVC/H.265 | ~50% better | high  | Apple/4K devices, licensed | premium / 4K          |
| AV1    | best        | very high| newer devices        | long-tail popular content |

Trade-off: better codec → less egress (huge $) but more transcode CPU and patchier device support. Hence **multiple renditions per video** and ABR picks per device.

---

## Optimizations

### Speed
- **Parallelize DAG stages** — chunk the video; encode chunks concurrently across the worker fleet.
- **Chunked / resumable upload** — split client upload; retry only the failed chunk.
- **Place upload centers close to users** — regional ingest endpoints cut RTT.
- **Decouple via queues** — upload, transcode, notify are independent async stages.

### Safety
- **Pre-signed URLs** — client uploads straight to blob storage without credentials touching app servers; URL is scoped + time-limited.
- **DRM** (Widevine, FairPlay, PlayReady) — prevents ripping premium content.
- **AES encryption** — encrypt segments; player fetches the key over an authorized channel.
- **Visual watermark** — overlay an ID to deter/trace leaks.

### Cost saving (attack egress)
- **CDN tiering — popular vs long-tail:**

```
   Popular (top ~5% of videos, ~95% of views)  → full CDN, many PoPs
   Long-tail (rare views)                       → serve from origin /
                                                  fewer regions / cold tier
```
- Only CDN-cache hot content; serve cold content from cheaper blob storage.
- Encode fewer renditions for low-view videos (encode-on-demand on first request).
- Move original masters to **cold storage** (Glacier-class) after transcoding.
- Use a more efficient codec for the most-watched videos to cut egress bytes.

---

## Error handling

| Failure                       | Handling                                            |
| ----------------------------- | --------------------------------------------------- |
| **Recoverable** (chunk upload fails, one transcode task fails) | Retry that chunk/task a few times |
| Retries exhausted             | Return clear error code to client                   |
| Upload error                  | Resume from last good chunk (resumable upload)       |
| Transcoding error             | Re-run only the failed DAG node, not the whole video |
| Premature exit during stream  | Player resumes from last segment (stateless CDN)     |
| **Unrecoverable**             | Stop, surface error, alert ops                       |

Split into **recoverable** (retry) vs **unrecoverable** (fail fast + alert) — the same split as Ch4's fail-open/fail-closed thinking.

---

## Trade-offs and gotchas

- **Egress is the bill** — every cost optimization is really an egress optimization.
- **Don't proxy video bytes through app servers** — pre-signed URLs + direct-to-blob is mandatory at scale.
- **Encode-on-demand** trades first-view latency for storage/CPU on the long tail; great because views are extremely skewed.
- **ABR + multiple renditions** is non-negotiable — one rendition can't serve a 4K TV and a 3G phone.
- **Thumbnails are their own scale problem** (billions of small objects) — store + CDN them like images, not like video.

---

## One-page summary

```
   GOAL: upload videos fast, stream them smoothly + cheaply at PB scale

   UPLOAD:   client ─pre-signed URL─► blob store (chunked, resumable)
   PROCESS:  DAG = inspect→{video,audio,thumb}→watermark→package
   STORE:    original (cold-able) + transcoded renditions
   STREAM:   HLS + DASH, adaptive bitrate, served from CDN
   CODEC:    H.264 default; VP9/HEVC for popular to cut egress
   COST:     CDN-tier hot vs long-tail; encode-on-demand; cold masters
   ERRORS:   recoverable→retry chunk/DAG node; else fail fast + alert
```

## Notes
_Add your own notes here._
