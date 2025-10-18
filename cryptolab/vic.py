"""
https://en.wikipedia.org/wiki/VIC_cipher
"""

from datetime import date
from operator import add, sub
from .transposition.sequencing import sequence
from .transposition.disrupted import (
    encrypt as dis_encrypt,
    decrypt as dis_decrypt,
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


def _digit_op(x: str, y: str, op) -> str:
    return "".join(str(op(int(a), int(b)) % 10) for a, b in zip(x, y))


def _seq_to_str(line: str) -> str:
    result: list[str] = [""] * len(line)
    for i, j in enumerate(sequence(line, zero_high=True)):
        result[i] = str((j + 1) % 10)
    return "".join(result)


def _chain_add(num: str, final_len: int) -> str:
    i = 0
    while len(num) != final_len:
        x, y = int(num[i]), int(num[i + 1])
        num += str((x + y) % 10)
        i += 1
    return num


def key_gen(
    personal_number: int, date: date, phrase: str, key_group: str
) -> tuple[list[int], list[int], list[int]]:
    # Line A: key_group
    line_a = key_group

    # Line B: date truncated to 5 digits
    str_date = f"{date.day}{date.month}{date.year}"
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
    date_str = f"{date.day}{date.month}{date.year}"
    index = int(date_str[5])
    groups = [ciphertext[i : i + 5] for i in range(0, len(ciphertext), 5)]
    keygroup = groups.pop(max(0, len(groups) - index))
    return keygroup, "".join(groups)


def inject_keygroup(ciphertext: str, date: date, keygroup: str) -> str:
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
):
    out = sad_encrypt(plaintext, board, digit_escape="triple")
    out += null_fill * (-len(out) % 5)
    out = col_encrypt(trans_key1, out)
    out = dis_encrypt(trans_key2, out)
    return out


def decrypt(
    ciphertext: str, board: Board, trans_key1: list[int], trans_key2: list[int]
):
    out = dis_decrypt(trans_key2, ciphertext)
    out = col_decrypt(trans_key1, out)
    out = sad_decrypt(out, board, digit_escape="triple")
    return out


if __name__ == "__main__":
    plaintext = "We are pleased to hear of your success in establishing your false identity You will be sent some money to cover expenses within a month".upper()

    keygroup = "77651"
    phrase = "I DREAM OF JEANNIE WITH T"

    # swap month & day for the example: http://www.quadibloc.com/crypto/pp1324.htm
    date_ = date(1776, 4, 7)
    pn = 8

    trans_key1, trans_key2, board_key = key_gen(pn, date_, phrase, keygroup)
    board = Board(("0", "8"), key=board_key, keyword="ATONESIR")

    enc = encrypt(plaintext, board, trans_key1, trans_key2)
    enc = inject_keygroup(enc, date_, keygroup)
    print([enc[i : i + 5] for i in range(0, len(enc), 5)], "\n")

    keygroup, ciphertext = extract_keygroup(date_, enc)
    dec = decrypt(ciphertext, board, trans_key1, trans_key2)
    print(dec)
