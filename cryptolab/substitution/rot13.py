"""
https://en.wikipedia.org/wiki/ROT13
"""

from cryptolab.substitution import caesar


def encrypt(
    plaintext: str,
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using ROT13.

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

    Examples
    --------
    >>> encrypt("Defend the east wall of the castle.")
    'Qrsraqgurrnfgjnyybsgurpnfgyr.'

    >>> encrypt("Defend the east wall of the castle.", preserve_nonalpha=True)
    'Qrsraq gur rnfg jnyy bs gur pnfgyr.'
    """
    return caesar.encrypt(
        plaintext,
        13,
        preserve_nonalpha=preserve_nonalpha,
    )


def decrypt(ciphertext: str) -> str:
    """
    Decrypt the ciphertext using ROT13.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    Returns
    -------
    str
        The decrypted ciphertext.

    Examples
    --------
    >>> decrypt("Qrsraq gur rnfg jnyy bs gur pnfgyr")
    'Defend the east wall of the castle'
    """
    return caesar.decrypt(ciphertext, 13)


if __name__ == "__main__":
    plaintext = "Defend the east wall of the castle."

    enc = encrypt(plaintext, preserve_nonalpha=True)
    print(enc, "\n")

    dec = decrypt(enc)
    print(dec)

    assert plaintext == dec
