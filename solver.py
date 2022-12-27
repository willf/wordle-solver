import argparse
import json
import math
import time

from rich import print

from wordhoard import *
from wordle import *


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


def stats(solutions, start_time, include_solutions=False):
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
    if include_solutions:
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
    else:
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
        }




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
        self.guesses = []

    def update(self, guess, feedback):
        self.guesses += [guess]

    def possible_solutions(self):
        return self.wordhoard.words

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
                self.update(guess, feedback)
            if self.verbose:
                word_string = "; ".join(
                    sorted(
                        list(self.possible_solutions())[0:20],
                        key=self.wordhoard.frequency,
                        reverse=True,
                    )
                )
                if len(self.possible_solutions()) > 20:
                    word_string += "..."
                status_string = f"{turn:2}. Target: {self.wordle.target} Guessing: {color_feedback(feedback,guess)}/{color_feedback(feedback, feedback)} words left: {len(self.possible_solutions())}"
                if len(self.possible_solutions()) > 0:
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
            "words_left": len(self.possible_solutions()),
            "elapsed_time": time.time() - start_time,
        }

    def guess(self):
        """Make a guess"""
        raise NotImplementedError("Guess not implemented")



def create_solver(solver_name, wordle, wordhoard, opts):
    """Create a solver by name"""
    if solver_name == "random":
        from random_solver import RandomSolver
        return RandomSolver(wordle, wordhoard, opts.verbose)
    elif solver_name == "frequency":
        from frequency_based_solver import FrequencyBasedSolver
        return FrequencyBasedSolver(wordle, wordhoard, opts.verbose)
    elif solver_name == "ir":
        from ir_solver import InfoTheoreticSolver
        return InfoTheoreticSolver(wordle, wordhoard, opts.verbose, opts.mode, opts.top_n)
    elif solver_name == "norvig":
        from norvig_solver import NorvigSolver
        return NorvigSolver(wordle, wordhoard, opts.verbose)
    else:
        raise ValueError(f"Unknown solver: {solver_name}")

if __name__ == "__main__":

    from signal import SIG_DFL, SIGPIPE, signal

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

    parser.add_argument("-g", "--guesses", help="Supplied Guesses", default=None)

    parser.add_argument("-w", "--words", help="Supplied Words", default=None)

    parser.add_argument('-s', '--solver', help='Solver class (frequency, random)', default='frequency' )

    parser.add_argument('-m', '--mode', help='Mode (hard/easy)', default='easy' )

    parser.add_argument('-n', '--top_n', help='Top N words to use', default=4500, type=int )

    args = parser.parse_args()
    if args.mode not in ['easy', 'hard']:
        raise ValueError(f"Unknown mode: {args.mode}")
    args.easy_mode = args.mode == 'easy'
    if args.solver not in ['frequency', 'random', 'ir', 'norvig']:
        raise ValueError(f"Unknown solver: {args.solver}")


    # puzzles = sys.stdin.read().splitlines()
    start_time = time.time()

    wordhoard = None
    if args.words:
        wordhoard = WordHoard(file=args.words)

    guesses = []
    if args.guesses:
        guesses = [guess.strip() for guess in args.guesses.split(",")]
    solutions = []
    for game, puzzle in enumerate(sys.stdin):
        solver = create_solver(args.solver, Wordle(target=puzzle.strip(), wordhoard=wordhoard), wordhoard, args)
        solutions.append(solver.solve(guesses=guesses))
    statistics = stats(solutions, start_time)
    print(json.dumps(statistics))
