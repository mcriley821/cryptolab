#!/usr/bin/env python3
from math import log2
from collections import Counter


def frequency_counts(text: str) -> Counter:
    return Counter(text)


def index_of_coincidence(text: str) -> float:
    """
    Compute the Index of Coincidence (IC) for a given text.
    Only alphabetic characters are considered, case-insensitive.

    :param text: The text to compute the IC of
    :return: The index of coincidence as a float, or None
    :raises ValueError: If the filtered text cannot be analyzed
    """
    filtered = [c.upper() for c in text if c.isalpha()]
    n = len(filtered)
    if n <= 1:
        raise ValueError("filtered text is too short to analyze")

    counts = Counter(filtered)
    numerator = sum(f * (f - 1) for f in counts.values())
    denominator = n * (n - 1)

    return numerator / denominator


def chi_squared(text: str) -> float:
    """
    Compute the Chi-squared statistic for a given text.
    Only alphabetic characters are considered, case-insensitive.

    :param text: The ciphertext/plaintext to analyze.
    :return: Chi-squared statistic.
    :raises ValueError: If the filtered text is empty.
    """
    expected_freq: dict = {
        "A": 0.08167,
        "B": 0.01492,
        "C": 0.02782,
        "D": 0.04253,
        "E": 0.12702,
        "F": 0.02228,
        "G": 0.02015,
        "H": 0.06094,
        "I": 0.06966,
        "J": 0.00153,
        "K": 0.00772,
        "L": 0.04025,
        "M": 0.02406,
        "N": 0.06749,
        "O": 0.07507,
        "P": 0.01929,
        "Q": 0.00095,
        "R": 0.05987,
        "S": 0.06327,
        "T": 0.09056,
        "U": 0.02758,
        "V": 0.00978,
        "W": 0.02360,
        "X": 0.00150,
        "Y": 0.01974,
        "Z": 0.00074,
    }

    filtered = [c.upper() for c in text if c.isalpha()]
    n = len(filtered)
    if n == 0:
        raise ValueError("filtered text is empty")

    counts = Counter(filtered)

    chi_sq = 0.0
    for letter, exp_p in expected_freq.items():
        observed = counts[letter]
        expected = exp_p * n
        chi_sq += (observed - expected) ** 2 / expected if expected > 0 else 0

    return chi_sq


def entropy(text: str) -> float:
    """
    Compute the Shannon entropy of the given text.

    :param text: The ciphertext/plaintext to analyze.
    :return: Shannon entropy
    :raises ValueError: If the text is empty
    """
    n = len(text)
    if n == 0:
        raise ValueError("text is empty")
    freq = Counter(text)
    return -sum((f / n) * log2(f / n) for f in freq.values())


def autocorrelation(text: str, top: int = 10) -> list[tuple[int, int]]:
    """
    Compute the autocorrelation index for all possible shifts (1..n-1).
    Only alphabetic characters are considered, case-insensitive.

    :param text: The ciphertext/plaintext to analyze.
    :return: List of (shift, score) where score = matches / (n - shift).
    """
    n = len(text)
    results = []

    for shift in range(1, n):
        matches = sum(1 for i in range(n - shift) if text[i] == text[i + shift])
        results.append((shift, matches))

    results.sort(key=lambda p: p[1], reverse=True)

    return results[:top]


if __name__ == "__main__":
    from argparse import ArgumentParser

    parser = ArgumentParser()
    parser.add_argument(
        "text",
        help="text to analyze",
    )
    ns = parser.parse_args()

    print("Counts:")
    for char, count in frequency_counts(ns.text).items():
        print(f"\t'{char}': {count}")

    try:
        print(f"IOC:         {index_of_coincidence(ns.text):.4f}")
    except ValueError:
        ...

    try:
        print(f"Chi-squared: {chi_squared(ns.text):.4f}")
    except ValueError:
        ...

    print(f"Entropy:     {entropy(ns.text):.4f}")
    print("Autocorrelation:")
    for shift, score in autocorrelation(ns.text):
        print(f"\t[{shift:2d}]: {score:.4f}")
    print()
