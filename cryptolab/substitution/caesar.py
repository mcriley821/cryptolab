"""
https://en.wikipedia.org/wiki/Caesar_cipher
"""

from . import affine
from ..scoring.ngram import monogram_score

from typing import Callable, Iterator


def encrypt(
    plaintext: str,
    key: int,
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt plaintext using the Caesar cipher.

    Parameters
    ----------
    plaintext : str
        The message to be encrypted.

    key : int
        The amount to shift each letter.

    preserve_nonalpha : bool, default=False
        Whether to preserve non-alphebeticals in the ciphertext.

    Returns
    -------
    str
        The resultant ciphertext.

    Examples
    --------
    >>> encrypt("Hello, world!", 3, preserve_space=True, preserve_symbols=True)
    'Khoor, zruog!'

    >>> encrypt("Hello, world!", 3)
    'Khoorzruog'
    """
    return affine.encrypt(
        plaintext,
        (1, key),
        preserve_nonalpha=preserve_nonalpha,
    )


def decrypt(ciphertext: str, key: int) -> str:
    """
    Decrypt ciphertext using the Caesar cipher.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decipher.

    key : int
        The amount to shift each letter.

    Returns
    -------
    str
        The resultant plaintext.

    Examples
    --------
    >>> decrypt("Khoor, zruog!", 3)
    'Hello, world!'
    """
    return affine.decrypt(ciphertext, (1, key))


def brute_force(ciphertext: str) -> Iterator[tuple[str, int]]:
    """
    Brute force decrypt the ciphertext.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to brute force decrypt.

    Returns
    -------
    Iterator[tuple[str, int]]
        An iterator yielding all possible Caesar decryptions paired with their
        key. There are 26 possible decryptions.
    """
    for i in range(26):
        yield (decrypt(ciphertext, i), i)


def crack(
    ciphertext: str, *, score: Callable[[str], float] = monogram_score
) -> tuple[str, int]:
    """
    Crack the decryption of the ciphertext using the score function.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to crack.

    score : Callable[[str], float], default=chi_squared
        The score function which treats higher values as more likely to be a
        valid decryption.

    Returns
    -------
    tuple[str, int]
        The best scoring decryption paired with its key.

    Examples
    --------
    >>> crack("iq mdq pueoahqdqp rxqq mf azoq")
    'we are discovered flee at once'
    """
    top: tuple[str, int, float] = ("", -1, -float("inf"))

    for text, key in brute_force(ciphertext):
        sc = score(text)
        if sc > top[2]:
            top = (text, key, sc)

    return top[0], top[1]


if __name__ == "__main__":
    from random import randint

    plaintext = "we are discovered flee at once"
    key = randint(1, 25)

    print(f"key: {key}")

    enc = encrypt(plaintext, key, preserve_nonalpha=True)
    print(enc, "\n")

    dec = decrypt(enc, key)
    print(dec, "\n")

    cracked = crack(enc)
    print(cracked, "\n")

    assert dec == plaintext
    assert dec == cracked[0]
    assert key == cracked[1]
