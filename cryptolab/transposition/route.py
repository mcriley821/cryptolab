"""
https://en.wikipedia.org/wiki/Transposition_cipher
"""

from collections.abc import Callable, Iterator

Route = Callable[[str], Iterator[int]]


def encrypt(plaintext: str, route: Route, *, pad: str = "\0") -> str:
    """
    Encrypt the plaintext with the given Route.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    route : Route
        The route algorithm to use.

    Returns
    -------
    str
        The resultant ciphertext.
    """
    p = plaintext
    return "".join(p[i] if i < len(p) else pad for i in route(p))


def decrypt(ciphertext: str, route: Route, *, pad: str = "\0") -> str:
    """
    Decrypt the ciphertext with the given Route.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    route : Route
        The route algorithm to use.

    Returns
    -------
    str
        The resultant plaintext.
    """
    c = ciphertext
    ret = ["\0"] * len(c)
    for i, j in zip(c, route(c)):
        ret[j] = i
    return "".join(ret).strip(pad)


if __name__ == "__main__":
    from .routes.spiral import spiral_ccw_in

    text = "Defend the east wall of the castle"

    enc = encrypt(text, spiral_ccw_in)
    print(enc, "\n")

    dec = decrypt(text, spiral_ccw_in)
    print(dec)
