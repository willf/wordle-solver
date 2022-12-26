import argparse
import functools
import itertools
import json
import math
import string
import time
from collections import Counter
from functools import cache

from rich import print

from bitset import BitSet
from globals import FREQ_FILE
from wordhoard import *


def all_possible_feedbacks(size):
    """Return a list of all possible feedbacks for a given size"""
    return ["".join(p) for p in itertools.product("byg", repeat=size)]

ALPHABET_SIZE = 26

def let_to_index(let, index):
    """
    Given a letter and an index, return the index of the letter in the
    alphabet for that index.
    >>> let_to_index('a', 0)
    0
    >>> let_to_index('a', 1)
    26
    >>> let_to_index('b', 0)
    1
    >>> let_to_index('b', 1)
    27
    """
    return (ALPHABET_SIZE * index) + ord(let) - ord('a')

@cache
def word_to_bitset(word):
    """
    Given a word, return a bitset representing it.
    >>> word_to_bitset("a")
    BitSet(26)
    >>> word_to_bitset("a") == word_to_bitset("a")
    True
    >>> word_to_bitset("a") == word_to_bitset("b")
    False
    """
    result = BitSet(ALPHABET_SIZE * len(word))
    for i, c in enumerate(word):
        result[let_to_index(c, i)] = True
    return result

def index_to_index(index, index2):
    """
    Given an index and an index2, return the index of the letter in the
    alphabet for that index.
    >>> index_to_index(0, 0)
    0
    >>> index_to_index(0, 1)
    26
    >>> index_to_index(1, 0)
    1
    >>> index_to_index(1, 1)
    27
    """
    return (ALPHABET_SIZE * index2) + index

class Solver:
    def __init__(self, wordhoard, size = 5):
        self.size = size
        self.wordhoard = wordhoard
        self.history = []
        self.feedback = []
        self.possibles = [set(string.ascii_lowercase) for _ in range(self.size)]
        self.bitset = BitSet(ALPHABET_SIZE*self.size)
        self.current_words = set(wordhoard.words)

    def _learn_from_feedback(self, feedback, word, update=True):
        possibles = self.possibles
        if not update:
            # make a copy of the possibles
            possibles = [set(p) for p in self.possibles]
        for i, c in enumerate(feedback):
            letter = word[i]
            c = c.lower()
            if c == "·" or c == "b" or c == " ":
                for j in range(self.size):
                    possibles[j].discard(letter)
            elif c == "y":
                possibles[i].discard(letter)
            elif c == "g":
                possibles[i] = set(letter)
            else:
                raise ValueError(f"Unknown feedback character {c}")
        if update:
            self.possibles = possibles
            self.update_possible_words()
        return possibles

    def learn_from_feedback(self, feedback, word, update=True):
        p = self.bitset
        if not update:
          p = self.bitset.copy()
        for i, c in enumerate(feedback):
              letter = word[i]
              c = c.lower()
              if c == "·" or c == "b" or c == " ":
                  for j in range(self.size):
                      let_j = let_to_index(letter, j)
                      p[let_j] = False
              elif c == "y":
                  let_i = let_to_index(letter, i)
                  p[let_i] = False
              elif c == "g":
                  for j in range(ALPHABET_SIZE):
                      let_j = index_to_index(letter, j)
                      p[let_j] = False
                  let_i = let_to_index(letter, i)
                  p[let_i] = True
              else:
                  raise ValueError(f"Unknown feedback character {c}")
        if update:
            self.bitset = p
            self.update_possible_words()
        return p


    def display_possibles(self):
        for i, p in enumerate(self.possibles):
            print(f"{i:2d}:", ''.join(sorted(list(p))))

    def _is_consistent(self, word, possibles=None, verbose=False):
        if possibles is None:
            possibles = self.possibles
        if verbose:
            print("checking", word, "for consistency", end =":")
        for i, c in enumerate(word):
            c_index = i * 26 + ord(c) - ord('a')
            if not possibles[c_index]:
                if verbose:
                    print("inconsistent at", i, "because", c, "not in", ''.join(sorted(list(possibles[i]))))
                return False
        if verbose:
            print("consistent")
        return True

    def is_consistent(self, word, bitset=None, verbose=False):
        if bitset is None:
            bitset = self.bitset
        word_bitset = word_to_bitset(word)
        if verbose:
            print("checking", word, "for consistency", end =":")
        consistent = bitset & word_bitset == word_bitset
        if verbose:
            if consistent:
                print("consistent")
            else:
                print("inconsistent")
        return consistent

    def update_possible_words(self):
        self.current_words = set(
            w for w in self.current_words if self.is_consistent(w, self.possibles)
        )

    def collect_wordgroups_by_feedback(self, word):
        wordgroups = {}
        for feedback in all_possible_feedbacks(self.size):
            wordgroups[feedback] = set(
                w for w in self.current_words if self.is_consistent(w, self.learn_from_feedback(feedback, word, update=False))
            )
        # remove empty wordgroups
        wordgroups = {k: v for k, v in wordgroups.items() if len(v) > 0}
        return wordgroups

    def wordgroups_entropy(self, wordgroups):
        return sum(len(words) * math.log(len(words), 2) for words in wordgroups.values()) / len(wordgroups)

    def guess_entropy(self, word):
        return self.wordgroups_entropy(self.collect_wordgroups_by_feedback(word))

    def most_informative_guess(self):
        return min([w for w in self.current_words], key=self.guess_entropy)




    def solve(self):
        raise NotImplementedError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wordhoard", type=str, default=FREQ_FILE)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--size", type=int, default=5)
    args = parser.parse_args()
    for feedback in all_possible_feedbacks(args.size):
      if feedback != 'ggggg':
        print(feedback.upper(), end=": ")
        wordhoard = WordHoard(args.wordhoard)
        solver = Solver(wordhoard, args.size)
        solver.learn_from_feedback(feedback, "stear")
        best_guess = solver.most_informative_guess()
        print(best_guess.upper())
        #wordgroups = solver.collect_wordgroups_by_feedback(best_guess)
        #print("Size of wordgroups:", len(wordgroups))
        #print("Average size of wordgroups:", sum(len(words) for words in wordgroups.values()) / len(wordgroups))
        #print("Max size of wordgroups:", max(len(words) for words in wordgroups.values()))
        #print("Entropy:", solver.wordgroups_entropy(wordgroups))
        #print("Bits of information:",  solver.wordgroups_entropy(wordgroups) / math.log(len(wordhoard.words), 2))
