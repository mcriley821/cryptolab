"""
https://en.wikipedia.org/wiki/Affine_cipher
"""

import sys
from argparse import ArgumentParser, RawDescriptionHelpFormatter
from dataclasses import dataclass
from textwrap import dedent
from typing import Callable, Iterator

from cryptolab.scoring.ngram import monogram_score


@dataclass
class Arguments:
    """
    Arguments needed to execute the affine cipher algorithm.

    Parameters
    ----------
    input : str | None
        Path to an input file to read the text from. If None, reads from stdin.

    key : tuple[int, int]
        The (a, b) coefficients for the affine algorithm.

    decrypt : bool
        Whether to decrypt the text.

    preserve : bool
        Whether to preserve non-alphabeticals in the output.
    """

    input: str | None
    key: tuple[int, int]
    decrypt: bool
    preserve: bool


def main() -> int:
    """
    The main function handles parsing the command line arguments and executing
    the affine cipher with those arguments.

    Returns
    -------
    int
        Return code. 1 if an error occured; 0 on success.
    """
    parser = ArgumentParser()
    configure_parser(parser)
    args = Arguments(**vars(parser.parse_args()))
    return execute(args)


def configure_parser(parser: ArgumentParser):
    """
    Configure the parser for the affine cipher. The parser will then produce
    a namespace suitable for conversion to affine.Arguments.
    """
    parser.formatter_class = RawDescriptionHelpFormatter
    parser.description = dedent("""\
    The affine cipher is a monoalphabetic substitution cipher where each letter
    in the alphabet is encrypted using a modular affine equation:

    (a * x + b) % 26

    The equation must be reversible to decrypt, and thus only a subset of
    values are suitable foe the "a" coefficient.

    See https://en.wikipedia.org/wiki/Affine_cipher for more info.
    """)
    parser.add_argument(
        "key",
        type=int,
        nargs=2,
        metavar=("a", "b"),
        help="the key coefficients such that (a*x + b) %% 26",
    )
    parser.add_argument(
        "input",
        nargs="?",
        default=None,
        help="the text file to encrypt or decrypt [default: stdin]",
    )
    parser.add_argument(
        "-d",
        "--decrypt",
        action="store_true",
        default=False,
        help="decrypt the text [default: %(default)s]",
    )
    parser.add_argument(
        "-p",
        "--preserve",
        action="store_true",
        default=False,
        help="preserve non-alphabeticals in the output [default: %(default)s]",
    )


def execute(args: Arguments) -> int:
    """
    Execute the affine cipher algorithm using the given args.

    Parameters
    ----------
    args : Arguments
        The arguments to the affine cipher algorithm.

    Returns
    -------
    int
        Return code. 1 if an error occurred; 0 on success.
    """
    try:
        if args.input is not None:
            with open(args.input, "r") as f:
                text = f.read()
        else:
            text = sys.stdin.read()

        if args.decrypt:
            print(decrypt(text, args.key, preserve_nonalpha=args.preserve))
        else:
            print(encrypt(text, args.key, preserve_nonalpha=args.preserve))
    except Exception as e:
        print(e)
        return 1

    return 0


def encrypt(
    plaintext: str,
    key: tuple[int, int],
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Encrypt the plaintext using the affine cipher.

    Each letter is encrypted with the function `(a*x + b) % 26`.
    To work properly, it is important that `a` is coprime to 26.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    key : tuple[int, int]
        A tuple representing the (a, b) coefficients.

    preserve_nonalpha : bool,default=False
        Whether to preserve non-alphabeticals in the ciphertext.

    Raises
    ------
    ValueError
        If the `a` coefficient is not coprime to 26.

    Returns
    -------
    str
        The resultant ciphertext.
    """

    a, b = key
    if a not in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        raise ValueError("coefficient `a` must be coprime to 26")

    ret = ""
    for c in plaintext:
        if not c.isalpha():
            if preserve_nonalpha:
                ret += c
            continue

        offset = ord("A") if c.isupper() else ord("a")

        i = ord(c) - offset
        new_i = (i * a + b) % 26
        ret += chr(new_i + offset)

    return ret


def decrypt(
    ciphertext: str,
    key: tuple[int, int],
    *,
    preserve_nonalpha: bool = False,
) -> str:
    """
    Decrypt the ciphertext using the affine cipher.

    Each letter is decrypted with the function `(a ** (-1)) * (x - b) % 26`
    where `a ** (-1)` is the modular multiplicative inverse.
    https://en.wikipedia.org/wiki/Modular_multiplicative_inverse

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    key : tuple[int, int]
        A tuple representing the (a, b) coefficients.

    preserve_nonalpha : bool,default=False
        Whether to preserve nonalphabetics in the output.

    Raises
    ------
    ValueError
        If the `a` coefficient is not coprime to 26.

    Returns
    -------
    str
        The resultant plaintext.
    """
    a, b = key
    if a not in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        msg = "coefficient `a` must be coprime to 26"
        raise ValueError(msg)

    ret = ""
    a_inv = pow(a, -1, 26)

    for c in ciphertext:
        if not c.isalpha():
            if preserve_nonalpha:
                ret += c
            continue

        offset = ord("A") if c.isupper() else ord("a")
        i = ord(c) - offset
        new_i = (a_inv * (i - b)) % 26
        ret += chr(new_i + offset)

    return ret


def brute_force(ciphertext: str) -> Iterator[tuple[str, tuple[int, int]]]:
    """
    Brute force decrypt the ciphertext.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to brute force decrypt.

    Returns
    -------
    tuple[str, tuple[int, int]]
        An iterator yielding all possible Affine decryptions paired with their
        key. There are 312 possible decryptions.
    """

    for a in (1, 3, 5, 7, 9, 11, 15, 17, 19, 21, 23, 25):
        for b in range(26):
            key = (a, b)
            yield (decrypt(ciphertext, key), key)


def crack(
    ciphertext: str, *, score: Callable[[str], float] = monogram_score
) -> tuple[str, tuple[int, int]]:
    """
    Crack the decryption of the ciphertext using the score function.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to crack.

    score : Callable[[str], float], default=monogram_score
        The score function which treats higher values as more likely to be a
        valid decryption.

    Returns
    -------
    tuple[str, tuple[int, int]]
        The best scoring decryption paired with its key.
    """
    top: tuple[str, tuple[int, int], float] = ("", (-1, -1), -float("inf"))

    for text, key in brute_force(ciphertext):
        sc = score(text)
        if sc > top[2]:
            top = (text, key, sc)

    return top[0], top[1]


if __name__ == "__main__":
    sys.exit(main())
