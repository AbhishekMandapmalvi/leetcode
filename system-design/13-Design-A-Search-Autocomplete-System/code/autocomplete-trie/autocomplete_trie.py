"""
Autocomplete trie with top-k completions cached at every node.

Idea (from the chapter):
- A trie stores each query along a path of characters from the root.
- The naive query "walk subtree, collect all completions, sort, take k" is
  too slow on every keystroke.
- So we CACHE the top-k (word, frequency) list directly on every node.
- A query then just walks the prefix (O(prefix length)) and returns the
  node's already-sorted cached list (O(k)).  Effectively O(1) per keystroke.
- The cost is paid at write/build time: when we insert or bump a word's
  frequency, we refresh the cached top-k on every node along that word's
  path (only those nodes can be affected).

`record_search(word)` simulates the data-gathering pipeline bumping a
query's frequency and keeping the cached rankings fresh.

Run:
    python autocomplete_trie.py
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable


@dataclass
class _Node:
    children: dict[str, "_Node"] = field(default_factory=dict)
    is_word: bool = False
    frequency: int = 0
    # Cached best completions under this prefix: list of (freq, word),
    # sorted by frequency desc (then word asc for stable ties).
    top_k: list[tuple[int, str]] = field(default_factory=list)


class AutocompleteTrie:
    def __init__(self, k: int = 5, max_prefix_len: int = 50):
        self.k = k
        self.max_prefix_len = max_prefix_len
        self._root = _Node()

    # ----- writes -------------------------------------------------------

    def insert(self, word: str, freq: int = 1) -> None:
        """Insert `word` (or add `freq` to it) and refresh cached top-k
        on every node along its path."""
        word = word[: self.max_prefix_len]
        if not word:
            return

        # Walk down, creating nodes, recording the path.
        path: list[_Node] = [self._root]
        node = self._root
        for ch in word:
            node = node.children.setdefault(ch, _Node())
            path.append(node)

        node.is_word = True
        node.frequency += freq
        new_freq = node.frequency

        # Only nodes on this word's path can have their top-k changed.
        for n in path:
            self._refresh_top_k(n, word, new_freq)

    def bulk_insert(self, iterable: Iterable) -> None:
        """Insert many items. Each item is either `word` or `(word, freq)`."""
        for item in iterable:
            if isinstance(item, tuple):
                self.insert(item[0], item[1])
            else:
                self.insert(item)

    def record_search(self, word: str, freq: int = 1) -> None:
        """A user searched `word`: bump its frequency and refresh the
        cached top-k along its path so rankings stay current."""
        self.insert(word, freq)

    # ----- read ---------------------------------------------------------

    def suggest(self, prefix: str, k: int | None = None) -> list[str]:
        """Return up to k highest-frequency completions of `prefix`.

        O(len(prefix)) to walk + O(k) to read the cached list.
        """
        k = self.k if k is None else k
        node = self._root
        for ch in prefix[: self.max_prefix_len]:
            node = node.children.get(ch)
            if node is None:
                return []
        return [word for _freq, word in node.top_k[:k]]

    # ----- internals ----------------------------------------------------

    def _refresh_top_k(self, node: _Node, word: str, new_freq: int) -> None:
        """Merge (new_freq, word) into node.top_k, keeping it sorted by
        frequency desc then word asc, truncated to k."""
        # Drop any stale entry for this word, then insert the fresh one.
        merged = [e for e in node.top_k if e[1] != word]
        merged.append((new_freq, word))
        # Sort: highest frequency first, ties broken alphabetically.
        merged.sort(key=lambda e: (-e[0], e[1]))
        node.top_k = merged[: self.k]


if __name__ == "__main__":
    trie = AutocompleteTrie(k=5)

    sample = [
        ("dinner", 1_200_000),
        ("dinner near me", 780_000),
        ("dinnerware", 140_000),
        ("dim sum", 430_000),
        ("dim sum near me", 95_000),
        ("dog", 2_400_000),
        ("dog food", 510_000),
        ("dodge", 60_000),
    ]
    trie.bulk_insert(sample)

    print('suggest("di"):')
    for s in trie.suggest("di"):
        print(f"  - {s}")

    print('\nsuggest("dinn"):')
    for s in trie.suggest("dinn"):
        print(f"  - {s}")

    print('\nsuggest("do"):')
    for s in trie.suggest("do"):
        print(f"  - {s}")

    # Simulate a surge of searches for a previously low-ranked query.
    print('\n--- recording 3,000,000 searches for "dodge" ---')
    trie.record_search("dodge", 3_000_000)

    print('\nsuggest("do") after surge:')
    for s in trie.suggest("do"):
        print(f"  - {s}")

    print('\nsuggest("dod"):')
    for s in trie.suggest("dod"):
        print(f"  - {s}")
