from importlib.resources import open_text
from math import log10


_ngram_data = dict[str, float]


def _load_data(
    file_name: str,
    *,
    module: str = "cryptolab.scoring.data",
) -> _ngram_data:
    data: dict[str, float] = {}

    with open_text(module, file_name) as f:
        n = 0
        for line in f:
            k, v = line.strip().split()
            data[k] = float(v)
            n += int(v)

    for k, v in data.items():
        data[k] = log10(v / n)

    return data


def _score(text: str, data: _ngram_data, window: int) -> float:
    it = filter(lambda x: x.isalpha(), iter(text.upper()))
    tot = 0.0
    w = ""
    for i, c in enumerate(it):
        if i != 0 and i % window == 0:
            tot += data.get(w, -5)
            w = ""
        w += c
    return tot


_monogram_data: _ngram_data | None = None


def monogram_score(text: str) -> float:
    global _monogram_data
    if _monogram_data is None:
        _monogram_data = _load_data("english_monograms.txt")
    return _score(text, _monogram_data, 1)


_bigram_data: _ngram_data | None = None


def bigram_score(text: str) -> float:
    global _bigram_data
    if _bigram_data is None:
        _bigram_data = _load_data("english_bigrams.txt")
    return _score(text, _bigram_data, 2)


_trigram_data: _ngram_data | None = None


def trigram_score(text: str) -> float:
    global _trigram_data
    if _trigram_data is None:
        _trigram_data = _load_data("english_trigrams.txt")
    return _score(text, _trigram_data, 3)


_quadgram_data: _ngram_data | None = None


def quadgram_score(text: str) -> float:
    global _quadgram_data
    if _quadgram_data is None:
        _quadgram_data = _load_data("english_quadgrams.txt")
    return _score(text, _quadgram_data, 4)


_quintgram_data: _ngram_data | None = None


def quintgram_score(text: str) -> float:
    global _quintgram_data
    if _quintgram_data is None:
        _quintgram_data = _load_data("english_quintgrams.txt")
    return _score(text, _quintgram_data, 5)


if __name__ == "__main__":
    text = "ATTACK THE EAST WALL OF THE CASTLE AT DAWN"

    print(1, monogram_score(text))
    print(2, bigram_score(text))
    print(3, trigram_score(text))
    print(4, quadgram_score(text))
    print(5, quintgram_score(text))
