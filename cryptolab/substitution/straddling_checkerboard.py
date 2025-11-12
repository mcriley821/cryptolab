"""
https://en.wikipedia.org/wiki/Straddling_checkerboard
"""

from collections.abc import Callable
from functools import partial
from itertools import combinations
from random import choice, randint, shuffle
from string import ascii_uppercase

from ..scoring.ngram import trigram_score
from ..utils.anneal import anneal


class Board:
    """
    Represents a Straddling Checkerboard cipher board.

    Parameters
    ----------
    digits : tuple[str, str]
        Two distinct digits used to identify the additional rows of the board.

    key : list[int], optional
        A permutation of digits 0–9 defining the column order.
        If None, defaults to the natural order [0, 1, 2, ..., 9].

    keyword : str, optional
        Optional keyword to reorder the alphabet. Unique characters from the
        keyword are placed first in order of appearance, followed by the remaining
        unused characters in A–Z followed by '.' and '/'.

    Attributes
    ----------
    _key : list[int]
        The 10-digit permutation used to determine column order.

    _digits : tuple[str, str]
        The digit labels for the second and third rows.

    _board : dict[str | None, list[str | None]]
        Mapping from row key (None, digits[0], digits[1]) to a list of 10 symbols.

    Raises
    ------
    ValueError
        If the provided key is not of length 10.

    Examples
    --------
    >>> board = Board(("1", "4"), keyword="ASINTOER")
    >>> board["15"]
    'H'
    >>> inv = board.invert()
    >>> inv["H"]
    '15'
    """

    def __init__(
        self,
        digits: tuple[str, str],
        key: list[int] | None = None,
        *,
        keyword: str = "",
    ):
        if key is None:
            self._key = list(range(10))
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

        self._alphabet = "".join(key_chars) + "".join(alphabet_set)
        assert len(self._alphabet) == 28
        it = iter(self._alphabet)

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
        """
        Retrieve a character from the board given its numeric code.

        Parameters
        ----------
        key : str
            A one or two digit string:
            - one digit: corresponding column from the unlabeled row
            - two digit: corresponding row-column

        Returns
        -------
        str
            The corresponding character

        Raises
        ------
        ValueError
            If the board does not contain a character for the given key
        """
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
        """
        Generate a reverse lookup table mapping characters to numeric code.

        Returns
        -------
        dict[str, str]
            Dictionary mapping characters to corresponding digits.
        """
        out: dict[str, str] = dict()
        for k, row in self._board.items():
            c = "" if k is None else k
            for i, j in enumerate(self._key):
                if (s := row[i]) is not None:
                    out[s] = c + str(j)
        return out

    @property
    def digits(self) -> tuple[str, str]:
        """
        The digits that label the second and third rows of the board.

        Returns
        -------
        tuple[str, str]
            The digit labels.
        """
        return self._digits

    @property
    def key(self) -> list[int]:
        """
        The column-wise key of the board.

        Returns
        -------
        list[int]
            The key.
        """
        return self._key.copy()

    @property
    def alphabet(self) -> str:
        """
        The alphabet of the board, by rows.

        Returns
        -------
        str
            The alphabet.
        """
        return self._alphabet

    def __str__(self) -> str:
        """
        Get a string representation of the board.

        Returns
        -------
        str
            The representation of the board.
        """
        a, b = self._digits
        key_row = "  " + " ".join(str(i) for i in self._key)
        no_row = "  " + " ".join(i if i else " " for i in self._board[None])
        a_row = f"{a} {' '.join(i for i in self._board[a] if i)}"
        b_row = f"{b} {' '.join(i for i in self._board[b] if i)}"
        return "\n".join((key_row, no_row, a_row, b_row))

    @staticmethod
    def random() -> "Board":
        """
        Generate a randomized Board.

        Returns
        -------
        Board
            A Board with random digits, key, and alphabet.
        """
        a = randint(0, 9)
        while (b := randint(0, 9)) == a:
            ...

        digs = (str(a), str(b))

        key = list(range(10))
        shuffle(key)

        alph = list(ascii_uppercase)
        shuffle(alph)

        return Board(digs, key, keyword="".join(alph))

    def random_mutation(self) -> "Board":
        """
        Get a random mutation of this board.

        Returns
        -------
        Board
            A new Board with the random mutation.

        Notes
        -----
        There are a total of 432 possible mutations:
        * 9 digit mutations (8 replace, 1 swap)
        * 45 key mutations
        * 378 alphabet mutations
        """
        r = randint(0, 2)
        if r == 0:
            r = randint(0, 2)
            a, b = self._digits
            if r == 0:  # swap digits
                return Board((b, a), self.key, keyword=self._alphabet)

            i = choice(tuple(set(map(str, range(10))) - set(self._digits)))
            if r == 1:  # replace first digit
                return Board((i, b), self.key, keyword=self._alphabet)

            return Board((a, i), self.key, keyword=self._alphabet)

        if r == 1:
            key = self.key
            a, b = choice(tuple(combinations(range(len(key)), 2)))
            key[a], key[b] = key[b], key[a]
            return Board(self._digits, key, keyword=self._alphabet)

        # r == 2
        alph = list(self._alphabet)
        a, b = choice(tuple(combinations(range(len(alph)), 2)))
        alph[a], alph[b] = alph[b], alph[a]
        return Board(self._digits, self.key, keyword="".join(alph))


def encrypt(plaintext: str, board: Board, *, digit_escape: str = "single") -> str:
    """
    Encrypt plaintext using the given Board.

    Parameters
    ----------
    plaintext : str
        Input plaintext. Characters that are not alphanumeric are skipped.

    board : Board
        The board used for encoding.

    digit_escape : str, default="single"
        Determines how digits are encoded:
        - "single": '/' followed by the digit (e.g., "/1/2/3")
        - "double": two copies of each digit between '/' markers (e.g. "/112233/")
        - "triple": three copies of each digit between '/' markers (e.g. "/111222333/")

    Returns
    -------
    str
        Resultant ciphertext.

    Raises
    ------
    ValueError
        If `digit_escape` is not one of the supported modes.
        If `digit_escape` is not "single" and the board character "/" is represented
        by a single digit code.

    Examples
    -------
    >>> board = Board(("1", "4"))
    >>> encrypt("WE ARE DISCOVERED. FLEE AT ONCE.", board)
    '4460196510403164361965487136604116153648'
    """

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
    """
    Decrypt ciphertext with the given Board.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    board: Board
        The board to use for decryption. Must match the board used for encryption.

    digit_escape : str, default="single"
        Must match what was used for encryption.
        Determines how digits are encoded:
        - "single": '/' followed by the digit (e.g., "/1/2/3")
        - "double": two copies of each digit between '/' markers (e.g. "/112233/")
        - "triple": three copies of each digit between '/' markers (e.g. "/111222333/")

    Returns
    -------
    str
        The resultant plaintext

    Raises
    ------
    ValueError
       If `digit_escape` is not one of the supported modes.
       If the ciphertext does not decode properly with the given board.

    Examples
    --------
    >>> board = Board(("1", "4"))
    >>> decrypt("4460196510403164361965487136604116153648", board)
    'WEAREDISCOVERED.FLEEATONCE.'
    """

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


def crack(
    ciphertext: str,
    *,
    score: Callable[[str], float] = trigram_score,
    digit_escape: str = "single",
) -> tuple[str, Board]:
    """
    Crack the ciphertext by finding the best decryption Board via annealing.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to crack.

    score : Callable[[str], float],default=trigram_score
        Scoring function to use.

    digit_escape : str,default="single"
        Digit escape when decrypting. See decrypt for more info.

    Returns
    -------
    tuple[str, Board]
        The highest scoring plaintext and corresponding Board
    """

    return anneal(
        ciphertext,
        Board.random,
        Board.random_mutation,
        partial(decrypt, digit_escape=digit_escape),
        score,
    )


if __name__ == "__main__":
    board = Board(("1", "4"), keyword="FUBCDORA.LETHINGKYMVPS/JQZXW")

    plaintext = "INCASEYOUMANAGETOCRACKTHISTHEPRIVATEKEYSBELONGTOHALFANDBETTERHALFANDTHEYALSONEEDFUNDSTOLIVE"

    print(plaintext)
    print(board)

    enc = encrypt(plaintext, board, digit_escape="triple")
    print(enc, "\n")

    dec = decrypt(enc, board, digit_escape="triple")
    print(dec, "\n")

    assert dec == plaintext

    dec, board = crack(enc, digit_escape="triple")
    print(dec)
    print(board)
