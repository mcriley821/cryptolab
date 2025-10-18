from math import ceil


def encrypt(key: list[int], phrase: str) -> str:
    paired = {j: phrase[i :: len(key)] for i, j in enumerate(key)}
    return "".join(paired[i] for i in range(len(key)))


def decrypt(key: list[int], phrase: str) -> str:
    rows = int(ceil(len(phrase) / len(key)))
    fill = rows * len(key)
    pads = len(key) - (fill - len(phrase))

    cols = [""] * len(key)
    paired = {j: i for i, j in enumerate(key)}

    it = iter(phrase)
    for i in range(len(key)):
        j = paired[i]
        if j >= pads:
            cols[j] = "".join(next(it) for _ in range(rows - 1)) + "."
        else:
            cols[j] = "".join(next(it) for _ in range(rows))

    return "".join(c[i] for i in range(rows) for c in cols)[: len(phrase)]


if __name__ == "__main__":
    from .sequencing import sequence

    keyword = "zebras"
    input = "wearediscoveredfleeatonce"

    key = sequence(keyword)
    print(f"keyword ({keyword}): {key}")

    enc = encrypt(key, input)
    print(enc)

    dec = decrypt(key, enc)
    print(dec)

    assert input == dec
