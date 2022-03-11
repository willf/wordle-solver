from wordhoard import *
from wordle import *
import time
import json
from collections import Counter
import math
import functools
import argparse
from rich import print


def color_feedback(feedback, word):
    cf = ""
    for f, w in zip(feedback, word):
        if f == "y":
            cf += f"[yellow]{w}[/yellow]"
        elif f == "g":
            cf += f"[green]{w}[/green]"
        else:
            cf += f"[white]{w}[/white]"
    return cf


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


class WordleKnowledge:
    def __init__(self, wordle, wordhoard):
        self.counter = Counter()
        for word in wordhoard.words:
            for letter in word:
                self.counter[letter] += 1
        letters = sorted(self.counter.keys())
        self.letter_sets = [set(letters) for i in range(wordle.size)]
        self.required_letters = set()
        self.wordle = wordle
        self.wordhoard = wordhoard

    def is_consistent(self, word):
        for i in range(self.wordle.size):
            letter = word[i]
            letter_set = self.letter_sets[i]
            found = letter in letter_set
            if not found:
                return False
        return all(letter in word for letter in self.required_letters)

    def update_exact(self, letter, position):
        self.required_letters.add(letter)
        self.letter_sets[position] = set(letter)

    def update_required(self, letter, position):
        self.required_letters.add(letter)
        if letter in self.letter_sets[position]:
            self.letter_sets[position].remove(letter)

    def update_forbidden(self, letter, position):
        for letter_set in self.letter_sets:
            if letter in letter_set and letter not in self.required_letters:
                letter_set.remove(letter)

    def __repr__(self):
        return f"{self.required_letters} {self.letter_sets}"


class Solver:
    """ 
    Solver class for the wordle puzzle
    """

    def __init__(self, wordle, wordhoard=None, verbose=False):
        self.wordle = wordle
        if wordhoard is None:
            self.wordhoard = WordHoard()
        else:
            self.wordhoard = wordhoard
        self.verbose = verbose
        self.state = WordleKnowledge(wordle, self.wordhoard)
        self.possible_solutions = set(self.wordhoard.words)

    def update_knowledge(self, guess, feedback):
        """Update the knowledge of the wordle puzzle
        """
        # print(f"[bold blue]{guess}[/bold blue]; {color_feedback(feedback, guess)}")
        for i in range(self.wordle.size):
            if feedback[i] == "g":
                self.state.update_exact(guess[i], i)
            elif feedback[i] == "y":
                self.state.update_required(guess[i], i)
            else:
                self.state.update_forbidden(guess[i], i)
        self.possible_solutions = [
            word
            for word in self.possible_solutions
            if self.state.is_consistent(word) and word != guess
        ]
        # print(f"{len(self.possible_solutions)} possible solutions")

    def solve(self, guesses=[], max_turns=math.inf):
        """Solve the wordle puzzle, maybe"""
        if self.verbose:
            print(f"Target: {self.wordle.target}")
        start_time = time.time()
        index = 0
        solved = False
        while not solved and index < max_turns:
            if index < len(guesses):
                guess = guesses[index]
            else:
                guess = self.guess()
            index += 1
            (solved, feedback, turn, is_valid, is_over,) = self.wordle.make_guess(guess)

            if is_valid:
                self.update_knowledge(guess, feedback)
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
                status_string = f"{turn:2}. Target: {self.wordle.target} Guessing: {color_feedback(feedback,guess)}/{color_feedback(feedback, feedback)} words left: {len(self.possible_solutions)}"
                if len(self.possible_solutions) > 0:
                    status_string += f": {word_string}"
                print(status_string)

        return {
            "target": self.wordle.target,
            "solver": self.__class__.__name__,
            "number_guesses": len(self.wordle.guesses()),
            "won": solved and len(self.wordle.guesses()) <= self.wordle.max_turns(),
            "found": solved,
            "guesses": self.wordle.guesses(),
            "word_count": len(self.wordle.words),
            "words_left": len(self.possible_solutions),
            "elapsed_time": time.time() - start_time,
        }

    def guess(self):
        """Make a guess"""
        return self.wordhoard.most_frequent_word(self.possible_solutions)


if __name__ == "__main__":

    from signal import signal, SIGPIPE, SIG_DFL

    signal(SIGPIPE, SIG_DFL)

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
    parser.add_argument(
        "--norvig",
        help="Use the Norvig list: handy, swift, glove, crump",
        default=False,
        action="store_true",
    )
    parser.add_argument("-g", "--guesses", help="Supplied Guesses", default=None)

    parser.add_argument("-w", "--words", help="Supplied Words", default=None)

    args = parser.parse_args()

    # puzzles = sys.stdin.read().splitlines()
    start_time = time.time()

    wordhoard = None
    if args.words:
        wordhoard = WordHoard(file=args.words)

    guesses = []
    if args.guesses:
        guesses = [guess.strip() for guess in args.guesses.split(",")]
    if args.norvig:
        guesses = "handy,swift,glove,crump".split(",")
    solutions = []
    for game, puzzle in enumerate(sys.stdin):
        solutions.append(
            Solver(
                Wordle(target=puzzle.strip(), wordhoard=wordhoard),
                verbose=args.verbose,
                wordhoard=wordhoard,
            ).solve(guesses=guesses)
        )
    statistics = stats(solutions, start_time)
    print(json.dumps(statistics))
