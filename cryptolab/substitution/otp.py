"""
https://en.wikipedia.org/wiki/One-time_pad
"""

from cryptolab.substitution import vigenere


def encrypt(
    plaintext: str,
    key: list[int],
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using the given key as a one-time-pad.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    key : list[int]
        The one-time-pad key. It should be at least as long as the plaintext.

    preserve_nonalpha : bool,default=False
        Whether to preserve nonalphabeticals in the ciphertext.

    Raises
    ------
    ValueError
        If the key is too short to encrypt the plaintext.

    Returns
    -------
    str
        The resultant ciphertext.
    """
    if len(key) < (s := sum(1 for i in plaintext if i.isalpha())):
        msg = f"Key stream is too short: {len(key)} < {s}"
        raise ValueError(msg)
    return vigenere.encrypt(plaintext, key, preserve_nonalpha=preserve_nonalpha)


def decrypt(
    ciphertext: str,
    key: list[int],
) -> str:
    """
    Decrypt the ciphertext using the given key as a one-time-pad.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    key : list[int]
        The one-time-pad key. It should be at least as long as the ciphertext.

    Raises
    ------
    ValueError
        If the key is too short to decrypt the ciphertext.

    Returns
    -------
    str
        The resultant plaintext.
    """
    if len(key) < len(ciphertext):
        msg = f"Key stream is too short: {len(key)} < {len(ciphertext)}"
        raise ValueError(msg)
    return vigenere.decrypt(ciphertext, key)


if __name__ == "__main__":
    from cryptolab.utils.keys import keyword

    key = keyword("RANDOMKEYSTREAMS")
    plaintext = "ManageOneTimePad"

    enc = encrypt(plaintext, key)
    print(enc, "\n")

    dec = decrypt(enc, key)
    print(dec, "\n")

    assert plaintext == dec
