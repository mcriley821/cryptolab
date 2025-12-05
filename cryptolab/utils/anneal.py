""" """

from collections.abc import Callable
from math import exp
from random import random
from typing import TypeVar

KeyType = TypeVar("KeyType")


def anneal(
    ciphertext: str,
    key_gen: Callable[[], KeyType],
    mutate: Callable[[KeyType], KeyType],
    decrypt: Callable[[str, KeyType], str],
    score: Callable[[str], float],
    *,
    temp: float = 1000.0,
    rate: float = 0.999,
    limit: float = 1e-6,
    max_steps: int = 1_000_000,
) -> tuple[str, KeyType]:
    """
    Perform simulated annealing to optimize a decryption key for a ciphertext.

    This function applies the simulated annealing metaheuristic to find a key
    that maximizes the scoring function over decrypted text. It repeatedly mutates
    the current key and probabilistically accepts worse solutions to escape local
    optima, gradually reducing the acceptance probability as temperature decreases.

    Parameters
    ----------
    ciphertext : str
        The encrypted text to decrypt and evaluate.

    key_gen : Callable[[], KeyType]
        Function that returns an initial random key or state.

    mutate : Callable[[KeyType], KeyType]
        Function that produces a small random modification (neighbor) of a given key.

    decrypt : Callable[[str, KeyType], str]
        Function that decrypts the ciphertext using the provided key.

    score : Callable[[str], float]
        Function that evaluates the fitness or likelihood of a decrypted text.

    temp : float, default=1000.0
        Initial temperature controlling the acceptance of worse solutions.

    rate : float, default=0.999
        Multiplicative cooling rate applied to the temperature each iteration.

    limit : float, default=1e-6
        Temperature threshold at which the algorithm stops.

    max_steps : int, default=1_000_000
        Maximum number of iterations before termination.

    Returns
    -------
    tuple[str, KeyType]
        The best decrypted text and its corresponding key.
    """
    key = key_gen()

    text = ""
    while text == "":
        try:
            text = decrypt(ciphertext, key)
        except Exception:
            key = key_gen()

    best = (score(text), text, key)
    current = best

    for i in range(max_steps):
        new_key = mutate(current[-1])
        try:
            text = decrypt(ciphertext, new_key)
        except Exception:
            continue

        sc = score(text)

        temp_i = temp * (rate**i)
        bound = exp(min((sc - current[0]) / temp_i, 700))

        if sc > current[0] or random() < bound:
            current = (sc, text, new_key)
            if sc > best[0]:
                best = current

        if temp_i < limit:
            break

    return best[1], best[2]


if __name__ == "__main__":
    from itertools import combinations
    from random import choice, shuffle
    from string import ascii_uppercase

    from cryptolab.scoring.ngram import trigram_score
    from cryptolab.substitution import simple

    plaintext = "Simulated annealing is a probabilistic technique for approximating the global optimum of a given function. Specifically, it is a metaheuristic to approximate global optimization in a large search space for an optimization problem."

    def gen_key() -> str:
        key = list(ascii_uppercase)
        shuffle(key)
        return "".join(key)

    def mutate(key: str) -> str:
        lkey = list(key)
        a, b = choice(tuple(combinations(range(len(lkey)), 2)))
        lkey[a], lkey[b] = lkey[b], lkey[a]
        return "".join(lkey)

    key = gen_key()

    print(plaintext)
    print(key, "\n")

    enc = simple.encrypt(plaintext, key)
    print(enc, "\n")

    dec, bkey = anneal(
        enc,
        gen_key,
        mutate,
        simple.decrypt,
        trigram_score,
    )

    print(dec)
    print(bkey)
