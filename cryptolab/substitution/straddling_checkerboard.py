class Board:
    def __init__(
        self,
        digits: tuple[str, str],
        key: list[int] | None = None,
        *,
        keyword: str = "",
    ):
        if key is None:
            self._key = [i for i in range(10)]
        elif len(key) != 10:
            raise ValueError("expected a key of length 10")
        else:
            self._key = key

        self._digits = digits

        alphabet_set = dict.fromkeys("ABCDEFGHIJKLMNOPQRSTUVWXYZ./")
        key_chars = dict.fromkeys(keyword)

        if keyword:
            for k in key_chars:
                del alphabet_set[k]

        alphabet = "".join(key_chars) + "".join(alphabet_set)
        assert len(alphabet) == 28
        it = iter(alphabet)

        row1: list[str | None] = [None] * 10
        for i, j in enumerate(self._key):
            if str(j) not in digits:
                row1[i] = next(it)

        self._board: dict[str | None, list[str | None]] = {
            None: row1,
            digits[0]: [next(it) for _ in range(10)],
            digits[1]: [next(it) for _ in range(10)],
        }

    def __getitem__(self, key: str) -> str:
        if len(key) == 2:
            row = self._board[key[0]]
        else:
            row = self._board[None]

        i = self._key.index(int(key[-1]))
        d = row[i]

        if d is None:
            raise ValueError("invalid board for decryption")

        return d

    def invert(self) -> dict[str, str]:
        out: dict[str, str] = dict()
        for k, row in self._board.items():
            c = "" if k is None else k
            for i, j in enumerate(self._key):
                if (s := row[i]) is not None:
                    out[s] = c + str(j)
        return out

    @property
    def digits(self):
        return self._digits


def encrypt(plaintext: str, board: Board, *, digit_escape: str = "single") -> str:
    inv_board = board.invert()

    out = ""

    i = 0
    while i < len(plaintext):
        c = plaintext[i]
        if c.isnumeric():
            if digit_escape == "single":
                out += inv_board["/"]
                out += c
            elif digit_escape == "double" or digit_escape == "triple":
                s = inv_board["/"]
                if len(s) != 2:
                    raise ValueError("cannot digit escape with given board")
                out += s
                mul = 2 if digit_escape == "double" else 3
                while (c := plaintext[i]).isnumeric() and i < len(plaintext):
                    out += str(c) * mul
                    i += 1
                out += s
                i -= 1  # undo since plaintext[i] is not numeric
            else:
                raise ValueError(f"unsupported digit escape: {digit_escape}")
        elif c.isalpha() or c == ".":
            out += inv_board[c.upper()]
        i += 1

    return out


def decrypt(ciphertext: str, board: Board, *, digit_escape: str = "single") -> str:
    out = ""

    i = 0
    while i < len(ciphertext):
        c = ciphertext[i]
        if c in board.digits:
            i += 1
            c += ciphertext[i]

        d = board[c]

        if d == "/":
            i += 1
            if digit_escape == "single":
                out += ciphertext[i]
                i += 1
            elif digit_escape == "double" or digit_escape == "triple":
                span = 2 if digit_escape == "double" else 3
                while ciphertext[i] * span == ciphertext[i : i + span]:
                    out += ciphertext[i]
                    i += span
                if ciphertext[i : i + 2] != c:
                    raise ValueError("unterminated digit escape")
                i += 2
            else:
                raise ValueError(f"unsupported digit escape: {digit_escape}")
        else:
            out += d
            i += 1

    return out


if __name__ == "__main__":
    board = Board(("1", "4"), keyword="FUBCDORA.LETHINGKYMVPS.JQZXW")

    plaintext = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"

    enc = encrypt(plaintext, board, digit_escape="triple")
    print(enc, "\n")

    dec = decrypt(enc, board, digit_escape="triple")
    print(dec)

    assert dec == plaintext
