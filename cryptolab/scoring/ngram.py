from functools import wraps
from math import log10
from pathlib import Path


_module_dir = Path(__file__).parent


def lazy_load(file: Path):
    def decorator(func):
        @wraps(func)
        def inner(*args, **kwargs):
            if not getattr(func, "data", None):
                data = {}
                with open(file) as f:
                    n = 0
                    for line in f:
                        k, v = line.strip().split()
                        data[k] = int(v)
                        n += int(v)

                for k, v in data.items():
                    data[k] = v / n

                setattr(func, "data", data)
            return func(*args, **kwargs, data=getattr(func, "data"))

        return inner

    return decorator


def _score(text: str, data: dict[str, int], window: int) -> float:
    it = filter(lambda x: x.isalpha(), iter(text.upper()))
    tot = 0.0
    w = ""
    for i, c in enumerate(it):
        if i != 0 and i % window == 0:
            tot += log10(data[w])
            w = ""
        w += c
    return tot


@lazy_load(_module_dir / "data" / "english_monograms.txt")
def monogram_score(text: str, *, data: dict[str, int] = {}) -> float:
    return _score(text, data, 1)


@lazy_load(_module_dir / "data" / "english_bigrams.txt")
def bigram_score(text: str, *, data: dict[str, int] = {}) -> float:
    return _score(text, data, 2)


@lazy_load(_module_dir / "data" / "english_trigrams.txt")
def trigram_score(text: str, *, data: dict[str, int] = {}) -> float:
    return _score(text, data, 3)


@lazy_load(_module_dir / "data" / "english_quadgrams.txt")
def quadgram_score(text: str, *, data: dict[str, int] = {}) -> float:
    return _score(text, data, 4)


@lazy_load(_module_dir / "data" / "english_quintgrams.txt")
def quintgram_score(text: str, *, data: dict[str, int] = {}) -> float:
    return _score(text, data, 5)


if __name__ == "__main__":
    text = "ATTACK THE EAST WALL OF THE CASTLE AT DAWN"

    print(1, monogram_score(text))
    print(2, bigram_score(text))
    print(3, trigram_score(text))
    print(4, quadgram_score(text))
    print(5, quintgram_score(text))
