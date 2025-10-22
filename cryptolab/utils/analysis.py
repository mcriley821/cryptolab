from math import log2
from collections import Counter


# Default frequencies used when computing chi-squared statistic
DEFAULT_FREQUENCIES: dict[str, float] = {
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


def frequency_counts(text: str) -> Counter:
    """
    Count the occurences of each character in the given text.

    Parameters
    ----------
    text : str
        The subject text

    Returns
    -------
    Counter
        A dictionary mapping characters to their counts

    Examples
    --------
    >>> frequency_counts("Defend the east wall of the castle".upper())
    Counter({'E': 6, ' ': 6, 'T': 4, 'A': 3, 'L': 3, 'D': 2, 'F': 2, 'H': 2, 'S': 2, 'N': 1, 'W': 1, 'O': 1, 'C': 1})
    """

    return Counter(text)


def index_of_coincidence(text: str) -> float:
    """
    Compute the Index of Coincidence (IC) for a given text.
    Only alphabetic characters are considered, case-insensitive.

    Parameters
    ----------
    text : str
        The subject text

    Returns
    -------
    float
        The index of coincidence

    Raises
    ------
    ValueError
        If there are less than 2 alphabetic characters in the text

    Examples
    --------
    >>> index_of_coincidence("Defend the east wall of the castle")
    0.082010582010582
    """

    n = 0
    freq_sum = 0
    for k, v in Counter(i.upper() for i in text if i.isalpha()).items():
        if k.upper().isalpha():
            n += v
            freq_sum += v * (v - 1)

    if n <= 1:
        raise ValueError("text must have at least 2 alphabetic characters")

    return freq_sum / (n * (n - 1))


def chi_squared(
    text: str, *, frequencies: dict[str, float] = DEFAULT_FREQUENCIES
) -> float:
    """
    Compute the Chi-squared statistic for the given text.
    Only alphabetic characters are considered, case-insensitive.

    Parameters
    ----------
    text : str
        The subject text.

    frequencies : dict[str, float], optional
        Character to float mapping of expected frequencies for symbols in the text.

    Returns
    -------
    float
        Computed chi-squared.

    Examples
    --------
    >>> chi_squared("Defend the east wall of the castle")
    18.528310082299488
    """

    counts = Counter(i.upper() for i in text if i.isalpha())
    n = sum(counts.values())

    chi_sq = 0.0
    for c, p in frequencies.items():
        exp = p * n
        chi_sq += (counts[c] - exp) ** 2 / exp if exp > 0 else 0

    return chi_sq


def entropy(text: str) -> float:
    """
    Compute the Shannon (log2) entropy of the given text.

    Parameters
    ----------
    text : str
        The subject text.

    Returns
    -------
    float
        Calculated Shannon entropy

    Raises
    ------
    ValueError
        If the text is empty
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

    Parameters
    ----------
    text : str
        The subject text.

    top : int, default=10
        Number of top scoring autocorrelations to return.

    Returns
    -------
    list[tuple[int, int]]
        List of (shift, score) of the top scoring autocorrelations.
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
