import random
import string
from typing import List

HEAT_LO = 1
HEAT_HI = 13

ALPHABET = string.ascii_lowercase


def generate_map(n: int) -> List[List[str]]:
    """
    Generate a nxn map of strings, where the length of each
    string is between HEAT_LO and HEAT_HI inclusive.

    Also enforces that for all A_ij, A_(i-1)(j+1) shares
    no characters with it.
    """
    heat = [
        [random.randint(HEAT_LO, HEAT_HI) for j in range(n)]
        for i in range(n)
    ]

    mp = [[''] * n for i in range(n)]
    for i in range(n):
        for j in range(n):
            cands = set(ALPHABET)
            if i - 1 >= 0 and j + 1 < n:
                cands -= set(mp[i - 1][j + 1])
            ltrs = random.sample(list(cands), heat[i][j])
            mp[i][j] = ''.join(ltrs)

    return mp


if __name__ == '__main__':
    mp = generate_map(4)
    for row in mp:
        print(*row)
