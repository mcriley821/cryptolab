"""
https://en.wikipedia.org/wiki/Affine_cipher
"""

from typing import Callable, Iterator

from cryptolab.scoring.ngram import monogram_score


def encrypt(
    plaintext: str,
    key: tuple[int, int],
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using the affine cipher.

    Each letter is encrypted with the function `(a*x + b) % 26`.
    To work properly, it is important that `a` is coprime to 26.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    key : tuple[int, int]
        A tuple representing the (a, b) coefficients.

    preserve_nonalpha : bool,default=False
        Whether to preserve non-alphabetical in the ciphertext.

    Raises
    ------
    ValueError
        If the `a` coefficient is not coprime to 26.

    Returns
    -------
    str
        The resultant ciphertext.
    """

    a, b = key
    if a not in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        raise ValueError("coefficient `a` must be coprime to 26")

    ret = ""
    for c in plaintext:
        if not c.isalpha():
            if preserve_nonalpha:
                ret += c
            continue

        offset = ord("A") if c.isupper() else ord("a")

        i = ord(c) - offset
        new_i = (i * a + b) % 26
        ret += chr(new_i + offset)

    return ret


def decrypt(ciphertext: str, key: tuple[int, int]) -> str:
    """
    Decrypt the ciphertext using the affine cipher.

    Each letter is decrypted with the function `(a ** (-1)) * (x - b) % 26`
    where `a ** (-1)` is the modular multiplicative inverse.
    https://en.wikipedia.org/wiki/Modular_multiplicative_inverse

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    key : tuple[int, int]
        A tuple representing the (a, b) coefficients.

    Raises
    ------
    ValueError
        If the `a` coefficient is not coprime to 26.

    Returns
    -------
    str
        The resultant plaintext.
    """
    a, b = key
    if a not in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        raise ValueError("coefficient `a` must be coprime to 26")

    ret = ""
    a_inv = pow(a, -1, 26)

    for c in ciphertext:
        if not c.isalpha():
            ret += c
            continue

        offset = ord("A") if c.isupper() else ord("a")
        i = ord(c) - offset
        new_i = (a_inv * (i - b)) % 26
        ret += chr(new_i + offset)

    return ret


def brute_force(ciphertext: str) -> Iterator[tuple[str, tuple[int, int]]]:
    """
    Brute force decrypt the ciphertext.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to brute force decrypt.

    Returns
    -------
    tuple[str, tuple[int, int]]
        An iterator yielding all possible Affine decryptions paired with their
        key. There are 312 possible decryptions.
    """

    for a in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        for b in range(26):
            key = (a, b)
            yield (decrypt(ciphertext, key), key)


def crack(
    ciphertext: str, *, score: Callable[[str], float] = monogram_score
) -> tuple[str, tuple[int, int]]:
    """
    Crack the decryption of the ciphertext using the score function.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to crack.

    score : Callable[[str], float], default=monogram_score
        The score function which treats higher values as more likely to be a
        valid decryption.

    Returns
    -------
    tuple[str, tuple[int, int]]
        The best scoring decryption paired with its key.
    """
    top: tuple[str, tuple[int, int], float] = ("", (-1, -1), -float("inf"))

    for text, key in brute_force(ciphertext):
        sc = score(text)
        if sc > top[2]:
            top = (text, key, sc)

    return top[0], top[1]


if __name__ == "__main__":
    from random import choice, randint

    plaintext = "Defend the east wall of the castle."

    a = choice((1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25))
    b = randint(1, 25)

    key = (a, b)
    print(f"key: {key}")

    enc = encrypt(plaintext, key, preserve_nonalpha=True)
    print(enc, "\n")

    dec = decrypt(enc, key)
    print(dec, "\n")

    assert plaintext == dec

    cracked = crack(enc)
    print(cracked, "\n")

    assert plaintext == cracked[0]
    assert key == cracked[1]
