from os import posix_spawn
from re import U
from wordhoard import *
from wordle import *
import time
import json
from collections import Counter
import math
import functools
import argparse


class Solver:
    """A solver for Wordle puzzles"""

    def __init__(self, wordle, verbose=False):
        self.wordle = wordle
        self.wordhoard = WordHoard()
        self.possible_solutions = set(
            [
                word
                for word in self.wordhoard.words
                if self.wordhoard.frequency(word) >= 7500
            ]
        )
        self.forbidden_letters = set()
        self.required_letters = set()
        self.greens = ["·"] * wordle.size
        self.yellows = ["·"] * wordle.size
        self.max_counter = Counter()
        self.verbose = verbose

    def solve(self):
        """Solve the puzzle, maybe"""
        start_time = time.time()
        is_over = False
        matches_solution = False
        while not matches_solution:
            guess = self.guess()
            (
                matches_solution,
                feedback,
                turn,
                is_valid,
                is_over,
            ) = self.wordle.make_guess(guess)
            if is_valid:  # and not matches_solution:
                self.update(guess, feedback)
            if self.verbose:
                word_string = "; ".join(
                    sorted(
                        list(self.possible_solutions)[0:20],
                        key=self.wordhoard.frequency,
                        reverse=True,
                    )
                )
                if len(self.possible_solutions) > 20:
                    word_string += "..."
                status_string = f"{turn:2}. Guessing: {guess} {feedback} words left: {len(self.possible_solutions)}"
                if len(self.possible_solutions) > 0:
                    status_string += f": {word_string}"
                print(status_string)
        return {
            "target": self.wordle.target,
            "solver": self.__class__.__name__,
            "number_guesses": len(self.wordle.guesses()),
            "no_solution": is_over,
            "won": matches_solution
            and len(self.wordle.guesses()) <= self.wordle.max_turns(),
            "found": matches_solution,
            "guesses": self.wordle.guesses(),
            "word_count": len(self.wordle.words),
            "words_left": len(self.possible_solutions),
            "elapsed_time": time.time() - start_time,
        }

    def guess(self):
        """Make a guess"""
        g = self.wordhoard.most_frequent_word(self.possible_solutions)
        return g

    def update(self, guess, feedback):
        self.update_pattern(guess, feedback)
        self.update_required_letters(guess, feedback)
        self.update_forbidden_letters(guess, feedback)
        self.update_possible_solutions(guess)

    def update_pattern(self, guess, feedback):
        """Update the pattern of 'green' letters.
        >>> s = Solver(Wordle(target="audio"))
        >>> s.update_pattern("alder", 'g·g··')
        >>> s.pattern
        ['a', '·', 'd', '·', '·']
        """
        for location, letter in enumerate(feedback):
            if letter.lower() == "g":
                self.greens[location] = guess[location]

    def update_forbidden_letters(self, guess, feedback):
        """Update the pattern of forbidden' letters.
           Must be run after yellow pattern update.
        >>> s = Solver(Wordle(target="audio"))
        >>> s.update_forbidden_letters("alder", 'g·g··')
        >>> s.forbidden_letters == set([ 'l', 'e', 'r'])
        True
        """
        for location, fb in enumerate(feedback):
            if fb.lower() == "·":
                letter = guess[location]
                yellow_greens = (
                    Counter(self.yellows)[letter] + Counter(self.greens)[letter]
                )
                if yellow_greens == 0:
                    self.forbidden_letters.add(letter)

    def update_required_letters(self, guess, feedback):
        """Update the pattern of required' letters.
        >>> s = Solver(Wordle(target="audio"))
        >>> s.update_required_letters("aldos", 'g·gy·')
        >>> s.required_letters == set([ 'a', 'd', 'o'])
        True
        """
        for location, letter in enumerate(feedback):
            if letter.lower() in "gy":
                self.required_letters.add(guess[location])
                self.max_counter[guess[location]] += 1
            if letter.lower() == "y":
                self.yellows[location] = guess[location]

    def update_possible_solutions(self, guess):
        """Update the possible solutions.
        >>> s = Solver(Wordle(target="audio"))
        >>> old_length = len(s.possible_solutions)
        >>> s.update('aldos', 'g·gy·')
        >>> new_length = len(s.possible_solutions)
        >>> old_length > new_length
        True
        """
        words = self.possible_solutions
        words = [
            word
            for word in words
            if word != guess
            and consistent_with_prototype(word, self.greens)
            and consistent_with_forbidden(word, self.forbidden_letters)
            and consistent_with_required(word, self.required_letters)
        ]
        self.possible_solutions = set(words)


def consistent_with_prototype(word, prototype):
    """Return True if the word is consistent with the greens
    >>> consistent_with_prototype("geeks", "geeks")
    True
    >>> consistent_with_prototype("geeks", "g···s")
    True
    >>> consistent_with_prototype("geeks", "s···g")
    False
    >>> consistent_with_prototype("geyan", "····y")
    False
    >>> consistent_with_prototype("geeks", "ge··s")
    True
    """
    for w_letter, p_letter in zip(word, prototype):
        if p_letter == "·":
            continue
        if p_letter != w_letter:
            return False
    return True


def consistent_with_required(word, required):
    """Is every letter in word also in the required set?
    >>> consistent_with_required("geeks", set("eg"))
    True
    >>> consistent_with_required("geeks", set("zwqr"))
    False
    """
    return required.issubset(word)


def consistent_with_forbidden(word, forbidden):
    """Is every letter in word not in the forbidden set?
    >>> consistent_with_forbidden("geeks", set("eg"))
    False
    >>> consistent_with_forbidden("happy", set("morbid"))
    True
    """
    return not forbidden.intersection(word)


def stats(solutions, start_time):
    n = len(solutions)
    number_solved = len(
        list(solution for solution in solutions if solution.get("won") == True)
    )
    percent_solved = 0
    if n > 0:
        percent_solved = number_solved / n
    number_no_solutions = len(
        list([s for s in solutions if s.get("no_solution") == True])
    )
    average_guesses = 0
    max_guesses = 0
    min_guesses = 0
    if n > 0:
        counts = [len(solution.get("guesses")) for solution in solutions]
        average_guesses = sum(counts) / n
        max_guesses = max(counts)
        min_guesses = min(counts)
    return {
        "number_played": n,
        "number_solved": number_solved,
        "percent_solved": percent_solved,
        "failure_rate": 1 - percent_solved,
        "number_no_solutions": number_no_solutions,
        "average_guesses": average_guesses,
        "max_guesses": max_guesses,
        "min_guesses": min_guesses,
        "elapsed_time": time.time() - start_time,
        "solutions": solutions,
    }


## ADDITIONAL SOLVERS


class TwoWordsSolver(Solver):
    """
    The first two guesses are given, then the rest are guessed.
    """

    def guess(self):
        if self.wordle.turn() == 1:
            return "paise"
        if self.wordle.turn() == 2:
            return "boult"
        return super(TwoWordsSolver, self).guess()


class ReductionSolver(Solver):
    """
    We find the most ...
    """

    def best_word(self):
        """Return the best words"""
        mfl = set(self.wordhoard.most_frequent_letters(self.possible_solutions, n=26))
        known_letters = set(self.greens).union(self.yellows)
        required_letters = mfl.difference(known_letters)
        cmp = [
            (
                len(set(word).intersection(required_letters)),
                self.wordhoard.frequency(word),
                word,
            )
            for word in self.possible_solutions
        ]
        guess_pair = max(cmp)
        return guess_pair[2]

    def guess(self):
        best = self.best_word()
        return best


class TwoWordReductionSolver(ReductionSolver):
    """
    We find the most ...
    """

    def guess(self):
        if self.wordle.turn() == 1:
            return "paise"
        if self.wordle.turn() == 2:
            return "boult"
        return super(ReductionSolver, self).guess()


class OneWordReductionSolver(ReductionSolver):
    """
    The first guess is given, then the rest are guessed.
    """

    def guess(self):
        if self.wordle.turn() == 1:
            return "paise"
        return super(OneWordReductionSolver, self).guess()


class UltimaSolver(Solver):
    """
    we'll see
    """

    def guess(self):
        if len(self.possible_solutions) == 1:
            return list(self.possible_solutions)[0]
        if len(self.possible_solutions) <= 4:
            # print("returning most frequent")
            return self.wordhoard.most_frequent_word(self.possible_solutions)
        if self.wordle.turn() == 6:
            return self.wordhoard.most_frequent_word(self.possible_solutions)
        if self.wordle.turn() == 1:
            # return "arise"
            return "adieu"
        return self.best_word()

    def known_letters(self):
        return set(self.forbidden_letters).union(self.required_letters)

    def word_entropy_without_known_letters(self, word, letters):
        """Return the entropy of the word ignoring known letters"""
        entropy = 0
        known = self.known_letters()
        for letter in word:
            if letter in letters:
                continue
            p = self.wordhoard.frequency(letter)
            if p > 0:
                entropy += -p * math.log(p, 2)
        return entropy

    def combine_word_information(self, word, n, intersection, difference):
        freq = self.wordhoard.frequency(word)
        # entropy = self.word_entropy_without_known_letters(word)
        # unknown_letters = set(word).difference(self.known_letters())

        number_of_differences_in_word = len(set(word).intersection(difference))
        entropy = self.word_entropy_without_known_letters(word, intersection)
        return (number_of_differences_in_word, entropy, freq, n, word)

    def all_word_informations(self):
        word_sets = [set(w) for w in self.possible_solutions]
        intersection = intersect_all(word_sets)
        if len(intersection) == self.wordle.size:  # all words are the same set!
            the_word = self.wordhoard.most_frequent_word(self.possible_solutions)
            return [(0, 0, self.wordhoard.frequency(the_word), 1, the_word)]
        union = union_all(word_sets)
        difference = union.difference(intersection)
        if self.verbose:
            dls = "".join(sorted(difference))
            uls = "".join(sorted(union))
            ils = "".join(sorted(intersection))
            print(
                f"                          > Union: {uls}  intersection: {ils}  difference: {dls}"
            )
        possibles = [
            self.combine_word_information(word, 1, intersection, difference)
            for word in self.possible_solutions
        ]
        other_words = [
            word
            for word in self.wordle.words.difference(self.wordle.guesses())
            if self.wordhoard.frequency(word) >= 100_000
        ]
        others = [
            self.combine_word_information(word, 0, intersection, difference)
            for word in other_words
        ]
        return possibles + others

    def best_word(self):
        "best of all possible worlds"
        # word_sets = [set(w) for w in self.possible_solutions]
        # intersection = intersect_all(word_sets)
        # union = union_all(word_sets)
        # difference = union.difference(intersection)
        # dls = "".join(sorted(difference))
        # uls = "".join(sorted(union))
        # ils = "".join(sorted(intersection))
        # print(f"    Union: {uls}  intersection: {ils}  difference: {dls}")
        cmp = self.all_word_informations()
        m = max(cmp)
        # print(f"    Best of all possible words {m}")
        return m[4]


def intersect_all(l):
    return functools.reduce(lambda a, b: a.intersection(b), l)


def union_all(l):
    return functools.reduce(lambda a, b: a.union(b), l)


if __name__ == "__main__":

    example_text = """examples:

 echo 'badly' | python solver.py
 echo 'badly' | python solver.py -v
 cat wordlist.txt | python solver.py"""

    parser = argparse.ArgumentParser(
        epilog=example_text,
        formatter_class=argparse.RawDescriptionHelpFormatter,
        description="Wordle solver",
    )
    parser.add_argument(
        "-v",
        "--verbose",
        help="Run in verbose/debugging mode",
        default=False,
        action="store_true",
    )
    args = parser.parse_args()

    puzzles = sys.stdin.read().splitlines()
    start_time = time.time()

    solutions = []
    for game, puzzle in enumerate(puzzles):
        solutions.append(
            UltimaSolver(Wordle(target=puzzle), verbose=args.verbose).solve()
        )
    statistics = stats(solutions, start_time)
    print(json.dumps(statistics))
