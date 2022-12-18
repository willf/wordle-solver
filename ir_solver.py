import argparse
import functools
import itertools
import json
import math
import string
import time
from collections import Counter

from rich import print

from globals import FREQ_FILE
from wordhoard import *


def all_possible_feedbacks(size):
    """Return a list of all possible feedbacks for a given size"""
    return ["".join(p) for p in itertools.product("byg", repeat=size)]

class Solver:
    def __init__(self, wordhoard, size = 5):
        self.size = size
        self.wordhoard = wordhoard
        self.history = []
        self.feedback = []
        self.possibles = [set(string.ascii_lowercase) for _ in range(self.size)]
        self.current_words = set(wordhoard.words)

    def learn_from_feedback(self, feedback, word, update=True):
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

    def display_possibles(self):
        for i, p in enumerate(self.possibles):
            print(f"{i:2d}:", ''.join(sorted(list(p))))

    def is_consistent(self, word, possibles=None, verbose=False):
        if possibles is None:
            possibles = self.possibles
        if verbose:
            print("checking", word, "for consistency", end =":")
        for i, c in enumerate(word):
            if c not in possibles[i]:
                if verbose:
                    print("inconsistent at", i, "because", c, "not in", ''.join(sorted(list(possibles[i]))))
                return False
        if verbose:
            print("consistent")
        return True

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

    def solve(self):
        raise NotImplementedError

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--wordhoard", type=str, default=FREQ_FILE)
    parser.add_argument("--verbose", action="store_true")
    parser.add_argument("--size", type=int, default=5)
    args = parser.parse_args()
    wordhoard = WordHoard(args.wordhoard)
    solver = Solver(wordhoard, args.size)
    solver.is_consistent("stear", verbose=True)
    solver.learn_from_feedback("bbbby", "stear")
    #solver.learn_from_feedback("bybbb", "brain")
    #solver.is_consistent("stear", verbose=True)
    #solver.is_consistent("rough", verbose=True)
    #solver.learn_from_feedback('yybby', 'rough')
    #solver.display_possibles()
    #solver.is_consistent("whorl", verbose=True)
    #solver.learn_from_feedback('bgggb', 'whorl')
    print("CRONY")
    wordgroups = solver.collect_wordgroups_by_feedback('crony')
    print("Size of wordgroups:", len(wordgroups))
    print("Average size of wordgroups:", sum(len(words) for words in wordgroups.values()) / len(wordgroups))
    print("Max size of wordgroups:", max(len(words) for words in wordgroups.values()))

    # print out all the wordgroups
    feedbacks = sorted(wordgroups.keys())
    for feedback in feedbacks:
        words = sorted(wordgroups[feedback])
        if feedback == 'bggbb':
          nyt = set(['broil', 'brood', 'brook', 'broom', 'droid', 'droll', 'drool', 'droop', 'groom', 'group', 'growl', 'promo', 'proof', 'proud', 'prowl', 'vroom'])
          w = set(words)
          print("NYT:", nyt - w)
          print("ME:", w - nyt)
          print("BOTH:", w & nyt)
    #wordgroups = solver.collect_wordgroups_by_feedback('brain')
    #print("Size of wordgroups:", len(wordgroups))
    #print("Average size of wordgroups:", sum(len(words) for words in wordgroups.values()) / len(wordgroups))
    #print("Max size of wordgroups:", max(len(words) for words in wordgroups.values()))

# TODO -- do infomation gain analysis
# TODO -- do a search for the best word to guess
# TODO -- interactive mode
