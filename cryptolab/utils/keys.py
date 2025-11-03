""" """

from string import ascii_lowercase, ascii_uppercase


def keyed_alphabet(key: str, *, alphabet: str | None = None) -> str:
    """
    Create a keyed alphabet from the given key.

    A keyed alphabet moves the key characters to the beginning of the alphabet.

    Parameters
    ----------
    key : str
        The key word to use. Characters not in the alphabet are omitted.

    alphabet : str | None,default=None
        The alphabet to use. If None, will use ascii_lowercase if
        key.islower(), otherwise ascii_uppercase

    Returns
    -------
    str
        The keyed alphabet.

    Examples
    --------
    >>> keyed_alphabet("CIPHER")
    'CIPHERABDFGJKLMNOQSTUVWXYZ'

    >>> keyed_alphabet("cipher")
    'cipherabdfgjklmnoqstuvwxyx'

    >>> keyed_alphabet("cipher", alphabet="cde")
    'ced'
    """
    if alphabet is None:
        alph = dict.fromkeys(ascii_lowercase if key.islower() else ascii_uppercase)
    else:
        alph = dict.fromkeys(alphabet)

    key_chars = dict.fromkeys(key)

    for k in key_chars:
        del alph[k]

    return "".join(key_chars) + "".join(alph)


def keyword(word: str, *, alphabet: str | None = None) -> list[int]:
    """
    Convert the word to a list of indices of the alphabet.

    Parameters
    ----------
    word : str
        The word to convert. Characters not in the alphabet are omitted.

    alphabet : str | None,default=None
        The alphabet to use when indexing. If None, will default to
        string.ascii_uppercase if word.isupper() is True, otherwise
        string.ascii_lowercase.

    Returns
    -------
    list[int]
        List of character indices in the alphabet.

    Examples
    --------
    >>> keyword("CIPHER")
    [2, 0, 0, 0, 4, 0]

    >>> keyword("cipher")
    []

    >>> keyword("cipher", alphabet="cde")
    [0, 2]
    """
    if alphabet is None:
        alphabet = ascii_uppercase if word.isupper() else ascii_lowercase

    return [alphabet.index(i) for i in word if i in alphabet]
