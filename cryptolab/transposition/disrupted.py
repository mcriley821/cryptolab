from .sequencing import sequence
from .columnar import (
    encrypt as col_encrypt,
    decrypt as col_decrypt,
)
from math import ceil


def encrypt(key: list[int], plaintext: str) -> str:
    i_1 = key.index(0)
    i_2 = key.index(1)

    rows = int(ceil(len(plaintext) / len(key)))
    filled = [""] * rows

    it = iter(plaintext)

    for i in range(rows):
        filled[i] = "".join(next(it) for _ in range(i_1))
        if i_1 == len(key):
            break
        i_1 += 1

    for j in range(i + 1, rows):
        filled[j] = "".join(next(it) for _ in range(i_2))
        if i_2 == len(key):
            break
        i_2 += 1

    i = 0
    for c in it:
        while len(filled[i]) >= len(key):
            i += 1
        filled[i] += c

    return col_encrypt(key, "".join(filled))


def decrypt(key: list[int], ciphertext: str) -> str:
    temp = col_decrypt(key, ciphertext)

    i_1 = key.index(0)
    i_2 = key.index(1)

    h1 = []
    h2 = []

    for i in range(0, len(temp), len(key)):
        row = temp[i : i + len(key)]

        if i_1 > len(key):
            h1.append(row[:i_2])
            h2.append(row[i_2:])
            i_2 += 1

        if i_1 <= len(key):
            h1.append(row[:i_1])
            h2.append(row[i_1:])
            i_1 += 1

    return "".join(h1) + "".join(h2)


if __name__ == "__main__":
    from .sequencing import sequence

    key = sequence("94735236270398134", zero_high=True)
    print(f"key (cipher): {key}")

    input = "092002745346860181384805777868831596370253911018309880750797004794027027992906280860654204048324030833654811448180352434864084447840054705621546580540"

    enc = encrypt(key, input)
    print(enc)

    dec = decrypt(key, enc)
    print(dec)

    assert input == dec
