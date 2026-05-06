"""
Consistent-hashing ring with virtual nodes.

Each physical server is hashed to `vnodes_per_server` points on the ring.
Larger M => more even distribution at the cost of metadata size.

Demo prints distribution + remap percentage on adding a server,
and how stdev shrinks as M grows.
"""

import bisect
import hashlib
import statistics


def _hash(s: str) -> int:
    return int(hashlib.md5(s.encode()).hexdigest()[:16], 16)


class HashRingVNodes:
    def __init__(self, vnodes_per_server: int = 100):
        self.vnodes_per_server = vnodes_per_server
        self._sorted: list[int] = []
        self._owner: dict[int, str] = {}

    def _vnode_keys(self, server: str) -> list[int]:
        return [_hash(f"{server}#{i}") for i in range(self.vnodes_per_server)]

    def add_server(self, server: str) -> None:
        for h in self._vnode_keys(server):
            if h in self._owner:
                continue
            bisect.insort(self._sorted, h)
            self._owner[h] = server

    def remove_server(self, server: str) -> None:
        for h in self._vnode_keys(server):
            if h in self._owner:
                self._sorted.remove(h)
                del self._owner[h]

    def get_server(self, key: str) -> str | None:
        if not self._sorted:
            return None
        h = _hash(key)
        idx = bisect.bisect_right(self._sorted, h)
        if idx == len(self._sorted):
            idx = 0
        return self._owner[self._sorted[idx]]


def measure_distribution(ring: HashRingVNodes, n_keys: int) -> dict[str, int]:
    counts: dict[str, int] = {}
    for i in range(n_keys):
        s = ring.get_server(f"key-{i}")
        counts[s] = counts.get(s, 0) + 1
    return counts


def stdev_pct(counts: dict[str, int]) -> float:
    values = list(counts.values())
    return statistics.stdev(values) / statistics.mean(values) * 100


if __name__ == "__main__":
    servers = [f"S{i}" for i in range(8)]
    n_keys = 100_000

    print(f"{'vnodes/server':>14} | {'load stdev %':>12}")
    print("-" * 32)
    for m in [1, 5, 25, 100, 200, 500]:
        ring = HashRingVNodes(vnodes_per_server=m)
        for s in servers:
            ring.add_server(s)
        counts = measure_distribution(ring, n_keys)
        print(f"{m:>14} | {stdev_pct(counts):>11.2f}%")

    # Remap percentage when adding a server.
    ring = HashRingVNodes(vnodes_per_server=200)
    for s in servers:
        ring.add_server(s)
    before = {f"key-{i}": ring.get_server(f"key-{i}") for i in range(n_keys)}
    ring.add_server("S8")
    after = {f"key-{i}": ring.get_server(f"key-{i}") for i in range(n_keys)}
    moved = sum(1 for k in before if before[k] != after[k])
    print(f"\nAdding S8 to 8-server ring (M=200): moved {moved:,}/{n_keys:,} "
          f"({moved/n_keys*100:.2f}%) -- expected ~1/9 ~= 11%")
