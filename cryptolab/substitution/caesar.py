"""
The Caesar cipher is a monoalphabetic substitution cipher that shifts each
letter of the plaintext by a given shift amount.

Generally, it is used only on alphabetical characters, case insensitively.
Valid shift values are in the range [0-26).

Also, spaces and punctuation tend to be preserved.
"""


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


if __name__ == "__main__":
    plaintext = "we are discovered flee at once"
    shift = 5

    enc = encrypt(plaintext, shift)
    print(enc, "\n")

    dec = decrypt(enc, shift)
    print(dec)

    assert dec == plaintext
