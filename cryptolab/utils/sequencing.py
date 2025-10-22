def sequence(text: str, *, zero_high: bool = False) -> list[int]:
    """
    Sequence the given text. Sequencing is the process of assigning indices to
    the elements such that the indices would be strictly increasing if the
    string is sorted.

    Parameters
    ----------
    text : str
        An alphabetical or numerical string

    zero_high : bool, default=False
        Whether to treat 0 as greater than 9

    Returns
    -------
    list[int]
        A list containing the assigned indices.

    Examples
    --------
    >>> sequence("cipher")
    [0, 3, 4, 2, 1, 5]
    >>> sequence("47262056")
    [3, 7, 1, 5, 2, 0, 4, 6]
    >>> sequence("47262056", zero_high=True)
    [2, 6, 0, 4, 1, 7, 3, 5]
    """
    indexed = list(enumerate(text))
    if text.isalpha():
        indexed.sort(key=lambda x: x[1])
    elif text.isnumeric() and zero_high:
        indexed.sort(key=lambda x: (int(x[1]) - 1) % 10)
    elif text.isnumeric():
        indexed.sort(key=lambda x: int(x[1]))

    result: list[int] = [0] * len(text)
    for i, (j, _) in enumerate(indexed):
        result[j] = i
    return result


if __name__ == "__main__":
    print(sequence("cipher"))
    print(sequence("543041"))
    print(sequence("543041", zero_high=True))
