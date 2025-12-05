"""
https://en.wikipedia.org/wiki/Hill_climbing
"""

from collections.abc import Callable, Iterator
from typing import TypeVar

KeyType = TypeVar("KeyType")


def hill_climb(
    ciphertext: str,
    gen_key: Callable[[], KeyType],
    mutate: Callable[[KeyType], Iterator[KeyType]],
    decrypt: Callable[[str, KeyType], str],
    score: Callable[[str], float],
    *,
    restarts: int = 50,
    try_all: bool = False,
    iterations: int = 1_000,
) -> tuple[str, KeyType]:
    """
    Generic hill climb algorithm.

    Supports simple, steepest ascent, stochastic, and shotgun hill climbing.

    Parameters
    ----------
    ciphertext : str
        The ciphertext to decrypt.

    gen_key : Callable[[], KeyType]
        The function to generate a new key. This is used at the beginning of
        each restart and should be random.

    mutate : Callable[[KeyType], Iterator[KeyType]]
        A function to generate new keys from the current key. For steepest
        ascent, the generator should be exhaustable, otherwise the algorithm
        will run indefinitely. The algorithm becomes stochastic if the
        generator is randomized in some way (e.g. random order combinations).

    decrypt : Callable[[str, KeyType], str]
        The decryption function to decrypt the ciphertext with the new keys.

    score : Callable[[str], float]
        A scoring function to determine if a new key is a better key.

    restarts : int,default=50
        Number of restarts to run of the algorithm. For random-restart hill
        climbing, this should be greater than 1.

    try_all : bool,default=False
        Whether to exhaust the generator returned by mutate. For steepest
        ascent, this should be set to True.

    iterations : int,default=1_000
        Maximum number of key mutations to try before returning. This is
        equivalent to the maximum number of times that mutate may be called.
        Exiting early is still possible if an iteration does not improve the
        overall score.
    """

    def _single_restart(_: int) -> tuple[float, str, KeyType]:
        """
        Run a single restart of the hill climb algorithm.

        Parameters
        ----------
        index : int
            The index of this restart. Unused.

        Returns
        -------
        tuple[float, str, KeyType]
            A tuple of the best (score, text, key) for this restart.
        """
        key = gen_key()

        text = ""
        while text == "":
            try:
                text = decrypt(ciphertext, key)
            except Exception:
                key = gen_key()

        best = (score(text), text, key)

        for _ in range(iterations):
            best_i = best

            for new_key in mutate(key):
                try:
                    text = decrypt(ciphertext, new_key)
                    sc = score(text)
                except Exception:
                    continue

                if sc > best_i[0]:
                    best_i = (sc, text, new_key)
                    key = new_key
                    if not try_all:
                        break

            if best_i[0] > best[0]:
                best = best_i
            else:
                break  # no improvement

        return best

    top = _single_restart(0)
    for i in range(1, restarts):
        res = _single_restart(i)
        if res[0] > top[0]:
            top = res

    return top[1], top[2]


if __name__ == "__main__":
    from itertools import combinations
    from random import shuffle
    from string import ascii_uppercase

    from cryptolab.scoring.ngram import quadgram_score
    from cryptolab.substitution import simple

    plaintext = """In simple hill climbing, the first closer node is chosen,
    whereas in steepest ascent hill climbing all successors are compared and
    the closest to the solution is chosen. Both forms fail if there is no
    closer node, which may happen if there are local maxima in the search space
    which are not solutions. Steepest ascent hill climbing is similar to
    best-first search, which tries all possible extensions of the current path
    instead of only one."""

    # make plaintext print ok
    plaintext = "\n".join(plaintext.split("\n    "))

    def gen_key() -> str:
        alph = list(ascii_uppercase)
        shuffle(alph)
        return "".join(alph)

    key = gen_key()

    print(plaintext, "\n")
    print(ascii_uppercase)
    print(key, "\n")

    enc = simple.encrypt(plaintext, key)
    print(enc, "\n")

    def mutate(key: str) -> Iterator[str]:
        for a, b in combinations(range(len(key)), 2):
            alph = list(key)
            alph[a], alph[b] = alph[b], alph[a]
            yield "".join(alph)

    def stochastic_mutate(key: str) -> Iterator[str]:
        keys = list(mutate(key))
        shuffle(keys)
        yield from keys

    for name, mut, kwargs in (
        ("simple", mutate, {"restarts": 1}),
        ("steepest", mutate, {"restarts": 1, "try_all": True}),
        ("stochastic", stochastic_mutate, {"restarts": 1}),
        ("shotgun", mutate, {}),
        ("steepest shotgun", mutate, {"try_all": True}),
        ("stochastic shotgun", stochastic_mutate, {}),
    ):
        dec, bkey = hill_climb(
            enc,
            gen_key,
            mut,
            simple.decrypt,
            quadgram_score,
            **kwargs,  # type:ignore
        )
        print(f"{name}:")
        print(dec, "\n")
        print(bkey)
        print(ascii_uppercase, "\n")
