"""Shared lexical-plus-recency ranking and its use as STI stimulus."""

HARNESS_ECAN_ARMS = ("harness_ecan", "harness_ecan_nofeedback")
KEYWORD_STIMULUS = 0.25


def recency(now, last):
    return 0.0 if last is None else 2.0 ** (1 + last - now)


def rank(ids, scores, priority, k):
    return sorted(ids, key=lambda i: (-scores[i], priority[i]))[:k]


def harness_rank(ids, hits, now, seen, used, priority, k):
    scores = [hits[i] + (0.5 * recency(now, used.get(i))
                         + 0.25 * recency(now, seen.get(i))) for i in ids]
    return rank(ids, scores, priority, k)


def stimulate_from_harness(sti, ids, hits, now, seen, priority, k):
    # Proof history is deliberately absent from both hybrids' retrieval scores.
    for i in harness_rank(ids, hits, now, seen, {}, priority, k):
        sti[i] += KEYWORD_STIMULUS
