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
    for f, w in zip(feedback, word.upper()):
        if f == "y":
            cf += f"[yellow bold]{w}[/yellow bold]"
        elif f == "g":
            cf += f"[green bold]{w}[/green bold]"
        else:
            cf += f"[strike]{w}[/strike]"
    return cf


statuses = ["Genius", "Magnificent", "Splendid", "Impressive", "Great", "Phew!"]
print("Welcome to Wordle!")
finished = False
turn = 1
good_guesses = []
forbidden_letters = set()
required_letters = set()
matched_letters = set()


def update_stuff(feedback, guess):
    global matched_letters
    global required_letters
    global forbidden_letters
    for f, w in zip(feedback, guess.upper()):
        if f == "g":
            matched_letters.add(w)
        elif f == "y":
            required_letters.add(w)
        else:
            forbidden_letters.add(w)


def letter_status(letter):
    global matched_letters
    global required_letters
    global forbidden_letters
    if letter in matched_letters:
        return f"[green bold]{letter}[/green bold]"
    elif letter in forbidden_letters:
        return "_"
    elif letter in required_letters:
        return f"[yellow bold]{letter}[/yellow bold]"
    else:
        return letter


def alphabet():
    return "".join(
        [letter_status(w) for w in "AEIOU"]
        + [" / "]
        + [letter_status(w) for w in "BCDFGHJKLMNPQRSTVWXYZ"]
    )


while not finished:
    guess = input(f" {turn:2}. Guess a word: ")
    matches_solution, feedback, _, is_valid, is_over = w.make_guess(guess)

    if is_valid:
        turn += 1
        good_guesses.append(guess)
        update_stuff(feedback, guess)
        print(
            f"                   {color_feedback_and_word(feedback, guess)} : {alphabet()}"
        )
    if (is_over and is_valid) or matches_solution:
        finished = True
    if not is_valid:
        print(f"[red]{guess.upper()}[/red] is not a valid guess")
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
