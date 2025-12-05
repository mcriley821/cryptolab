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
    rout = list(route(c))
    ret = [pad] * len(rout)
    for i, j in zip(c, rout):
        ret[j] = i
    return "".join(ret).strip(pad)


if __name__ == "__main__":
    from cryptolab.transposition.routes import spirals

    text = "Defend the east wall of the castle"
    print(text, "\n")

    # D e f e n d
    #   t h e   e
    # a s t   w a
    # l l   o f
    # t h e   c a
    # s t l e

    enc = encrypt(text, spirals.ccw_in)
    print(enc, "\n")

    assert enc == "D altstle\0\0a aednefetslhe cfw eht o "

    dec = decrypt(enc, spirals.ccw_in)
    print(dec)

    assert dec == text
