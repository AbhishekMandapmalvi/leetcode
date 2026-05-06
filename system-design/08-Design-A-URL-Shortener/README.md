# Chapter 8: Design A URL Shortener

Design a tinyurl-like URL shortening service.

## Key Topics
- Back-of-the-envelope estimation (writes/sec, reads/sec, storage over 10 years)
- API endpoints (POST /api/v1/data/shorten, GET /api/v1/shortUrl)
- URL redirecting (301 vs 302)
- URL shortening logic
- Hash function:
  - Hash + collision resolution (MD5, SHA-1)
  - Base 62 conversion
- Database design (id, shortURL, longURL)
- Cache & load balancer
- Deep dive: write path, read path, rate limiter, analytics

## Notes
_Add your notes here._
