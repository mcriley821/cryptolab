from math import ceil, sqrt
from typing import Iterator, Literal


def ccw_in(
    text: str,
    *,
    size: tuple[int, int] | Literal["sqr"] = "sqr",
) -> Iterator[int]:
    """
    A Route that spirals counter-clockwise inward.

    Parameters
    ----------
    text : str
        The text to traverse.

    corner : tuple[int, int], default=(0, 0)
        The corner of the text to start at in (row, column) format.

    Returns
    -------
    list[int]
        Indexes of text to properly traverse the route.

    Raises
    ------
    ValueError
        If the size cannot accomodate the text.

    Examples
    --------

    """
    match size:
        case "sqr":
            n = ceil(sqrt(len(text)))
            size = (n, n)
        case (x, y):
            if x * y < len(text):
                raise ValueError(f"text cannot fit on {size}")

    left, top = 0, 0
    right, bottom = size
    width = size[0]
    while left <= right or top <= bottom:
        for i in range(top, bottom):
            yield left + i * width
        left += 1

        for i in range(left, right):
            yield (bottom - 1) * width + i
        bottom -= 1

        for i in range(bottom - 1, top - 1, -1):
            yield (right - 1) + i * width
        right -= 1

        for i in range(right - 1, left - 1, -1):
            yield top * width + i
        top += 1


if __name__ == "__main__":
    from ..route import decrypt, encrypt

    text = "Defend the east wall of the castle"
    print(text, "\n")

    enc = encrypt(text, ccw_in)
    print(enc, "\n")

    dec = decrypt(enc, ccw_in)
    print(dec)

    assert dec == text
