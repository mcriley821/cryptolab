"""
https://en.wikipedia.org/wiki/Transposition_cipher
"""

from math import ceil


def encrypt(key: list[int], plaintext: str) -> str:
    """
    Encrypt the plaintext by columnar transposition keyed by key.

    Parameters
    ----------
    key : list[int]
        A list of indices to reorder the columns.

    plaintext : str
        The plaintext to encrypt.

    Returns
    -------
    str
        The resultant ciphertext.

    Examples
    --------
    >>> encrypt(sequence("zebras"), "we are discovered. flee at once.")
    'rcden irl edeft.aseeoeo. cw v ae'
    """

    paired = {j: plaintext[i :: len(key)] for i, j in enumerate(key)}
    return "".join(paired[i] for i in range(len(key)))


def decrypt(key: list[int], ciphertext: str) -> str:
    """
    Decrypt the given ciphertext by columnar transposition keyed by key.

    Parameters
    ----------
    key : list[int]
        A list of indices to reorder the columns.

    ciphertext : str
        The ciphertext to decrypt.

    Returns
    -------
    str
        The resultant plaintext.

    Examples
    --------
    >>> decrypt(sequence("zebras"), "rcden irl edeft.aseeoeo. cw v ae")
    'we are discovered. flee at once.'
    """

    rows = int(ceil(len(ciphertext) / len(key)))
    fill = rows * len(key)
    pads = len(key) - (fill - len(ciphertext))

    cols = [""] * len(key)
    paired = {j: i for i, j in enumerate(key)}

    it = iter(ciphertext)
    for i in range(len(key)):
        j = paired[i]
        if j >= pads:
            cols[j] = "".join(next(it) for _ in range(rows - 1)) + "."
        else:
            cols[j] = "".join(next(it) for _ in range(rows))

    return "".join(c[i] for i in range(rows) for c in cols)[: len(ciphertext)]


if __name__ == "__main__":
    from ..utils.sequencing import sequence

    keyword = "zebras"
    input = "wearediscoveredfleeatonce"

    key = sequence(keyword)
    print(f"keyword ({keyword}): {key}")

    enc = encrypt(key, input)
    print(enc)

    dec = decrypt(key, enc)
    print(dec)

    assert input == dec
