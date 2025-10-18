def sequence(line: str, *, zero_high=False) -> list[int]:
    indexed = list(enumerate(line))
    if line.isalpha():
        indexed.sort(key=lambda x: x[1])
    elif line.isnumeric() and zero_high:
        indexed.sort(key=lambda x: (int(x[1]) - 1) % 10)
    elif line.isnumeric():
        indexed.sort(key=lambda x: int(x[1]))

    result: list[int] = [0] * len(line)
    for i, (j, _) in enumerate(indexed):
        result[j] = i
    return result


if __name__ == "__main__":
    print(sequence("cipher"))
    print(sequence("543041"))
    print(sequence("543041", zero_high=True))
