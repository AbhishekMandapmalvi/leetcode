"""
Basic consistent-hashing ring (no virtual nodes).

- Each server is hashed to one position on the ring.
- A key is owned by the first server clockwise from the key's hash.
- Add/remove a server only relocates keys on adjacent arcs.

Demonstrates the two issues with the basic approach:
  1. Uneven partitions (random server positions).
  2. Skewed key distribution (real keys never hash perfectly uniformly).
"""

import bisect
import hashlib


def _hash(s: str) -> int:
    # 64-bit hash from MD5 (good enough for educational purposes).
    return int(hashlib.md5(s.encode()).hexdigest()[:16], 16)


class HashRing:
    def __init__(self) -> None:
        self._sorted_hashes: list[int] = []
        self._hash_to_server: dict[int, str] = {}

    def add_server(self, server: str) -> None:
        h = _hash(server)
        if h in self._hash_to_server:
            return
        bisect.insort(self._sorted_hashes, h)
        self._hash_to_server[h] = server

    def remove_server(self, server: str) -> None:
        h = _hash(server)
        if h not in self._hash_to_server:
            return
        self._sorted_hashes.remove(h)
        del self._hash_to_server[h]

    def get_server(self, key: str) -> str | None:
        if not self._sorted_hashes:
            return None
        h = _hash(key)
        idx = bisect.bisect_right(self._sorted_hashes, h)
        if idx == len(self._sorted_hashes):
            idx = 0
        return self._hash_to_server[self._sorted_hashes[idx]]


def distribution(ring: HashRing, n_keys: int = 100_000) -> dict[str, int]:
    counts: dict[str, int] = {}
    for i in range(n_keys):
        s = ring.get_server(f"key-{i}")
        counts[s] = counts.get(s, 0) + 1
    return counts


if __name__ == "__main__":
    ring = HashRing()
    for s in ["S0", "S1", "S2", "S3"]:
        ring.add_server(s)

    print("4 servers, 100K keys -> distribution (expect uneven without vnodes):")
    for s, c in sorted(distribution(ring).items()):
        print(f"  {s}: {c:,}")

    print("\nAdd S4 and remap:")
    before = {f"key-{i}": ring.get_server(f"key-{i}") for i in range(100_000)}
    ring.add_server("S4")
    after = {f"key-{i}": ring.get_server(f"key-{i}") for i in range(100_000)}
    moved = sum(1 for k in before if before[k] != after[k])
    print(f"  keys moved on adding S4: {moved:,} / 100,000  ({moved/1000:.2f}%)")
