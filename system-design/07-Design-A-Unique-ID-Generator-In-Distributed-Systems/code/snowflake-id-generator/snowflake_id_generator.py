"""
Twitter-Snowflake style 64-bit unique ID generator (thread-safe, stdlib only).

Layout of the 64-bit signed integer:

    63        62 .................. 22  21 .. 17  16 .. 12  11 ........ 0
  +------+------------------------------+----------+----------+------------+
  | sign |   41-bit timestamp (ms)      | 5b dc    | 5b mach. | 12b seq    |
  +------+------------------------------+----------+----------+------------+
     1                41                     5          5          12

  - sign       : always 0 -> ID stays positive.
  - timestamp  : milliseconds since a CUSTOM epoch (~69 years of range).
  - datacenter : 0..31  (assigned at startup, fixed at runtime).
  - machine    : 0..31  (assigned at startup, fixed at runtime).
  - sequence   : 0..4095 per machine per millisecond (4096 IDs / ms / node).

Properties: globally unique (given unique dc/machine), ~time-sortable,
~4.1M IDs/sec/node, no per-ID coordination.

How to run:
    python snowflake_id_generator.py
No external dependencies (Python 3.9+ for the `dict[...]` hints; otherwise typing).
"""

import threading
import time
from dataclasses import dataclass

# --- Bit allocation -------------------------------------------------------
DATACENTER_ID_BITS = 5
MACHINE_ID_BITS = 5
SEQUENCE_BITS = 12

MAX_DATACENTER_ID = (1 << DATACENTER_ID_BITS) - 1   # 31
MAX_MACHINE_ID = (1 << MACHINE_ID_BITS) - 1         # 31
MAX_SEQUENCE = (1 << SEQUENCE_BITS) - 1             # 4095

# --- Bit shifts (left offset of each section) -----------------------------
MACHINE_ID_SHIFT = SEQUENCE_BITS                                  # 12
DATACENTER_ID_SHIFT = SEQUENCE_BITS + MACHINE_ID_BITS             # 17
TIMESTAMP_SHIFT = SEQUENCE_BITS + MACHINE_ID_BITS + DATACENTER_ID_BITS  # 22

# Custom epoch: 2024-01-01T00:00:00Z in ms. Maximizes the ~69-year window.
CUSTOM_EPOCH_MS = 1_704_067_200_000


@dataclass
class DecodedID:
    timestamp_ms: int      # absolute unix epoch ms
    datacenter_id: int
    machine_id: int
    sequence: int


class SnowflakeIDGenerator:
    """Thread-safe Snowflake ID generator for a single (datacenter, machine)."""

    def __init__(self, datacenter_id: int, machine_id: int,
                 epoch_ms: int = CUSTOM_EPOCH_MS):
        if not (0 <= datacenter_id <= MAX_DATACENTER_ID):
            raise ValueError(f"datacenter_id must be 0..{MAX_DATACENTER_ID}")
        if not (0 <= machine_id <= MAX_MACHINE_ID):
            raise ValueError(f"machine_id must be 0..{MAX_MACHINE_ID}")

        self.datacenter_id = datacenter_id
        self.machine_id = machine_id
        self.epoch_ms = epoch_ms

        self._lock = threading.Lock()
        self._last_timestamp = -1
        self._sequence = 0

    @staticmethod
    def _now_ms() -> int:
        return int(time.time() * 1000)

    def _wait_next_ms(self, last_timestamp: int) -> int:
        """Spin-wait until the wall clock advances past `last_timestamp`."""
        ts = self._now_ms()
        while ts <= last_timestamp:
            ts = self._now_ms()
        return ts

    def next_id(self) -> int:
        with self._lock:
            timestamp = self._now_ms()

            # Monotonic clock guard: the clock moved backward (NTP / leap sec).
            if timestamp < self._last_timestamp:
                # Small drift -> wait it out. Large regression would be a bug;
                # raising would be the alternative (alert + reject).
                timestamp = self._wait_next_ms(self._last_timestamp)

            if timestamp == self._last_timestamp:
                # Same millisecond: bump the sequence.
                self._sequence = (self._sequence + 1) & MAX_SEQUENCE
                if self._sequence == 0:
                    # Sequence exhausted (>4096 in this ms): wait next ms.
                    timestamp = self._wait_next_ms(self._last_timestamp)
            else:
                # New millisecond: reset the sequence.
                self._sequence = 0

            self._last_timestamp = timestamp

            return (
                ((timestamp - self.epoch_ms) << TIMESTAMP_SHIFT)
                | (self.datacenter_id << DATACENTER_ID_SHIFT)
                | (self.machine_id << MACHINE_ID_SHIFT)
                | self._sequence
            )

    def decode(self, snowflake_id: int) -> DecodedID:
        """Decompose an ID back into its sections (for debugging/inspection)."""
        sequence = snowflake_id & MAX_SEQUENCE
        machine_id = (snowflake_id >> MACHINE_ID_SHIFT) & MAX_MACHINE_ID
        datacenter_id = (snowflake_id >> DATACENTER_ID_SHIFT) & MAX_DATACENTER_ID
        timestamp_ms = (snowflake_id >> TIMESTAMP_SHIFT) + self.epoch_ms
        return DecodedID(
            timestamp_ms=timestamp_ms,
            datacenter_id=datacenter_id,
            machine_id=machine_id,
            sequence=sequence,
        )


if __name__ == "__main__":
    gen = SnowflakeIDGenerator(datacenter_id=3, machine_id=7)

    # Generate a batch and verify monotonic-increasing + unique.
    n = 10_000
    ids = [gen.next_id() for _ in range(n)]

    is_sorted = all(ids[i] < ids[i + 1] for i in range(len(ids) - 1))
    is_unique = len(set(ids)) == len(ids)

    print(f"Generated {n} IDs")
    print(f"  first id : {ids[0]}")
    print(f"  last  id : {ids[-1]}")
    print(f"  unique   : {is_unique}")
    print(f"  monotonic increasing: {is_sorted}")

    # Decode one ID back into its parts.
    sample = ids[len(ids) // 2]
    parts = gen.decode(sample)
    readable = time.strftime("%Y-%m-%d %H:%M:%S",
                             time.gmtime(parts.timestamp_ms / 1000))
    print(f"\nDecode {sample}:")
    print(f"  timestamp_ms  : {parts.timestamp_ms}  ({readable} UTC)")
    print(f"  datacenter_id : {parts.datacenter_id}")
    print(f"  machine_id    : {parts.machine_id}")
    print(f"  sequence      : {parts.sequence}")

    # Re-encode the decoded parts of the sample's millisecond as a sanity check.
    rebuilt = (
        ((parts.timestamp_ms - gen.epoch_ms) << TIMESTAMP_SHIFT)
        | (parts.datacenter_id << DATACENTER_ID_SHIFT)
        | (parts.machine_id << MACHINE_ID_SHIFT)
        | parts.sequence
    )
    print(f"\n  re-encoded == original ? {rebuilt == sample}")
