import os, sys
import random
from collections import Counter
from typing import OrderedDict
from functools import lru_cache
from globals import FREQ_FILE


def split_line(line):
    parts = line.strip().split("\t")
    if len(parts) == 1:
        return parts[0], 1
    else:
        return parts[0], int(parts[1])


class WordHoard:
    def __init__(self, file=FREQ_FILE):
        if file is None:
            file = FREQ_FILE
        self.frequencies = self.read_words_and_frequencies(file)
        self.words = set(self.frequencies.keys())

    def read_words_and_frequencies(self, file):
        """Read a file of words and frequencies, return a dict of words and frequencies"""

        return dict([split_line(line) for line in open(file)])

    def frequency(self, word):
        """Return the frequency of a given word, 0 if not found"
        >>> wh = WordHoard(FREQ_FILE)
        >>> wh.frequency("audio") > 10
        True
        >>> wh.frequency("audioa")
        0
        """
        return self.frequencies.get(word, 0)

    def letter_frequencies(self, words):
        """Return a Counter of the frequencies of letters in a word
        >>> wh = WordHoard(FREQ_FILE)
        >>> c = wh.letter_frequencies(["zzaudio"])
        >>> c.get("a") == 1
        True
        >>> c.get("Q") == 0
        False
        >>> c.get("z") == 2
        True
        >>> list(wh.letter_frequencies(["zzaudio"]).items())[0]
        ('z', 2)
        """
        counter = Counter()
        for word in words:
            counter.update(list(word))
        return OrderedDict(
            [
                (l, k)
                for k, l in sorted([(j, i) for i, j in counter.items()], reverse=True)
            ]
        )

    def most_frequent_letters(self, words, n=6):
        """Return the most frequent letters in a set of words
        >>> wh = WordHoard(FREQ_FILE)
        >>> wh.most_frequent_letters(["zzaudio"], 1)
        ['z']
        """
        return list(self.letter_frequencies(words).keys())[0:n]

    def most_frequent_word(self, words):
        """Return the most frequent words in a list of words
        >>> wh = WordHoard(FREQ_FILE)
        >>> wh.most_frequent_word(["every", "audio", "ZZZZZ"])
        'every'
        """
        return max(words, key=lambda word: self.frequencies.get(word, 0))

    def words_with_frequency(self, frequency=10000):
        return [w for w, f in self.frequencies.items() if f >= frequency]

    def letter_frequencies_ignoring(self, words, letter_set):
        """
        Collect the letter frequencies of a set of words, ignoring the letters in letter_set
        >>> wh = WordHoard(FREQ_FILE)
        >>> wh.letter_frequencies_ignoring(["zzaudio"], set(["z"]))
        Counter({'a': 1, 'u': 1})
        """
        counter = Counter()
        for word in words:
            counter.update(list(word))
        for l in letter_set:
            counter.pop(l, None)
        return OrderedDict(
            [
                (l, k)
                for k, l in sorted([(j, i) for i, j in counter.items()], reverse=True)
            ]
        )


@lru_cache(maxsize=None)
def is_vowel(letter):
    """Return True if the letter is a vowel, False otherwise
    >>> is_vowel("a")
    True
    >>> is_vowel("b")
    False
    """
    return letter in "aeiou"


@lru_cache(maxsize=None)
def is_consonant(letter):
    """Return True if the letter is a consonant, False otherwise
    >>> is_consonant("a")
    False
    >>> is_consonant("b")
    True
    """
    return letter in "bcdfghjklmnpqrstvwxyz"


@lru_cache(maxsize=None)
def set_of(letters):
    """Return a set of letters
    >>> set_of("a")
    {'a'}
    >>> set_of("ab")
    {'a', 'b'}
    """
    return set(letters)


if __name__ == "__main__":
    import doctest

    print("Testing...")
    doctest.testmod()
    print("Done.")
