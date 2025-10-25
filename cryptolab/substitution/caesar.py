"""
https://en.wikipedia.org/wiki/Caesar_cipher
"""

from ..utils.analysis import chi_squared

from typing import Callable, Iterator


def encrypt(
    text: str,
    shift: int,
    preserve_space: bool = True,
    preserve_punct: bool = True,
) -> str:
    """
    Encrypt plaintext using the Caesar cipher.

    Parameters
    ----------
    text : str
        The message to be enciphered.

    shift : int
        The amount to shift each letter.

    preserve_space : bool, default=True
        Whether to preserve whitespace in the ciphertext.

    preserve_punct : bool, default=True
        Whether to preserve punctuation in the ciphertext.

    Returns
    -------
    str
        The resultant ciphertext.

    Examples
    --------
    >>> caesar.encrypt("Hello, world!", 3)
    'Khoor, zruog!'

    >>> caesar.encrypt("Hello, world!", 3, False, False)
    'Khoorzruog'
    """
    shift %= 26

    ret = ""
    for char in text:
        if char.isspace() and preserve_space:
            ret += char
            continue

        if not char.isalpha():
            if preserve_punct:
                ret += char
            continue

        offset = ord("A") if char.isupper() else ord("a")

        index = ord(char) - offset  # subtract offset to get a zero-based index
        shifted = (index + shift) % 26  # shift, looping to 'A' if necessary
        ret += chr(shifted + offset)  # add back offset for ascii index

    return ret


def decrypt(
    ciphertext: str,
    shift: int,
) -> str:
    """
    Decrypt ciphertext using the Caesar cipher.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decipher.

    shift : int
        The amount to shift each letter.

    Returns
    -------
    str
        The resultant plaintext.

    Examples
    --------
    >>> caesar.decrypt("Khoor, zruog!", 3)
    'Hello, world!'
    """

    ret = ""
    for char in ciphertext:
        if not char.isalpha():
            ret += char
            continue

        offset = ord("A") if char.isupper() else ord("a")
        index = ord(char) - offset  # subtract offset to get a zero-based index
        shifted = (index - shift) % 26  # shift, looping to 'Z' if necessary
        ret += chr(shifted + offset)  # add back offset for ascii index

    return ret


def brute_force(ciphertext: str) -> Iterator[str]:
    """
    Brute force decrypt the ciphertext.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to brute force decrypt.

    Returns
    -------
    Iterator[str]
        An iterator yielding all possible Caesar decryptions.
    """
    for i in range(26):
        yield decrypt(ciphertext, i)


def crack(ciphertext: str, *, score: Callable[[str], float] = chi_squared) -> str:
    """
    Crack the decryption of the ciphertext using the score function.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to crack.

    score : Callable[[str], float], default=chi_squared
        The score function which treats lower values as more likely to be a
        valid decryption.

    Returns
    -------
    str
        The lowest scoring decryption.

    Examples
    --------
    >>> crack("iq mdq pueoahqdqp rxqq mf azoq")
    'we are discovered flee at once'

    Notes
    -----
    TODO: replace the score function type with one from a scoring module
    """
    top: tuple[str, float] = ("", float("inf"))

    for text in brute_force(ciphertext):
        if (sc := score(text)) < top[1]:
            top = (text, sc)

    return top[0]


if __name__ == "__main__":
    from random import randint

    plaintext = "we are discovered flee at once"
    shift = randint(1, 25)

    enc = encrypt(plaintext, shift)
    print(enc, "\n")

    dec = decrypt(enc, shift)
    print(dec, "\n")

    cracked = crack(enc)
    print(cracked, "\n")

    for i in brute_force(enc):
        print(i)
    print()

    assert dec == plaintext
    assert dec == cracked
