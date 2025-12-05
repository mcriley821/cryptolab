"""
https://en.wikipedia.org/wiki/Atbash
"""

from cryptolab.substitution import affine


def encrypt(
    plaintext: str,
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using Atbash.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    preserve_nonalpha : bool,default=False
        Whether to preserve non-alphabeticals in the ciphertext.

    Returns
    -------
    str
        The resultant ciphertext.
    """

    return affine.encrypt(
        plaintext,
        (25, 25),
        preserve_nonalpha=preserve_nonalpha,
    )


def decrypt(ciphertext: str) -> str:
    """
    Decrypt the ciphertext using Atbash.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    Returns
    -------
    str
        The resultant plaintext.
    """

    return affine.decrypt(ciphertext, (25, 25))


if __name__ == "__main__":
    plaintext = "Defend the east wall of the castle."

    enc = encrypt(plaintext, preserve_nonalpha=True)
    print(enc, "\n")

    dec = decrypt(enc)
    print(dec)

    assert plaintext == dec
