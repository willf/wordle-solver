from hashlib import new
from wordle import Wordle, wordle_number
from rich import print
import argparse
import random

parser = argparse.ArgumentParser()
parser.add_argument(
    "-n", "--number", help="Archived Wordle game", type=int, default=None
)
args = parser.parse_args()

if args.number == None:
    w = Wordle()
    frequent_words = w.wordhoard.words_with_frequency(frequency=100000)
    target = random.choice(frequent_words)
    w.target = target
else:
    w = wordle_number(args.number)


def color_feedback(feedback):
    return feedback.replace("y", "🟨").replace("g", "🟩").replace("·", "⬜")


def color_feedback_and_word(feedback, word):
    cf = ""
    for f, w in zip(feedback, word):
        if f == "y":
            cf += f"[yellow]{w}[/yellow]"
        elif f == "g":
            cf += f"[green]{w}[/green]"
        else:
            cf += f"[white]{w}[/white]"
    return cf


statuses = ["Genius", "Magnificent", "Splendid", "Impressive", "Great", "Phew!"]
print("Welcome to Wordle!")
finished = False
turn = 1
good_guesses = []
while not finished:
    guess = input(f" {turn:2}. Guess a word: ")
    matches_solution, feedback, _, is_valid, is_over = w.make_guess(guess)

    if is_valid:
        turn += 1
        good_guesses.append(guess)
        print(f"                   {color_feedback_and_word(feedback, guess)}")
    if (is_over and is_valid) or matches_solution:
        finished = True
    if not is_valid:
        print(f"[red]{guess}[/red] is not a valid guess")
    if (is_over and is_valid) and not matches_solution:
        print(f"\nAnswer was: [green]{w.target}[/green]")

if matches_solution and turn <= w.max_turns() + 1:
    print(f"\n[green]{statuses[turn-2]}![/green]")
if args.number != None:
    print(f"\nWordle {args.number} {turn-1}/6")
else:
    print(f"\nWordle {turn-1}/6")
for i, guess in enumerate(good_guesses):
    print(f"{color_feedback(w.feedback(guess, w.target))}")
