from dataclasses import dataclass, field
from importlib.resources import files
from math import log10
from threading import Lock


@dataclass(slots=True)
class _WordScorer:
    """
    Lazy loading word score data class.

    Implements dynamic programming to find the most probable segmentation of
    text into English words, based on first-order and second-order word frequencies.
    """

    _loaded: bool = False
    _lock: Lock = Lock()

    # first-order word probabilities
    _Pw: dict[str, float] = field(default_factory=dict[str, float])

    # second-order word probabilities
    _Pw2: dict[str, float] = field(default_factory=dict[str, float])

    # unknown words score
    _unseen: list[float] = field(default_factory=list[float])

    # total number of samples (lazily loaded)
    _n: int = 0

    _MAX_WORD_LEN: int = 20

    def _load_data(
        self,
        *,
        module: str = "cryptolab.scoring.data",
        first_order_file: str = "count_1w.txt",
        second_order_file: str = "count_2w.txt",
        n: int = 1024908267229,
    ):
        """
        Load first-order and second-order word frequencies.

        Parameters
        ----------
        module : str, default="cryptolab.scoring.data"
            Import path containing data files.

        first_order_file : str, default="count_1w.txt"
            Name of the first-order word frequency file.

        second_order_file : str, default="count_2w.txt"
            Name of the second-order word frequency file.
        """
        with self._lock:
            if self._loaded:
                return

            self._n = n

            with (files(module) / first_order_file).open() as f:
                for line in f:
                    word, countStr = line.strip().split("\t")
                    count = int(countStr)
                    self._Pw[word.upper()] = self._Pw.get(word.upper(), 0) + count

            for k, v in list(self._Pw.items()):
                self._Pw[k] = log10(v / self._n)

            with (files(module) / second_order_file).open() as f:
                for line in f:
                    key, count = line.strip().split("\t")
                    key = key.upper()
                    self._Pw2[key] = self._Pw2.get(key, 0) + int(count)

            for key, v in self._Pw2.items():
                w1, _ = key.split()
                self._Pw2[key] = log10(v / self._n) - self._Pw.get(w1, 0)

            self._unseen = [log10(10.0 / (self._n * 10**L)) for L in range(50)]
            self._loaded = True

    def _cPw(self, word: str, prev: str = "<UNK>") -> float:
        """
        Compute the probability that word follows the previous word.

        Parameters
        ----------
        word : str
            Candidate word.

        prev : str, default="<UNK>"
            Previous word context.

        Returns
        -------
        float
            The probability.
        """
        if word not in self._Pw:
            return self._unseen[min(len(word), len(self._unseen) - 1)]
        ret = self._Pw2.get(f"{prev} {word}")
        return ret if ret is not None else self._Pw[word]

    def _score_impl(self, text: str) -> tuple[float, list[str]]:
        """
        Calculate the best segmentation and score for given text.

        Parameters
        ----------
        text : str
            The ciphertext to operate on

        Returns
        -------
        tuple[float, list[str]]
            Best word segmentation and its score as (score, segmentation)
        """
        n = len(text)
        L = min(self._MAX_WORD_LEN, n)

        # prob[i][j] holds the best probability up to index i where the last word has length j+1
        prob = [[float("-inf")] * L for _ in range(n)]

        # segs[i][j] holds the corresponding word segmentations
        segs: list[list[list[str]]] = [[list() for _ in range(L)] for _ in range(n)]

        # initialize all possible starting words at position 0
        for j in range(L):
            word = text[: j + 1]
            prob[0][j] = self._cPw(word)
            segs[0][j] = [word]

        # i = current text position / end of the current word
        # j = current word length - 1
        # k = possible previous word lengths - 1
        for i in range(1, n):
            for j in range(min(L, n - i)):
                word = text[i : i + j + 1]
                best_val = float("-inf")
                best_seg: list[str] = []

                # look at all word boundaries up to i
                for k in range(min(i, L)):
                    prev_prob = prob[i - k - 1][k]
                    if prev_prob == float("-inf"):
                        continue

                    # get the last word of the previous segment for scoring
                    prev_word = segs[i - k - 1][k][-1]

                    # add the probability this word follows the previous word
                    val = prev_prob + self._cPw(word, prev_word)
                    if val > best_val:
                        best_val = val
                        best_seg = segs[i - k - 1][k] + [word]

                prob[i][j] = best_val
                segs[i][j] = best_seg

        # find the best ending position and corresponding segmentation
        ends = [(prob[n - i - 1][i], segs[n - i - 1][i]) for i in range(min(n, L))]
        return max(ends, key=lambda x: x[0])

    def analyze(self, text: str) -> tuple[float, list[str]]:
        """
        Determine and score the most probable segmentation of the given text.

        Parameters
        ----------
        text : str
            The text to analyze.

        Returns
        -------
        tuple[float, list[str]]
            Probability and corresponding segmentation.
        """
        if not self._loaded:
            self._load_data()
        return self._score_impl(text)

    def score(self, text: str) -> float:
        """
        Score the most probable word segmentation of the given text.

        Parameters
        ----------
        text : str
            The text to score.

        Returns
        -------
        float
            The calculated score.
        """
        return self.analyze(text)[0]

    def segment(self, text: str) -> list[str]:
        """
        Determine the most probable word segmentation of the given text.

        Parameters
        ----------
        text : str
            The text to segment into words.

        Returns
        list[str]
            The most probable segmentation.
        """
        return self.analyze(text)[1]


_scorer = _WordScorer()


def word_analyze(text: str) -> tuple[float, list[str]]:
    """
    Determine the best word segmentation of the text and its probability.

    Parameters
    ----------
    text : str
        The text to analyze.

    Returns
    -------
    tuple[float, list[str]]
        Most probable word segmentation and its probability as (probability, segmentation)
    """
    return _scorer.analyze(text)


def word_score(text: str) -> float:
    """
    Score the text by word probability.

    Parameters
    ----------
    text : str
        The text to score.

    Returns
    -------
    float
        The calculated score.
    """
    return _scorer.score(text.upper())


def word_segments(text: str) -> list[str]:
    """
    Determine the most probable segmentation.

    Parameters
    ----------
    text : str
        The text to segment into words.

    Returns
    -------
    list[str]
        List of segmented words.
    """
    return _scorer.segment(text.upper())


if __name__ == "__main__":
    text = "ATTACKTHEEASTWALLOFTHECASTLEATDAWN"
    score, segmentation = word_analyze(text)

    print(f"Text: {text}")
    print(f"Score: {score:.4f}")
    print("Segmentation:", " ".join(segmentation))
