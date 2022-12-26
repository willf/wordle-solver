import os
import random
import sys
from collections import Counter

from globals import FREQ_FILE, SOLUTION_FILE
from wordhoard import WordHoard

WORD_SIZE = 5


class Wordle:
    def __init__(self, size=WORD_SIZE, target=None, max_turns=6, wordhoard=None):
        """Initialize the wordle with a given size etc
        >>> w = Wordle()
        >>> w.size
        5
        >>> len(w.words) > 1000
        True
        >>> w.target in w.words
        True
        >>> w.max_turns()
        6
        """
        self.size = size
        if wordhoard is None:
            self.wordhoard = WordHoard(FREQ_FILE)
        else:
            self.wordhoard = wordhoard
        words = self.wordhoard.words

        assert all(len(word) == size for word in words)
        self.words = words
        if target:
            if target not in self.words:
                print(f"Target word {target} not in word list")
                sys.exit(1)
            assert target in self.words
            self.target = target
        else:
            # frequent = self.wordhoard.words_with_frequency(size)
            self.target = random.choice(list(self.words))
        self._turn = 1
        self._max_turns = max_turns
        self._guesses = []

    def feedback(self, word, target):
        """Return a feedback string for a given word and target
        >>> w = Wordle(5)
        >>> w.feedback("audio", "audio")
        'ggggg'
        >>> w.feedback("rived", "liver")
        'yggg·'
        >>> w.feedback("abcde", "ezzzz")
        '····y'
        >>> w.feedback("audio", "liver")
        '···y·'
        >>> w.feedback('blood', 'knoll')
        '·yg··'
        >>> w.feedback('ollas', 'knoll')
        'yyy··'
        >>> w.feedback('lulls', 'knoll')
        'y··g·'
        """
        feedback = ["·"] * self.size
        green_counts = Counter()
        letter_counts = Counter(target)
        yellow_counts = Counter()
        # Do Green
        for i in range(self.size):
            if word[i] == target[i]:
                feedback[i] = "g"
                green_counts[word[i]] += 1
        # Do yellow
        for i in range(self.size):
            if word[i] in target and word[i] != target[i]:
                yellow_counts[word[i]] += 1
                if (
                    yellow_counts[word[i]] + green_counts[word[i]]
                    <= letter_counts[word[i]]
                ):
                    feedback[i] = "y"
        return "".join(feedback)

    def matches_solution(self, word):
        """Return True if the word is solved, False otherwise
        >>> w = Wordle(target="audio")
        >>> w.matches_solution("audio")
        True
        >>> w.matches_solution("radio")
        False
        """
        return word == self.target

    def is_valid(self, word):
        """Return True if the word is a valid guess
        >>> w = Wordle(target="audio")
        >>> w.is_valid("audio")
        True
        >>> w.is_valid("*****")
        False
        """
        return word in self.words

    def turn(self):
        """Return the current turn number
        >>> w = Wordle(target="audio")
        >>> w.turn()
        1
        """
        return self._turn

    def max_turns(self):
        """Return the maximum number of turns
        >>> w = Wordle(target="audio")
        >>> w.max_turns()
        6
        """
        return self._max_turns

    def is_over(self):
        """Return True if the game is over, False otherwise
        >>> w = Wordle(target="audio")
        >>> w.is_over()
        False
        >>> fb = w.make_guess("audio")
        >>> w.is_over()
        True
        """
        return self._turn >= self._max_turns or (
            any(self.matches_solution(guess) for guess in self.guesses())
        )

    def solution(self):
        """Return the solution
        >>> w = Wordle(target="audio")
        >>> w.solution()
        'audio'
        """
        return self.target

    def guesses(self):
        """Return a list of guesses
        >>> w = Wordle(target="audio")
        >>> g = w.make_guess("audio")
        >>> w.guesses()
        ['audio']
        """
        return self._guesses

    def give_feedback(self, word):
        """
        Return a tuple of (matches_solution, feedback, turn, is_valid)
        >>> w = Wordle(target="audio")
        >>> w.give_feedback("audio") # note no guess actually made yet
        (True, 'ggggg', 1, True, False)
        >>> w.give_feedback("radio")
        (False, '·yggg', 1, True, False)
        """
        return (
            self.matches_solution(word),
            self.feedback(word, self.target),
            self.turn(),
            self.is_valid(word),
            self.is_over(),
        )

    def make_guess(self, guess):
        """Take a turn and return a tuple of (matches_solution, feedback, turn, is_valid, is_over)
        >>> w = Wordle(target="audio")
        >>> w.make_guess("audio")
        (True, 'ggggg', 1, True, True)
        >>> w.make_guess("radio") # note, we are guessing again even tho solved
        (False, '·yggg', 2, True, True)
        >>> w = Wordle(target="audio")
        >>> fs = [w.make_guess(guess) for guess in ["river", "talks", "radio", "fishy", "buddy"]]
        >>> w.make_guess("ocean")
        (False, 'y··y·', 6, True, True)

        """
        self._guesses.append(guess)
        f = self.give_feedback(guess)
        _, _, _, is_valid, _ = f
        if is_valid:
            self._turn += 1
        return f

    def make_guesses(self, *guesses):
        """Make several guesses and return feebacks"""
        return [self.make_guess(guess) for guess in guesses]


def wordle_number(n):
    """Return a wordle game where the target is the nth entry in puzzles.txt
    >>> w = wordle_number(0)
    >>> w.solution()
    'cigar'
    """
    puzzles = [line.strip() for line in open(SOLUTION_FILE)]
    return Wordle(target=puzzles[n])


if __name__ == "__main__":
    import doctest

    print("Testing...")
    doctest.testmod()
    print("Done.")
