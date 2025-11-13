from importlib.resources import open_text
from math import log10
from functools import lru_cache
from typing import Dict, List, Tuple


class _WordScorer:
    """Efficient word-level scoring for unsegmented ciphertexts.

    Implements dynamic programming to find the most probable segmentation of
    text into English words, based on unigram and bigram frequencies.
    """

    __slots__ = ("_loaded", "_Pw", "_Pw2", "_unseen", "_N", "_MAX_WORD_LEN")

    def __init__(self) -> None:
        """Initialize internal structures.

        Parameters
        ----------
        None

        Returns
        -------
        None
        """
        self._loaded = False
        self._Pw: Dict[str, float] = {}
        self._Pw2: Dict[str, float] = {}
        self._unseen: List[float] = []
        self._N = 1024908267229.0
        self._MAX_WORD_LEN = 20

    def _load_data(
        self,
        *,
        module: str = "cryptolab.scoring.data",
        unigram_file: str = "count_1w.txt",
        bigram_file: str = "count_2w.txt",
    ) -> None:
        """Load unigram and bigram word frequencies lazily.

        Parameters
        ----------
        module : str, optional
            Import path containing data files.
        unigram_file : str, optional
            Name of the unigram frequency file.
        bigram_file : str, optional
            Name of the bigram frequency file.

        Returns
        -------
        None
        """
        if self._loaded:
            return

        with open_text(module, unigram_file) as f:
            for line in f:
                word, count = line.strip().split()
                self._Pw[word.upper()] = self._Pw.get(word.upper(), 0.0) + int(count)

        for k, v in list(self._Pw.items()):
            self._Pw[k] = log10(v / self._N)

        with open_text(module, bigram_file) as f:
            for line in f:
                pair, count = line.strip().split("\t")
                w1, w2 = pair.upper().split()
                key = f"{w1} {w2}"
                self._Pw2[key] = self._Pw2.get(key, 0.0) + int(count)

        for key, v in list(self._Pw2.items()):
            w1, _ = key.split()
            base = self._Pw.get(w1, 0)
            self._Pw2[key] = log10(v / self._N) - base

        self._unseen = [log10(10.0 / (self._N * 10**L)) for L in range(50)]
        self._loaded = True

    @lru_cache(maxsize=4096)
    def _cPw(self, word: str, prev: str = "<UNK>") -> float:
        """Compute conditional log10 probability P(word | prev).

        Parameters
        ----------
        word : str
            Candidate word.
        prev : str, optional
            Previous word context (default "<UNK>").

        Returns
        -------
        float
            Conditional log10 probability.
        """
        word = word.upper()
        prev = prev.upper()
        if word not in self._Pw:
            return self._unseen[min(len(word), len(self._unseen) - 1)]
        pair = f"{prev} {word}"
        if pair not in self._Pw2:
            return self._Pw[word]
        return self._Pw2[pair]

    def _score_impl(self, text: str) -> Tuple[float, List[str]]:
        """Compute best segmentation and log probability for given text.

        Parameters
        ----------
        text : str
            Ciphertext with no spaces.

        Returns
        -------
        tuple[float, list[str]]
            Best log probability and word segmentation.
        """
        text = text.upper()
        n = len(text)
        L = min(self._MAX_WORD_LEN, n)

        prob: List[List[float]] = [[float("-inf")] * L for _ in range(n)]
        segs: List[List[List[str]]] = [[[] for _ in range(L)] for _ in range(n)]

        for j in range(L):
            word = text[: j + 1]
            prob[0][j] = self._cPw(word)
            segs[0][j] = [word]

        for i in range(1, n):
            for j in range(min(L, n - i)):
                word = text[i : i + j + 1]
                best_val = float("-inf")
                best_seg: List[str] = []
                for k in range(min(i, L)):
                    prev_prob = prob[i - k - 1][k]
                    if prev_prob == float("-inf"):
                        continue
                    prev_word = segs[i - k - 1][k][-1]
                    val = prev_prob + self._cPw(word, prev_word)
                    if val > best_val:
                        best_val = val
                        best_seg = segs[i - k - 1][k] + [word]
                prob[i][j] = best_val
                segs[i][j] = best_seg

        ends = [(prob[n - i - 1][i], segs[n - i - 1][i]) for i in range(min(n, L))]
        return max(ends, key=lambda x: x[0])

    def analyze(self, text: str) -> Tuple[float, List[str]]:
        """Compute both score and segmentation in one pass.

        Parameters
        ----------
        text : str
            Ciphertext (no spaces).

        Returns
        -------
        tuple[float, list[str]]
            Log10 probability and corresponding segmentation.
        """
        if not self._loaded:
            self._load_data()
        return self._score_impl(text)

    def score(self, text: str) -> float:
        """Return only the total log-likelihood score.

        Parameters
        ----------
        text : str
            Ciphertext (no spaces).

        Returns
        -------
        float
            Log10 probability score.
        """
        return self.analyze(text)[0]

    def segment(self, text: str) -> List[str]:
        """Return only the best segmentation.

        Parameters
        ----------
        text : str
            Ciphertext (no spaces).

        Returns
        -------
        list[str]
            List of segmented words.
        """
        return self.analyze(text)[1]


_scorer = _WordScorer()


def word_analyze(text: str) -> Tuple[float, List[str]]:
    """Compute best log probability and segmentation for ciphertext.

    Parameters
    ----------
    text : str
        Ciphertext (no spaces).

    Returns
    -------
    tuple[float, list[str]]
        Log10 probability score and segmentation list.
    """
    return _scorer.analyze(text)


def word_score(text: str) -> float:
    """Return only the log10 probability score.

    Parameters
    ----------
    text : str
        Ciphertext (no spaces).

    Returns
    -------
    float
        Log10 probability score.
    """
    return _scorer.score(text)


def word_segment(text: str) -> List[str]:
    """Return only the most probable segmentation.

    Parameters
    ----------
    text : str
        Ciphertext (no spaces).

    Returns
    -------
    list[str]
        List of segmented words.
    """
    return _scorer.segment(text)


if __name__ == "__main__":
    text = "ATTACKTHEEASTWALLOFTHECASTLEATDAWN"
    score, segmentation = word_analyze(text)

    print(f"Text: {text}")
    print(f"Score: {score:.4f}")
    print("Segmentation:", " ".join(segmentation))
