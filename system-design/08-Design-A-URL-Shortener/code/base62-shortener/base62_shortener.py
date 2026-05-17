"""
Base62 URL shortener (single-process, thread-safe, stdlib only).

Approach: ID -> short code.
- Every long URL gets a unique auto-increment integer ID.
- The ID is encoded to a base62 string ([0-9a-zA-Z]) -> the short code.
  Base62 has no collisions (the ID is unique by construction) and stays
  short: 62^7 ~= 3.5 trillion codes fit in 7 chars.
- Resolving a short code: decode base62 -> ID -> look up the long URL.
- shorten() is idempotent: the same long URL always returns the same code
  (a long_url -> id map dedupes), matching real-world shorteners.

Run:
    python base62_shortener.py
"""

import threading

_ALPHABET = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
_BASE = len(_ALPHABET)  # 62
_CHAR_TO_VAL = {c: i for i, c in enumerate(_ALPHABET)}


def to_base62(num: int) -> str:
    """Encode a non-negative integer to a base62 string."""
    if num < 0:
        raise ValueError("num must be non-negative")
    if num == 0:
        return _ALPHABET[0]
    chars: list[str] = []
    while num > 0:
        num, rem = divmod(num, _BASE)
        chars.append(_ALPHABET[rem])
    return "".join(reversed(chars))


def from_base62(s: str) -> int:
    """Decode a base62 string back to its integer value."""
    if not s:
        raise ValueError("empty string")
    num = 0
    for ch in s:
        if ch not in _CHAR_TO_VAL:
            raise ValueError(f"invalid base62 char: {ch!r}")
        num = num * _BASE + _CHAR_TO_VAL[ch]
    return num


class URLShortener:
    def __init__(self, base_url: str = "https://tiny.url/", start_id: int = 1):
        self.base_url = base_url
        self._next_id = start_id
        self._id_to_long: dict[int, str] = {}
        self._long_to_short: dict[str, str] = {}  # idempotency map
        self._lock = threading.Lock()

    def shorten(self, long_url: str) -> str:
        """Return a short URL for long_url. Idempotent for the same URL."""
        with self._lock:
            existing = self._long_to_short.get(long_url)
            if existing is not None:
                return existing

            new_id = self._next_id
            self._next_id += 1

            code = to_base62(new_id)
            short_url = self.base_url + code

            self._id_to_long[new_id] = long_url
            self._long_to_short[long_url] = short_url
            return short_url

    def resolve(self, short: str) -> str:
        """Resolve a short code or short URL back to the original long URL."""
        code = short[len(self.base_url):] if short.startswith(self.base_url) else short
        new_id = from_base62(code)
        with self._lock:
            long_url = self._id_to_long.get(new_id)
        if long_url is None:
            raise KeyError(f"unknown short code: {code!r}")
        return long_url


if __name__ == "__main__":
    s = URLShortener()

    urls = [
        "https://example.com/very/long/path?a=1&b=2",
        "https://docs.python.org/3/library/threading.html",
        "https://github.com/anthropics",
    ]

    print("Shorten:")
    codes = []
    for u in urls:
        short = s.shorten(u)
        codes.append(short)
        print(f"  {short}  <-  {u}")

    print("\nResolve back:")
    for short in codes:
        print(f"  {short}  ->  {s.resolve(short)}")

    print("\nIdempotency (same URL -> same short):")
    again = s.shorten(urls[0])
    print(f"  first : {codes[0]}")
    print(f"  again : {again}")
    print(f"  equal : {again == codes[0]}")

    print("\nBase62 round-trip:")
    for n in (0, 1, 61, 62, 12345, 2_009_215_674_938):
        enc = to_base62(n)
        dec = from_base62(enc)
        print(f"  {n:>15} -> {enc:>8} -> {dec:>15}  ok={dec == n}")
