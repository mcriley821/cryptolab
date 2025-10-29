""" """

from string import ascii_uppercase


def _make_alphabet(key: str) -> str:
    alphabet = dict.fromkeys(ascii_uppercase)
    key_chars = dict.fromkeys(key.upper())
    for k in key_chars:
        del alphabet[k]
    return "".join(key_chars) + "".join(alphabet)


def encrypt(
    plaintext: str,
    key: str,
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using a keyed alphabet.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    key : str
        The key word to use in the alphabet construction.

    preserve_nonalpha : bool,default=False
        Whether to preserve non alphabeticals in the ciphertext.

    Raises
    ------
    ValueError
        If the key contains non-alphabetical characters.

    Returns
    -------
    str
        The resultant ciphertext.
    """
    if not key.isalpha():
        raise ValueError("key must be alphabetical")

    alphabet = _make_alphabet(key)
    trans = str.maketrans(ascii_uppercase, alphabet)

    ret = ""
    for c in plaintext:
        if not c.isalpha():
            if preserve_nonalpha:
                ret += c
            continue

        if c.islower():
            ret += c.upper().translate(trans).lower()
        else:
            ret += c.translate(trans)

    return ret


def decrypt(ciphertext: str, key: str) -> str:
    """
    Decrypt the ciphertext using a keyed alphabet.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    key : str
        The key word to use in the alphabet construction.

    Raises
    ------
    ValueError
        If the key contains non-alphabetical characters.

    Returns
    -------
    str
        The resultant plaintext.
    """
    if not key.isalpha():
        raise ValueError("key must be alphabetical")

    alphabet = _make_alphabet(key)
    trans = str.maketrans(alphabet, ascii_uppercase)

    ret = ""
    for c in ciphertext:
        if not c.isalpha():
            ret += c
            continue

        if c.islower():
            ret += c.upper().translate(trans).lower()
        else:
            ret += c.translate(trans)

    return ret


if __name__ == "__main__":
    plaintext = "flee at once. we are discovered!"
    key = "grandmother"

    enc = encrypt(plaintext, key, preserve_nonalpha=True)
    print(enc, "\n")

    dec = decrypt(enc, key)
    print(dec, "\n")
