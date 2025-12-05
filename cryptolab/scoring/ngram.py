from dataclasses import dataclass, field
from importlib.resources import files
from math import log10
from threading import Lock


@dataclass(slots=True)
class _NgramScorer:
    """
    Lazy loading ngram score data class.

    Parameters
    ----------
    file_name : str
        The file name of the ngram data.
    """

    _file_name: str
    _loaded: bool = False
    _lock: Lock = Lock()

    _data: dict[str, float] = field(default_factory=dict[str, float])

    # default score when ngram is not in the data (lazy loaded)
    _floor: float = float("NaN")

    # ngram length (lazy loaded)
    _ngram_len: int = 0

    def _load_data(
        self,
        *,
        module: str = "cryptolab.scoring.data",
    ):
        """
        Load the ngram data from the file.

        Parameters
        ----------
        module : str,default="cryptolab.scoring.data"
            The module to find the data file.
        """
        with self._lock:
            if self._loaded:
                return

            with (files(module) / self._file_name).open() as f:
                n = 0
                for line in f:
                    k, v = line.strip().split()
                    self._data[k] = float(v)
                    n += int(v)

            k: str = ""
            for k, v in self._data.items():
                self._data[k] = log10(v / n)

            self._ngram_len = len(k)
            self._floor = log10(0.01 / n)
            self._loaded = True

    def score(self, text: str) -> float:
        """
        Score the text using the ngram data.

        Parameters
        ----------
        text : str
            The text to score.

        Returns
        -------
        float
            The calculated score.
        """
        if not self._loaded:
            self._load_data()

        total = 0.0
        for i in range(len(text) - self._ngram_len + 1):
            ngram = text[i : i + self._ngram_len]
            total += self._data.get(ngram.upper(), self._floor)

        return total


_monogram = _NgramScorer("english_monograms.txt")
_bigram = _NgramScorer("english_bigrams.txt")
_trigram = _NgramScorer("english_trigrams.txt")
_quadgram = _NgramScorer("english_quadgrams.txt")
_quintgram = _NgramScorer("english_quintgrams.txt")


def monogram_score(text: str) -> float:
    """
    Score the text using monogram data.

    Parameters
    ----------
    text : str
        The text to score.

    Returns
    -------
    float
        The calculated score.
    """
    return _monogram.score(text)


def bigram_score(text: str) -> float:
    """
    Score the text using bigram data.

    Parameters
    ----------
    text : str
        The text to score.

    Returns
    -------
    float
        The calculated score.
    """
    return _bigram.score(text)


def trigram_score(text: str) -> float:
    """
    Score the text using trigram data.

    Parameters
    ----------
    text : str
        The text to score.

    Returns
    -------
    float
        The calculated score.
    """
    return _trigram.score(text)


def quadgram_score(text: str) -> float:
    """
    Score the text using quadgram data.

    Parameters
    ----------
    text : str
        The text to score.

    Returns
    -------
    float
        The calculated score.
    """
    return _quadgram.score(text)


def quintgram_score(text: str) -> float:
    """
    Score the text using quintgram data.

    Parameters
    ----------
    text : str
        The text to score.

    Returns
    -------
    float
        The calculated score.
    """
    return _quintgram.score(text)


if __name__ == "__main__":
    text = "ATTACK THE EAST WALL OF THE CASTLE AT DAWN"

    print(1, monogram_score(text))
    print(2, bigram_score(text))
    print(3, trigram_score(text))
    print(4, quadgram_score(text))
    print(5, quintgram_score(text))
