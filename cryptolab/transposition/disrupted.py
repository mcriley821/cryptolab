"""
https://en.wikipedia.org/wiki/Transposition_cipher
"""

from math import ceil
from dataclasses import dataclass
from typing import Callable

from .columnar import (
    encrypt as col_encrypt,
    decrypt as col_decrypt,
)


@dataclass
class Filler:
    """
    A Filler is a pair of fill and unfill functions.
    It is used to change the fill algorithm for disrupted transpositions.

    Parameters
    ----------
    fill : Callable[[list[int], str], str]
        fill function to fill the columns before encryption

    unfill : Callable[[list[int], str], str]
        unfill function to read the columns after decryption
    """

    fill: Callable[[list[int], str], str]
    unfill: Callable[[list[int], str], str]


def encrypt(key: list[int], plaintext: str, filler: Filler):
    """
    Encrypt the plaintext using disrupted transposition.

    Parameters
    ----------
    key : list[int]
       A list of indexes that order the columns.

    plaintext : str
        The text to encrypt.

    Returns
    -------
    str
        The resultant ciphertext.

    Examples
    --------
    >>> encrypt(sequence("cipher"), "Defend the east wall of the castle", VIC)
    ' Dee eltctel  setwofntaafedhs hal '
    """
    return col_encrypt(key, filler.fill(key, plaintext))


def decrypt(key: list[int], ciphertext: str, filler: Filler):
    """
    Decrypt ciphertext that was encrypted by disrupted transposition.

    Parameters
    ----------
    key : list[int]
       A list of indexes that order the columns.

    ciphertext : str
        The text to decrypt.

    Returns
    -------
    str
        The resultant plaintext.

    Examples
    --------
    >>> decrypt(sequence("cipher"), " Dee eltctel  setwofntaafedhs hal ", VIC)
    'Defend the east wall of the castle'
    """
    return filler.unfill(key, col_decrypt(key, ciphertext))


def _vic_fill(key: list[int], plaintext: str) -> str:
    """
    Fill the columns according to the VIC algorithm.

    https://en.wikipedia.org/wiki/VIC_cipher

    Parameters
    ----------
    key : list[int]
        The transposition key.

    ciphertext : str
        The ciphertext to fill the columns before encryption.

    Returns
    -------
    str
        The result of filling the columns.

    Examples
    --------
    >>> _vic_fill(sequence("cipher"), "Defend the east wall of the castle")
    ' wall Dof thefe caendstl thee east'
    """

    rows = int(ceil(len(plaintext) / len(key)))
    last = len(plaintext) % len(key)
    filled = [""] * rows

    it = iter(plaintext)

    n = 0
    j = key.index(n)

    for i in range(rows):
        if i == rows - 1:
            filled[i] = "".join(next(it) for _ in range(last))
        else:
            filled[i] = "".join(next(it) for _ in range(j))

        if j == len(key):
            n += 1
            if n >= len(key):
                n = 0
            j = key.index(n)
        else:
            j += 1

    i = 0
    for c in it:
        while len(filled[i]) >= len(key):  # skip full rows
            i += 1
        filled[i] += c  # add next char until full

    return "".join(filled)


def _vic_unfill(key: list[int], plaintext: str) -> str:
    """
    Unfill the decrypted text according to the VIC algorithm.
    It is the inverse of VIC fill.

    https://en.wikipedia.org/wiki/VIC_cipher

    Parameters
    ----------
    key : list[int]
        The transposition key.

    plaintext : str
        The decrypted plaintext columns to read.

    Returns
    -------
    str
        The result of reading the columns.

    Examples
    --------
    >>> _vic_unfill(sequence("cipher"), " wall Dof thefe caendstl thee east")
    'Defend the east wall of the castle'
    """

    h1: list[str] = []
    h2: list[str] = []

    rows = int(ceil(len(plaintext) / len(key)))
    last = len(plaintext) % len(key)
    it = iter(plaintext)

    n = 0
    j = key.index(n)

    for i in range(rows):
        if i == rows - 1:
            row = "".join(next(it) for _ in range(last))
            h1.append(row)
            break

        row = "".join(next(it) for _ in range(len(key)))

        h1.append(row[:j])
        h2.append(row[j:])

        if j == len(key):
            n += 1
            if n >= len(key):
                n = 0
            j = key.index(n)
        else:
            j += 1

    return "".join(h1) + "".join(h2)


VIC = Filler(_vic_fill, _vic_unfill)


if __name__ == "__main__":
    key = [5, 2, 1, 3, 4, 0]
    plaintext = "WEAREDISCOVEREDFLEEATONCE"

    enc = encrypt(key, plaintext, VIC)
    print(enc, "\n")

    dec = decrypt(key, enc, VIC)
    print(dec)

    assert dec == plaintext
