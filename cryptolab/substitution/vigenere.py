"""
https://en.wikipedia.org/wiki/Vigen%C3%A8re_cipher
"""

from itertools import cycle

from cryptolab.substitution import caesar


def encrypt(
    plaintext: str,
    key: list[int],
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using the Vigenère cipher.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    key : list[int]
        A list of shifts to use as the key.

    preserve_nonalpha : bool,default=False
        Whether to preserve nonalphabeticals in the ciphertext.

    Returns
    -------
    str
        The resultant ciphertext.
    """
    ret = ""

    for c, shift in zip(plaintext, cycle(key)):
        ret += caesar.encrypt(
            c,
            shift,
            preserve_nonalpha=preserve_nonalpha,
        )

    return ret


def decrypt(ciphertext: str, key: list[int]) -> str:
    """
    Decrypt the ciphertext using the Vigenère cipher.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    key : list[int]
        A list of shifts to use as the key.

    Returns
    -------
    str
        The resultant plaintext.
    """
    ret = ""

    for c, shift in zip(ciphertext, cycle(key)):
        ret += caesar.decrypt(c, shift)

    return ret


if __name__ == "__main__":
    from random import randint, shuffle
    from string import ascii_uppercase

    from cryptolab.utils.keys import keyword

    plaintext = "ATTACK THE EAST WALL OF THE CASTLE AT DAWN"
    key = list(ascii_uppercase)
    shuffle(key)
    key = keyword("".join(key)[: randint(5, 11)])
    print(plaintext)
    print(key, "\n")

    enc = encrypt(plaintext, key, preserve_nonalpha=True)
    print(enc, "\n")

    dec = decrypt(enc, key)
    print(dec, "\n")

    assert plaintext == dec
