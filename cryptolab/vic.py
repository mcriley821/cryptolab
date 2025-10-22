"""
https://en.wikipedia.org/wiki/VIC_cipher
"""

from datetime import date
from operator import add, sub
from typing import Callable

from .utils.sequencing import sequence
from .transposition.disrupted import (
    encrypt as dis_encrypt,
    decrypt as dis_decrypt,
    VIC,
)
from .transposition.columnar import (
    encrypt as col_encrypt,
    decrypt as col_decrypt,
)
from .substitution.straddling_checkerboard import (
    Board,
    encrypt as sad_encrypt,
    decrypt as sad_decrypt,
)


def _digit_op(x: str, y: str, op: Callable[[int, int], int]) -> str:
    """
    Perform the given op element-wise on the given numeric strings.
    The result of calling `op` is reduced modulo 10.

    Parameters
    ----------
    x : str
        Left operand numeric string

    y : str
        Right operand numeric string

    op : Callable[[int, int], int]
        Called on int-coerced elements of x and y.

    Returns
    -------
    str
        The resultant numeric string.

    Examples
    --------
    >>> _digit_op("123", "789", add)
    '802'
    """

    return "".join(str(op(int(a), int(b)) % 10) for a, b in zip(x, y))


def _seq_to_str(line: str) -> str:
    """
    Sequence the given numeric string.

    Parameters
    ----------
    line : str
        Numeric string to sequence

    Returns
    -------
    str
        The resultant numeric string.

    Examples
    --------
    >>> _seq_to_str("6826372929")
    '5816472930'
    """

    return "".join(str((j + 1) % 10) for j in sequence(line, zero_high=True))


def _chain_add(num: str, final_len: int) -> str:
    """
    Perform chain addition on the numeric string, appending the result until
    the desired length is reached. Addition is performed modulo 10.

    Parameters
    ----------
    num : str
        The numeric string to chain add.

    final_len : int
        The desired length.

    Returns
    -------
    str
        The resultant numeric string

    Examples
    --------
    >>> _chain_add("12345", 10)
    '1237835051'
    """

    i = 0
    while len(num) != final_len:
        x, y = int(num[i]), int(num[i + 1])
        num += str((x + y) % 10)
        i += 1
    return num


def key_gen(
    personal_number: int, date: date, phrase: str, key_group: str
) -> tuple[list[int], list[int], list[int]]:
    """
    Generate VIC columnar transposition key, disrupted transposition key, and
    straddling checkerboard key following the key generation algorithm as
    defined by https://en.wikipedia.org/wiki/VIC_cipher

    Parameters
    ----------
    personal_number : int
        A one or two digit personal number that helps determine the length of
        the transposition keys.

    date : date
        A key date.

    phrase : str
        A key phrase.

    key_group : str
        A 5-digit numeric string that is generally random.

    Returns
    -------
    tuple[list[int], list[int], list[int]]
        A 3-tuple containing:
            * columnar transposition key
            * disrupted transposition key
            * straddling checkerboard key
        for use with VIC encryption or decryption.
    """

    # Line A: key_group
    line_a = key_group

    # Line B: date truncated to 5 digits
    str_date = f"{date.day}{date.month}{date.year:04d}"
    line_b = str_date[:5]

    # Line C: digit by digit, A - B
    line_c = _digit_op(line_a, line_b, sub)

    # Line D: Phrase, truncated to 20 chars
    alpha_phrase = "".join(i.upper() for i in phrase if i.isalpha())
    line_d = (alpha_phrase[:10], alpha_phrase[10:20])

    # Line E: Sequenced Line D
    line_e = (_seq_to_str(line_d[0]), _seq_to_str(line_d[1]))

    # Line F: Line C chain addition, and 1234567890
    line_f = (_chain_add(line_c, 10), "1234567890")

    # Line G: digit by digit, E[0] + F[0]
    line_g = _digit_op(line_e[0], line_f[0], add)

    # Line H: encode Line G with Line E[1] & F[1]
    trans = str.maketrans(line_f[1], line_e[1])  # replace F with E
    line_h = line_g.translate(trans)

    line_j = _seq_to_str(line_h)

    block = _chain_add(line_h, 60)[10:]  # trim line_h from beginning

    line_p = block[-10:]
    b, a = list(dict.fromkeys(line_p[::-1]))[:2]  # last two unique digits

    columns = {(int(j) - 1) % 10: block[i::10] for i, j in enumerate(line_j)}
    concat = "".join(columns[i] for i in range(len(columns)))

    i = int(a) + personal_number
    line_q = concat[:i]
    line_r = concat[i : i + int(b) + personal_number]
    line_s = _seq_to_str(line_p)

    return (
        sequence(line_q, zero_high=True),
        sequence(line_r, zero_high=True),
        sequence(line_s),
    )


def extract_keygroup(date: date, ciphertext: str) -> tuple[str, str]:
    """
    Extract the 5-digit numeric keygroup from the ciphertext.

    Parameters
    ----------
    date : date
        The key date to determine the keygroup index.

    ciphertext : str
        The ciphertext from which to extract the keygroup.

    Returns
    -------
    tuple[str, str]
        A 2-tuple containing:
            * the extracted keygroup
            * the ciphertext with the keygroup removed
    """

    date_str = f"{date.day}{date.month}{date.year}"
    index = int(date_str[5])
    groups = [ciphertext[i : i + 5] for i in range(0, len(ciphertext), 5)]
    keygroup = groups.pop(max(0, len(groups) - index))
    return keygroup, "".join(groups)


def inject_keygroup(ciphertext: str, date: date, keygroup: str) -> str:
    """
    Inject the keygroup into the ciphertext.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to inject the keygroup into.

    date : date
        The key date to determine the keygroup index.

    keygroup : str
        The 5-digit numeric keygroup to inject.

    Returns
    -------
    str
        The ciphertext with the keygroup injected.
    """

    date_str = f"{date.day}{date.month}{date.year}"
    index = int(date_str[5])
    groups = [ciphertext[i : i + 5] for i in range(0, len(ciphertext), 5)]
    groups.insert(max(0, len(groups) - index + 1), keygroup)
    return "".join(groups)


def encrypt(
    plaintext: str,
    board: Board,
    trans_key1: list[int],
    trans_key2: list[int],
    *,
    null_fill: str = "9",
) -> str:
    """
    Encrypt the plaintext using the VIC algorithm.

    Parameters
    ----------
    plaintext : str
        The plaintext to encrypt.

    board : Board
        The straddling checkerboard.

    trans_key1 : list[int]
        The columnar transposition key.

    trans_key2 : list[int]
        The disrupted transposition key.

    null_fill : str, default="9"
        A single digit string to fill the ciphertext to a multiple of 5 before
        transposition.

    Returns
    -------
    str
        The resultant ciphertext.
    """

    out = sad_encrypt(plaintext, board, digit_escape="triple")
    out += null_fill * (-len(out) % 5)
    out = col_encrypt(trans_key1, out)
    out = dis_encrypt(trans_key2, out, VIC)
    return out


def decrypt(
    ciphertext: str, board: Board, trans_key1: list[int], trans_key2: list[int]
) -> str:
    """
    Decrypt the ciphertext using the VIC algorithm.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    board : Board
        The straddling checkerboard.

    trans_key1 : list[int]
        The columnar transposition key.

    trans_key2 : list[int]
        The disrupted transposition key.

    Returns
    -------
    str
        The resultant plaintext.
    """
    out = dis_decrypt(trans_key2, ciphertext, VIC)
    out = col_decrypt(trans_key1, out)
    out = sad_decrypt(out, board, digit_escape="triple")
    return out


if __name__ == "__main__":
    # https://everything2.com/user/raincomplex/writeups/VIC+cipher
    text = "IVES INVALIDATED . REPORT IMMEDIATELY TO SAFE HOUSE . AWAIT EXTRACTION INSTRUCTIONS WITHIN WEEK .. ASSIGNED OBJECT"

    board = Board(
        ("3", "4"),
        key=[2, 9, 6, 0, 5, 8, 1, 7, 3, 4],
        keyword="ASINTOERBDGJLPUWY.CFHKMQVXZ/",
    )
    trans_key1 = [8, 12, 0, 1, 9, 14, 2, 11, 5, 16, 6, 7, 15, 10, 13, 17, 3, 4, 18]
    trans_key2 = [15, 3, 17, 11, 16, 4, 12, 13, 0, 6, 14, 18, 10, 1, 5, 7, 8, 2, 9, 19]

    enc = encrypt(text, board, trans_key1, trans_key2)
    spaced = " ".join(enc[i : i + 5] for i in range(0, len(enc), 5))
    print(spaced, "\n")

    assert (
        spaced
        == "43983 65293 32548 69254 35932 24039 19375 91234 12656 67402 16873 56133 55075 33511 36926 06608 14241 84749 14863 46177 11450 65326 11433 30085 37495 29149"
    )

    dec = decrypt(enc, board, trans_key1, trans_key2)
    print(dec)

    assert dec == text.replace(" ", "")  # spaces are skipped
